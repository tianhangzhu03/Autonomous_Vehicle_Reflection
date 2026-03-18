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
    "KEEP": 0,
    "CAUTIOUS_HOLD": 1,
    "COMMIT_EGO": 2,
    "ABORT_ENTRY": 3,
}
STATE_COLS = list(STATE_TO_ID.keys())

ORACLE_TO_ID = {
    "UNSAFE_EGO": 0,
    "UNCERTAIN_EGO": 1,
    "CONFIRMABLE_EGO": 2,
}
ID_TO_ORACLE = {v: k for k, v in ORACLE_TO_ID.items()}

N_RUNS = 100
BASE_SEED = 20260316
DT = 0.10
DIST_START = 80.0
SIM_T_MAX = 12.0

FIELD_DISTANCE_DESC = np.linspace(DIST_START, 0.0, 401)
FIELD_DISTANCE_ASC = FIELD_DISTANCE_DESC[::-1]
GRID_DISTANCE_DESC = np.linspace(DIST_START, 0.0, 161)
GRID_DISTANCE_ASC = GRID_DISTANCE_DESC[::-1]

COMMIT_THRESHOLD = 0.35

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
    if abs(x_grid[right] - x) < abs(x_grid[left] - x):
        return right
    return left


def interp_cont(field: Dict[str, np.ndarray], col: str, distance: float) -> float:
    return float(np.interp(distance, field["distance_m"], field[col]))


def interp_nearest_str(field: Dict[str, np.ndarray], col: str, distance: float) -> str:
    idx = nearest_index(field["distance_m"], distance)
    return str(field[col][idx])


# ============================================================
# Scenario definition
# ============================================================
@dataclass
class B1Case:
    run_id: int
    seed: int
    v0: float
    lane2_open: bool
    lane3_open: bool
    scenario_tag: str

    glare_base: float
    glare_amp1: float
    glare_center1: float
    glare_width1: float
    glare_amp2: float
    glare_center2: float
    glare_width2: float

    occl_amp: float
    occl_center: float
    occl_width: float

    ambiguity_base: float
    ambiguity_amp: float
    ambiguity_center: float
    ambiguity_width: float

    motion_base: float
    motion_amp: float
    motion_center: float
    motion_width: float

    osc_window_center: float
    osc_window_width: float
    osc_attr_amp: float
    osc_conflict_amp: float
    osc_open_amp: float
    osc_phase: float
    osc_cycles: float
    osc_enabled: bool

    semantic_noise_scale: float
    attr_noise_scale: float
    motion_noise_scale: float


def sample_case(run_id: int, base_seed: int = BASE_SEED) -> B1Case:
    rng = np.random.default_rng(base_seed + run_id)
    p = float(rng.uniform())

    # Make the canonical B1 case dominant:
    # adjacent open-looking cue is visible, but ego lane itself is not open.
    if p < 0.80:
        lane2_open, lane3_open, tag = True, False, "adjacent_open_risk"
    elif p < 0.90:
        lane2_open, lane3_open, tag = True, True, "both_open"
    elif p < 0.95:
        lane2_open, lane3_open, tag = False, True, "ego_open_only"
    else:
        lane2_open, lane3_open, tag = False, False, "both_closed"

    has_secondary_glare = float(rng.uniform()) < 0.55
    osc_enabled = (tag == "adjacent_open_risk" and float(rng.uniform()) < 0.45) or (tag != "adjacent_open_risk" and float(rng.uniform()) < 0.18)

    return B1Case(
        run_id=run_id,
        seed=base_seed + run_id,
        v0=float(rng.uniform(17.0, 23.0)),
        lane2_open=lane2_open,
        lane3_open=lane3_open,
        scenario_tag=tag,
        glare_base=float(rng.uniform(0.08, 0.20)),
        glare_amp1=float(rng.uniform(0.30, 0.75)),
        glare_center1=float(rng.uniform(18.0, 38.0)),
        glare_width1=float(rng.uniform(6.0, 12.5)),
        glare_amp2=float(rng.uniform(0.08, 0.25)) if has_secondary_glare else 0.0,
        glare_center2=float(rng.uniform(8.0, 24.0)),
        glare_width2=float(rng.uniform(3.5, 7.5)),
        occl_amp=float(rng.uniform(0.05, 0.35)),
        occl_center=float(rng.uniform(10.0, 36.0)),
        occl_width=float(rng.uniform(2.5, 7.0)),
        ambiguity_base=float(rng.uniform(0.16, 0.32)),
        ambiguity_amp=float(rng.uniform(0.20, 0.42)),
        ambiguity_center=float(rng.uniform(12.0, 32.0)),
        ambiguity_width=float(rng.uniform(5.0, 10.0)),
        motion_base=float(rng.uniform(0.10, 0.22)),
        motion_amp=float(rng.uniform(0.14, 0.35)),
        motion_center=float(rng.uniform(8.0, 22.0)),
        motion_width=float(rng.uniform(5.0, 10.0)),
        osc_window_center=float(rng.uniform(22.0, 31.0)),
        osc_window_width=float(rng.uniform(5.0, 9.5)),
        osc_attr_amp=float(rng.uniform(0.06, 0.14)) if osc_enabled else 0.0,
        osc_conflict_amp=float(rng.uniform(0.08, 0.18)) if osc_enabled else 0.0,
        osc_open_amp=float(rng.uniform(0.02, 0.07)) if osc_enabled else 0.0,
        osc_phase=float(rng.uniform(0.0, 2.0 * math.pi)),
        osc_cycles=float(rng.uniform(1.5, 3.5)) if osc_enabled else 0.0,
        osc_enabled=osc_enabled,
        semantic_noise_scale=float(rng.uniform(0.020, 0.050)),
        attr_noise_scale=float(rng.uniform(0.018, 0.040)),
        motion_noise_scale=float(rng.uniform(0.010, 0.028)),
    )

# ============================================================
# Latent environment fields
# ============================================================
def latent_glare(distance: float, case: B1Case) -> float:
    value = (
        case.glare_base
        + case.glare_amp1 * gaussian(distance, case.glare_center1, case.glare_width1)
        + case.glare_amp2 * gaussian(distance, case.glare_center2, case.glare_width2)
    )
    return clamp(value, 0.0, 1.0)


def latent_occlusion(distance: float, case: B1Case) -> float:
    value = case.occl_amp * gaussian(distance, case.occl_center, case.occl_width)
    return clamp(value, 0.0, 1.0)


def latent_attr_ambiguity(distance: float, case: B1Case, glare: float) -> float:
    value = (
        case.ambiguity_base
        + case.ambiguity_amp * gaussian(distance, case.ambiguity_center, case.ambiguity_width)
        + 0.16 * glare
    )
    return clamp(value, 0.0, 1.0)


def latent_motion_contradiction(distance: float, case: B1Case) -> float:
    value = case.motion_base + case.motion_amp * gaussian(distance, case.motion_center, case.motion_width)
    if case.lane2_open and not case.lane3_open:
        value += 0.10
    return clamp(value, 0.0, 1.0)


def lane_signal_visibility(distance: float, glare: float, occlusion: float) -> float:
    proximity_gain = logistic((42.0 - distance) / 8.5)
    value = proximity_gain * (1.0 - 0.35 * occlusion) * (1.0 - 0.15 * glare)
    return clamp(value, 0.0, 1.0)


def oscillation_envelope(distance: float, case: B1Case) -> float:
    if not case.osc_enabled:
        return 0.0
    return gaussian(distance, case.osc_window_center, case.osc_window_width)


def oscillation_wave(distance: float, case: B1Case) -> float:
    if not case.osc_enabled:
        return 0.0
    x = (distance - case.osc_window_center) / max(case.osc_window_width, 1e-6)
    return math.sin(case.osc_phase + 2.0 * math.pi * case.osc_cycles * x)

# ============================================================
# Ground-truth support variables
# ============================================================
def true_open_strength(distance: float, case: B1Case, vis: float) -> float:
    strength_l2 = (0.95 if case.lane2_open else 0.05) * vis
    strength_l3 = (0.90 if case.lane3_open else 0.05) * vis
    return clamp(max(strength_l2, strength_l3), 0.0, 1.0)


def true_attr_target(distance: float, case: B1Case, vis: float, glare: float, ambiguity: float) -> float:
    near_gain = logistic((26.0 - distance) / 5.8)
    clarity = clamp(0.55 * vis + 0.25 * (1.0 - glare) + 0.20 * (1.0 - ambiguity), 0.0, 1.0)

    if case.lane3_open and not case.lane2_open:
        base = 0.62 + 0.26 * near_gain + 0.08 * clarity
    elif case.lane2_open and not case.lane3_open:
        # Canonical B1 risk: adjacent lane has open cue, but ego lane should not inherit it.
        base = 0.10 + 0.05 * near_gain + 0.04 * (1.0 - ambiguity)
    elif case.lane2_open and case.lane3_open:
        base = 0.42 + 0.18 * near_gain + 0.10 * clarity
    else:
        base = 0.08 + 0.03 * near_gain

    return clamp(base, 0.0, 1.0)

# ============================================================
# Oracle state
# ============================================================
def oracle_state(distance: float, glare: float, vis: float, attr_truth: float, case: B1Case) -> str:
    if not case.lane3_open:
        return "UNSAFE_EGO"
    if distance < 28.0 and vis > 0.45 and glare < 0.60 and attr_truth > 0.55:
        return "CONFIRMABLE_EGO"
    return "UNCERTAIN_EGO"

# ============================================================
# Shared field generation
# ============================================================
def build_shared_field(case: B1Case) -> Dict[str, np.ndarray]:
    """
    Generate one shared environment + observation field for the case.
    This field is reused by all architectures. Differences between stacks
    come from fusion / arbitration / policy, not from different noise draws.
    """
    rng = np.random.default_rng(case.seed + 777)

    rows: List[Dict[str, Any]] = []
    sem_noise_state = 0.0
    attr_noise_state = 0.0
    motion_noise_state = 0.0

    for distance in FIELD_DISTANCE_DESC:
        glare = latent_glare(distance, case)
        occlusion = latent_occlusion(distance, case)
        ambiguity = latent_attr_ambiguity(distance, case, glare)
        motion_contra = latent_motion_contradiction(distance, case)
        visibility = lane_signal_visibility(distance, glare, occlusion)
        osc_env = oscillation_envelope(distance, case)
        osc_wave = oscillation_wave(distance, case)

        open_support = true_open_strength(distance, case, visibility)
        attr_truth = true_attr_target(distance, case, visibility, glare, ambiguity)
        oracle = oracle_state(distance, glare, visibility, attr_truth, case)

        # Shared correlated observation noise across all architectures.
        sem_noise_state = 0.74 * sem_noise_state + float(rng.normal(0.0, case.semantic_noise_scale))
        attr_noise_state = 0.76 * attr_noise_state + float(rng.normal(0.0, case.attr_noise_scale))
        motion_noise_state = 0.78 * motion_noise_state + float(rng.normal(0.0, case.motion_noise_scale))

        # Shared observed channels
        z_open = clamp(
            0.06 + 0.86 * open_support + 0.18 * glare - 0.06 * occlusion
            + case.osc_open_amp * osc_env * osc_wave
            + sem_noise_state,
            0.0,
            1.0,
        )
        z_attr = clamp(
            attr_truth + 0.10 * ambiguity + 0.06 * glare - 0.05 * motion_contra
            - case.osc_attr_amp * osc_env * osc_wave
            + attr_noise_state,
            0.0,
            1.0,
        )
        z_conflict = clamp(
            0.60 * motion_contra + 0.40 * ambiguity
            + case.osc_conflict_amp * osc_env * osc_wave
            + motion_noise_state,
            0.0,
            1.0,
        )

        rows.append(
            {
                "distance_m": distance,
                "glare": glare,
                "occlusion": occlusion,
                "attr_ambiguity": ambiguity,
                "motion_contradiction": motion_contra,
                "signal_visibility": visibility,
                "open_support": open_support,
                "attr_truth": attr_truth,
                "oracle_state": oracle,
                "oracle_id": ORACLE_TO_ID[oracle],
                "z_open": z_open,
                "z_attr": z_attr,
                "z_conflict": z_conflict,
                "oscillation_env": osc_env,
            }
        )

    df = pd.DataFrame(rows).sort_values("distance_m")
    return {col: df[col].to_numpy() for col in df.columns}

# ============================================================
# Architecture-specific fusion and decision
# ============================================================
def update_passability_belief(
    architecture: str,
    prev_belief: float,
    z_open: float,
    z_attr: float,
    z_conflict: float,
) -> float:
    """
    Architecture differences live here:
    - camera_only: over-converts open-looking visual evidence into passability belief
    - multi_sensor_permissive: fuses contradiction cues but still commits relatively early
    - mitigation: same evidence channels as multi-sensor, but with guarded damping
    """
    if architecture == "camera_only":
        effective_attr = clamp(0.78 * z_attr + 0.22, 0.0, 1.0)
        raw = z_open * effective_attr + 0.04 * z_open
        alpha = 0.36

    elif architecture == "multi_sensor_permissive":
        effective_attr = z_attr
        raw = z_open * effective_attr * (1.0 - 0.10 * z_conflict) + 0.03 * z_open
        alpha = 0.50

    else:
        effective_attr = clamp(z_attr - 0.08 * z_conflict, 0.0, 1.0)
        raw = z_open * effective_attr * (1.0 - 0.30 * z_conflict)
        if z_attr < 0.22:
            raw *= 0.55
        alpha = 0.64

    belief = alpha * prev_belief + (1.0 - alpha) * raw
    return clamp(belief, 0.0, 1.0)


def decide_state(
    architecture: str,
    distance: float,
    z_open: float,
    z_attr: float,
    z_conflict: float,
    b_pass: float,
    prev_state: str,
    confirm_count: int,
) -> tuple[str, int]:
    in_zone = distance < 52.0
    near_gate = distance < 22.0

    if architecture == "camera_only":
        if not in_zone:
            return "KEEP", 0

        score = 0.75 * b_pass + 0.25 * z_open
        if score > 0.35:
            return "COMMIT_EGO", 0
        if near_gate and score < 0.16 and z_conflict > 0.42:
            return "ABORT_ENTRY", 0
        if z_open > 0.30 or z_conflict > 0.36:
            return "CAUTIOUS_HOLD", 0
        return "KEEP", 0

    if architecture == "multi_sensor_permissive":
        if not in_zone:
            return "KEEP", 0

        score = 0.72 * b_pass + 0.20 * z_attr + 0.10 * z_open - 0.08 * z_conflict
        if prev_state == "COMMIT_EGO" and (score < 0.27 or z_conflict > 0.42 or z_attr < 0.14):
            return "CAUTIOUS_HOLD", 0
        if score > 0.31 and z_attr > 0.16:
            return "COMMIT_EGO", 0
        if near_gate and score < 0.17 and z_conflict > 0.43:
            return "ABORT_ENTRY", 0
        if z_open > 0.22 or z_conflict > 0.30:
            return "CAUTIOUS_HOLD", 0
        return "KEEP", 0

    # Mitigation: explicit "unconfirmed -> cautious hold -> multi-frame confirmation" logic
    if not in_zone:
        return "KEEP", 0

    confirmed_frame = (b_pass > 0.29) and (z_attr > 0.26) and (z_conflict < 0.44)

    if confirmed_frame:
        confirm_count += 1
    elif z_conflict > 0.52 or z_attr < 0.18 or b_pass < 0.16:
        confirm_count = max(confirm_count - 2, 0)
    else:
        confirm_count = max(confirm_count - 1, 0)

    if confirm_count >= 3 and b_pass > 0.30 and z_conflict < 0.48:
        return "COMMIT_EGO", confirm_count

    if near_gate and (z_conflict > 0.60 or (confirm_count == 0 and (z_attr < 0.22 or b_pass < 0.18))):
        return "ABORT_ENTRY", confirm_count

    return "CAUTIOUS_HOLD", confirm_count

# ============================================================
# Speed policy and simple dynamics
# ============================================================
def target_speed(architecture: str, state: str, v0: float, z_conflict: float) -> float:
    if architecture == "camera_only":
        if state == "KEEP":
            return v0
        if state == "CAUTIOUS_HOLD":
            return (0.88 - 0.03 * z_conflict) * v0
        if state == "COMMIT_EGO":
            return 0.95 * v0
        return 0.84 * v0

    if architecture == "multi_sensor_permissive":
        if state == "KEEP":
            return 0.98 * v0
        if state == "CAUTIOUS_HOLD":
            return (0.82 - 0.05 * z_conflict) * v0
        if state == "COMMIT_EGO":
            return 0.91 * v0
        return 0.80 * v0

    if state == "KEEP":
        return 0.96 * v0
    if state == "CAUTIOUS_HOLD":
        return (0.79 - 0.05 * z_conflict) * v0
    if state == "COMMIT_EGO":
        return 0.90 * v0
    return 0.79 * v0


def acceleration_bounds(state: str) -> tuple[float, float]:
    if state == "KEEP":
        return -2.0, 1.5
    if state == "CAUTIOUS_HOLD":
        return -3.0, 1.0
    if state == "COMMIT_EGO":
        return -2.0, 1.0
    return -3.5, 0.8

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
    c_unsafe_commit = float(action == "COMMIT_EGO" and oracle == "UNSAFE_EGO")
    c_premature = float(action == "COMMIT_EGO" and oracle == "UNCERTAIN_EGO")
    c_late = float(action != "COMMIT_EGO" and oracle == "CONFIRMABLE_EGO")
    c_unnecessary_merge = float(action == "ABORT_ENTRY" and oracle == "CONFIRMABLE_EGO")
    c_osc = float(action != prev_action)
    c_eff = max(v_ref - speed, 0.0) / max(v_ref, 1e-6)

    weights = {
        "unsafe_commit": 10.0,
        "premature_commit": 4.0,
        "late_confirmation": 1.5,
        "unnecessary_merge": 1.5,
        "oscillation": 1.0,
        "efficiency": 0.5,
    }

    total = (
        weights["unsafe_commit"] * c_unsafe_commit
        + weights["premature_commit"] * c_premature
        + weights["late_confirmation"] * c_late
        + weights["unnecessary_merge"] * c_unnecessary_merge
        + weights["oscillation"] * c_osc
        + weights["efficiency"] * c_eff
    )

    return {
        "cost_unsafe_commit": c_unsafe_commit,
        "cost_premature_commit": c_premature,
        "cost_late_confirmation": c_late,
        "cost_unnecessary_merge": c_unnecessary_merge,
        "cost_oscillation": c_osc,
        "cost_efficiency": c_eff,
        "cost_total": total,
    }

# ============================================================
# Simulation
# ============================================================
def simulate_run(case: B1Case, field: Dict[str, np.ndarray], architecture: str) -> pd.DataFrame:
    t = 0.0
    distance = DIST_START
    speed = case.v0
    belief = 0.0
    prev_state = "KEEP"
    confirm_count = 0

    rows: List[Dict[str, Any]] = []

    while distance > 0.0 and t < SIM_T_MAX:
        glare = interp_cont(field, "glare", distance)
        occlusion = interp_cont(field, "occlusion", distance)
        ambiguity = interp_cont(field, "attr_ambiguity", distance)
        motion_contra = interp_cont(field, "motion_contradiction", distance)
        visibility = interp_cont(field, "signal_visibility", distance)
        open_support = interp_cont(field, "open_support", distance)
        attr_truth = interp_cont(field, "attr_truth", distance)
        osc_env = interp_cont(field, "oscillation_env", distance)

        z_open = interp_cont(field, "z_open", distance)
        z_attr = interp_cont(field, "z_attr", distance)
        z_conflict = interp_cont(field, "z_conflict", distance)
        oracle = interp_nearest_str(field, "oracle_state", distance)

        belief = update_passability_belief(architecture, belief, z_open, z_attr, z_conflict)
        state, confirm_count = decide_state(
            architecture=architecture,
            distance=distance,
            z_open=z_open,
            z_attr=z_attr,
            z_conflict=z_conflict,
            b_pass=belief,
            prev_state=prev_state,
            confirm_count=confirm_count,
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
                "lane2_open": case.lane2_open,
                "lane3_open": case.lane3_open,
                "scenario_tag": case.scenario_tag,
                "glare": glare,
                "occlusion": occlusion,
                "attr_ambiguity": ambiguity,
                "motion_contradiction": motion_contra,
                "signal_visibility": visibility,
                "open_support": open_support,
                "attr_truth": attr_truth,
                "oscillation_env": osc_env,
                "z_open": z_open,
                "z_attr": z_attr,
                "z_conflict": z_conflict,
                "b_pass": belief,
                "decision_state": state,
                "decision_id": STATE_TO_ID[state],
                "oracle_state": oracle,
                "oracle_id": ORACLE_TO_ID[oracle],
                "confirm_count": confirm_count,
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
def summarize_run(run_df: pd.DataFrame, case: B1Case) -> Dict[str, Any]:
    states = run_df["decision_state"].to_numpy()
    oracle = run_df["oracle_state"].to_numpy()
    decision_ids = run_df["decision_id"].to_numpy()
    distance = run_df["distance_m"].to_numpy()
    speed = run_df["speed_mps"].to_numpy()

    commit_mask = states == "COMMIT_EGO"
    hold_mask = states == "CAUTIOUS_HOLD"
    merge_mask = states == "ABORT_ENTRY"

    wrong_commit_mask = commit_mask & (oracle == "UNSAFE_EGO")
    premature_commit_mask = commit_mask & (oracle == "UNCERTAIN_EGO")
    confirmable_noncommit_mask = (~commit_mask) & (oracle == "CONFIRMABLE_EGO")
    confirmable_mask = oracle == "CONFIRMABLE_EGO"

    t_final = float(run_df["time_s"].iloc[-1] + DT)
    t_nominal = DIST_START / case.v0

    min_gate_time_wrong_commit = np.inf
    if wrong_commit_mask.any():
        min_gate_time_wrong_commit = float(np.min(distance[wrong_commit_mask] / np.maximum(speed[wrong_commit_mask], 1e-6)))
    first_commit_distance = float(distance[commit_mask][0]) if commit_mask.any() else np.nan
    first_confirmable_distance = float(distance[confirmable_mask][0]) if confirmable_mask.any() else np.nan
    ecl_m = (
        first_commit_distance - first_confirmable_distance
        if commit_mask.any() and confirmable_mask.any()
        else np.nan
    )

    out = {
        "run_id": case.run_id,
        "architecture": run_df["architecture"].iloc[0],
        "scenario_tag": case.scenario_tag,
        "lane2_open": case.lane2_open,
        "lane3_open": case.lane3_open,

        # Headline metrics for paper tables
        "WCR_event": float(wrong_commit_mask.any()),
        "PCR_event": float(premature_commit_mask.any()),
        "ECL_m": ecl_m,
        "DOC": int(np.sum(decision_ids[1:] != decision_ids[:-1])),
        "Ttravel_s": t_final,
        "Tdelay_s": max(t_final - t_nominal, 0.0),

        # Auxiliary ratios
        "commit_ratio": float(commit_mask.mean()),
        "hold_ratio": float(hold_mask.mean()),
        "abort_entry_ratio": float(merge_mask.mean()),
        "wrong_commit_ratio": float(wrong_commit_mask.mean()),
        "premature_commit_ratio": float(premature_commit_mask.mean()),
        "confirmable_noncommit_ratio": float(confirmable_noncommit_mask.mean()),

        # Useful diagnostics
        "first_commit_distance_m": first_commit_distance,
        "first_abort_distance_m": float(distance[merge_mask][0]) if merge_mask.any() else np.nan,
        "first_confirmable_distance_m": first_confirmable_distance,
        "mean_attr_truth": float(run_df["attr_truth"].mean()),
        "mean_z_open": float(run_df["z_open"].mean()),
        "mean_z_attr": float(run_df["z_attr"].mean()),
        "mean_z_conflict": float(run_df["z_conflict"].mean()),
        "mean_b_pass": float(run_df["b_pass"].mean()),
        "min_gate_time_wrong_commit_s": min_gate_time_wrong_commit,

        # Auxiliary cost
        "total_cost": float(run_df["cost_total"].sum() * DT),
        "unsafe_commit_cost": float(run_df["cost_unsafe_commit"].sum() * DT),
        "premature_commit_cost": float(run_df["cost_premature_commit"].sum() * DT),
        "late_confirmation_cost": float(run_df["cost_late_confirmation"].sum() * DT),
        "unnecessary_merge_cost": float(run_df["cost_unnecessary_merge"].sum() * DT),
        "oscillation_cost": float(run_df["cost_oscillation"].sum() * DT),
        "efficiency_cost": float(run_df["cost_efficiency"].sum() * DT),
    }
    return out


def interpolate_run_to_grid(run_df: pd.DataFrame, case: B1Case, architecture: str) -> pd.DataFrame:
    df = run_df.sort_values("distance_m")
    xp = df["distance_m"].to_numpy()

    out = {
        "run_id": np.full_like(GRID_DISTANCE_ASC, case.run_id, dtype=int),
        "architecture": np.array([architecture] * len(GRID_DISTANCE_ASC)),
        "distance_m": GRID_DISTANCE_ASC.copy(),
        "lane2_open": np.array([case.lane2_open] * len(GRID_DISTANCE_ASC)),
        "lane3_open": np.array([case.lane3_open] * len(GRID_DISTANCE_ASC)),
        "scenario_tag": np.array([case.scenario_tag] * len(GRID_DISTANCE_ASC)),
    }

    interp_cols = [
        "glare", "occlusion", "attr_ambiguity", "motion_contradiction",
        "signal_visibility", "attr_truth", "z_open", "z_attr", "z_conflict", "oscillation_env",
        "b_pass", "speed_mps", "cost_total",
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
        "glare", "occlusion", "attr_ambiguity", "motion_contradiction",
        "signal_visibility", "attr_truth", "z_open", "z_attr", "z_conflict", "oscillation_env",
        "b_pass", "speed_mps", "cost_total",
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
        (raw_df["scenario_tag"] == "adjacent_open_risk")
        & (raw_df["architecture"] == "multi_sensor_permissive")
    ]
    run_ids = sorted(sub["run_id"].unique())
    if len(run_ids) == 0:
        return

    candidate = (
        sub.groupby("run_id", as_index=False)
        .agg(
            doc=("decision_id", lambda x: int(np.sum(x.to_numpy()[1:] != x.to_numpy()[:-1]))),
            wcr=("oracle_state", lambda x: 0.0),
            mean_gap=("b_pass", lambda x: float(np.mean(np.abs(x.to_numpy() - COMMIT_THRESHOLD)))),
            osc_env=("oscillation_env", "mean"),
        )
    )
    wrong_commit_ids = set(
        sub.loc[
            (sub["decision_state"] == "COMMIT_EGO") & (sub["oracle_state"] == "UNSAFE_EGO"),
            "run_id",
        ].unique()
    )
    candidate["wcr"] = candidate["run_id"].isin(wrong_commit_ids).astype(float)
    candidate = candidate.sort_values(["wcr", "doc", "osc_env", "mean_gap"], ascending=[True, False, False, True])
    run_id = int(candidate.iloc[0]["run_id"])

    fig, axes = plt.subplots(4, 1, figsize=(10, 11), sharex=True)

    # Shared environment
    df_ref = raw_df[
        (raw_df["run_id"] == run_id)
        & (raw_df["architecture"] == "camera_only")
    ].sort_values("distance_m", ascending=False)
    axes[0].plot(df_ref["distance_m"], df_ref["glare"], linewidth=2.0, label="Glare")
    axes[0].plot(df_ref["distance_m"], df_ref["attr_ambiguity"], linewidth=2.0, label="Attribution ambiguity")
    axes[0].plot(df_ref["distance_m"], df_ref["z_conflict"], linewidth=2.0, label="Observed conflict")
    axes[0].set_ylabel("Shared env.")
    axes[0].set_title(f"Typical adjacent-open-risk run (run_id={run_id})")
    axes[0].grid(alpha=0.25)
    axes[0].legend(ncol=3, fontsize=9)

    # Beliefs
    axes[1].plot(df_ref["distance_m"], df_ref["z_open"], linestyle="--", linewidth=2.0, label="Shared open cue")
    axes[1].plot(df_ref["distance_m"], df_ref["z_attr"], linestyle="--", linewidth=2.0, label="Shared ego-lane cue")
    for arch in ARCHITECTURES:
        df = raw_df[
            (raw_df["run_id"] == run_id)
            & (raw_df["architecture"] == arch)
        ].sort_values("distance_m", ascending=False)
        axes[1].plot(df["distance_m"], df["b_pass"], linewidth=2.2, label=f"{ARCH_LABELS[arch]} belief")
    axes[1].axhline(COMMIT_THRESHOLD, linestyle=":", linewidth=1.2)
    axes[1].set_ylabel("Belief")
    axes[1].grid(alpha=0.25)
    axes[1].legend(ncol=2, fontsize=8)

    # Decisions
    for arch in ARCHITECTURES:
        df = raw_df[
            (raw_df["run_id"] == run_id)
            & (raw_df["architecture"] == arch)
        ].sort_values("distance_m", ascending=False)
        axes[2].step(df["distance_m"], df["decision_id"], where="post", linewidth=2.0, label=ARCH_LABELS[arch])
    axes[2].set_ylabel("Decision")
    axes[2].set_yticks(list(STATE_TO_ID.values()), list(STATE_TO_ID.keys()))
    axes[2].grid(alpha=0.25)
    axes[2].legend(ncol=3, fontsize=9)

    # Speed
    for arch in ARCHITECTURES:
        df = raw_df[
            (raw_df["run_id"] == run_id)
            & (raw_df["architecture"] == arch)
        ].sort_values("distance_m", ascending=False)
        axes[3].plot(df["distance_m"], df["speed_mps"], linewidth=2.0, label=ARCH_LABELS[arch])
    axes[3].set_ylabel("Speed (m/s)")
    axes[3].set_xlabel("Distance to entrance (m)")
    axes[3].invert_xaxis()
    axes[3].grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(save_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_fitted_beliefs(fitted_df: pd.DataFrame, save_path: Path) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(9.5, 11), sharex=True)

    for ax, arch in zip(axes, ARCHITECTURES):
        sub = fitted_df[fitted_df["architecture"] == arch].sort_values("distance_m", ascending=False)
        x = sub["distance_m"].to_numpy()

        for metric, label in [
            ("z_open", "Open cue"),
            ("z_attr", "Ego-lane cue"),
            ("b_pass", "Passability belief"),
        ]:
            ax.plot(x, sub[f"{metric}_mean"], linewidth=2.3, label=label)
            ax.fill_between(x, sub[f"{metric}_q25"], sub[f"{metric}_q75"], alpha=0.15)

        ax.axhline(COMMIT_THRESHOLD, linestyle=":", linewidth=1.2)
        ax.set_title(ARCH_LABELS[arch])
        ax.set_ylabel("Probability / belief")
        ax.set_ylim(0, 1)
        ax.grid(alpha=0.25)

    axes[-1].set_xlabel("Distance to entrance (m)")
    axes[-1].invert_xaxis()
    axes[0].legend(ncol=3, fontsize=9)

    fig.tight_layout()
    fig.savefig(save_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_headline_metrics(summary_df: pd.DataFrame, save_path: Path) -> None:
    metrics = ["WCR_event", "DOC", "Tdelay_s", "ECL_m"]
    titles = [
        "Wrong commitment rate",
        "Decision oscillation count",
        "Travel delay (s)",
        "Early-commit lead (m)",
    ]

    mean_df = summary_df.groupby("architecture", as_index=False)[metrics].mean().set_index("architecture").loc[ARCHITECTURES]
    std_df = summary_df.groupby("architecture")[metrics].std().reindex(ARCHITECTURES)
    count_df = summary_df.groupby("architecture").size().reindex(ARCHITECTURES)

    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.6))
    axes = axes.ravel()
    x = np.arange(len(ARCHITECTURES))

    for ax, metric, title in zip(axes, metrics, titles):
        vals = mean_df[metric].to_numpy()
        if metric == "WCR_event":
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
        "unsafe_commit_cost",
        "premature_commit_cost",
        "late_confirmation_cost",
        "unnecessary_merge_cost",
        "oscillation_cost",
        "efficiency_cost",
    ]
    labels = [
        "Unsafe commit",
        "Premature commit",
        "Late confirm",
        "Unnecessary merge",
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
        "WCR_event",
        "DOC",
        "Tdelay_s",
        "total_cost",
    ]
    disp = summary_means[show_cols].copy()
    disp["architecture"] = disp["architecture"].map(ARCH_LABELS)
    disp = disp.round(3)

    table = ax.table(
        cellText=disp.values,
        colLabels=["Architecture", "WCR", "DOC", "Tdelay (s)", "Aux. cost"],
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

    summary_means = (
        summary_df.groupby("architecture", as_index=False)
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

    stem = "b1_aligned_partA"

    raw_path = DATAS_DIR / f"{stem}_runs.csv"
    summary_path = DATAS_DIR / f"{stem}_summary.csv"
    fitted_path = DATAS_DIR / f"{stem}_fitted_curves.csv"
    cases_path = DATAS_DIR / f"{stem}_cases.csv"
    means_path = DATAS_DIR / f"{stem}_summary_means.csv"
    by_tag_path = DATAS_DIR / f"{stem}_summary_by_tag.csv"

    raw_df.to_csv(raw_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    fitted_df.to_csv(fitted_path, index=False)
    cases_df.to_csv(cases_path, index=False)
    summary_means.to_csv(means_path, index=False)
    summary_by_tag.to_csv(by_tag_path, index=False)

    plot_typical_case(raw_df, FIGURES_DIR / f"{stem}_typical_case.png")
    plot_fitted_beliefs(fitted_df, FIGURES_DIR / f"{stem}_fitted_beliefs.png")
    plot_headline_metrics(summary_df, FIGURES_DIR / f"{stem}_headline_metrics.png")
    plot_cost_breakdown(summary_df, FIGURES_DIR / f"{stem}_cost_breakdown.png")
    plot_summary_table(summary_means, FIGURES_DIR / f"{stem}_summary_table.png")

    print("Saved:")
    print(raw_path)
    print(summary_path)
    print(fitted_path)
    print(cases_path)
    print(means_path)
    print(by_tag_path)
    print(FIGURES_DIR / f"{stem}_typical_case.png")
    print(FIGURES_DIR / f"{stem}_fitted_beliefs.png")
    print(FIGURES_DIR / f"{stem}_headline_metrics.png")
    print(FIGURES_DIR / f"{stem}_cost_breakdown.png")
    print(FIGURES_DIR / f"{stem}_summary_table.png")

    print("\nAverage headline summary:")
    print(
        summary_means[
            ["architecture", "WCR_event", "DOC", "Tdelay_s", "ECL_m", "total_cost"]
        ].round(3).to_string(index=False)
    )

    print("\nStratified by scenario tag:")
    print(
        summary_by_tag[
            ["scenario_tag", "architecture", "WCR_event", "DOC", "Tdelay_s", "ECL_m", "PCR_event"]
        ].round(3).to_string(index=False)
    )


if __name__ == "__main__":
    main()
