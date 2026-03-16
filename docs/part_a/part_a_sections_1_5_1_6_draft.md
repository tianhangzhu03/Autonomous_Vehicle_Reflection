# Part A Draft for Section 1.5 and Section 1.6

## 1.5 Simulation and Evaluation Setup (Part A)

### 1.5.1 Platform and Setup Assumptions

Part A uses **CARLA** as the primary simulation platform because it supports camera, LiDAR, and radar pipelines within one reproducible environment and can be instrumented for internal planner/fusion logging. The objective of this section is not photometric perfection; it is to evaluate whether the stack preserves uncertainty under contradictory evidence.

To make A1/A2 physically meaningful, scenario assets are configured with explicit material overrides:

- **A1 reflective facade:** high specular reflectance to amplify mirror-like visual projections and cross-modal inconsistency.
- **A2 garage door:** high transmittance with scattering behavior to emulate transparent-boundary depth degradation and localized depth voids.

Without these material assumptions, false-positive and false-free-space effects become visually plausible but physically ungrounded.

### 1.5.2 Scenario Instantiation in CARLA

**A1 (Ghost Vehicle).** Urban corridor with a reflective side facade. A non-ego-lane vehicle produces a mirror projection into ego camera FOV. Trigger window logs camera confidence, LiDAR support stability, radar return strength, track promotion, and braking commands.

**A2 (Transparent Garage Door).** Underground parking garage exit with a closed transparent glass door. The ego vehicle approaches from a dim ramp toward a brighter outside street scene. Camera semantics suggest traversability continuity, while LiDAR support at the door boundary is missing or unstable.

### 1.5.3 Unified Metrics and Formal Definitions

#### A1 metric: Phantom Braking Severity (PBS)

Let $a_{\\text{long}}(t)$ be ego longitudinal acceleration, and let $\\mathbb{I}(\\cdot)$ be the indicator function. Let $TTC_{\\text{virtual}}(t)$ be the planner-side TTC computed against the promoted ghost hypothesis. Phantom Braking Severity is defined as

$$
PBS = \\max_{t \\in [t_0, t_{\\text{end}}]}
\\left(
\\left|a_{\\text{long}}(t)\\right|
\\cdot
\\mathbb{I}\\left(
TTC_{\\text{virtual}}(t) < \\tau_{\\text{safe}}
\\land
\\text{No Physical Target}
\\right)
\\right).
$$

`PBS` captures the peak safety-critical intervention caused by a phantom obstacle rather than a real collision threat.

#### A2 metric: Evidential Violation Rate (EVR)

Let $\\mathcal{G}_{\\text{door}}$ denote ground-truth occupied cells of the garage door region. At the trajectory crossing instant $t_{\\text{cross}}$, define

$$
EVR =
\\frac{1}{\\left|\\mathcal{G}_{\\text{door}}\\right|}
\\sum_{c \\in \\mathcal{G}_{\\text{door}}}
m_c^{t_{\\text{cross}}}(F).
$$

`EVR` quantifies how aggressively evidential uncertainty is collapsed into free-space in a physically non-traversable region. Values near 1 indicate severe unknown-to-free violation.

#### Complementary safety metrics

To keep comparability with the full report, Part A also logs:

- `FBR`: false brake rate per 100 runs (A1),
- `GTP`: ghost-track persistence duration (A1),
- `BCR`: barrier collision rate (A2),
- `Peak Jerk`: $\\max_t |da/dt|$ (A1/A2).

### 1.5.4 Baseline vs Mitigation Experimental Matrix

Three stacks are evaluated under identical route geometry, traffic seeds, and controller settings:

| Stack | Definition | Expected failure mode |
|---|---|---|
| Baseline 1 (`camera-only`) | Pure visual semantics; no independent depth validation | A1 semantic over-commitment, A2 traversability over-commitment |
| Baseline 2 (`multi-sensor permissive`) | Multi-sensor stack with permissive fusion/occupancy defaults | A1 weak auxiliary traces treated as corroboration; A2 missing depth folded into free-space |
| Mitigation (`contradiction-aware`) | Contradiction-aware fusion + conservative unknown handling | Delayed commitment under conflict; reduced phantom braking and barrier penetration |

Each stack is run on both scenarios with multiple seeds (minimum 12 per cell recommended) to support stable comparative trends.

### 1.5.5 Reproducibility and Reporting Outputs

Each run records synchronized logs from perception/fusion/occupancy/planning/control modules. Section 1.5 reports at least one table and one timeline figure per scenario:

- **A1:** `PBS`, `FBR`, `GTP`, `Peak Jerk` plus TTC/acceleration timeline.
- **A2:** `EVR`, `BCR`, stop margin, `Peak Jerk` plus occupancy-state evolution near the door ROI.

This setup ensures that the evaluation measures not only collision outcomes, but the mechanism of unsafe commitment under evidential contradiction.

## 1.6 Mitigation Strategies (Part A)

### 1.6.1 Design principle

Part A mitigation is centered on one principle: **contradiction is first-class safety evidence**. The stack should not treat conflict as noise to be averaged away; it should treat conflict as a reason to delay high-authority motion commitment.

### 1.6.2 A1 mitigation: contradiction-aware fusion under reflective ambiguity

A1 mitigation is implemented at the fusion-planning interface. Candidate obstacles near reflective regions are maintained in an "uncertain obstacle" state unless geometric and temporal consistency is sustained.

A practical confidence update is:

`C_{t+1} = lambda*C_t + w_cam*s_cam + w_lid*s_lid + w_rad*s_rad - gamma*I_contradiction`

where `I_contradiction` is asserted when camera evidence remains strong but LiDAR/radar support is repeatedly inconsistent. Track promotion requires both confidence threshold and contradiction-free dwell time.

This mechanism directly addresses the A1 failure chain: a reflected target may still be detected, but it is prevented from becoming a high-authority planning obstacle without consistent cross-modal support.

### 1.6.3 A2 mitigation: conservative unknown handling for transparent barriers

A2 mitigation is implemented at occupancy/traversability update and planning guard layers.

The key rule is:

- if near-field boundary cues exist and depth support is missing/inconsistent, update cells to `unknown` (not `free`);
- planning cannot commit trajectories through unresolved `unknown` regions in the barrier ROI;
- system enters crawl/stop-confirm behavior until evidence resolves.

This converts A2 from collision-prone free-space overcommitment to conservative uncertainty management, which is exactly the intended safety behavior for low-speed transparent-boundary scenes.

### 1.6.4 Why these mitigations are defensible in this project

The proposed policies are specific, testable, and architecture-comparable. They do not require new hardware or large model retraining, which is critical under project constraints. More importantly, they target the exact escalation points identified in Part A:

- A1 escalation point: uncertain perception -> overconfident obstacle promotion.
- A2 escalation point: unresolved depth -> unjustified free-space commitment.

Therefore, the mitigation section can claim measurable safety impact while staying within a credible implementation scope for the course timeline.

### 1.6.5 Expected outcome pattern (baseline vs mitigation)

- In A1, mitigation should significantly reduce `FBR` and `GTP`, with lower peak jerk and no increase in true-collision risk.
- In A2, mitigation should reduce `BCR` and `EVR`; deadlock may rise slightly if stop-confirm is conservative, but unsafe barrier penetration should drop sharply.

This tradeoff should be discussed explicitly: in safety-critical ambiguity, limited efficiency loss is acceptable when it prevents high-risk actions.
