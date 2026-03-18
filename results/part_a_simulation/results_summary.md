# Part A Phenomenological Simulation Results

Runs per cell: 40 seeds across three stacks (`camera_only`, `multi_sensor_permissive`, `mitigation`).

## Key Outcomes

- **A1 PBS (multi-sensor permissive -> mitigation)**: 2.002 -> 1.220 (reduction 39.1%, Mann-Whitney p=2.78e-05).
- **A2 EVR (multi-sensor permissive -> mitigation)**: 0.942 -> 0.098 (reduction 89.6%, Mann-Whitney p=1.44e-14).
- **A2 collision rate**: camera-only=1.000, multi-sensor permissive=1.000, mitigation=0.000.

## Safety-Efficiency Tradeoff

- **A2 travel time (s)**: camera-only=6.11, multi-sensor permissive=6.11, mitigation=19.89.
- **A2 stop-time ratio**: camera-only=0.000, multi-sensor permissive=0.000, mitigation=0.666.

## Interpretation

- The mitigation stack reduces unsafe commitment in both scenarios while preserving progress to goal under randomized conditions.
- Domain randomization avoids single-point conclusions and yields non-trivial variability for significance testing.
