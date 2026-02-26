# Part A Unsafe Scenarios (Revised Report Draft: Reflection and Transparent Glass)

This section defines and analyzes the two glass-related corner scenarios assigned to Part A. The two scenarios are intentionally paired: they share the same material family (glass surfaces that create reflection and/or transmission effects), but they produce opposite safety failure polarities.

- **A1 (reflective facade / ghost vehicle):** overreaction to a non-physical obstacle (false obstacle confirmation -> false braking / false evasive behavior)
- **A2 (transparent glass barrier / free-space leak):** underreaction to a physical non-traversable barrier (depth failure -> traversability error -> low-speed collision or deadlock)

The pair is analytically useful because it tests two different system assumptions under a common physical cause:

1. whether the stack can avoid overconfident obstacle confirmation under cross-modal disagreement (A1), and
2. whether the stack preserves `unknown` rather than collapsing missing depth into `free` (A2).

Unless otherwise stated, road class, exact speed limit, lighting schedule, and sensor hardware model are treated as **unspecified**; this is intentional and consistent with the evidence discipline established in the literature review. Citation tags `[L#]` refer to the verified source bank in `/Users/benjaminzth/Desktop/Courses/EE495AutonomousVehicles/Autonomous_Vehicle_Reflection/docs/part_a/part_a_literature_review.md`.

---

## A1. Glass Facade Reflection Creates a Ghost Vehicle and Triggers False Braking / False Evasive Behavior

### A1.1 Scenario Definition and Operating Assumptions

**Environment.** The ego vehicle drives in a dense urban corridor with a large roadside glass facade or another mirror-like vertical reflective plane. The relevant geometry is that a real moving vehicle in a neighboring or opposing lane can appear in the ego camera view as a visually plausible vehicle-like target whose image projects near the ego path.

**Actors.**
- ego vehicle,
- one or more real vehicles in adjacent or opposing traffic,
- a reflective glass facade (static infrastructure).

Optional road users (pedestrians, parked vehicles) may be present but are not required to trigger the core failure chain.

**Architectures compared (required by the course project).**
- `camera-only`
- `camera+LiDAR+radar`

**Core trigger condition.** A camera detector outputs a stable vehicle hypothesis in a reflection-prone region; LiDAR support is absent, sparse, or geometrically inconsistent near the reflective surface; radar may provide weak or multipath-affected evidence; fusion/tracking promotes the hypothesis to a persistent obstacle state and forwards it to prediction/planning.[L9][L10][L11]

### A1.2 Expected Safe Behavior (Safety Objective)

The expected safe behavior is not "ignore anything uncertain." It is a **conservative but physically grounded response** to cross-modal contradiction in a reflection-prone region. A safety-conscious stack should:

- avoid collapsing the hypothesis into a hard obstacle too early,
- reduce speed smoothly (rather than immediately issuing maximum braking) when collision geometry is unconfirmed,
- maintain lane unless lateral maneuver safety is independently established,
- propagate uncertainty to planning/control rather than hiding it in a perception-only confidence score,
- preserve traceability (e.g., logs or event flags) for data closure and regression testing.

This expected behavior is consistent with two external frames:
- false/inappropriate activation is a recognized safety issue in AEB regulation (FMVSS No. 127), not merely a comfort issue,[L14]
- standardized crash-avoidance testing often constrains reflective/confounding surroundings to preserve repeatability, which supports the relevance of reflective corner-case analysis outside the standardized envelope.[L15]

### A1.3 Failure Analysis (Perception -> Prediction -> Planning)

#### A1.3.1 Perception and fusion failure mechanism

The first failure is not necessarily a single-module "misclassification." It is a **mismatch between appearance and geometry**.

- In RGB space, a reflection can preserve enough shape, texture, and motion cues to produce a stable vehicle detection.
- In LiDAR, glass and mirror-like surfaces can produce inconsistent returns (surface return, behind-surface return, reflected return, or sparse support), and these inconsistencies may vary across viewpoint and frame.[L10]
- In radar, multipath can create ambiguous target evidence rather than reliable contradiction, depending on geometry.[L11]

If the fusion logic is designed around permissive confirmation (for example, treating a strong camera detection plus weak auxiliary support as sufficient), the stack can produce an unsafe internal state:
- a persistent ghost track, or
- a phantom occupancy artifact that behaves like a legitimate obstacle for downstream modules.[L9]

**Evidence boundary.** The sensor-level mechanisms (reflection ambiguity, LiDAR inconsistency, radar multipath ghosts) are literature-supported.[L9]-[L11] The exact fusion promotion path is scenario-specific and should be presented as an engineering failure hypothesis unless measured in your experiment logs.

#### A1.3.2 Prediction failure mechanism (engineering inference)

Once a ghost obstacle is stabilized as a track, prediction may generate physically plausible future trajectories (e.g., stationary in-lane obstacle, slow lead vehicle, or cut-in candidate) because prediction modules typically assume the tracked object is real unless explicitly marked as uncertain. If the projected position lies near the lane centerline, estimated TTC may fall quickly and trigger a risk escalation.

This step is presented as an engineering inference consistent with standard AV pipeline structure; the project should verify it through logs (e.g., track state, predicted trajectories, TTC trend), not just narrative description.

#### A1.3.3 Planning/control failure mechanism (engineering inference)

If planning heavily penalizes potential collision but lacks a strong penalty for acting on poorly supported obstacles, the planner may choose:
- **false hard braking** (rear-end risk), or
- **false lateral avoidance** (side-conflict risk).

The safety issue is therefore not only false perception. It is the conversion of uncertain evidence into a high-authority control action without sufficient contradiction handling.

### A1.4 Camera-Only vs Camera+LiDAR+Radar (Required Architecture Comparison)

#### `camera-only`

A camera-only stack is more exposed to A1 because it lacks an independent geometric channel for rejecting a reflection that is semantically convincing. If the reflection looks vehicle-like and is temporally stable, a detector/tracker can remain confident longer than is safe.

At the same time, camera-only avoids a different failure mode: it cannot incorrectly treat weak radar multipath or unstable LiDAR returns as supporting evidence because those modalities are absent. This is not an advantage in safety by itself; it simply removes one source of false reinforcement.

#### `camera+LiDAR+radar`

A multi-modal stack is theoretically better positioned to reject reflections. In many scenes, geometry and cross-modal consistency should suppress vision-only false positives.[L5][L6]

A1 remains difficult because glass facades are precisely the kind of environment where the disambiguation channels can themselves be unreliable or ambiguous:
- LiDAR support may be missing or inconsistent near the reflective plane,[L10]
- radar evidence may be weak or multipath-affected,[L11]
- fusion logic may misread absence of clean support as uncertainty to be resolved later rather than contradiction to be handled now.

For this reason, A1 should be framed as a **fusion-confidence stress test** rather than a simple vision stress test.

### A1.5 Qualitative Risk Characterization

**Severity (qualitative): medium to high.**
- At higher speeds, false braking can create a rear-end collision hazard.
- In urban settings, sudden evasive maneuvers can create lateral conflict and high-jerk responses.

**Probability (qualitative): low to medium.**
- Occurrence depends on scene geometry, reflection angle, facade material properties, and traffic alignment.
- Exposure is non-trivial because modern urban corridors frequently contain glass facades, storefront glazing, and reflective barriers.
- Protocol constraints around reflective/confounding surroundings suggest these effects are operationally relevant even if they are not standard test fixtures.[L15]

### A1.6 Mitigation Strategy (Near-Term vs Long-Term)

#### Near-term (software-first, project-compatible)

**1) Contradiction-aware fusion gating**
- Distinguish "no support yet" from "repeated contradiction / repeated missing geometric support under valid conditions."
- Decay track confidence if LiDAR support remains inconsistent over multiple frames in a region known to be reflection-prone.
- Treat `camera strong + LiDAR inconsistent + radar weak/ambiguous` as an explicitly uncertain state, not a quasi-confirmed obstacle.

**2) Reflection-risk region conditioning**
- Use reflection detection/segmentation or a simpler proxy mask (e.g., known glass facade region in simulation) to raise confirmation thresholds inside high-risk observation zones.[L9]
- Require stronger temporal consistency or multi-view evidence before obstacle promotion in those zones.

**3) Uncertainty-aware planning response**
- Prefer lane-keeping and smooth deceleration over hard braking or abrupt lateral avoidance when collision geometry is unconfirmed.
- Propagate uncertainty labels into planning/control, rather than collapsing to a binary obstacle state upstream.

#### Long-term (system redesign / future work)

**1) Reflection-aware mapping and scene priors**
- Maintain reflective plane hypotheses over time (mapping/SLAM support) and use them to discount mirror projections or flag high-risk perception regions.[L10]
- Extend ODD coverage and regression suites to explicitly include reflective urban facades, glass noise barriers, and storefronts.

**2) Sensor and imaging upgrades**
- Explore polarization-based imaging or reflection-suppression pipelines as a longer-term route to reduce ambiguity at the image formation stage (e.g., PolarFree-style directions).[L17]

### A1.7 Evaluation Hooks for the Project Report (What to Measure and Show)

This subsection is included so the scenario text remains tied to measurable outcomes and does not read as a purely conceptual story.

**Recommended figures (minimum set).**
- `Fig_A1_setup`: top-view geometry sketch (ego lane, real vehicle, reflective plane, reflected image location, apparent ghost position)
- `Fig_A1_failure_chain`: reflection -> cross-modal ambiguity -> ghost track -> TTC drop -> false brake/evasion
- `Fig_A1_sensor_compare` (optional but strong): RGB / LiDAR / fusion visualization for one representative frame sequence

**Recommended metrics (baseline vs mitigation).**
- false braking events per 100 passes
- peak deceleration and peak jerk
- minimum TTC
- ghost-track persistence duration
- modal consistency score (define once and reuse across all four scenarios)

**Important limitation to state explicitly.**
For a course project, a detection-level or fusion-level artifact injection is acceptable and often preferable to a physically perfect reflection simulation. The key requirement is to preserve the causal logic (ambiguous cross-modal evidence -> incorrect obstacle promotion -> unsafe control tendency) and to quantify how mitigation changes the outcome.

---

## A2. Transparent Glass Door / Storefront Causes Depth Holes and Free-Space Misclassification

### A2.1 Scenario Definition and Operating Assumptions

**Environment.** The ego vehicle approaches a low-speed access area (e.g., garage exit, mall entrance, lobby transition, or storefront approach) containing a transparent glass door, wall, or partition. The main geometric feature is a visually open region that is physically non-traversable because a transparent barrier occupies the path.

**Actors.**
- ego vehicle,
- transparent glass barrier (static).

Pedestrians may be included in an extended version, but they are not required for the core failure mode analyzed here.

**Architectures compared (required by the course project).**
- `camera-only`
- `camera+LiDAR+radar`

**Core trigger condition.** The camera sees background content through the glass (possibly with superimposed reflections), while LiDAR/depth support is missing, sparse, or unstable at the barrier boundary. Occupancy/traversability estimation interprets the region as `free` (or functionally traversable), causing the planner to generate a path through the barrier.[L8][L13]

### A2.2 Expected Safe Behavior (Safety Objective)

A2 is a traversability-safety problem, so the expected behavior should be phrased in occupancy and planning terms rather than only detector confidence terms.

When near-field geometry is visually plausible but depth is missing or inconsistent, the system should:
- preserve an `unknown` state instead of immediately assigning `free`,
- reduce speed to crawl/creep in access zones,
- stop and wait for stronger evidence if traversability remains unresolved,
- avoid committing to a path that crosses a transparent-looking boundary without confirmation.

This behavior is consistent with the logic of probabilistic occupancy mapping under uncertainty (free / occupied / unknown distinction) and with modern mapping frameworks that treat unknown space as first-class rather than incidental.[L1]-[L4]

### A2.3 Failure Analysis (Perception / Occupancy -> Planning)

#### A2.3.1 Perception and occupancy failure mechanism

A2 is best described as a **representation failure induced by sensing ambiguity**.

Glass can degrade or distort depth sensing in ways that create two common occupancy errors:

1. **Depth-hole failure:** returns at the barrier boundary are missing or too sparse, leaving cells unobserved; a downstream rule or planner later treats those cells as traversable.
2. **Misplaced-return failure:** unstable points from transmission/reflection effects appear at incorrect depths, corrupting occupancy updates and blurring the true barrier boundary.[L8][L10]

If glass semantics are absent and the occupancy builder (or downstream traversability layer) effectively interprets missing depth as likely free space, the system may infer a corridor through a physically non-traversable glass barrier. This is exactly why transparent-obstacle-specific detection and glass-aware occupancy updates matter.[L8][L13]

**Evidence boundary.** The sensing and occupancy mechanisms are directly supported by glass/transparent-obstacle literature.[L7][L8][L13] The exact rule by which a given AV stack collapses `unknown` to `free` is implementation-dependent and should be treated as a project hypothesis unless observed in code or logs.

#### A2.3.2 Prediction role (secondary for the base scenario)

Prediction is not the primary failure source in the static version of A2. The unsafe action can occur even with no moving obstacles if traversability is misclassified.

Prediction becomes relevant in extended variants (e.g., pedestrians near the glass, reflected motion behind the glass, or bidirectional interaction near an entrance), but it is reasonable to keep prediction secondary in the minimum Part A implementation.

#### A2.3.3 Planning/control failure mechanism

If the planner consumes a traversability map that marks the glass region as `free`, it may commit to a trajectory that intersects the barrier and execute a low-speed collision. A second, less severe but operationally important failure mode is **deadlock**: the system oscillates between partial progress and hesitation because the scene cannot be resolved cleanly.

This makes A2 a useful complement to A1. A1 tests overreaction to a non-existent obstacle; A2 tests underreaction to a real obstacle due to representational overconfidence in free space.

### A2.4 Camera-Only vs Camera+LiDAR+Radar (Required Architecture Comparison)

#### `camera-only`

A camera-only stack may detect glass boundaries from appearance cues (door frames, handles, edge highlights, reflections, context), but its performance is highly sensitive to scene appearance and training coverage. Minimal-frame glass doors, cluttered backgrounds, heavy reflections, tinting, and lighting changes can all degrade generalization.

In other words, camera-only may succeed when semantic priors are strong, but it lacks robust geometry for confirming traversability.

#### `camera+LiDAR+radar`

A multi-modal stack should, in principle, make traversability safer by adding geometry and motion cues. In practice, A2 remains difficult because depth-relevant modalities can become unreliable exactly where traversability must be decided.

If the system does not explicitly model transparent surfaces as **depth-unreliable regions**, multi-modal fusion can become overconfident in free-space inference:
- missing LiDAR returns are interpreted as open space,
- weak radar structure is ignored or misused,
- camera evidence of background visibility is read as confirmation of traversability.

This is why A2 should be framed as an **occupancy/traversability representation stress test**, not merely a sensor-availability problem.[L8][L13]

### A2.5 Qualitative Risk Characterization

**Severity (qualitative): medium.**
- Typical operating speeds are lower than A1, but collisions with glass can damage infrastructure, injure nearby pedestrians, and create hazardous secondary interactions.
- Deadlock at entrances/exits can obstruct traffic and complicate human intervention.

**Probability (qualitative): medium to high.**
- Transparent glass doors and partitions are widespread in garages, malls, office buildings, and mixed indoor/outdoor interfaces.
- Exposure is high even if the speed regime is relatively low.

### A2.6 Mitigation Strategy (Near-Term vs Long-Term)

#### Near-term (software-first, project-compatible)

**1) `Depth hole -> unknown` (not `free`) policy**
- In near-field regions where image cues suggest a boundary/foreground but depth support is missing or inconsistent, retain `unknown` and let planning treat the area conservatively.
- This is best presented as a representation policy grounded in occupancy-mapping logic, not merely a special-case heuristic.[L1]-[L4]

**2) Access-zone crawl and stop-confirm behavior**
- Add a low-speed safety shell for entrances/exits (garage, storefront, lobby transition) that requires stronger traversability evidence before crossing a transparent-looking boundary.
- The design principle is to trade efficiency for safety where collision energy is lower and uncertainty is resolvable through short-range observation.

**3) Transparent-boundary cues (TOPGN-style direction)**
- Use LiDAR intensity and local spatial consistency features to estimate likely transparent obstacle boundaries and inject them into occupancy/traversability as hard constraints.[L13]

**4) Glass semantics as a map/planning input, not only a perception label**
- If a glass plane or transparent barrier is detected (even weakly), pass that information to occupancy/traversability and planning instead of leaving it as a low-level perception annotation.[L8]

#### Long-term (system redesign / future work)

**1) Glass-aware mapping and local scene memory**
- Persist transparent barrier locations in repeated-operation environments (parking structures, campuses, logistics depots) and use them to adjust sensor trust and traversability inference.

**2) Imaging enhancement / polarization cues**
- Explore polarization and reflection-suppression pipelines to improve boundary visibility and reduce confusion between transmitted background content and barrier appearance.[L17]

**3) Data closure for transparent-obstacle scenes**
- Add transparent doors, glass partitions, and storefront glazing to scenario taxonomies and regression suites, with metrics tied to `unknown` handling and safe stopping behavior.

### A2.7 Evaluation Hooks for the Project Report (What to Measure and Show)

**Recommended figures (minimum set).**
- `Fig_A2_setup`: geometry sketch showing transparent barrier, visible background, and candidate ego path
- `Fig_A2_occupancy_compare`: occupancy/traversability visualization comparing baseline (free-space leak) vs mitigation (unknown/blocked)
- `Fig_A2_failure_chain`: transparent barrier -> depth ambiguity -> occupancy error -> collision or deadlock

**Recommended metrics (baseline vs mitigation).**
- collision-with-barrier rate
- deadlock rate (if modeled)
- stopping distance to barrier
- success rate to target (if alternate valid path exists)
- unknown-area ratio near barrier
- low-speed comfort proxy (avoid unnecessary harsh braking)

**Important limitation to state explicitly.**
As with A1, a course project does not need photometrically or physically perfect glass simulation. It is sufficient to reproduce the safety-relevant causal chain (depth ambiguity -> traversability error -> unsafe path commitment) with a transparent and documented injection method, then compare baseline and mitigation outcomes.

---

## Cross-Scenario Synthesis (Why A1 and A2 Are Both Representative and Different)

The value of Part A is not just that it covers "two glass cases." It is that the two cases jointly expose a broader systems weakness: **confidence mismanagement under material-induced ambiguity**.

| Dimension | A1: Reflective Facade Ghost Vehicle | A2: Transparent Glass Barrier / Free-Space Leak |
|---|---|---|
| Dominant optical effect | Specular reflection | Transmission + reflection overlay |
| Immediate internal failure | False obstacle confirmation | False traversability / free-space misclassification |
| Primary downstream module stressed | Fusion / tracking / prediction | Occupancy / traversability / planning |
| Typical unsafe action | False braking / false evasive maneuver | Low-speed collision with barrier or deadlock |
| Failure polarity | Overreaction to non-physical object | Underreaction to physical obstacle |
| Highest-value mitigation principle | Contradiction-aware fusion + uncertainty propagation | `Unknown`-first traversability + transparent-boundary constraints |

This cross-scenario comparison is also useful for the final report because it helps avoid a shallow conclusion ("glass is hard"). A more defensible conclusion is that **glass-rich environments break the usual alignment between appearance and geometry**, and safety depends on whether the stack preserves and acts on that ambiguity correctly.

