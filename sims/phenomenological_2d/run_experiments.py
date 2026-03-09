from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from .palette import PALETTE
from .simulator import A1Case, A2Case, CAVSimulation

MODES = ["camera_only", "multimodal_permissive", "mitigation"]
MODE_LABEL = {
    "camera_only": "Camera-only",
    "multimodal_permissive": "Multi-modal permissive",
    "mitigation": "Mitigation",
}

SCENARIO_METRICS = {
    "A1": ["pbs", "false_brake_frames", "peak_jerk", "travel_time_s", "avg_speed"],
    "A2": ["evr", "barrier_collision", "peak_jerk", "travel_time_s", "stop_time_ratio", "min_stop_margin_m"],
}

PAIRWISE = [
    ("camera_only", "multimodal_permissive"),
    ("multimodal_permissive", "mitigation"),
    ("camera_only", "mitigation"),
]


def _mean_std(values: list[float]) -> tuple[float, float, float]:
    arr = np.array(values, dtype=float)
    if arr.size == 0:
        return 0.0, 0.0, 0.0
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0
    ci95 = float(stats.sem(arr) * stats.t.ppf(0.975, arr.size - 1)) if arr.size > 1 else 0.0
    return mean, std, ci95


def _bootstrap_diff_ci(
    x: np.ndarray, y: np.ndarray, *, n_boot: int = 3000, seed: int = 42
) -> tuple[float, float, float]:
    """Mean difference x - y with bootstrap 95% CI."""
    rng = np.random.default_rng(seed)
    x = x.astype(float)
    y = y.astype(float)
    if x.size == 0 or y.size == 0:
        return 0.0, 0.0, 0.0

    diffs = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        xb = rng.choice(x, size=x.size, replace=True)
        yb = rng.choice(y, size=y.size, replace=True)
        diffs[i] = np.mean(xb) - np.mean(yb)

    mean_diff = float(np.mean(x) - np.mean(y))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return mean_diff, float(lo), float(hi)


def _mann_whitney_p(x: np.ndarray, y: np.ndarray) -> float:
    if x.size == 0 or y.size == 0:
        return 1.0
    if np.allclose(x, x[0]) and np.allclose(y, y[0]) and np.isclose(x[0], y[0]):
        return 1.0
    try:
        _, p = stats.mannwhitneyu(x, y, alternative="two-sided")
        return float(p)
    except Exception:
        return 1.0


def _case_to_dict(case: A1Case | A2Case) -> dict[str, float]:
    d: dict[str, float] = {}
    for key, value in case.__dict__.items():
        if isinstance(value, tuple):
            continue
        d[f"cfg_{key}"] = float(value)
    return d


def run_batch(
    n_seeds: int,
) -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, float]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    per_run: list[dict[str, Any]] = []
    sample_runs: dict[str, dict[str, Any]] = {}

    for seed in range(n_seeds):
        sampler = CAVSimulation(seed=seed)
        a1_case = sampler.sample_a1_case()
        a2_case = sampler.sample_a2_case()

        noise_seed_a1 = 100_000 + seed
        noise_seed_a2 = 200_000 + seed

        for mode in MODES:
            sim = CAVSimulation(seed=seed)
            a1 = sim.run_a1(mode, case=a1_case, noise_seed=noise_seed_a1)
            a2 = sim.run_a2(mode, case=a2_case, noise_seed=noise_seed_a2)

            row_a1 = {
                "seed": seed,
                "scenario": "A1",
                "mode": mode,
                **a1["metrics"],
                **_case_to_dict(a1_case),
            }
            row_a2 = {
                "seed": seed,
                "scenario": "A2",
                "mode": mode,
                **a2["metrics"],
                **_case_to_dict(a2_case),
            }
            per_run.append(row_a1)
            per_run.append(row_a2)

            if seed == 7:
                sample_runs.setdefault("A1", {})[mode] = a1
                sample_runs.setdefault("A2", {})[mode] = a2

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in per_run:
        grouped.setdefault((row["scenario"], row["mode"]), []).append(row)

    summary: dict[tuple[str, str], dict[str, float]] = {}
    for key, rows in grouped.items():
        scenario, _mode = key
        metric_keys = [k for k in rows[0].keys() if k not in {"seed", "scenario", "mode"} and not k.startswith("cfg_")]
        summary_row: dict[str, float] = {"n": float(len(rows))}
        for mk in metric_keys:
            vals = [float(r[mk]) for r in rows]
            mean, std, ci95 = _mean_std(vals)
            summary_row[f"{mk}_mean"] = mean
            summary_row[f"{mk}_std"] = std
            summary_row[f"{mk}_ci95"] = ci95
        summary[key] = summary_row

    significance_rows: list[dict[str, Any]] = []
    for scenario, metrics in SCENARIO_METRICS.items():
        for metric in metrics:
            for mode_a, mode_b in PAIRWISE:
                xa = np.array(
                    [float(r[metric]) for r in per_run if r["scenario"] == scenario and r["mode"] == mode_a],
                    dtype=float,
                )
                xb = np.array(
                    [float(r[metric]) for r in per_run if r["scenario"] == scenario and r["mode"] == mode_b],
                    dtype=float,
                )
                mean_diff, ci_lo, ci_hi = _bootstrap_diff_ci(xa, xb, n_boot=3000, seed=17)
                p_value = _mann_whitney_p(xa, xb)
                significance_rows.append(
                    {
                        "scenario": scenario,
                        "metric": metric,
                        "mode_a": mode_a,
                        "mode_b": mode_b,
                        "mean_a": float(np.mean(xa)) if xa.size else 0.0,
                        "mean_b": float(np.mean(xb)) if xb.size else 0.0,
                        "mean_diff_a_minus_b": mean_diff,
                        "bootstrap_ci95_low": ci_lo,
                        "bootstrap_ci95_high": ci_hi,
                        "mann_whitney_p": p_value,
                        "significant_p_lt_0_05": int(p_value < 0.05),
                    }
                )

    return per_run, summary, significance_rows, sample_runs


def plot_a1_run(runs: dict[str, Any], out: Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 5.0), sharex=True)
    fig.patch.set_facecolor("white")

    for mode in MODES:
        run = runs[mode]
        axes[0].plot(
            run["time"],
            run["accel"],
            lw=1.7,
            label=MODE_LABEL[mode],
            color=PALETTE[mode],
        )

    axes[0].set_ylabel("Longitudinal accel (m/s$^2$)")
    axes[0].grid(True, color="#eaeaea", lw=0.8)
    axes[0].legend(loc="upper right", fontsize=8)
    axes[0].set_title("A1: Ghost-Vehicle-Induced Braking")

    for mode in MODES:
        run = runs[mode]
        ttc = np.where(np.isfinite(run["ttc_virtual"]), run["ttc_virtual"], np.nan)
        axes[1].plot(
            run["time"],
            ttc,
            lw=1.5,
            label=f"{MODE_LABEL[mode]} TTC$_{{virtual}}$",
            color=PALETTE[mode],
        )

    axes[1].axhline(3.0, color=PALETTE["bg_neutral_1"], lw=1.2, ls=":", label="Safety threshold")
    axes[1].set_ylabel("TTC$_{virtual}$ (s)")
    axes[1].set_xlabel("Time (s)")
    axes[1].grid(True, color="#eaeaea", lw=0.8)
    axes[1].legend(loc="upper right", fontsize=7)

    fig.tight_layout()
    fig.savefig(out, dpi=220)
    plt.close(fig)


def plot_a2_run(runs: dict[str, Any], out: Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(6.6, 4.4), sharex=True)
    fig.patch.set_facecolor("white")

    plot_order = ["multimodal_permissive", "camera_only", "mitigation"]

    for mode in plot_order:
        run = runs[mode]
        style: dict[str, Any] = {"lw": 1.8}
        if mode == "multimodal_permissive":
            style.update({"ls": "--"})
        elif mode == "camera_only":
            # Marker overlay makes camera-only visible when it numerically overlaps
            # with multi-modal permissive in A2 speed trajectories.
            style.update({"marker": "o", "ms": 2.8, "markevery": 8, "mfc": "white", "mew": 0.9})
        axes[0].plot(run["time"], run["speed"], label=MODE_LABEL[mode], color=PALETTE[mode], **style)
    axes[0].set_ylabel("Speed (m/s)")
    axes[0].set_ylim(bottom=0.0)
    axes[0].grid(True, color="#eaeaea", lw=0.8)
    axes[0].legend(loc="upper right", fontsize=8)
    axes[0].set_title("A2: Transparent Barrier Handling (Compact Timeline)")

    if np.allclose(runs["camera_only"]["speed"], runs["multimodal_permissive"]["speed"]):
        axes[0].text(
            0.02,
            0.08,
            "Camera-only speed overlaps\nwith multi-modal permissive",
            transform=axes[0].transAxes,
            fontsize=7,
            color=PALETTE["bg_neutral_1"],
        )

    for mode in plot_order:
        run = runs[mode]
        style = {"lw": 1.8}
        if mode == "multimodal_permissive":
            style["ls"] = "--"
        elif mode == "camera_only":
            style.update({"marker": "o", "ms": 2.8, "markevery": 8, "mfc": "white", "mew": 0.9})
        axes[1].plot(run["time"], run["unknown_series"], label=MODE_LABEL[mode], color=PALETTE[mode], **style)
    axes[1].set_ylabel("Unknown mass $m(\\Omega)$")
    axes[1].set_ylim(0.0, 1.05)
    axes[1].grid(True, color="#eaeaea", lw=0.8)
    axes[1].set_xlabel("Time (s)")

    fig.tight_layout()
    fig.savefig(out, dpi=220)
    plt.close(fig)


def plot_summary(summary: dict[tuple[str, str], dict[str, float]], out: Path) -> None:
    labels = ["A1 PBS", "A2 EVR", "A2 Collision"]
    x = np.arange(len(labels), dtype=float)
    width = 0.24

    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    fig.patch.set_facecolor("white")

    values = {
        "camera_only": [
            summary[("A1", "camera_only")]["pbs_mean"],
            summary[("A2", "camera_only")]["evr_mean"],
            summary[("A2", "camera_only")]["barrier_collision_mean"],
        ],
        "multimodal_permissive": [
            summary[("A1", "multimodal_permissive")]["pbs_mean"],
            summary[("A2", "multimodal_permissive")]["evr_mean"],
            summary[("A2", "multimodal_permissive")]["barrier_collision_mean"],
        ],
        "mitigation": [
            summary[("A1", "mitigation")]["pbs_mean"],
            summary[("A2", "mitigation")]["evr_mean"],
            summary[("A2", "mitigation")]["barrier_collision_mean"],
        ],
    }

    offsets = {
        "camera_only": -width,
        "multimodal_permissive": 0.0,
        "mitigation": width,
    }

    for mode in MODES:
        ax.bar(
            x + offsets[mode],
            values[mode],
            width=width,
            color=PALETTE[mode],
            label=MODE_LABEL[mode],
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Mean metric value")
    ax.grid(axis="y", color="#eaeaea", lw=0.8)
    ax.legend(loc="upper right", fontsize=8)

    fig.tight_layout()
    fig.savefig(out, dpi=220)
    plt.close(fig)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    keys: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_markdown(
    path: Path,
    summary: dict[tuple[str, str], dict[str, float]],
    significance: list[dict[str, Any]],
    n_seeds: int,
) -> None:
    def pick(s: str, m: str, k: str) -> float:
        return summary[(s, m)].get(k, 0.0)

    def find_sig(scenario: str, metric: str, a: str, b: str) -> float:
        for row in significance:
            if row["scenario"] == scenario and row["metric"] == metric and row["mode_a"] == a and row["mode_b"] == b:
                return float(row["mann_whitney_p"])
        return 1.0

    p_a1 = find_sig("A1", "pbs", "multimodal_permissive", "mitigation")
    p_a2 = find_sig("A2", "evr", "multimodal_permissive", "mitigation")

    pbs_multi = pick("A1", "multimodal_permissive", "pbs_mean")
    pbs_mit = pick("A1", "mitigation", "pbs_mean")
    pbs_drop = 100.0 * (pbs_multi - pbs_mit) / max(pbs_multi, 1e-9)

    evr_multi = pick("A2", "multimodal_permissive", "evr_mean")
    evr_mit = pick("A2", "mitigation", "evr_mean")
    evr_drop = 100.0 * (evr_multi - evr_mit) / max(evr_multi, 1e-9)

    text = f"""# Part A Phenomenological Simulation Results

Runs per cell: {n_seeds} seeds across three stacks (`camera_only`, `multimodal_permissive`, `mitigation`).

## Key Outcomes

- **A1 PBS (multi-modal permissive -> mitigation)**: {pbs_multi:.3f} -> {pbs_mit:.3f} (reduction {pbs_drop:.1f}%, Mann-Whitney p={p_a1:.3g}).
- **A2 EVR (multi-modal permissive -> mitigation)**: {evr_multi:.3f} -> {evr_mit:.3f} (reduction {evr_drop:.1f}%, Mann-Whitney p={p_a2:.3g}).
- **A2 collision rate**: camera-only={pick('A2','camera_only','barrier_collision_mean'):.3f}, multi-modal permissive={pick('A2','multimodal_permissive','barrier_collision_mean'):.3f}, mitigation={pick('A2','mitigation','barrier_collision_mean'):.3f}.

## Safety-Efficiency Tradeoff

- **A2 travel time (s)**: camera-only={pick('A2','camera_only','travel_time_s_mean'):.2f}, multi-modal permissive={pick('A2','multimodal_permissive','travel_time_s_mean'):.2f}, mitigation={pick('A2','mitigation','travel_time_s_mean'):.2f}.
- **A2 stop-time ratio**: camera-only={pick('A2','camera_only','stop_time_ratio_mean'):.3f}, multi-modal permissive={pick('A2','multimodal_permissive','stop_time_ratio_mean'):.3f}, mitigation={pick('A2','mitigation','stop_time_ratio_mean'):.3f}.

## Interpretation

- The mitigation stack reduces unsafe commitment in both scenarios while preserving progress to goal under randomized conditions.
- Domain randomization avoids single-point conclusions and yields non-trivial variability for significance testing.
"""
    path.write_text(text, encoding="utf-8")


def write_compact_summary(path: Path, summary: dict[tuple[str, str], dict[str, float]]) -> None:
    rows: list[dict[str, Any]] = []
    for scenario in ("A1", "A2"):
        for mode in MODES:
            s = summary[(scenario, mode)]
            rows.append(
                {
                    "scenario": scenario,
                    "mode": mode,
                    "n": int(s["n"]),
                    "pbs_mean": s.get("pbs_mean", ""),
                    "pbs_ci95": s.get("pbs_ci95", ""),
                    "evr_mean": s.get("evr_mean", ""),
                    "evr_ci95": s.get("evr_ci95", ""),
                    "collision_rate": s.get("barrier_collision_mean", ""),
                    "travel_time_s_mean": s.get("travel_time_s_mean", ""),
                    "travel_time_s_ci95": s.get("travel_time_s_ci95", ""),
                    "avg_speed_mean": s.get("avg_speed_mean", ""),
                    "stop_time_ratio_mean": s.get("stop_time_ratio_mean", ""),
                    "min_stop_margin_m_mean": s.get("min_stop_margin_m_mean", ""),
                }
            )
    write_csv(path, rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Part A phenomenological 2D simulation")
    parser.add_argument("--seeds", type=int, default=40, help="Number of random seeds per mode/scenario")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/part_a_simulation"),
        help="Output directory for CSV/plots",
    )
    parser.add_argument("--single-seed", type=int, default=7, help="Seed used for timeline plots")
    args = parser.parse_args()

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    per_run, summary, significance, sample_runs = run_batch(args.seeds)

    write_csv(out_dir / "per_run_metrics.csv", per_run)

    summary_rows: list[dict[str, Any]] = []
    for (scenario, mode), values in sorted(summary.items()):
        row = {"scenario": scenario, "mode": mode}
        row.update(values)
        summary_rows.append(row)
    write_csv(out_dir / "summary_metrics.csv", summary_rows)
    write_compact_summary(out_dir / "summary_compact.csv", summary)
    write_csv(out_dir / "significance_tests.csv", significance)

    # Use sample runs from fixed seed if available; otherwise synthesize.
    if "A1" in sample_runs and "A2" in sample_runs:
        runs_a1 = sample_runs["A1"]
        runs_a2 = sample_runs["A2"]
    else:
        sim = CAVSimulation(seed=args.single_seed)
        a1_case = sim.sample_a1_case()
        a2_case = sim.sample_a2_case()
        runs_a1 = {
            m: CAVSimulation(seed=args.single_seed).run_a1(m, case=a1_case, noise_seed=100_000 + args.single_seed)
            for m in MODES
        }
        runs_a2 = {
            m: CAVSimulation(seed=args.single_seed).run_a2(m, case=a2_case, noise_seed=200_000 + args.single_seed)
            for m in MODES
        }

    plot_a1_run(runs_a1, out_dir / "a1_three_modes_timeline.png")
    plot_a2_run(runs_a2, out_dir / "a2_three_modes_timeline.png")
    plot_summary(summary, out_dir / "summary_bar_metrics.png")

    write_summary_markdown(out_dir / "results_summary.md", summary, significance, args.seeds)

    print("[done] wrote outputs to", out_dir)


if __name__ == "__main__":
    main()
