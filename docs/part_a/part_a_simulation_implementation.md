# Part A 2D Phenomenological Simulation: Implementation Note

## 1. What Was Implemented

A lightweight CPU-only simulator was implemented under `sims/phenomenological_2d/` with three stack settings:
- `camera_only`
- `multimodal_permissive`
- `mitigation`

Core modules:

- `sims/phenomenological_2d/evidential_grid.py`
  - Dempster-Shafer evidential grid: `m(O), m(F), m(Ω)`.
  - A2 depth-void phenomenological injection.
- `sims/phenomenological_2d/fusion_planner.py`
  - Baseline vs mitigation policy for A1/A2.
  - A1 contradiction-aware confidence penalty.
  - A2 unknown-preserving update and creep/stop guard.
- `sims/phenomenological_2d/simulator.py`
  - Closed-loop longitudinal control and metric extraction.

Batch runner and plotting:
- `sims/phenomenological_2d/run_experiments.py`

## 2. Reproducibility

From repo root:

```bash
.venv/bin/python -m sims.phenomenological_2d.run_experiments --seeds 40 --single-seed 7
```

Outputs:
- `results/part_a_simulation/per_run_metrics.csv`
- `results/part_a_simulation/summary_metrics.csv`
- `results/part_a_simulation/significance_tests.csv`
- `results/part_a_simulation/results_summary.md`
- `results/part_a_simulation/a1_three_modes_timeline.png`
- `results/part_a_simulation/a2_three_modes_timeline.png`
- `results/part_a_simulation/summary_bar_metrics.png`

## 3. Current Quantitative Results (40 seeds)

- A1 PBS (multi-modal permissive vs mitigation): `2.002` -> `1.220` (reduction `39.1%`).
- A2 EVR (multi-modal permissive vs mitigation): `0.942` -> `0.098` (reduction `89.6%`).
- A2 collision rate: camera-only `1.000`, multi-modal permissive `1.000`, mitigation `0.000`.
- A2 travel time (s): camera-only `6.11`, multi-modal permissive `6.11`, mitigation `19.89`.

## 4. Interpretation for Section 4/5

- Baseline reproduces expected failure mechanisms:
  - A1: phantom obstacle over-commitment leads to strong braking interventions.
  - A2: unknown-to-free collapse drives barrier penetration.
- Mitigation enforces contradiction-aware arbitration and conservative unknown handling, reducing both PBS and EVR, with explicit safety-efficiency tradeoff visible in travel time and stop ratio.
