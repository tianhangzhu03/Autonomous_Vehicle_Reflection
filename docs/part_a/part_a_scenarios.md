# Part A Unsafe Scenarios Draft (Glass / Reflection)

Status: Working draft for direct integration into the final report's `Unsafe Scenarios` section (and parts of `Mitigation Strategies`)

Scope:
- A1: Glass facade reflection ghost vehicle (false obstacle confirmation -> false braking / false evasive behavior)
- A2: Transparent glass door/storefront depth hole (false traversability / free-space error -> low-speed collision or deadlock)

Notes for team merge:
- This file is written in report-ready English and intentionally mirrors the course handout requirements.
- It explicitly compares `camera-only` vs `camera+LiDAR+radar` in each scenario.
- Working citation tags (`[R#]`) match `/Users/benjaminzth/Desktop/Courses/EE495AutonomousVehicles/Autonomous_Vehicle_Reflection/docs/part_a/part_a_literature_review.md`.

## Part A Framing (Why These Two Scenarios Belong Together)

These two scenarios are representative of reflection/glass corner cases because both originate from material-dependent sensing failures at glass interfaces, yet they lead to opposite planning hazards:

- **A1 (glass facade ghost vehicle)** stresses a `false positive` path: the stack overreacts to a non-physical obstacle because reflective imagery and weak/ambiguous cross-modal evidence are fused into a track.
- **A2 (transparent glass door/storefront)** stresses a `false traversability` / `false negative` path: the stack underreacts to a real barrier because depth support is missing or unreliable where a transparent obstacle exists.

This pairing gives Part A strong narrative coherence while preserving scenario diversity. It also supports the assignment's requirement to compare `camera-only` and multi-modal AV architectures under the same thematic family.

---

## A1. Glass Facade Reflection Creates a Ghost Vehicle and Triggers False Braking / False Evasive Behavior

### A1.1 Scenario Setup (Scenario definition)

**Environment.** A dense urban corridor with large roadside glass facades or mirror-like reflective planes (road class, exact speed limit, and time-of-day are unspecified). The ego vehicle drives along a lane adjacent to or opposite reflective surfaces. The reflective geometry can project the image of a real vehicle (e.g., in the oncoming or neighboring lane) into the ego camera's field of view, creating an apparent vehicle-like target that seems to lie near the ego path.

**Actors.** Ego vehicle; one or more real vehicles in an adjacent or opposing lane; a large glass facade / reflective wall. Optional additional actors (pedestrians, parked cars) can be present but are not required for the core failure mode.

**Sensor modalities for architecture comparison.**
- `camera-only`
- `camera+LiDAR+radar` (specific sensor models/placements unspecified)

**Trigger condition.** A camera detector produces a stable vehicle-class detection in the reflective region; LiDAR returns are sparse, inconsistent, or geometrically unsupported near the reflective surface; radar may provide weak or multipath-affected evidence; fusion and tracking promote the hypothesis to a high-confidence obstacle (or sufficiently persistent track), which then influences prediction and planning.[R3][R4][R5]

### A1.2 Expected Safe Behavior (What a safety-conscious stack should do)

When obstacle evidence is cross-modally inconsistent and concentrated in a reflection-prone region, the AV should respond conservatively but explainably. A safety-oriented expected behavior is:

- prioritize **smooth deceleration** over aggressive emergency braking when collision threat is not physically confirmed,
- maintain lane unless a lane change is clearly justified and safe,
- increase time headway and reduce speed to buy sensing time,
- propagate an explicit uncertainty signal (or low confidence state) into planning and control,
- log the event as a candidate corner case for data closure rather than treating it as an ordinary high-confidence obstacle.

This expected behavior is consistent with the broader safety concern around false activations in AEB-like logic (FMVSS 127 framing) and with the reality that standardized test protocols often avoid reflective backgrounds to preserve measurement reliability (Euro NCAP protocol constraints).[R1][R2]

### A1.3 Failure Hypothesis (Perception / Prediction / Planning)

#### A1.3.1 Perception failure hypothesis

A reflected vehicle image can carry realistic texture, shape, and motion cues in RGB space, which may cause a vision detector to classify it as a real vehicle. In the same scene, LiDAR measurements near glass/mirror surfaces can be inconsistent due to specular reflection and transmission effects, leading to sparse support, depth holes, or geometrically unstable returns across frames/viewpoints.[R4]

As a result, the perception stack may produce one of the following unsafe internal states:
- a camera-only obstacle hypothesis with insufficient geometric verification,
- a fused track that is incorrectly stabilized because weak or ambiguous radar/LiDAR evidence is treated as support rather than contradiction,
- phantom occupancy artifacts (e.g., a local phantom obstacle / wall-like occupancy) that later affect planning costs.[R3]

#### A1.3.2 Prediction failure hypothesis

Once a ghost obstacle enters tracking, prediction modules may generate plausible future motion branches (e.g., stationary obstacle ahead, slowing lead vehicle, or merging vehicle hypothesis), especially if the projected object position is near the ego lane centerline. This can reduce estimated TTC and elevate collision risk scores.

This prediction behavior is an engineering inference consistent with standard AV pipeline design: prediction generally assumes tracked objects are physically real unless upstream confidence handling or object semantics explicitly marks them as uncertain.

#### A1.3.3 Planning/control failure hypothesis

If planning cost design heavily penalizes potential collision without an equally strong mechanism for handling cross-modal contradiction, the planner may choose a high-deceleration brake event or a sudden lateral evasive maneuver. That reaction can create second-order risk:
- rear-end risk from following vehicles (false-brake path),
- lateral conflict risk with neighboring lanes (false-evasion path).

This is the core Part A safety message for A1: reflection-induced sensing inconsistency becomes dangerous when uncertainty is converted into hard collision-avoidance behavior too early.

### A1.4 Camera-Only vs Camera+LiDAR+Radar Comparison

#### `camera-only`

**Relative weakness in A1.** A camera-only architecture lacks an independent geometric modality for cross-checking reflected targets, so it is more vulnerable to stable false positives when the reflection looks semantically plausible.

**Relative simplification.** It does not suffer from radar multipath support artifacts or LiDAR reflection inconsistency in the fusion stage, simply because those modalities are absent. However, that simplification does not make it safer; it mostly removes opportunities for contradiction-aware confirmation.

#### `camera+LiDAR+radar`

**Theoretical advantage.** Multi-modal sensing should help reject visual reflections through geometric and motion consistency.

**Why A1 remains difficult.** Glass facades are adversarial to that assumption because they can simultaneously degrade LiDAR geometric reliability and create reflective geometries where radar multipath becomes plausible. In such cases, the issue is not lack of sensors but lack of robust disagreement handling.[R4][R5]

**Key design implication.** A1 is a fusion stress test, not merely a vision stress test. The presence of more modalities increases safety only if the fusion/tracking stack treats missing support and contradictory support differently, and if planning consumes uncertainty rather than only binary obstacle confirmations.

### A1.5 Qualitative Risk Assessment (Severity / Probability)

**Severity: Medium to High (qualitative).**
- High-speed false braking can induce rear-end collisions.
- Urban false evasive maneuvers can create lateral conflicts or uncomfortable/high-jerk control events.

**Probability: Low to Medium (qualitative).**
- The event depends on geometry, incidence angle, material properties, and traffic alignment.
- However, modern urban environments contain many high-exposure reflective surfaces (glass facades, glass noise barriers, commercial storefronts), and test protocol exclusions around reflective environments suggest the phenomenon is not negligible in practice.[R2]

### A1.6 Mitigation Strategies (Short-term patch vs Long-term redesign)

#### Short-term mitigation (project-implementable or simulator-evaluable)

1. **Contradiction-aware fusion gating (anti-confirmation bias):**
   - Decay track confidence when LiDAR repeatedly fails to provide geometrically consistent support under otherwise usable sensing conditions.
   - Require stronger persistence / multi-frame consistency for targets emerging within reflection-prone regions.
   - Treat "camera strong + LiDAR absent/unstable + radar weak" as an explicitly uncertain state, not an ordinary positive confirmation.

2. **Reflection risk-region conditioning:**
   - Use reflection detection/segmentation (or a simpler proxy region mask in simulation) to tag high-risk observation zones and raise obstacle confirmation thresholds for targets within them.[R3]

3. **Uncertainty-aware planning response:**
   - Prefer smooth deceleration and lane keeping over immediate hard braking or abrupt lateral avoidance when obstacle certainty is low and collision geometry is unconfirmed.
   - Pass uncertainty labels into planning/control instead of collapsing early into a binary obstacle state.

#### Long-term mitigation (future work / system roadmap)

1. **Reflection-aware perception and mapping:**
   - Maintain reflective plane hypotheses over time (e.g., map or SLAM-supported), and use them as priors for discounting likely mirror projections.
   - Expand ODD coverage and regression tests to include reflective urban facades as explicit scene categories.

2. **Enhanced sensing for reflection suppression:**
   - Explore polarization-based imaging or reflection-suppression pipelines (e.g., PolarFree-style ideas) as a long-term hardware+algorithm direction for reducing reflection contamination in RGB observations.[R8]

### A1.7 What to Show in the Report / Slides (recommended assets)

**Figures (minimum):**
- `Fig_A1_setup`: top-view sketch showing ego path, real vehicle, reflective facade plane, reflected image location, and apparent ghost projection
- `Fig_A1_failure_chain`: failure-chain diagram (reflection -> sensor inconsistency -> fusion ghost track -> low TTC -> false brake/evasion)
- `Fig_A1_sensor_view`: optional CARLA screenshot or mockup with RGB, LiDAR point cloud behavior, and fusion output side-by-side

**Metrics (minimum, for later experiment fill-in):**
- false braking events per 100 passes
- peak deceleration (`m/s^2`)
- peak jerk (`m/s^3`)
- minimum TTC (`s`)
- ghost-track persistence duration (`s`)
- modal consistency score (custom; definition to be shared across team)

**Baseline vs mitigation comparison template:**
- Baseline: permissive fusion confirmation (single strong visual detection plus weak support can confirm obstacle)
- Mitigation: contradiction-aware gating + reflection risk-region thresholding + uncertainty-aware planner behavior

---

## A2. Transparent Glass Door / Storefront Causes Depth Holes and Free-Space Misclassification

### A2.1 Scenario Setup (Scenario definition)

**Environment.** A low-speed access area such as a garage exit, shopping mall entrance, office lobby transition, or storefront approach with a transparent glass door, wall, or partition (specific geometry, slope, lighting, and speed limit unspecified). The ego vehicle approaches the glass barrier at low speed.

**Actors.** Ego vehicle; transparent glass barrier (static). Optional pedestrians may be present but are not required for the core failure mode.

**Sensor modalities for architecture comparison.**
- `camera-only`
- `camera+LiDAR+radar` (specific models/placements unspecified)

**Trigger condition.** The camera sees the background through the glass (possibly with reflections overlaid), while LiDAR / depth sensing yields missing, sparse, or unreliable geometry at the glass boundary. Occupancy or traversability inference treats the region as `free-space` (or treats beyond-glass background as the reachable corridor), causing the planner to produce a path through a non-traversable region.[R6][R7]

### A2.2 Expected Safe Behavior (What a safety-conscious stack should do)

For near-field regions that are visually present but depth-unsupported or depth-inconsistent, the system should default to a conservative traversability policy:

- mark the region as `unknown` (or temporarily non-traversable) rather than `free`,
- reduce speed to crawl/creep,
- stop for confirmation if traversability remains uncertain,
- avoid committing to a trajectory that requires crossing the uncertain transparent boundary.

In low-speed entry/exit areas, this policy trades efficiency for safety in a way that is usually acceptable. The literature on transparent obstacle detection and navigation supports treating transparent barriers as a dedicated perception/navigation problem rather than assuming generic depth pipelines are sufficient.[R6][R7][R10]

### A2.3 Failure Hypothesis (Perception / Prediction / Planning)

#### A2.3.1 Perception / occupancy failure hypothesis

Transparent barriers can break depth-based occupancy assumptions in two ways:

1. **Depth hole / no return path:** the glass boundary yields missing or sparse returns, and the occupancy grid incorrectly leaves the region as free or unknown that later gets collapsed to free.
2. **Misleading return path:** reflections or transmission effects generate unstable points that do not correctly represent the true glass boundary, contaminating occupancy mapping.

If glass semantics are absent and the occupancy builder assumes missing depth implies traversable space (especially near low-texture, visually open areas), the system can infer a physically impossible corridor through the glass barrier.[R6][R7]

#### A2.3.2 Prediction failure hypothesis

Prediction is not the primary failure module in the static version of A2. However, if pedestrians are near the glass door, reflection/transmission effects can complicate localization and path interaction reasoning. For the core Part A implementation, prediction can be treated as secondary and not necessary to trigger the main failure.

#### A2.3.3 Planning/control failure hypothesis

If the planner consumes an occupancy/traversability map that labels the glass region as `free`, it may generate and execute a path through the glass barrier, leading to low-speed collision. A secondary failure mode is deadlock: if the stack partially recognizes something is wrong but cannot resolve traversability, it may oscillate or stop indefinitely near the entrance.

This makes A2 a strong complement to A1: the system does not overreact to a fake object, but under-constrains motion in the presence of a real obstacle.

### A2.4 Camera-Only vs Camera+LiDAR+Radar Comparison

#### `camera-only`

**Potential strength.** A camera-only system can, in principle, learn semantic glass boundaries from appearance cues (frames, handles, reflections, edge highlights, context).

**Primary difficulty.** Glass appearance varies widely with lighting, cleanliness, tinting, reflections, and background clutter. Without reliable depth, the system depends heavily on learned priors and training distribution coverage. Generalization can be poor, especially for unusual storefronts or minimal-frame glass doors.

#### `camera+LiDAR+radar`

**Theoretical advantage.** Multi-modal systems can use geometry and signal characteristics to confirm barriers and free-space boundaries.

**Why A2 remains difficult.** Glass can make depth modalities unreliable exactly where traversability must be decided. If the fusion stack does not explicitly model "transparent object = depth failure domain," the multi-modal system can become overconfident in free-space inference because depth holes are misinterpreted as open space.[R6][R7]

**Key design implication.** A2 is an occupancy/traversability representation stress test. Better safety comes from transparent-obstacle-aware modeling and conservative unknown handling, not from adding modalities alone.

### A2.5 Qualitative Risk Assessment (Severity / Probability)

**Severity: Medium (qualitative).**
- Typical speeds are low, but collisions with glass can cause material damage and potentially injure nearby pedestrians or occupants.
- Deadlock at entrances/exits can also create operational disruption and traffic blockage.

**Probability: Medium to High (qualitative).**
- Transparent glass doors and partitions are common in garages, malls, offices, and mixed indoor/outdoor access points.
- The infrastructure exposure is high even if severe crashes are less common than highway false-braking events.

### A2.6 Mitigation Strategies (Short-term patch vs Long-term redesign)

#### Short-term mitigation (project-implementable or simulator-evaluable)

1. **`Depth hole -> unknown` policy (not `free`):**
   - In near-field regions where RGB suggests a boundary or foreground structure but depth is missing/inconsistent, mark cells as `unknown` and trigger cautious behavior.

2. **Creep-and-confirm strategy for low-speed access zones:**
   - Add a safety shell for entrances/exits (garage, storefront, lobby) that limits speed and requires stronger traversability confirmation before crossing a transparent-looking boundary.

3. **Transparent obstacle boundary cues (TOPGN-style features):**
   - Use LiDAR intensity and spatial consistency features to estimate likely transparent obstacle boundaries and inject them as hard occupancy constraints.[R6]

4. **Glass semantics as an occupancy constraint:**
   - If a glass plane or transparent barrier is detected (even weakly), propagate that information into occupancy/traversability rather than leaving it only in a perception confidence channel.[R7]

#### Long-term mitigation (future work / system roadmap)

1. **Glass-aware mapping and scene memory:**
   - Persist transparent barrier locations in local maps where repeated operation occurs (e.g., parking structures, campus buildings, logistics depots).
   - Treat transparent surfaces as explicit environment semantics that alter sensor trust models.

2. **Imaging enhancement / polarization cues:**
   - Explore polarization and reflection-suppression imaging to improve boundary visibility and reduce reflection interference in glass-rich scenes.[R8]

3. **Data closure for transparent obstacles:**
   - Add transparent doors, storefronts, glass partitions, and glass barriers to scenario coverage taxonomy and regression suites, with explicit metrics for unknown handling and traversability safety.

### A2.7 What to Show in the Report / Slides (recommended assets)

**Figures (minimum):**
- `Fig_A2_setup`: top-view or perspective sketch showing transparent glass barrier, visible background, and ego trajectory candidate
- `Fig_A2_occupancy_compare`: heatmap or occupancy visualization comparing `baseline (free-space leak)` vs `mitigation (unknown/blocked)`
- `Fig_A2_failure_chain`: transparent glass -> depth hole/inconsistency -> occupancy error -> path through glass / deadlock

**Metrics (minimum, for later experiment fill-in):**
- collision-with-barrier rate / blocked-path failure rate
- deadlock rate (if modeled)
- stopping distance to glass barrier (`m`)
- success rate to target without collision (for scenarios with alternate valid path)
- unknown-area ratio near glass boundary
- comfort proxy (avoid unnecessary harsh braking in low-speed approach)

**Baseline vs mitigation comparison template:**
- Baseline: depth hole interpreted as free or weakly constrained traversability
- Mitigation: `depth hole -> unknown` + crawl/stop-confirm + transparent-boundary constraint injection

---

## Cross-Scenario Comparison (A1 vs A2) for Part A Reporting

This table is useful in both the report and the deck because it makes the "representative but different" argument explicit.

| Dimension | A1: Glass Facade Ghost Vehicle | A2: Transparent Glass Door / Storefront |
|---|---|---|
| Material effect | Reflection / mirror-like visual projection | Transparency + reflection overlay + depth failure |
| Core perception issue | False obstacle confirmation | False traversability / free-space leak |
| Main downstream module stressed | Fusion + tracking + prediction | Occupancy / traversability + planning |
| Typical unsafe action | False brake / false evasive maneuver | Low-speed collision with glass or deadlock |
| Failure polarity | Overreaction to non-physical object | Underreaction to real non-traversable barrier |
| Most important mitigation principle | Contradiction-aware fusion + uncertainty propagation | `Unknown`-first traversability + transparent-boundary constraints |

## Suggested Text Block for the Team Report's Part A Transition (optional)

The two glass-related scenarios in Part A were selected to span two complementary safety failure polarities under a shared physical cause (glass/reflection-induced sensing inconsistency). Scenario A1 examines how reflective facades can create vehicle-like ghost observations that are incorrectly stabilized by fusion and tracking, leading to false braking or false evasive behavior. Scenario A2 examines how transparent barriers can create depth failures that leak into occupancy/traversability inference, causing the planner to treat a non-traversable region as free space. Together, they allow a controlled comparison of `camera-only` and `camera+LiDAR+radar` architectures while emphasizing that additional sensing modalities only improve safety when disagreement and uncertainty are modeled explicitly.

## Integration Checklist (for later, after experiments are ready)

When you and your teammate merge final content, ensure each Part A scenario has:
- one scenario setup figure
- one failure-chain figure
- one baseline vs mitigation metric figure
- one explicit `camera-only` vs multi-modal comparison paragraph
- one short paragraph on limitations / assumptions (e.g., injected artifacts vs physical simulation fidelity)

