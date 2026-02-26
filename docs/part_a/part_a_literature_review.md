# Part A Literature Review Draft (Glass / Reflection Corner Cases)

Status: Working draft for team report integration (English, report-ready prose)

Scope: This draft supports Part A only (the two glass-related scenarios you own):
- A1: Glass facade reflection creates a ghost vehicle and triggers false braking / false evasive behavior
- A2: Transparent glass door / storefront causes depth holes and free-space misclassification

How to use this file in the final report:
- Merge the prose into the report's `Literature Review` section.
- Convert the working source tags (e.g., `[R1]`) into your final IEEE citation style.
- Keep the statements that are directly evidence-backed, and move scenario-specific engineering assumptions to the `Unsafe Scenarios` section if you need to shorten this section.

## 1. Why Reflection/Glass Belongs in a Safety-Focused AV Literature Review

The course project asks the team to act as safety engineers and identify corner scenarios that can make an autonomous vehicle (AV) unsafe, rather than focusing on average-case benchmark performance. Reflection- and glass-related failures fit this goal well because they expose a recurring systems problem: physically plausible but cross-modally inconsistent observations can be promoted into high-confidence downstream decisions if fusion and planning logic are not designed to represent uncertainty explicitly.

This is not only an academic concern. Two external evidence streams make these scenarios appropriate for a safety-oriented course project. First, recent regulatory language in the United States explicitly treats false activations in automatic emergency braking (AEB) as a safety issue, not merely a comfort issue. The FMVSS 127 final rule includes false activation test concepts and discusses risks associated with inappropriate braking behavior.[R1] Second, Euro NCAP crash-avoidance protocols constrain test environments to avoid confounding backgrounds (including reflective surfaces and target-like visual structures), which implicitly acknowledges that environmental geometry and reflectance can induce abnormal sensing outcomes.[R2]

Taken together, these sources justify using reflection and transparent-glass scenarios as red-team corner cases: they are realistic, safety-relevant, and not fully covered by standard test setups.

## 2. Physical Failure Mechanisms Across Modalities: Reflection and Transparency Are Not Just "Noise"

A key point for Part A is that glass-related failures are often caused by physically meaningful interactions between sensing modalities and scene materials, not random sensor glitches. The literature helps frame this in a way that supports both technical analysis and mitigation design.

### 2.1 Camera-based perception: strong semantics, weak geometry under reflection/transparent surfaces

RGB cameras are strong at semantic cues (vehicle texture, contours, lane markings, signs), but they can also be strongly misled by reflective and transparent surfaces. In reflective urban facades, mirror-like reflections can preserve enough visual structure for a detector to output a stable vehicle classification even when no physical obstacle exists in the ego lane. In transparent-door scenarios, the camera may clearly see background content through glass, which can make a blocked region appear visually traversable if the system relies heavily on semantic priors without reliable geometric confirmation.

This is one reason A1 and A2 are complementary. A1 emphasizes camera false positives induced by reflections (a "phantom obstacle" path), while A2 emphasizes camera visibility through transparent barriers combined with missing or unreliable depth (a "false traversability" path).

### 2.2 LiDAR around glass and mirror-like surfaces: inconsistent returns, holes, and apparent contradictions

Recent work on LiDAR reflections and plane-based reasoning shows that reflective and glass surfaces can generate inconsistent measurements across viewpoints and frames, including cases that appear as returns on the glass plane, behind the glass plane, or from reflected content.[R4] This directly supports the failure modeling in your two scenarios:

- In A1 (glass facade ghost vehicle), LiDAR may provide sparse, unstable, or contradictory support for a camera-detected object near a reflective facade.
- In A2 (transparent glass door), LiDAR may produce depth holes or otherwise unreliable geometric evidence at the exact location of a physically non-traversable barrier.

The 3DRef benchmark is also useful here because it treats reflection detection as a structured perception problem in RGB and LiDAR data, and explicitly motivates reflection-induced phantom occupancy / planning failures as a real systems issue rather than a purely visual artifact.[R3]

### 2.3 Radar multipath and ghost support in reflective environments

Automotive radar can be robust in conditions where vision degrades, but it introduces its own corner cases, especially under multipath propagation in reflective geometries. Recent work on ghost target detection for automotive radar in the presence of multipath provides a concrete basis for discussing how spurious radar tracks may appear and persist long enough to affect downstream tracking and fusion.[R5]

For Part A, radar should be handled carefully in the narrative: the point is not to claim radar will always generate a ghost in A1, but to show that reflective urban scenes can produce weak or ambiguous radar evidence that may incorrectly reinforce a camera hypothesis if fusion logic lacks contradiction-aware gating. This framing is both technically defensible and consistent with the course requirement to compare `camera-only` against `camera+LiDAR+radar`.

## 3. Why Multi-Modal Fusion Does Not Automatically Fix Glass Problems

A common intuition is that multi-modal sensing should always reduce false detections. The literature and system behavior in reflective/transparent scenes suggest a more nuanced conclusion: multi-modal sensing improves robustness only when the fusion stack can interpret disagreement correctly.

In reflective glass scenarios, disagreement is not necessarily random missing data. It is often material-dependent and geometry-dependent. Camera may produce a strong semantic positive; LiDAR may provide sparse or inconsistent geometry; radar may provide weak or multipath-corrupted evidence. If fusion logic is designed with a "one strong positive plus weak support is enough" policy, the system can accidentally convert a hard sample into a highly stable false track. This is precisely the failure mode your A1 scenario is meant to stress-test.

In transparent obstacle scenarios, the risk shifts from false obstacle confirmation to false free-space confirmation. If depth holes are implicitly treated as traversable space, multi-modal fusion can fail in a different way: the system may become overconfident in free-space inference even though the scene contains a real barrier. This makes A2 especially useful for illustrating that safety failures can emerge from how occupancy and traversability are represented, not only from object detection errors.

This section can be framed as a literature-backed systems insight:
- Literature supports the physical sensing irregularities around glass/reflection.[R3][R4][R5][R6][R7]
- The downstream prediction/planning consequences are an engineering inference that follows from standard AV pipelines and safety cost structures (e.g., collision avoidance costs dominating under uncertain object confirmation).

## 4. Transparent Obstacle Detection and Traversability: From Depth Failure to Safety Policy

Transparent obstacles have been studied as a distinct perception and navigation problem in robotics because they break assumptions used in standard depth-based occupancy estimation. This literature is especially relevant to A2.

The TOPGN line of work (real-time transparent obstacle detection using LiDAR point cloud intensity) is important because it shows a practical route to recover transparent obstacle boundaries using signal properties beyond naive point presence/absence.[R6] In other words, transparent obstacles often require specialized features and modeling; they are not reliably solved by simply adding more sensors.

LiDAR-based glass detection studies similarly motivate the need to identify and filter incorrect glass-related measurements before feeding them into occupancy maps, which directly supports your planned mitigation strategy of treating glass/transparent regions as explicit map or occupancy constraints rather than assuming they are ordinary free space.[R7]

A useful literature-to-design bridge for the report is:
- Perception literature explains why glass causes unreliable depth and misleading geometry.
- Navigation/safety logic should therefore default to `unknown` (or conservative non-traversable) when near-field geometry is visually present but depth evidence is missing or inconsistent.
- This conservative policy is especially appropriate in low-speed access areas (garage exits, storefront approaches, building entrances), where the cost of a brief pause is lower than the cost of colliding with glass.

## 5. Reflection-Aware Perception and Long-Term Mitigation Directions

Your Part A mitigation design benefits from splitting short-term and long-term strategies, and the literature supports this split.

### 5.1 Short-term, software-first mitigation directions (report-ready and simulator-friendly)

Short-term mitigations that are realistic for a course project (and suitable for simulation/injection experiments) include:

- Reflection/Glass risk region detection: Use reflection detection or segmentation cues to mark high-risk observation regions and raise confirmation thresholds for objects observed inside them (A1).[R3]
- Contradiction-aware fusion gating: Decay object confidence when geometric support is repeatedly absent under otherwise usable LiDAR conditions, or when multi-frame consistency tests fail (A1).[R4]
- `unknown` propagation and conservative traversability: Treat visually plausible but depth-missing regions near transparent obstacles as `unknown` rather than `free`, and trigger creep/stop-confirm behavior (A2).[R6][R7]

These are strong choices for the project because they are explainable, measurable, and can be evaluated through baseline-vs-mitigation comparisons without requiring physically perfect sensor simulation.

### 5.2 Longer-term, hardware+algorithm directions

The literature also points to longer-term options that can be referenced to show engineering maturity, even if you do not implement them in this project:

- Polarization-based reflection suppression / reflection-free imaging (e.g., PolarFree) offers a path toward richer reflection cues beyond standard RGB intensity.[R8]
- Reflection/transparent-surface-aware mapping and data closure can incorporate glass facades, glass barriers, and reflective structures as explicit ODD dimensions for regression testing and failure analysis.[R3][R7]

In the report, these should be presented as future-facing directions, not as requirements for your current implementation.

## 6. Regulatory and Evaluation Framing: Why These Corner Cases Matter Even If They Are Hard to Standardize

A strong literature review for this project should not stop at sensor physics. It should explain why the chosen corner cases remain safety-relevant even when standard test suites do not directly reproduce them.

FMVSS 127's attention to false activation makes A1 (ghost obstacle -> inappropriate braking/avoidance) directly relevant to real safety risk framing.[R1] Euro NCAP's protocol constraints on reflective backgrounds and confounding structures support the argument that reflective environments are known sources of measurement ambiguity and therefore plausible corner-case generators.[R2]

This framing is valuable in your eventual presentation and report discussion sections because it lets you make a careful claim:
- You are not claiming that standard test protocols are wrong.
- You are showing that your Part A scenarios investigate realistic combinations of sensing and material effects that standard protocols may intentionally avoid to preserve repeatability.

That is exactly the kind of red-team perspective the assignment is asking for.

## 7. Research Gap and Positioning of This Project's Part A

Based on the above literature, the gap your Part A can claim is not "nobody has studied glass/reflection." Instead, the gap is the integration gap between sensing irregularities and AV safety behavior.

Most cited sources do one of the following well:
- characterize sensing phenomena (reflection, multipath, transparent obstacles),
- provide detection/benchmark methods, or
- define regulatory/safety concerns (false activation, test constraints).

What is often missing in a compact, course-project-friendly form is a clear, comparative safety analysis that connects:
1. material-driven sensing irregularities,
2. fusion/tracking/occupancy design choices,
3. `camera-only` vs `camera+LiDAR+radar` behavior differences, and
4. concrete planning-level consequences (false braking, false evasive action, or traversability mistakes).

Your two Part A scenarios are well-positioned to fill that gap in a coherent way because they represent two opposite failure polarities under the same material family:
- A1 (glass facade reflection): overreaction to a non-existent obstacle (`false positive` path)
- A2 (transparent glass barrier): underreaction to a real non-traversable obstacle (`false free-space / false negative` path)

This pairing gives the literature review a clean narrative arc and gives the `Unsafe Scenarios` and `Mitigation Strategies` sections a strong technical spine.

## 8. Working Source Bank for Part A (convert to final IEEE citations later)

These are the core sources referenced by the draft. They are intentionally limited to the sources most useful for Part A.

- `[R1]` NHTSA, *Final Rule: Automatic Emergency Braking Systems for Light Vehicles (FMVSS 127)* (web version, 2024).
  - https://www.nhtsa.gov/sites/nhtsa.gov/files/2024-04/final-rule-automatic-emergency-braking-systems-light-vehicles_web-version.pdf
  - Use in report: safety motivation for false activation / inappropriate braking concerns.

- `[R2]` Euro NCAP, *Protocol - Crash Avoidance - Frontal Collisions* (v11, protocol PDF).
  - https://www.euroncap.com/media/91710/euro-ncap-protocol-crash-avoidance-frontal-collisions-v11.pdf
  - Use in report: test-environment constraints (reflective backgrounds / confounders), motivation for corner-case relevance.

- `[R3]` *3DRef: 3D Dataset and Benchmark for Reflection Detection in RGB and Lidar Data* (arXiv, 2024).
  - https://arxiv.org/abs/2403.06538
  - Use in report: reflection detection benchmark; motivation linking reflections to phantom occupancy / planning failure.

- `[R4]` *Detection and Utilization of Reflections in LiDAR Scans Through Plane Optimization and Plane SLAM* (arXiv, 2024; also PMC mirror exists).
  - https://arxiv.org/abs/2406.10494
  - Use in report: LiDAR reflection inconsistency mechanisms near glass/mirror surfaces.

- `[R5]` *Detection of Ghost Targets for Automotive Radar in the Presence of Multipath* (IEEE TSP / arXiv preprint).
  - https://arxiv.org/abs/2309.13585
  - Use in report: radar multipath ghost-target mechanism, especially as weak/ambiguous evidence in A1.

- `[R6]` *TOPGN: Real-time Transparent Obstacle Detection using Lidar Point Cloud Intensity for Autonomous Robot Navigation* (arXiv, 2024).
  - https://arxiv.org/abs/2408.05608
  - Use in report: transparent obstacle boundary detection via LiDAR intensity / layered-grid style reasoning, A2 mitigation motivation.

- `[R7]` *LiDAR-Based Glass Detection for Improved Occupancy ...* (Sensors, 2021; title truncated in source list but sufficient to retrieve).
  - https://www.mdpi.com/1424-8220/21/7/2263
  - Use in report: glass detection and occupancy-map improvement motivation for A2 and mapping-level mitigation.

- `[R8]` *PolarFree: Polarization-based Reflection-Free Imaging* (CVPR 2025).
  - https://openaccess.thecvf.com/content/CVPR2025/papers/Yao_PolarFree_Polarization-based_Reflection-Free_Imaging_CVPR_2025_paper.pdf
  - Use in report: long-term hardware+algorithm direction for reflection suppression.

- `[R9]` NHTSA ODI, *phantom braking* investigation material (PE22002 document).
  - https://static.nhtsa.gov/odi/inv/2022/INOA-PE22002-4385.PDF
  - Use in report: background context for false-braking risk narrative (optional for Part A, but useful if you want stronger real-world motivation).

- `[R10]` *Real-Time Glass Detection and Reprojection using Sensor Fusion Onboard Aerial Robots* (arXiv, 2025).
  - https://arxiv.org/abs/2510.06518
  - Use in report: additional transparent/glass detection reference for A2-related discussion (optional, but useful for breadth).

## 9. Suggested Merge Placement in the Final Team Report

When you merge this into the team report, a practical split is:
- Keep Sections 1, 2, and 6 here (global literature framing for the whole report).
- Keep Sections 3, 4, and 5 as the Part A-specific literature subsection.
- Move the final paragraph of Section 7 into the `Introduction` or `Unsafe Scenarios` transition if you need to shorten the literature review.

