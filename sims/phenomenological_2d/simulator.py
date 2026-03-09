from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .evidential_grid import EvidentialGrid
from .fusion_planner import FusionAndPlanner, VALID_MODES

try:
    from scipy.signal import savgol_filter
except Exception:  # pragma: no cover - optional smoothing fallback
    savgol_filter = None


@dataclass
class A1Case:
    total_time_s: float
    x_goal: float
    ghost_world_x: float
    visible_back_margin: float
    visible_front_margin: float
    reflection_strength: float
    noise_scale: float
    init_speed: float
    slope: float


@dataclass
class A2Case:
    total_time_s: float
    x_goal_margin_after_door: float
    grid_size: tuple[int, int]
    cell_size_m: float
    door_col: int
    door_half_height_cells: int
    transparency: float
    noise_scale: float
    init_speed: float
    slope: float
    depth_void_span_m: float


class CAVSimulation:
    """Closed-loop phenomenological 2D simulator for A1/A2."""

    def __init__(self, seed: int = 0, dt: float = 0.1) -> None:
        self.seed = seed
        self.dt = dt
        self.rng = np.random.default_rng(seed)

    @staticmethod
    def _control_step(
        speed: float,
        target_speed: float,
        *,
        tau: float,
        a_min: float,
        a_max: float,
    ) -> float:
        raw = (target_speed - speed) / max(tau, 1e-6)
        return float(np.clip(raw, a_min, a_max))

    @staticmethod
    def _apply_grade(a_cmd: float, slope: float, a_min: float, a_max: float) -> float:
        # Approximate longitudinal gravity component.
        a_total = a_cmd - 9.81 * slope
        return float(np.clip(a_total, a_min, a_max))

    def _smooth(self, data: np.ndarray) -> np.ndarray:
        if savgol_filter is None or data.size < 9:
            return data
        window = min(11, data.size - (1 - data.size % 2))
        if window < 5:
            return data
        return savgol_filter(data, window_length=window, polyorder=2)

    def sample_a1_case(self) -> A1Case:
        return A1Case(
            total_time_s=14.0 + float(self.rng.uniform(-1.0, 2.0)),
            x_goal=62.0 + float(self.rng.uniform(-4.0, 6.0)),
            ghost_world_x=42.0 + float(self.rng.uniform(-6.0, 8.0)),
            visible_back_margin=float(self.rng.uniform(4.0, 10.0)),
            visible_front_margin=float(self.rng.uniform(28.0, 40.0)),
            reflection_strength=float(self.rng.uniform(0.72, 0.98)),
            noise_scale=float(self.rng.uniform(0.70, 1.55)),
            init_speed=float(self.rng.uniform(7.0, 9.5)),
            slope=float(self.rng.uniform(-0.05, 0.05)),
        )

    def sample_a2_case(self) -> A2Case:
        return A2Case(
            total_time_s=19.0 + float(self.rng.uniform(-2.0, 3.5)),
            x_goal_margin_after_door=float(self.rng.uniform(6.5, 10.5)),
            grid_size=(60, 60),
            cell_size_m=float(self.rng.uniform(0.68, 0.82)),
            door_col=int(self.rng.integers(34, 47)),
            door_half_height_cells=int(self.rng.integers(2, 5)),
            transparency=float(self.rng.uniform(0.72, 0.98)),
            noise_scale=float(self.rng.uniform(0.75, 1.60)),
            init_speed=float(self.rng.uniform(2.0, 5.0)),
            slope=float(self.rng.uniform(-0.06, 0.06)),
            depth_void_span_m=float(self.rng.uniform(5.0, 10.0)),
        )

    def run_a1(self, mode: str, *, case: A1Case | None = None, noise_seed: int | None = None) -> dict[str, Any]:
        if mode not in VALID_MODES:
            raise ValueError(f"Unsupported mode: {mode}")
        case = case if case is not None else self.sample_a1_case()
        rng = np.random.default_rng(self.seed + 101 if noise_seed is None else noise_seed)

        planner = FusionAndPlanner(mode=mode)

        steps = int(case.total_time_s / self.dt)
        t = np.arange(steps) * self.dt

        x = 0.0
        v = case.init_speed
        track_conf = 0.05

        speed = np.zeros(steps, dtype=float)
        accel = np.zeros(steps, dtype=float)
        target_speed = np.zeros(steps, dtype=float)
        ttc_virtual = np.full(steps, np.inf, dtype=float)
        track_hist = np.zeros(steps, dtype=float)
        contradiction_hist = np.zeros(steps, dtype=float)

        reached_goal_idx: int | None = None

        for k in range(steps):
            distance = case.ghost_world_x - x
            ghost_visible = -case.visible_back_margin <= distance <= case.visible_front_margin

            noise_scale = case.noise_scale
            if ghost_visible:
                cam_mean = 0.82 + 0.16 * case.reflection_strength
                cam_prob = np.clip(cam_mean + 0.06 * noise_scale * rng.standard_normal(), 0.0, 1.0)
                # reflective ambiguity: lidar/radar are weak but not fully zero.
                lid_prob = np.clip(0.06 + 0.20 * (1.0 - case.reflection_strength) + 0.10 * noise_scale * abs(rng.standard_normal()), 0.0, 1.0)
                rad_prob = np.clip(0.08 + 0.24 * case.reflection_strength + 0.12 * noise_scale * abs(rng.standard_normal()), 0.0, 1.0)
            else:
                cam_prob = np.clip(0.06 + 0.05 * noise_scale * abs(rng.standard_normal()), 0.0, 1.0)
                lid_prob = np.clip(0.05 + 0.05 * noise_scale * abs(rng.standard_normal()), 0.0, 1.0)
                rad_prob = np.clip(0.05 + 0.07 * noise_scale * abs(rng.standard_normal()), 0.0, 1.0)

            track_conf, contradiction = planner.update_a1_track_confidence(track_conf, cam_prob, lid_prob, rad_prob)

            if ghost_visible and distance > 0.0:
                ttc_k = distance / max(v, 0.1)
            else:
                ttc_k = np.inf

            v_target = planner.plan_a1_target_speed(track_conf, contradiction, ttc_k, v)
            a_cmd = self._control_step(v, v_target, tau=0.35, a_min=-6.8, a_max=2.6)
            a = self._apply_grade(a_cmd, case.slope, -6.8, 2.6)

            x += v * self.dt + 0.5 * a * self.dt * self.dt
            v = max(0.0, v + a * self.dt)

            if reached_goal_idx is None and x >= case.x_goal:
                reached_goal_idx = k

            speed[k] = v
            accel[k] = a
            target_speed[k] = v_target
            ttc_virtual[k] = ttc_k
            track_hist[k] = track_conf
            contradiction_hist[k] = contradiction

        jerk = np.abs(np.diff(accel, prepend=accel[0])) / self.dt
        event_mask = np.isfinite(ttc_virtual) & (ttc_virtual < planner.ttc_safe)

        pbs = float(np.max(np.abs(accel[event_mask])) if np.any(event_mask) else 0.0)
        false_brake_count = int(np.sum((accel < -3.0) & event_mask))
        gtp = float(np.sum(track_hist >= planner.a1_conf_threshold) * self.dt)

        if reached_goal_idx is None:
            travel_time = float(case.total_time_s)
            reached_goal = 0
        else:
            travel_time = float(t[reached_goal_idx])
            reached_goal = 1

        return {
            "scenario": "A1",
            "mode": mode,
            "time": t,
            "speed": self._smooth(speed),
            "accel": accel,
            "target_speed": target_speed,
            "ttc_virtual": ttc_virtual,
            "track_conf": track_hist,
            "contradiction": contradiction_hist,
            "case": case,
            "metrics": {
                "pbs": pbs,
                "false_brake_frames": false_brake_count,
                "ghost_track_persistence_s": gtp,
                "peak_jerk": float(np.max(jerk)),
                "min_accel": float(np.min(accel)),
                "travel_time_s": travel_time,
                "avg_speed": float(np.mean(speed)),
                "speed_efficiency_ratio": float(np.mean(speed) / max(planner.v_nominal_a1, 1e-6)),
                "reached_goal": reached_goal,
                "min_ttc_virtual": float(np.nanmin(ttc_virtual[np.isfinite(ttc_virtual)]) if np.any(np.isfinite(ttc_virtual)) else np.inf),
            },
        }

    def run_a2(self, mode: str, *, case: A2Case | None = None, noise_seed: int | None = None) -> dict[str, Any]:
        if mode not in VALID_MODES:
            raise ValueError(f"Unsupported mode: {mode}")
        case = case if case is not None else self.sample_a2_case()
        rng = np.random.default_rng(self.seed + 202 if noise_seed is None else noise_seed)

        planner = FusionAndPlanner(mode=mode)

        steps = int(case.total_time_s / self.dt)
        t = np.arange(steps) * self.dt

        grid = EvidentialGrid(case.grid_size)
        row_center = case.grid_size[0] // 2
        door_rows = np.arange(
            row_center - case.door_half_height_cells,
            row_center + case.door_half_height_cells + 1,
            dtype=int,
        )
        door_cols = np.full_like(door_rows, case.door_col)
        door_cells = list(zip(door_rows.tolist(), door_cols.tolist()))

        door_x_world = case.door_col * case.cell_size_m
        x_goal = door_x_world + case.x_goal_margin_after_door

        x = 0.0
        v = case.init_speed

        speed: list[float] = []
        accel: list[float] = []
        target_speed: list[float] = []
        x_hist: list[float] = []
        evr_hist: list[float] = []
        unknown_center_hist: list[float] = []
        risk_hist: list[float] = []

        crossed_idx: int | None = None
        reached_goal_idx: int | None = None
        collision = False

        for k in range(steps):
            distance_to_door = door_x_world - x
            near_door = -1.5 <= distance_to_door <= 16.0
            depth_zone = 0.0 <= distance_to_door <= case.depth_void_span_m

            noise_scale = case.noise_scale
            base_cam_free = 0.45 + 0.50 * case.transparency
            base_lid_occ = 0.38 * (1.0 - case.transparency)

            if near_door:
                cam_free = np.clip(base_cam_free + 0.08 * noise_scale * rng.standard_normal(), 0.0, 1.0)
            else:
                cam_free = np.clip(0.50 + 0.06 * noise_scale * rng.standard_normal(), 0.0, 1.0)

            if depth_zone:
                # Depth void probability increases with transparency and proximity.
                proximity = np.clip((case.depth_void_span_m - distance_to_door) / max(case.depth_void_span_m, 1e-6), 0.0, 1.0)
                p_void = float(np.clip(0.20 + 0.75 * case.transparency * proximity, 0.0, 1.0))
                is_depth_void = bool(rng.random() < p_void)
                lid_occ = np.clip(base_lid_occ + 0.05 * noise_scale * rng.standard_normal(), 0.0, 1.0)
            else:
                is_depth_void = False
                lid_occ = np.clip(0.25 + 0.20 * (1.0 - case.transparency) + 0.10 * noise_scale * rng.standard_normal(), 0.0, 1.0)

            if is_depth_void:
                # Do not force deterministic 0; allow sparse returns under high noise.
                lid_occ = float(np.clip(0.02 + 0.04 * noise_scale * abs(rng.standard_normal()), 0.0, 0.20))
                cam_free = float(np.clip(max(cam_free, 0.75), 0.0, 1.0))

            cell_center = grid.get_cell(row_center, case.door_col)
            updated_center, v_target, risk_score = planner.update_grid_and_plan(
                cell_center,
                cam_free,
                lid_occ,
                distance_to_door,
            )
            grid.set_cell(row_center, case.door_col, updated_center)

            emergency_envelope = False
            if mode == "mitigation":
                if distance_to_door < 4.0 and updated_center[2] > 0.55:
                    v_target = min(v_target, 0.4)
                if distance_to_door < 2.2 and updated_center[2] > 0.60:
                    v_target = 0.0

                # Kinematic safety envelope: if stopping distance exceeds remaining door distance
                # under high uncertainty, force maximum deceleration.
                if distance_to_door > 0.0 and updated_center[2] > 0.55:
                    a_cmd_max = 6.5
                    a_eff = max(0.8, a_cmd_max + 9.81 * case.slope)
                    d_stop = (v * v) / (2.0 * a_eff)
                    safety_margin = 1.2 + max(0.0, -case.slope) * 12.0
                    if distance_to_door <= d_stop + safety_margin:
                        v_target = 0.0
                        emergency_envelope = True

            for r, c in door_cells:
                if r == row_center and c == case.door_col:
                    continue
                cell = grid.get_cell(r, c)
                updated, _, _ = planner.update_grid_and_plan(cell, cam_free, lid_occ, distance_to_door)
                grid.set_cell(r, c, updated)

            if mode == "mitigation":
                if emergency_envelope:
                    a_cmd = -6.5
                    a = self._apply_grade(a_cmd, case.slope, -6.5, 1.4)
                else:
                    a_cmd = self._control_step(v, v_target, tau=0.68, a_min=-3.0, a_max=1.4)
                    a = self._apply_grade(a_cmd, case.slope, -3.0, 1.4)
            else:
                a_cmd = self._control_step(v, v_target, tau=0.52, a_min=-3.1, a_max=1.9)
                a = self._apply_grade(a_cmd, case.slope, -3.1, 1.9)
            x += v * self.dt + 0.5 * a * self.dt * self.dt
            v = max(0.0, v + a * self.dt)

            if crossed_idx is None and x >= door_x_world:
                crossed_idx = k

            if reached_goal_idx is None and x >= x_goal:
                reached_goal_idx = k

            if x >= door_x_world and v > 0.35:
                collision = True

            speed.append(v)
            accel.append(a)
            target_speed.append(v_target)
            x_hist.append(x)
            evr_hist.append(grid.door_evr(door_cells))
            unknown_center_hist.append(grid.front_unknown(row_center, case.door_col))
            risk_hist.append(risk_score)

            if collision:
                break
            if reached_goal_idx is not None:
                break

        speed_arr = np.array(speed, dtype=float)
        accel_arr = np.array(accel, dtype=float)
        x_arr = np.array(x_hist, dtype=float)
        evr_arr = np.array(evr_hist, dtype=float)
        unknown_arr = np.array(unknown_center_hist, dtype=float)
        risk_arr = np.array(risk_hist, dtype=float)
        time_arr = t[: len(speed_arr)]

        if crossed_idx is not None and crossed_idx < evr_arr.size:
            ref_idx = crossed_idx
        else:
            ref_idx = int(np.argmin(np.abs(door_x_world - x_arr))) if x_arr.size else 0

        evr = float(evr_arr[ref_idx]) if evr_arr.size else 0.0
        jerk = np.abs(np.diff(accel_arr, prepend=accel_arr[0])) / self.dt if accel_arr.size else np.array([0.0])

        if reached_goal_idx is None:
            travel_time = float(time_arr[-1]) if time_arr.size else 0.0
            reached_goal = 0
        else:
            travel_time = float(time_arr[reached_goal_idx])
            reached_goal = 1

        stop_time_ratio = float(np.mean(speed_arr < 0.5)) if speed_arr.size else 1.0
        door_margin = door_x_world - x_arr
        min_stop_margin = float(np.min(np.maximum(door_margin, 0.0)) if x_arr.size else door_x_world)

        return {
            "scenario": "A2",
            "mode": mode,
            "time": time_arr,
            "speed": self._smooth(speed_arr),
            "accel": accel_arr,
            "target_speed": np.array(target_speed, dtype=float),
            "x": x_arr,
            "evr_series": evr_arr,
            "unknown_series": unknown_arr,
            "risk_series": risk_arr,
            "case": case,
            "metrics": {
                "evr": evr,
                "barrier_collision": int(collision),
                "crossed_door": int(crossed_idx is not None),
                "reached_goal": reached_goal,
                "travel_time_s": travel_time,
                "avg_speed": float(np.mean(speed_arr) if speed_arr.size else 0.0),
                "stop_time_ratio": stop_time_ratio,
                "min_stop_margin_m": min_stop_margin,
                "peak_jerk": float(np.max(jerk) if jerk.size else 0.0),
                "unknown_at_ref": float(unknown_arr[ref_idx]) if unknown_arr.size else 1.0,
                "risk_at_ref": float(risk_arr[ref_idx]) if risk_arr.size else 0.0,
                "final_progress_m": float(x_arr[-1]) if x_arr.size else 0.0,
            },
        }
