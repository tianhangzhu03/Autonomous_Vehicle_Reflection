from __future__ import annotations

import numpy as np

VALID_MODES = {"camera_only", "multi_sensor_permissive", "mitigation"}


class FusionAndPlanner:
    """Fusion and planning logic for three stacks:

    1) camera_only
    2) multi_sensor_permissive
    3) mitigation (contradiction-aware + conservative unknown handling)
    """

    def __init__(self, mode: str) -> None:
        if mode not in VALID_MODES:
            raise ValueError(f"Unsupported mode: {mode}")

        self.mode = mode
        self.v_nominal_a1 = 8.0
        self.v_nominal_a2 = 5.0
        self.v_creep = 1.5
        self.ttc_safe = 3.0

        if mode == "camera_only":
            self.a1_conf_threshold = 0.58
            self.w_cam, self.w_lid, self.w_rad = 1.0, 0.0, 0.0
            self.lambda_var = 0.0
        elif mode == "multi_sensor_permissive":
            self.a1_conf_threshold = 0.62
            self.w_cam, self.w_lid, self.w_rad = 0.65, 0.20, 0.15
            self.lambda_var = 0.0
        else:
            self.a1_conf_threshold = 0.74
            self.w_cam, self.w_lid, self.w_rad = 0.65, 0.20, 0.15
            self.lambda_var = 0.65

        self._track_memory = 0.05

        # A2 hysteresis state (used in mitigation only).
        self._a2_risk_state = 0.0
        self._a2_speed_cap = self.v_nominal_a2

    def update_a1_track_confidence(
        self,
        track_conf: float,
        cam_prob: float,
        lid_prob: float,
        rad_prob: float,
    ) -> tuple[float, float]:
        """Return (updated_track_conf, contradiction_score)."""
        cam_prob = float(np.clip(cam_prob, 0.0, 1.0))
        lid_prob = float(np.clip(lid_prob, 0.0, 1.0))
        rad_prob = float(np.clip(rad_prob, 0.0, 1.0))

        if self.mode == "camera_only":
            evidence = np.array([cam_prob, 0.0, 0.0], dtype=float)
            additive = cam_prob
        else:
            evidence = np.array([cam_prob, lid_prob, rad_prob], dtype=float)
            additive = self.w_cam * cam_prob + self.w_lid * lid_prob + self.w_rad * rad_prob

        contradiction = float(np.var(evidence))
        fused = float(np.clip(additive - self.lambda_var * contradiction, 0.0, 1.0))

        updated = 0.38 * track_conf + 0.62 * fused
        self._track_memory = 0.82 * self._track_memory + 0.18 * updated
        return float(np.clip(updated, 0.0, 1.0)), contradiction

    def plan_a1_target_speed(
        self,
        track_conf: float,
        contradiction: float,
        ttc_virtual: float,
        current_speed: float,
    ) -> float:
        if not np.isfinite(ttc_virtual):
            return self.v_nominal_a1

        if self.mode == "camera_only":
            if track_conf >= self.a1_conf_threshold and ttc_virtual < self.ttc_safe:
                severity = np.clip((self.ttc_safe - ttc_virtual) / self.ttc_safe, 0.0, 1.0)
                return float(max(0.0, self.v_nominal_a1 * (1.0 - 1.45 * severity)))
            return self.v_nominal_a1

        if self.mode == "multi_sensor_permissive":
            if track_conf >= self.a1_conf_threshold and ttc_virtual < self.ttc_safe:
                severity = np.clip((self.ttc_safe - ttc_virtual) / self.ttc_safe, 0.0, 1.0)
                return float(max(0.0, self.v_nominal_a1 * (1.0 - 1.30 * severity)))
            return self.v_nominal_a1

        # mitigation: contradiction-first arbitration
        if contradiction > 0.11 and ttc_virtual < self.ttc_safe:
            return float(min(self.v_nominal_a1, max(5.4, current_speed - 0.22)))

        if track_conf >= self.a1_conf_threshold and contradiction < 0.08 and ttc_virtual < 2.0:
            return float(max(0.0, self.v_nominal_a1 * (ttc_virtual / 2.0)))

        return self.v_nominal_a1

    @staticmethod
    def _normalize(cell: np.ndarray) -> np.ndarray:
        cell = np.clip(cell.astype(float), 0.0, None)
        s = float(np.sum(cell))
        if s <= 1e-12:
            return np.array([0.0, 0.0, 1.0], dtype=float)
        return cell / s

    def update_grid_and_plan(
        self,
        cell: np.ndarray,
        cam_free_prob: float,
        lid_occ_prob: float,
        distance_to_door: float,
    ) -> tuple[np.ndarray, float, float]:
        """Update evidential cell and return (updated_cell, target_speed, risk_score)."""
        m_o, m_f, m_u = [float(v) for v in cell]
        cam_free_prob = float(np.clip(cam_free_prob, 0.0, 1.0))
        lid_occ_prob = float(np.clip(lid_occ_prob, 0.0, 1.0))

        if self.mode == "camera_only":
            kappa = cam_free_prob
            new_m_f = m_f + kappa * m_u
            new_m_u = (1.0 - kappa) * m_u
            new_m_o = m_o
            updated = self._normalize(np.array([new_m_o, new_m_f, new_m_u], dtype=float))
            return updated, self.v_nominal_a2, 0.0

        if self.mode == "multi_sensor_permissive":
            # Missing depth is implicitly interpreted as free support.
            kappa = np.clip(0.75 * cam_free_prob + 0.20 * (1.0 - lid_occ_prob), 0.0, 1.0)
            new_m_f = m_f + kappa * m_u
            new_m_u = (1.0 - kappa) * m_u
            new_m_o = m_o + 0.22 * lid_occ_prob * new_m_u
            updated = self._normalize(np.array([new_m_o, new_m_f, new_m_u], dtype=float))
            return updated, self.v_nominal_a2, 0.0

        # mitigation: keep uncertainty when visual free-space conflicts with depth evidence.
        contradiction = np.clip(cam_free_prob - lid_occ_prob, 0.0, 1.0)
        if contradiction > 0.65:
            new_m_u = max(m_u, 0.65 + 0.25 * contradiction)
            new_m_f = min(m_f, 0.25)
            new_m_o = max(m_o, 0.05 + 0.08 * lid_occ_prob)
        else:
            kappa = np.clip(cam_free_prob * (0.25 + 0.50 * lid_occ_prob), 0.0, 0.55)
            new_m_f = m_f + kappa * m_u
            residual_u = (1.0 - kappa) * m_u
            new_m_o = m_o + 0.55 * lid_occ_prob * residual_u
            new_m_u = max(0.0, residual_u - 0.55 * lid_occ_prob * residual_u)

        updated = self._normalize(np.array([new_m_o, new_m_f, new_m_u], dtype=float))

        # Continuous risk + hysteresis speed policy to avoid threshold-induced jerk spikes.
        near_factor = np.clip((18.0 - distance_to_door) / 18.0, 0.0, 1.0)
        risk = float(updated[2] * near_factor)

        if risk > 0.58:
            self._a2_risk_state = min(1.0, 0.82 * self._a2_risk_state + 0.28 * risk + 0.12)
        elif risk < 0.42:
            self._a2_risk_state = max(0.0, 0.75 * self._a2_risk_state + 0.25 * risk - 0.06)
        else:
            self._a2_risk_state = 0.90 * self._a2_risk_state + 0.10 * risk

        self._a2_risk_state = float(np.clip(self._a2_risk_state, 0.0, 1.0))
        smooth_risk = self._a2_risk_state**1.25
        desired_cap = self.v_nominal_a2 * (1.0 - 0.95 * smooth_risk)
        desired_cap = max(0.2, desired_cap)

        if distance_to_door < 5.0 and updated[2] > 0.55:
            desired_cap = min(desired_cap, 1.0)
        if distance_to_door < 2.2 and updated[2] > 0.68:
            desired_cap = min(desired_cap, 0.15)

        if desired_cap < self._a2_speed_cap:
            self._a2_speed_cap = desired_cap
        else:
            self._a2_speed_cap = min(self.v_nominal_a2, self._a2_speed_cap + 0.35)

        return updated, float(self._a2_speed_cap), self._a2_risk_state
