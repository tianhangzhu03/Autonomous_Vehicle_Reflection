# Part A Phenomenological Simulation Results

Runs per cell: 100 seeds across three stacks (`camera_only`, `multi_sensor_permissive`, `mitigation`).

## Key Outcomes

- **A1 PBS (multi-sensor permissive -> mitigation)**: 1.933 -> 1.188 (reduction 38.5%, Mann-Whitney p=1.08e-13).
- **A2 EVR (multi-sensor permissive -> mitigation)**: 0.942 -> 0.104 (reduction 89.0%, Mann-Whitney p=2.56e-34).
- **A2 collision rate**: camera-only=1.000, multi-sensor permissive=1.000, mitigation=0.000.

## Safety-Efficiency Tradeoff

- **A2 travel time (s)**: camera-only=6.09, multi-sensor permissive=6.09, mitigation=19.63.
- **A2 stop-time ratio**: camera-only=0.000, multi-sensor permissive=0.000, mitigation=0.664.

## Interpretation

- The mitigation stack reduces unsafe commitment in both scenarios while preserving progress to goal under randomized conditions.
- Domain randomization avoids single-point conclusions and yields non-trivial variability for significance testing.
