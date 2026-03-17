from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any

import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ============================================================
# Paths
# ============================================================
ROOT = Path(__file__).resolve().parent.parent
RESULTS_ROOT = ROOT / "results_"
DATAS_DIR = RESULTS_ROOT / "datas"
FIGURES_DIR = RESULTS_ROOT / "figures"
DATAS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# Global configuration
# ============================================================
ARCHITECTURES = ["camera_only", "multi_sensor_permissive", "mitigation"]
ARCH_LABELS = {
    "camera_only": "Camera-only",
    "multi_sensor_permissive": "Multi-sensor permissive",
    "mitigation": "Mitigation",
}

STATE_TO_ID = {
    "KEEP_ROUTE": 0,
    "EXIT_PREP": 1,
    "CAUTIOUS_HOLD": 2,
    "MERGE_BACK": 3,
    "EXIT_COMMIT": 4,
}
STATE_COLS = list(STATE_TO_ID.keys())

ORACLE_TO_ID = {
    "OPEN_EXIT": 0,
    "TRANSITION_UNCERTAIN": 1,
    "CLOSED_EXIT": 2,
    "NO_RETURN": 3,
}

N_RUNS = 100
BASE_SEED = 20260316
DT = 0.10
DIST_START = 80.0
SIM_T_MAX = 12.0

FIELD_DISTANCE_DESC = np.linspace(DIST_START, 0.0, 401)
FIELD_DISTANCE_ASC = FIELD_DISTANCE_DESC[::-1]
GRID_DISTANCE_DESC = np.linspace(DIST_START, 0.0, 161)
GRID_DISTANCE_ASC = GRID_DISTANCE_DESC[::-1]

NO_RETURN_DISTANCE = 20.0
EXIT_COMMIT_THRESHOLD = 0.33

# ============================================================
# Helpers
# ============================================================
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def gaussian(x: float, center: float, width: float) -> float:
    return math.exp(-0.5 * ((x - center) / max(width, 1e-6)) ** 2)


def nearest_index(x_grid: np.ndarray, x: float) -> int:
    idx = int(np.searchsorted(x_grid, x, side="left"))
    if idx <= 0:
        return 0
    if idx >= len(x_grid):
        return len(x_grid) - 1
    left = idx - 1
    right = idx
    return right if abs(x_grid[right] - x) < abs(x_grid[left] - x) else left


def interp_cont(field: Dict[str, np.ndarray], col: str, distance: float) -> float:
    return float(np.interp(distance, field["distance_m"], field[col]))


def interp_nearest_str(field: Dict[str, np.ndarray], col: str, distance: float) -> str:
    idx = nearest_index(field["distance_m"], distance)
    return str(field[col][idx])


# ============================================================
# Scenario definition
# ============================================================
@dataclass
class B2Case:
    run_id: int
    seed: int
    v0: float
    exit_closed: bool
    scenario_tag: str

    stale_prior_base: float
    stale_prior_amp: float
    stale_decay_center: float
    stale_decay_width: float

    temp_ctrl_amp: float
    temp_ctrl_center: float
    temp_ctrl_width: float

    boundary_amp: float
    boundary_center: float
    boundary_width: float

    osc_amp: float
    osc_center: float
    osc_width: float
    osc_freq: float
    osc_phase: float

    merge_gap_base: float
    merge_gap_dip: float
    merge_gap_center: float
    merge_gap_width: float

    prior_noise_scale: float
    temp_noise_scale: float
    boundary_noise_scale: float
    conflict_noise_scale: float


def sample_case(run_id: int, base_seed: int = BASE_SEED) -> B2Case:
    rng = np.random.default_rng(base_seed + run_id)
    p = float(rng.uniform())

    # Dominant B2 case: stale exit prior conflicts with near-field temporary closure.
    if p < 0.72:
        scenario_tag = "closed_transition_conflict"
        exit_closed = True

        return B2Case(
            run_id=run_id,
            seed=base_seed + run_id,
            v0=float(rng.uniform(18.0, 22.0)),
            exit_closed=exit_closed,
            scenario_tag=scenario_tag,

            stale_prior_base=float(rng.uniform(0.26, 0.40)),
            stale_prior_amp=float(rng.uniform(0.36, 0.52)),
            stale_decay_center=float(rng.uniform(28.0, 36.0)),
            stale_decay_width=float(rng.uniform(6.0, 9.0)),

            temp_ctrl_amp=float(rng.uniform(0.58, 0.88)),
            temp_ctrl_center=float(rng.uniform(28.0, 38.0)),
            temp_ctrl_width=float(rng.uniform(5.0, 8.5)),

            boundary_amp=float(rng.uniform(0.74, 0.96)),
            boundary_center=float(rng.uniform(16.0, 24.0)),
            boundary_width=float(rng.uniform(4.0, 6.5)),

            osc_amp=float(rng.uniform(0.06, 0.14)),
            osc_center=float(rng.uniform(15.0, 24.0)),
            osc_width=float(rng.uniform(5.0, 8.0)),
            osc_freq=float(rng.uniform(0.9, 1.5)),
            osc_phase=float(rng.uniform(0.0, 2.0 * math.pi)),

            merge_gap_base=float(rng.uniform(0.55, 0.80)),
            merge_gap_dip=float(rng.uniform(0.10, 0.30)),
            merge_gap_center=float(rng.uniform(14.0, 26.0)),
            merge_gap_width=float(rng.uniform(4.0, 8.0)),

            prior_noise_scale=float(rng.uniform(0.020, 0.050)),
            temp_noise_scale=float(rng.uniform(0.020, 0.050)),
            boundary_noise_scale=float(rng.uniform(0.012, 0.030)),
            conflict_noise_scale=float(rng.uniform(0.015, 0.035)),
        )

    if p < 0.87:
        scenario_tag = "open_valid_exit"
        exit_closed = False

        return B2Case(
            run_id=run_id,
            seed=base_seed + run_id,
            v0=float(rng.uniform(18.0, 22.0)),
            exit_closed=exit_closed,
            scenario_tag=scenario_tag,

            stale_prior_base=float(rng.uniform(0.28, 0.42)),
            stale_prior_amp=float(rng.uniform(0.34, 0.50)),
            stale_decay_center=float(rng.uniform(26.0, 34.0)),
            stale_decay_width=float(rng.uniform(6.0, 9.0)),

            temp_ctrl_amp=float(rng.uniform(0.08, 0.22)),
            temp_ctrl_center=float(rng.uniform(24.0, 32.0)),
            temp_ctrl_width=float(rng.uniform(5.0, 8.0)),

            boundary_amp=float(rng.uniform(0.08, 0.22)),
            boundary_center=float(rng.uniform(14.0, 22.0)),
            boundary_width=float(rng.uniform(4.0, 6.5)),

            osc_amp=float(rng.uniform(0.00, 0.04)),
            osc_center=float(rng.uniform(15.0, 24.0)),
            osc_width=float(rng.uniform(5.0, 8.0)),
            osc_freq=float(rng.uniform(0.8, 1.2)),
            osc_phase=float(rng.uniform(0.0, 2.0 * math.pi)),

            merge_gap_base=float(rng.uniform(0.65, 0.90)),
            merge_gap_dip=float(rng.uniform(0.04, 0.14)),
            merge_gap_center=float(rng.uniform(16.0, 24.0)),
            merge_gap_width=float(rng.uniform(4.0, 8.0)),

            prior_noise_scale=float(rng.uniform(0.020, 0.045)),
            temp_noise_scale=float(rng.uniform(0.015, 0.035)),
            boundary_noise_scale=float(rng.uniform(0.010, 0.025)),
            conflict_noise_scale=float(rng.uniform(0.012, 0.028)),
        )

    scenario_tag = "partial_redirect_conflict"
    exit_closed = True

    return B2Case(
        run_id=run_id,
        seed=base_seed + run_id,
        v0=float(rng.uniform(18.0, 22.0)),
        exit_closed=exit_closed,
        scenario_tag=scenario_tag,

        stale_prior_base=float(rng.uniform(0.28, 0.44)),
        stale_prior_amp=float(rng.uniform(0.32, 0.48)),
        stale_decay_center=float(rng.uniform(28.0, 36.0)),
        stale_decay_width=float(rng.uniform(6.0, 9.5)),

        temp_ctrl_amp=float(rng.uniform(0.46, 0.70)),
        temp_ctrl_center=float(rng.uniform(26.0, 36.0)),
        temp_ctrl_width=float(rng.uniform(5.5, 9.0)),

        boundary_amp=float(rng.uniform(0.56, 0.78)),
        boundary_center=float(rng.uniform(16.0, 24.0)),
        boundary_width=float(rng.uniform(4.0, 7.0)),

        osc_amp=float(rng.uniform(0.10, 0.20)),
        osc_center=float(rng.uniform(14.0, 24.0)),
        osc_width=float(rng.uniform(5.0, 9.0)),
        osc_freq=float(rng.uniform(1.0, 1.8)),
        osc_phase=float(rng.uniform(0.0, 2.0 * math.pi)),

        merge_gap_base=float(rng.uniform(0.50, 0.75)),
        merge_gap_dip=float(rng.uniform(0.12, 0.32)),
        merge_gap_center=float(rng.uniform(14.0, 24.0)),
        merge_gap_width=float(rng.uniform(4.0, 8.0)),

        prior_noise_scale=float(rng.uniform(0.020, 0.050)),
        temp_noise_scale=float(rng.uniform(0.020, 0.050)),
        boundary_noise_scale=float(rng.uniform(0.012, 0.030)),
        conflict_noise_scale=float(rng.uniform(0.015, 0.035)),
    )


# ============================================================
# Latent environment fields
# ============================================================
def latent_stale_prior(distance: float, case: B2Case) -> float:
    value = case.stale_prior_base + case.stale_prior_amp * logistic((distance - case.stale_decay_center) / case.stale_decay_width)
    return clamp(value, 0.0, 1.0)


def latent_temp_control(distance: float, case: B2Case) -> float:
    value = case.temp_ctrl_amp * logistic((case.temp_ctrl_center - distance) / case.temp_ctrl_width)
    return clamp(value, 0.0, 1.0)


def latent_boundary_risk(distance: float, case: B2Case) -> float:
    value = case.boundary_amp * logistic((case.boundary_center - distance) / case.boundary_width)
    return clamp(value, 0.0, 1.0)


def latent_merge_gap(distance: float, case: B2Case) -> float:
    value = case.merge_gap_base - case.merge_gap_dip * gaussian(distance, case.merge_gap_center, case.merge_gap_width)
    return clamp(value, 0.0, 1.0)


def oscillation_window(distance: float, case: B2Case) -> float:
    return gaussian(distance, case.osc_center, case.osc_width)


def oracle_state(distance: float, temp_ctrl: float, boundary: float, case: B2Case) -> str:
    if not case.exit_closed:
        if distance < 20.0 and temp_ctrl < 0.40 and boundary < 0.35:
            return "OPEN_EXIT"
        return "TRANSITION_UNCERTAIN"

    if distance < NO_RETURN_DISTANCE and boundary > 0.60:
        return "NO_RETURN"
    if distance < 34.0 and temp_ctrl > 0.46:
        return "CLOSED_EXIT"
    return "TRANSITION_UNCERTAIN"


# ============================================================
# Shared field generation
# ============================================================
def build_shared_field(case: B2Case) -> Dict[str, np.ndarray]:
    """
    Shared environment + observation field reused by all architectures.
    Differences across stacks come from fusion / arbitration / policy,
    not from different random draws.
    """
    rng = np.random.default_rng(case.seed + 911)

    rows: List[Dict[str, Any]] = []

    prior_noise_state = 0.0
    temp_noise_state = 0.0
    boundary_noise_state = 0.0
    conflict_noise_state = 0.0

    for distance in FIELD_DISTANCE_DESC:
        stale_prior = latent_stale_prior(distance, case)
        temp_ctrl = latent_temp_control(distance, case)
        boundary = latent_boundary_risk(distance, case)
        merge_gap = latent_merge_gap(distance, case)
        osc_win = oscillation_window(distance, case)
        osc_val = case.osc_amp * osc_win * math.sin(case.osc_freq * distance + case.osc_phase)

        oracle = oracle_state(distance, temp_ctrl, boundary, case)

        prior_noise_state = 0.74 * prior_noise_state + float(rng.normal(0.0, case.prior_noise_scale))
        temp_noise_state = 0.76 * temp_noise_state + float(rng.normal(0.0, case.temp_noise_scale))
        boundary_noise_state = 0.78 * boundary_noise_state + float(rng.normal(0.0, case.boundary_noise_scale))
        conflict_noise_state = 0.76 * conflict_noise_state + float(rng.normal(0.0, case.conflict_noise_scale))

        # Shared observed channels
        z_exit_prior = clamp(
            stale_prior - 0.35 * osc_val - 0.03 * temp_ctrl + prior_noise_state,
            0.0,
            1.0,
        )
        z_temp_ctrl = clamp(
            temp_ctrl + 0.85 * osc_val + 0.10 * boundary + temp_noise_state,
            0.0,
            1.0,
        )
        z_boundary = clamp(
            boundary + 0.25 * abs(osc_val) + boundary_noise_state,
            0.0,
            1.0,
        )
        z_merge_gap = clamp(
            merge_gap - 0.12 * z_boundary + 0.25 * float(rng.normal(0.0, 0.02)),
            0.0,
            1.0,
        )
        z_conflict = clamp(
            0.45 * min(z_exit_prior, z_temp_ctrl)
            + 0.25 * z_boundary
            + 0.15 * abs(z_exit_prior - z_temp_ctrl)
            + 0.10 * (1.0 - z_merge_gap)
            + 0.40 * abs(osc_val)
            + conflict_noise_state,
            0.0,
            1.0,
        )

        rows.append(
            {
                "distance_m": distance,
                "stale_prior": stale_prior,
                "temp_control": temp_ctrl,
                "boundary_risk": boundary,
                "merge_gap": merge_gap,
                "osc_window": osc_win,
                "osc_val": osc_val,
                "oracle_state": oracle,
                "oracle_id": ORACLE_TO_ID[oracle],
                "z_exit_prior": z_exit_prior,
                "z_temp_ctrl": z_temp_ctrl,
                "z_boundary": z_boundary,
                "z_merge_gap": z_merge_gap,
                "z_conflict": z_conflict,
            }
        )

    df = pd.DataFrame(rows).sort_values("distance_m")
    return {col: df[col].to_numpy() for col in df.columns}


# ============================================================
# Architecture-specific fusion and decision
# ============================================================
def update_exit_belief(
    architecture: str,
    prev_belief: float,
    z_exit_prior: float,
    z_temp_ctrl: float,
    z_boundary: float,
    z_conflict: float,
) -> float:
    """
    b_exit = belief that the original exit remains valid and should still be followed.
    """
    if architecture == "camera_only":
        raw = (
            0.88 * z_exit_prior
            - 0.18 * z_temp_ctrl
            - 0.12 * z_boundary
            - 0.08 * z_conflict
            + 0.03
        )
        alpha = 0.38

    elif architecture == "multi_sensor_permissive":
        raw = (
            0.76 * z_exit_prior
            - 0.19 * z_temp_ctrl
            - 0.14 * z_boundary
            - 0.08 * z_conflict
            + 0.02
        )
        alpha = 0.47

    else:
        raw = (
            0.70 * z_exit_prior
            - 0.40 * z_temp_ctrl
            - 0.38 * z_boundary
            - 0.22 * z_conflict
        )
        if z_temp_ctrl > 0.48 or z_boundary > 0.52:
            raw *= 0.72
        alpha = 0.63

    raw = clamp(raw, 0.0, 1.0)
    belief = alpha * prev_belief + (1.0 - alpha) * raw
    return clamp(belief, 0.0, 1.0)


def decide_state(
    architecture: str,
    distance: float,
    z_exit_prior: float,
    z_temp_ctrl: float,
    z_boundary: float,
    z_merge_gap: float,
    z_conflict: float,
    osc_window_v: float,
    b_exit: float,
    prev_state: str,
    exit_confirm_count: int,
    override_count: int,
    reroute_locked: bool,
) -> tuple[str, int, int, bool]:
    in_zone = distance < 58.0
    near_gate = distance < 24.0
    no_return = distance < NO_RETURN_DISTANCE

    if architecture == "camera_only":
        if not in_zone:
            return "KEEP_ROUTE", 0, 0, False

        score = 0.70 * b_exit + 0.20 * z_exit_prior - 0.08 * z_temp_ctrl - 0.05 * z_boundary

        if distance > 36.0:
            if score > 0.25:
                return "EXIT_PREP", 0, 0, False
            return "KEEP_ROUTE", 0, 0, False

        if score > 0.31 or (near_gate and b_exit > 0.29):
            return "EXIT_COMMIT", 0, 0, False
        if z_conflict > 0.36 or z_temp_ctrl > 0.30 or z_boundary > 0.30:
            return "CAUTIOUS_HOLD", 0, 0, False
        if score > 0.22:
            return "EXIT_PREP", 0, 0, False
        return "KEEP_ROUTE", 0, 0, False

    if architecture == "multi_sensor_permissive":
        if not in_zone:
            return "KEEP_ROUTE", 0, 0, False

        score = 0.66 * b_exit + 0.19 * z_exit_prior - 0.12 * z_temp_ctrl - 0.10 * z_boundary
        oscillatory_band = (
            near_gate
            and osc_window_v > 0.22
            and 0.14 < b_exit < 0.31
            and z_temp_ctrl > 0.34
        )

        if distance > 38.0:
            if score > 0.23:
                return "EXIT_PREP", 0, 0, False
            return "KEEP_ROUTE", 0, 0, False

        if oscillatory_band:
            if prev_state == "MERGE_BACK":
                return "CAUTIOUS_HOLD", 0, 0, False
            if prev_state == "CAUTIOUS_HOLD":
                if z_boundary + 0.18 * z_conflict > 0.52 or z_merge_gap < 0.49:
                    return "MERGE_BACK", 0, 0, False
                if score > 0.24 and z_temp_ctrl < 0.52:
                    return "EXIT_PREP", 0, 0, False
                return "CAUTIOUS_HOLD", 0, 0, False
            if prev_state == "EXIT_PREP" and score > 0.24 and z_boundary < 0.52:
                return "EXIT_COMMIT", 0, 0, False
            return "CAUTIOUS_HOLD", 0, 0, False

        if near_gate and score > 0.21 and z_boundary < 0.62 and z_temp_ctrl < 0.70:
            return "EXIT_COMMIT", 0, 0, False
        if near_gate and (z_temp_ctrl > 0.60 or z_boundary > 0.64 or z_merge_gap < 0.42):
            return "MERGE_BACK", 0, 0, False
        if z_conflict > 0.40 or z_temp_ctrl > 0.34:
            return "CAUTIOUS_HOLD", 0, 0, False
        if score > 0.20:
            return "EXIT_PREP", 0, 0, False
        return "KEEP_ROUTE", 0, 0, False

    # Mitigation: temporary-control override + hysteresis + dwell-time + no-return lock
    if reroute_locked:
        return "MERGE_BACK", exit_confirm_count, override_count, True

    if not in_zone:
        return "KEEP_ROUTE", 0, 0, False

    strong_override = (z_temp_ctrl > 0.40) or (z_boundary > 0.42) or (z_conflict > 0.46)
    override_confident = (z_temp_ctrl > z_exit_prior + 0.08) and (z_temp_ctrl > 0.38)
    strong_exit = (b_exit > 0.30) and (z_temp_ctrl < 0.28) and (z_boundary < 0.28) and (z_conflict < 0.34)

    if strong_override:
        override_count += 1
        exit_confirm_count = 0
    else:
        override_count = max(override_count - 1, 0)

    if strong_exit:
        exit_confirm_count += 1
    else:
        exit_confirm_count = max(exit_confirm_count - 1, 0)

    if reroute_locked:
        return "MERGE_BACK", 0, override_count, True

    if no_return or override_count >= 2:
        return "MERGE_BACK", 0, override_count, True
    if distance < 24.0 and override_confident and z_boundary > 0.36:
        return "MERGE_BACK", 0, max(override_count + 1, 2), True

    if distance > 28.0:
        if strong_override:
            return "CAUTIOUS_HOLD", 0, override_count, False
        if b_exit > 0.22 and z_temp_ctrl < 0.32 and z_boundary < 0.32:
            return "EXIT_PREP", exit_confirm_count, override_count, False
        if z_conflict > 0.28 or z_temp_ctrl > 0.26 or z_boundary > 0.26:
            return "CAUTIOUS_HOLD", 0, override_count, False
        return "KEEP_ROUTE", 0, override_count, False

    if (
        distance < 28.0
        and exit_confirm_count >= 3
        and z_temp_ctrl < 0.28
        and z_boundary < 0.28
        and z_conflict < 0.34
    ):
        return "EXIT_COMMIT", exit_confirm_count, override_count, False

    if strong_override or z_conflict > 0.28 or z_temp_ctrl > 0.24 or z_boundary > 0.24:
        return "CAUTIOUS_HOLD", 0, override_count, False

    if b_exit > 0.22 and z_temp_ctrl < 0.32 and z_boundary < 0.32:
        return "EXIT_PREP", exit_confirm_count, override_count, False

    return "KEEP_ROUTE", 0, override_count, False


# ============================================================
# Speed policy and dynamics
# ============================================================
def target_speed(architecture: str, state: str, v0: float, z_conflict: float) -> float:
    if architecture == "camera_only":
        if state == "KEEP_ROUTE":
            return v0
        if state == "EXIT_PREP":
            return 0.97 * v0
        if state == "CAUTIOUS_HOLD":
            return (0.84 - 0.04 * z_conflict) * v0
        if state == "MERGE_BACK":
            return (0.80 - 0.05 * z_conflict) * v0
        return 0.92 * v0

    if architecture == "multi_sensor_permissive":
        if state == "KEEP_ROUTE":
            return 0.99 * v0
        if state == "EXIT_PREP":
            return 0.95 * v0
        if state == "CAUTIOUS_HOLD":
            return (0.80 - 0.05 * z_conflict) * v0
        if state == "MERGE_BACK":
            return (0.79 - 0.05 * z_conflict) * v0
        return 0.90 * v0

    if state == "KEEP_ROUTE":
        return 0.98 * v0
    if state == "EXIT_PREP":
        return 0.94 * v0
    if state == "CAUTIOUS_HOLD":
        return (0.78 - 0.05 * z_conflict) * v0
    if state == "MERGE_BACK":
        return (0.77 - 0.05 * z_conflict) * v0
    return 0.89 * v0


def acceleration_bounds(state: str) -> tuple[float, float]:
    if state == "KEEP_ROUTE":
        return -2.0, 1.5
    if state == "EXIT_PREP":
        return -2.5, 1.2
    if state == "CAUTIOUS_HOLD":
        return -3.2, 1.0
    if state == "MERGE_BACK":
        return -3.4, 0.8
    return -2.4, 1.0


# ============================================================
# Auxiliary decision cost
# ============================================================
def step_decision_cost(
    action: str,
    prev_action: str,
    oracle: str,
    speed: float,
    v_ref: float,
) -> Dict[str, float]:
    unsafe_exit_commit = float(action == "EXIT_COMMIT" and oracle in {"CLOSED_EXIT", "NO_RETURN"})
    late_mergeback = float(action != "MERGE_BACK" and oracle == "NO_RETURN")
    unnecessary_reroute = float(action == "MERGE_BACK" and oracle == "OPEN_EXIT")
    oscillation = float(action != prev_action)
    efficiency = max(v_ref - speed, 0.0) / max(v_ref, 1e-6)

    weights = {
        "unsafe_exit_commit": 10.0,
        "late_mergeback": 4.0,
        "unnecessary_reroute": 2.0,
        "oscillation": 1.0,
        "efficiency": 0.5,
    }

    total = (
        weights["unsafe_exit_commit"] * unsafe_exit_commit
        + weights["late_mergeback"] * late_mergeback
        + weights["unnecessary_reroute"] * unnecessary_reroute
        + weights["oscillation"] * oscillation
        + weights["efficiency"] * efficiency
    )

    return {
        "cost_unsafe_exit_commit": unsafe_exit_commit,
        "cost_late_mergeback": late_mergeback,
        "cost_unnecessary_reroute": unnecessary_reroute,
        "cost_oscillation": oscillation,
        "cost_efficiency": efficiency,
        "cost_total": total,
    }


# ============================================================
# Simulation
# ============================================================
def simulate_run(case: B2Case, field: Dict[str, np.ndarray], architecture: str) -> pd.DataFrame:
    t = 0.0
    distance = DIST_START
    speed = case.v0
    b_exit = 0.0
    prev_state = "KEEP_ROUTE"
    exit_confirm_count = 0
    override_count = 0
    reroute_locked = False

    rows: List[Dict[str, Any]] = []

    while distance > 0.0 and t < SIM_T_MAX:
        stale_prior = interp_cont(field, "stale_prior", distance)
        temp_control = interp_cont(field, "temp_control", distance)
        boundary_risk = interp_cont(field, "boundary_risk", distance)
        merge_gap = interp_cont(field, "merge_gap", distance)
        osc_window_v = interp_cont(field, "osc_window", distance)

        z_exit_prior = interp_cont(field, "z_exit_prior", distance)
        z_temp_ctrl = interp_cont(field, "z_temp_ctrl", distance)
        z_boundary = interp_cont(field, "z_boundary", distance)
        z_merge_gap = interp_cont(field, "z_merge_gap", distance)
        z_conflict = interp_cont(field, "z_conflict", distance)

        oracle = interp_nearest_str(field, "oracle_state", distance)

        b_exit = update_exit_belief(
            architecture,
            b_exit,
            z_exit_prior,
            z_temp_ctrl,
            z_boundary,
            z_conflict,
        )

        state, exit_confirm_count, override_count, reroute_locked = decide_state(
            architecture=architecture,
            distance=distance,
            z_exit_prior=z_exit_prior,
            z_temp_ctrl=z_temp_ctrl,
            z_boundary=z_boundary,
            z_merge_gap=z_merge_gap,
            z_conflict=z_conflict,
            osc_window_v=osc_window_v,
            b_exit=b_exit,
            prev_state=prev_state,
            exit_confirm_count=exit_confirm_count,
            override_count=override_count,
            reroute_locked=reroute_locked,
        )

        v_target = target_speed(architecture, state, case.v0, z_conflict)
        a_cmd = (v_target - speed) / 0.8
        a_min, a_max = acceleration_bounds(state)
        a = clamp(a_cmd, a_min, a_max)
        speed = clamp(speed + a * DT, 4.8, 32.0)

        cost_parts = step_decision_cost(state, prev_state, oracle, speed, case.v0)

        rows.append(
            {
                "run_id": case.run_id,
                "architecture": architecture,
                "time_s": t,
                "distance_m": distance,
                "speed_mps": speed,
                "accel_mps2": a,
                "v_target": v_target,
                "exit_closed": case.exit_closed,
                "scenario_tag": case.scenario_tag,

                "stale_prior": stale_prior,
                "temp_control": temp_control,
                "boundary_risk": boundary_risk,
                "merge_gap": merge_gap,
                "osc_window": osc_window_v,

                "z_exit_prior": z_exit_prior,
                "z_temp_ctrl": z_temp_ctrl,
                "z_boundary": z_boundary,
                "z_merge_gap": z_merge_gap,
                "z_conflict": z_conflict,

                "b_exit": b_exit,
                "decision_state": state,
                "decision_id": STATE_TO_ID[state],
                "oracle_state": oracle,
                "oracle_id": ORACLE_TO_ID[oracle],
                "exit_confirm_count": exit_confirm_count,
                "override_count": override_count,
                "reroute_locked": reroute_locked,
                **cost_parts,
            }
        )

        prev_state = state
        distance = max(distance - speed * DT, 0.0)
        t += DT

    return pd.DataFrame(rows)


# ============================================================
# Summaries
# ============================================================
def summarize_run(run_df: pd.DataFrame, case: B2Case) -> Dict[str, Any]:
    states = run_df["decision_state"].to_numpy()
    oracle = run_df["oracle_state"].to_numpy()
    decision_ids = run_df["decision_id"].to_numpy()
    distance = run_df["distance_m"].to_numpy()

    exit_commit_mask = states == "EXIT_COMMIT"
    hold_mask = states == "CAUTIOUS_HOLD"
    merge_mask = states == "MERGE_BACK"

    unsafe_commit_mask = exit_commit_mask & np.isin(oracle, ["CLOSED_EXIT", "NO_RETURN"])

    t_final = float(run_df["time_s"].iloc[-1] + DT)
    t_nominal = DIST_START / case.v0

    first_merge_distance = float(distance[merge_mask][0]) if merge_mask.any() else np.nan
    first_exit_commit_distance = float(distance[exit_commit_mask][0]) if exit_commit_mask.any() else np.nan

    # Late merge-back severity:
    # 0 means merge-back happened before the no-return zone.
    # Larger means later / worse.
    if case.exit_closed:
        if merge_mask.any():
            lms = max(0.0, NO_RETURN_DISTANCE - first_merge_distance)
        elif unsafe_commit_mask.any():
            lms = NO_RETURN_DISTANCE + 5.0
        else:
            lms = NO_RETURN_DISTANCE
    else:
        lms = np.nan

    out = {
        "run_id": case.run_id,
        "architecture": run_df["architecture"].iloc[0],
        "scenario_tag": case.scenario_tag,
        "exit_closed": case.exit_closed,

        # Headline metrics
        "CIR_event": float(unsafe_commit_mask.any()),
        "DOC": int(np.sum(decision_ids[1:] != decision_ids[:-1])),
        "Ttravel_s": t_final,
        "Tdelay_s": max(t_final - t_nominal, 0.0),
        "LMS_m": lms,

        # Auxiliary ratios / diagnostics
        "exit_commit_ratio": float(exit_commit_mask.mean()),
        "hold_ratio": float(hold_mask.mean()),
        "merge_back_ratio": float(merge_mask.mean()),
        "unsafe_commit_ratio": float(unsafe_commit_mask.mean()),
        "first_exit_commit_distance_m": first_exit_commit_distance,
        "first_merge_back_distance_m": first_merge_distance,
        "mean_z_exit_prior": float(run_df["z_exit_prior"].mean()),
        "mean_z_temp_ctrl": float(run_df["z_temp_ctrl"].mean()),
        "mean_z_boundary": float(run_df["z_boundary"].mean()),
        "mean_z_conflict": float(run_df["z_conflict"].mean()),
        "mean_b_exit": float(run_df["b_exit"].mean()),

        # Auxiliary cost
        "total_cost": float(run_df["cost_total"].sum() * DT),
        "unsafe_exit_commit_cost": float(run_df["cost_unsafe_exit_commit"].sum() * DT),
        "late_mergeback_cost": float(run_df["cost_late_mergeback"].sum() * DT),
        "unnecessary_reroute_cost": float(run_df["cost_unnecessary_reroute"].sum() * DT),
        "oscillation_cost": float(run_df["cost_oscillation"].sum() * DT),
        "efficiency_cost": float(run_df["cost_efficiency"].sum() * DT),
    }
    return out


def interpolate_run_to_grid(run_df: pd.DataFrame, case: B2Case, architecture: str) -> pd.DataFrame:
    df = run_df.sort_values("distance_m")
    xp = df["distance_m"].to_numpy()

    out = {
        "run_id": np.full_like(GRID_DISTANCE_ASC, case.run_id, dtype=int),
        "architecture": np.array([architecture] * len(GRID_DISTANCE_ASC)),
        "distance_m": GRID_DISTANCE_ASC.copy(),
        "exit_closed": np.array([case.exit_closed] * len(GRID_DISTANCE_ASC)),
        "scenario_tag": np.array([case.scenario_tag] * len(GRID_DISTANCE_ASC)),
    }

    interp_cols = [
        "stale_prior",
        "temp_control",
        "boundary_risk",
        "merge_gap",
        "osc_window",
        "z_exit_prior",
        "z_temp_ctrl",
        "z_boundary",
        "z_merge_gap",
        "z_conflict",
        "b_exit",
        "speed_mps",
        "cost_total",
    ]
    for col in interp_cols:
        out[col] = np.interp(GRID_DISTANCE_ASC, xp, df[col].to_numpy())

    dec_ids = df["decision_id"].to_numpy()
    nearest_idx = np.searchsorted(xp, GRID_DISTANCE_ASC, side="left")
    nearest_idx = np.clip(nearest_idx, 0, len(xp) - 1)
    dec_grid = dec_ids[nearest_idx]

    for state_name, state_id in STATE_TO_ID.items():
        out[f"state_{state_name}"] = (dec_grid == state_id).astype(float)

    return pd.DataFrame(out)


def fit_curves(interp_df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "stale_prior",
        "temp_control",
        "boundary_risk",
        "merge_gap",
        "osc_window",
        "z_exit_prior",
        "z_temp_ctrl",
        "z_boundary",
        "z_merge_gap",
        "z_conflict",
        "b_exit",
        "speed_mps",
        "cost_total",
    ] + [f"state_{name}" for name in STATE_COLS]

    records: List[Dict[str, Any]] = []

    for arch in ARCHITECTURES:
        sub_arch = interp_df[interp_df["architecture"] == arch]
        for distance in GRID_DISTANCE_ASC:
            sub = sub_arch[sub_arch["distance_m"] == distance]
            row: Dict[str, Any] = {"architecture": arch, "distance_m": float(distance)}
            for metric in metrics:
                vals = sub[metric].to_numpy()
                row[f"{metric}_mean"] = float(np.mean(vals))
                row[f"{metric}_q25"] = float(np.quantile(vals, 0.25))
                row[f"{metric}_q75"] = float(np.quantile(vals, 0.75))
            records.append(row)

    return pd.DataFrame(records)


# ============================================================
# Plotting
# ============================================================
def plot_typical_case(raw_df: pd.DataFrame, save_path: Path) -> None:
    sub = raw_df[
        (raw_df["scenario_tag"] == "closed_transition_conflict")
        & (raw_df["architecture"] == "multi_sensor_permissive")
    ].sort_values(["run_id", "distance_m"], ascending=[True, False])

    if len(sub) == 0:
        return

    def doc_of_group(g: pd.DataFrame) -> int:
        d = g["decision_id"].to_numpy()
        return int(np.sum(d[1:] != d[:-1]))

    docs = sub.groupby("run_id").apply(doc_of_group)
    candidate_rows = []
    for run_id in docs.index:
        df_cam = raw_df[(raw_df["run_id"] == run_id) & (raw_df["architecture"] == "camera_only")]
        df_multi = raw_df[(raw_df["run_id"] == run_id) & (raw_df["architecture"] == "multi_sensor_permissive")]
        df_miti = raw_df[(raw_df["run_id"] == run_id) & (raw_df["architecture"] == "mitigation")]
        cam_unsafe = bool(((df_cam["decision_state"] == "EXIT_COMMIT") & df_cam["oracle_state"].isin(["CLOSED_EXIT", "NO_RETURN"])).any())
        miti_unsafe = bool(((df_miti["decision_state"] == "EXIT_COMMIT") & df_miti["oracle_state"].isin(["CLOSED_EXIT", "NO_RETURN"])).any())
        multi_doc = doc_of_group(df_multi)
        candidate_rows.append((int(run_id), cam_unsafe, miti_unsafe, multi_doc))
    candidate_rows.sort(key=lambda x: (not x[1], x[2], -x[3], x[0]))
    run_id = candidate_rows[0][0]

    fig, axes = plt.subplots(4, 1, figsize=(10.5, 12.0), sharex=True)

    df_ref = raw_df[
        (raw_df["run_id"] == run_id)
        & (raw_df["architecture"] == "camera_only")
    ].sort_values("distance_m", ascending=False)

    axes[0].plot(df_ref["distance_m"], df_ref["z_exit_prior"], linewidth=2.0, label="Shared exit-prior cue")
    axes[0].plot(df_ref["distance_m"], df_ref["z_temp_ctrl"], linewidth=2.0, label="Shared temporary-control cue")
    axes[0].plot(df_ref["distance_m"], df_ref["z_boundary"], linewidth=2.0, label="Boundary risk")
    axes[0].plot(df_ref["distance_m"], df_ref["z_conflict"], linewidth=2.0, label="Observed conflict")
    axes[0].set_ylabel("Shared env.")
    axes[0].set_title(f"Typical closed-transition-conflict run (run_id={run_id})")
    axes[0].grid(alpha=0.25)
    axes[0].legend(ncol=2, fontsize=9, loc="upper right", frameon=True)

    axes[1].plot(df_ref["distance_m"], df_ref["z_exit_prior"], linestyle="--", linewidth=2.0, label="Shared exit-prior cue")
    axes[1].plot(df_ref["distance_m"], df_ref["z_temp_ctrl"], linestyle="--", linewidth=2.0, label="Shared temporary-control cue")
    for arch in ARCHITECTURES:
        df = raw_df[
            (raw_df["run_id"] == run_id)
            & (raw_df["architecture"] == arch)
        ].sort_values("distance_m", ascending=False)
        axes[1].plot(df["distance_m"], df["b_exit"], linewidth=2.2, label=f"{ARCH_LABELS[arch]} belief")
    axes[1].axhline(EXIT_COMMIT_THRESHOLD, linestyle=":", linewidth=1.2)
    axes[1].set_ylabel("Exit-validity belief")
    axes[1].grid(alpha=0.25)
    axes[1].legend(ncol=2, fontsize=8, loc="upper right")

    for arch in ARCHITECTURES:
        df = raw_df[
            (raw_df["run_id"] == run_id)
            & (raw_df["architecture"] == arch)
        ].sort_values("distance_m", ascending=False)
        axes[2].step(df["distance_m"], df["decision_id"], where="post", linewidth=2.0, label=ARCH_LABELS[arch])
    axes[2].set_ylabel("Decision")
    axes[2].set_yticks(list(STATE_TO_ID.values()), list(STATE_TO_ID.keys()))
    axes[2].grid(alpha=0.25)
    axes[2].legend(ncol=3, fontsize=9, loc="upper right")

    for arch in ARCHITECTURES:
        df = raw_df[
            (raw_df["run_id"] == run_id)
            & (raw_df["architecture"] == arch)
        ].sort_values("distance_m", ascending=False)
        axes[3].plot(df["distance_m"], df["speed_mps"], linewidth=2.0, label=ARCH_LABELS[arch])
    axes[3].set_ylabel("Speed (m/s)")
    axes[3].set_xlabel("Distance to exit area (m)")
    axes[3].invert_xaxis()
    axes[3].grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(save_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_fitted_beliefs(fitted_df: pd.DataFrame, save_path: Path) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(9.5, 11.5), sharex=True)

    for ax, arch in zip(axes, ARCHITECTURES):
        sub = fitted_df[fitted_df["architecture"] == arch].sort_values("distance_m", ascending=False)
        x = sub["distance_m"].to_numpy()

        for metric, label in [
            ("z_exit_prior", "Exit-prior cue"),
            ("z_temp_ctrl", "Temporary-control cue"),
            ("b_exit", "Exit-validity belief"),
        ]:
            ax.plot(x, sub[f"{metric}_mean"], linewidth=2.3, label=label)
            ax.fill_between(x, sub[f"{metric}_q25"], sub[f"{metric}_q75"], alpha=0.15)

        ax.axhline(EXIT_COMMIT_THRESHOLD, linestyle=":", linewidth=1.2)
        ax.set_title(ARCH_LABELS[arch])
        ax.set_ylabel("Probability / belief")
        ax.set_ylim(0, 1)
        ax.grid(alpha=0.25)

    axes[-1].set_xlabel("Distance to exit area (m)")
    axes[-1].invert_xaxis()
    axes[0].legend(ncol=3, fontsize=9)

    fig.tight_layout()
    fig.savefig(save_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_headline_metrics(summary_df: pd.DataFrame, save_path: Path) -> None:
    metrics = ["CIR_event", "DOC", "Tdelay_s", "LMS_m"]
    titles = [
        "Conflict intrusion rate",
        "Decision oscillation count",
        "Travel delay (s)",
        "Late merge-back severity (m)",
    ]

    mean_df = summary_df.groupby("architecture", as_index=False)[metrics].mean().set_index("architecture").loc[ARCHITECTURES]
    std_df = summary_df.groupby("architecture")[metrics].std().reindex(ARCHITECTURES)
    count_df = summary_df.groupby("architecture").size().reindex(ARCHITECTURES)

    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.8))
    axes = axes.ravel()
    x = np.arange(len(ARCHITECTURES))

    for ax, metric, title in zip(axes, metrics, titles):
        vals = mean_df[metric].to_numpy()
        if metric == "CIR_event":
            z = 1.96
            lower_err = np.zeros(len(ARCHITECTURES))
            upper_err = np.zeros(len(ARCHITECTURES))
            for i, arch in enumerate(ARCHITECTURES):
                n = int(count_df.loc[arch])
                p = float(vals[i])
                denom = 1.0 + (z ** 2) / n
                center = (p + (z ** 2) / (2.0 * n)) / denom
                radius = z * math.sqrt((p * (1.0 - p) / n) + (z ** 2) / (4.0 * n * n)) / denom
                lower = max(0.0, center - radius)
                upper = min(1.0, center + radius)
                lower_err[i] = p - lower
                upper_err[i] = upper - p
            errs = np.vstack([lower_err, upper_err])
            ax.bar(x, vals, yerr=errs, width=0.50, capsize=5)
            ax.set_ylim(0.0, 1.0)
        else:
            errs = std_df[metric].fillna(0.0).to_numpy()
            ax.bar(x, vals, yerr=errs, width=0.50, capsize=5)
        ax.set_xticks(x, [ARCH_LABELS[a] for a in ARCHITECTURES], rotation=0)
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.25)

    fig.tight_layout()
    fig.savefig(save_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_cost_breakdown(summary_df: pd.DataFrame, save_path: Path) -> None:
    parts = [
        "unsafe_exit_commit_cost",
        "late_mergeback_cost",
        "unnecessary_reroute_cost",
        "oscillation_cost",
        "efficiency_cost",
    ]
    labels = [
        "Unsafe exit-commit",
        "Late merge-back",
        "Unnecessary reroute",
        "Oscillation",
        "Efficiency",
    ]
    mean_df = (
        summary_df.groupby("architecture", as_index=False)[parts]
        .mean()
        .set_index("architecture")
        .loc[ARCHITECTURES]
    )

    x = np.arange(len(ARCHITECTURES))
    bottom = np.zeros(len(ARCHITECTURES))

    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    for part, label in zip(parts, labels):
        vals = mean_df[part].to_numpy()
        ax.bar(x, vals, bottom=bottom, width=0.55, label=label)
        bottom += vals

    ax.set_xticks(x, [ARCH_LABELS[a] for a in ARCHITECTURES])
    ax.set_ylabel("Average auxiliary decision cost")
    ax.set_title("Auxiliary decision cost breakdown")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncol=2, fontsize=9)

    fig.tight_layout()
    fig.savefig(save_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_summary_table(summary_means: pd.DataFrame, save_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.0, 2.6))
    ax.axis("off")

    show_cols = [
        "architecture",
        "CIR_event",
        "DOC",
        "Tdelay_s",
        "LMS_m",
        "total_cost",
    ]
    disp = summary_means[show_cols].copy()
    disp["architecture"] = disp["architecture"].map(ARCH_LABELS)
    disp = disp.round(3)

    table = ax.table(
        cellText=disp.values,
        colLabels=["Architecture", "CIR", "DOC", "Tdelay (s)", "LMS (m)", "Aux. cost"],
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.0, 1.55)

    fig.tight_layout()
    fig.savefig(save_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


# ============================================================
# Main
# ============================================================
def main() -> None:
    cases = [sample_case(i) for i in range(N_RUNS)]

    case_rows: List[Dict[str, Any]] = []
    raw_runs: List[pd.DataFrame] = []
    summaries: List[Dict[str, Any]] = []
    interp_runs: List[pd.DataFrame] = []

    for case in cases:
        case_rows.append(asdict(case))
        shared_field = build_shared_field(case)

        for arch in ARCHITECTURES:
            run_df = simulate_run(case, shared_field, arch)
            raw_runs.append(run_df)
            summaries.append(summarize_run(run_df, case))
            interp_runs.append(interpolate_run_to_grid(run_df, case, arch))

    raw_df = pd.concat(raw_runs, ignore_index=True)
    summary_df = pd.DataFrame(summaries)
    interp_df = pd.concat(interp_runs, ignore_index=True)
    fitted_df = fit_curves(interp_df)
    cases_df = pd.DataFrame(case_rows)

    overall_summary_means = (
        summary_df.groupby("architecture", as_index=False)
        .mean(numeric_only=True)
        .set_index("architecture")
        .loc[ARCHITECTURES]
        .reset_index()
    )
    closed_transition_df = summary_df[summary_df["scenario_tag"] == "closed_transition_conflict"].copy()
    closed_transition_means = (
        closed_transition_df.groupby("architecture", as_index=False)
        .mean(numeric_only=True)
        .set_index("architecture")
        .loc[ARCHITECTURES]
        .reset_index()
    )
    summary_by_tag = (
        summary_df.groupby(["scenario_tag", "architecture"], as_index=False)
        .mean(numeric_only=True)
        .assign(architecture=lambda df: pd.Categorical(df["architecture"], categories=ARCHITECTURES, ordered=True))
        .sort_values(["scenario_tag", "architecture"])
    )

    stem = "b2_aligned_partA"

    raw_path = DATAS_DIR / f"{stem}_runs.csv"
    summary_path = DATAS_DIR / f"{stem}_summary.csv"
    fitted_path = DATAS_DIR / f"{stem}_fitted_curves.csv"
    cases_path = DATAS_DIR / f"{stem}_cases.csv"
    means_path = DATAS_DIR / f"{stem}_summary_means.csv"
    by_tag_path = DATAS_DIR / f"{stem}_summary_by_tag.csv"
    overall_means_path = DATAS_DIR / f"{stem}_overall_summary_means.csv"

    raw_df.to_csv(raw_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    fitted_df.to_csv(fitted_path, index=False)
    cases_df.to_csv(cases_path, index=False)
    closed_transition_means.to_csv(means_path, index=False)
    summary_by_tag.to_csv(by_tag_path, index=False)
    overall_summary_means.to_csv(overall_means_path, index=False)

    plot_typical_case(raw_df, FIGURES_DIR / f"{stem}_typical_case.png")
    plot_fitted_beliefs(fitted_df, FIGURES_DIR / f"{stem}_fitted_beliefs.png")
    plot_headline_metrics(closed_transition_df, FIGURES_DIR / f"{stem}_headline_metrics.png")
    plot_cost_breakdown(closed_transition_df, FIGURES_DIR / f"{stem}_cost_breakdown.png")
    plot_summary_table(closed_transition_means, FIGURES_DIR / f"{stem}_summary_table.png")

    print("Saved:")
    print(raw_path)
    print(summary_path)
    print(fitted_path)
    print(cases_path)
    print(means_path)
    print(by_tag_path)
    print(overall_means_path)
    print(FIGURES_DIR / f"{stem}_typical_case.png")
    print(FIGURES_DIR / f"{stem}_fitted_beliefs.png")
    print(FIGURES_DIR / f"{stem}_headline_metrics.png")
    print(FIGURES_DIR / f"{stem}_cost_breakdown.png")
    print(FIGURES_DIR / f"{stem}_summary_table.png")

    print("\nClosed-transition headline summary:")
    print(
        closed_transition_means[
            ["architecture", "CIR_event", "DOC", "Tdelay_s", "LMS_m", "total_cost"]
        ].round(3).to_string(index=False)
    )

    print("\nStratified by scenario tag:")
    print(
        summary_by_tag[
            ["scenario_tag", "architecture", "CIR_event", "DOC", "Tdelay_s", "LMS_m"]
        ].round(3).to_string(index=False)
    )


if __name__ == "__main__":
    main()
