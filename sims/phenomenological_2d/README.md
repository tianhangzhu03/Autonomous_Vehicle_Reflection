# Part A 2D Phenomenological Simulator

This module implements a lightweight CPU-only simulation for Part A:
- `A1`: ghost-vehicle false-positive obstacle commitment.
- `A2`: transparent-garage-door false free-space commitment.
- Three stacks: `camera_only`, `multi_sensor_permissive`, `mitigation`.

## Structure

- `evidential_grid.py`: D-S evidential occupancy grid (`m(O), m(F), m(Ω)`).
- `fusion_planner.py`: baseline vs contradiction-aware fusion/planning policy.
- `simulator.py`: closed-loop simulation with longitudinal controller.
- `run_experiments.py`: batch evaluation, plots, and CSV export.

## Run

From repo root:

```bash
.venv/bin/python -m pip install -r sims/phenomenological_2d/requirements.txt
.venv/bin/python -m sims.phenomenological_2d.run_experiments --seeds 40
```

Outputs are saved to `results/part_a_simulation/`.

## Main Metrics

- `PBS` (A1): Phantom Braking Severity.
- `EVR` (A2): Evidential Violation Rate.
- `barrier_collision`: binary collision outcome for A2.
- `travel_time_s`, `avg_speed`, `stop_time_ratio`: safety-efficiency tradeoff metrics.
- `significance_tests.csv`: bootstrap CI + Mann-Whitney tests.

## Notes

- Plot palette follows `docs/style/figure_table_legend_spec.md`.
- The environment is intentionally non-photorealistic; it focuses on decision logic under contradictory evidence.
