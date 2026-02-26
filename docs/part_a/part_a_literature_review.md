# Part A Literature Review (Revised, Verified Sources, Wider Time Span)

## Scope and Positioning

This literature review supports **Part A** of the course project, which focuses on two glass-related corner scenarios:

- **A1 (Reflective facade / ghost vehicle):** a reflected vehicle-like target is promoted into a false obstacle, causing false braking or false evasive behavior.
- **A2 (Transparent glass barrier / free-space leak):** a transparent glass door or storefront causes depth failure and traversability misclassification, leading to low-speed collision or deadlock.

The review is intentionally organized around a **causal safety chain** rather than a list of papers:

1. **Material optics** (reflection/transmission/specularity) alter sensor measurements.
2. **Perception / mapping / fusion assumptions** break under those measurements.
3. **Prediction and planning** consume overconfident outputs.
4. **Safety risk** appears as false activation or false traversability.

This structure is more useful for the course handout than a pure method survey because the assignment asks for unsafe scenarios, failure analysis, and mitigations, not only perception benchmarks.

## Evidence Strategy (and what each source is used for)

To reduce weak claims and generic overreach, this review uses an explicit evidence hierarchy.

### Evidence tiers used in this review

- **Tier 1 (regulatory / official protocol / investigation):** used for safety motivation and evaluation framing
  - NHTSA FMVSS No. 127 (AEB / PAEB final rule; false activation requirements)
  - Euro NCAP frontal collision avoidance protocol (test-track/surroundings constraints)
  - NHTSA ODI PE 22-002 (unexpected brake activation / "phantom braking" investigation)

- **Tier 2 (peer-reviewed robotics / sensing papers):** used for sensing and mapping mechanisms
  - reflection detection datasets and LiDAR reflection modeling
  - transparent obstacle detection and glass-aware occupancy mapping
  - radar multipath ghost target detection

- **Tier 3 (adjacent robotics/CV literature):** used for transferable mechanism insight, not direct AV prevalence claims
  - transparent-object depth completion / reflection removal papers (e.g., manipulation or imaging settings)

### Claim discipline used below

- If a paper demonstrates a sensing phenomenon in robotics/indoor settings, this review uses it to support a **mechanism claim**, not a direct statement about highway crash frequency.
- If a regulation or protocol discusses false activation or confounding backgrounds, this review uses it to support **safety relevance and test-design motivation**, not to claim protocol authors explicitly studied our exact glass scenarios.
- Downstream prediction/planning failure chains are presented as **engineering inferences** consistent with standard AV pipeline structure, unless an exact citation directly measures that step.

## Time Span Design (Why the review is intentionally wider than 2021-2026)

Your Part A scenarios are contemporary, but the logic behind them depends on older work in mapping and uncertainty representation. To make the argument rigorous, this review spans roughly **1985-2025**:

- **1985-2013:** foundational occupancy-grid / probabilistic mapping ideas (free / occupied / unknown semantics), which are central to A2.
- **2019-2021:** transparent-object depth failure and LiDAR glass detection (robotics/vision mechanisms relevant to A2).
- **2022-2023:** modern AV multi-modal fusion and uncertainty-aware fusion framing.
- **2024-2025:** reflection-specific LiDAR/benchmark papers, transparent obstacle navigation methods, and current safety protocols / standards.

This wider span avoids a common failure mode in course reports: citing only recent papers while leaving the representation assumptions (especially `unknown` vs `free`) ungrounded.

---

## 1. Why Glass/Reflection Is a Safety Problem (Not Just a Perception Edge Case)

A glass-related corner case becomes a **safety** problem when the stack turns ambiguous evidence into a committed motion decision. The key issue in both Part A scenarios is not simply that a sensor is wrong; it is that **material-dependent sensing irregularities produce evidence patterns that look partially plausible across modalities**.

That distinction matters for two reasons:

1. It explains why these scenarios can survive naive multi-modal fusion.
2. It aligns with the course objective of "red teaming" the AV stack at the level of system behavior, not single-module accuracy.

The strongest external support for this framing comes from safety standards and test protocols:

- **FMVSS No. 127** explicitly includes a false-activation requirement and test procedures in the AEB rule, and NHTSA states that false activations can create hard braking when not warranted and may introduce safety risk (including rear-end risk). The rule also makes clear that its false-activation tests are a baseline, not a complete coverage of real-world false-trigger conditions.[L14]
- **Euro NCAP's frontal collision avoidance protocol** imposes strict test-track and surroundings constraints, including avoiding reflective/confounding backgrounds and structures that may induce abnormal sensor measurements. That does not prove Euro NCAP studied our exact glass-facade scenario; it does show that reflective/confounding surroundings are considered serious enough to compromise repeatable evaluation.[L15]

For Part A, this gives a clean argument: reflective and transparent glass scenarios are appropriate because they are plausible, safety-relevant, and partially outside the simplified environments required for standardized testing.

---

## 2. The Material Physics Behind the Two Part A Scenarios

Part A is more convincing when A1 and A2 are presented as two outcomes of a shared physical cause: **glass changes the relationship between appearance and geometry**.

### 2.1 Reflection and transparency create different failure polarities

Glass surfaces can simultaneously create:

- **specular reflections** (mirror-like appearance of other objects), and
- **transmission / see-through effects** (background visibility through the surface).

These lead to two different safety failure polarities:

- **A1 (reflective facade ghost vehicle):** the system overreacts to a **non-physical obstacle** (false positive / false obstacle confirmation).
- **A2 (transparent glass door/storefront):** the system underreacts to a **physical non-traversable barrier** (false free-space / false traversability).

This pairing is not redundant. It is analytically useful because it tests two different design assumptions:

- A1 tests whether the stack can avoid converting ambiguous observations into a hard obstacle.
- A2 tests whether the stack preserves an `unknown` state instead of collapsing missing depth into `free`.

### 2.2 Why this is a systems problem rather than a single-sensor problem

A common simplification is to describe glass errors as "camera misdetection" or "LiDAR dropout." The literature suggests a more accurate view: glass can cause **cross-modal disagreement with partial support on multiple channels**, which is exactly the type of input most brittle fusion logic handles poorly.

That is why the review below focuses on:

- **modality-specific failure mechanisms**, then
- **fusion assumptions**, then
- **occupancy/traversability representation choices**.

---

## 3. Modality-Specific Evidence Relevant to A1 and A2

### 3.1 Camera / RGB sensing: semantically rich, geometrically weak under glass effects

Cameras remain indispensable because they provide dense semantic detail. However, for glass-rich scenes, the same density becomes a liability: reflected objects can preserve texture and contour cues, and transparent barriers can reveal background context that looks visually traversable.

This problem is well known outside AV as well. In robotics and vision, transparent objects are a standard failure case for RGB-D sensing and depth estimation. For example, **ClearGrasp** (ICRA 2020; arXiv 2019) treats transparent-object depth corruption as a primary problem and builds an explicit pipeline to estimate geometry using surface normals, masks, and occlusion boundaries.[L7] The setting is robotic manipulation, not autonomous driving, so it should not be cited as traffic evidence. It is still highly useful for Part A because it confirms the general mechanism: transparent materials break the usual assumptions of commodity depth sensing and require explicit modeling.

For A1, camera-related failure is not that the network is "bad"; it is that a reflected object may still be a visually consistent object hypothesis. For A2, camera-related failure is the opposite: visual access to the background can encourage a false traversability interpretation when geometry is missing.

### 3.2 LiDAR around glass/mirror surfaces: inconsistent returns are expected, not pathological

The LiDAR literature is central to both Part A scenarios.

#### 3.2.1 Glass can create inconsistent range behavior and occupancy artifacts

**LiDAR-Based Glass Detection for Improved Occupancy Grid Mapping and Object Detection** (Sensors, 2021) is directly relevant to A2 because it addresses how glass distorts LiDAR measurements and degrades occupancy mapping if untreated. Importantly, the paper's contribution is not only detecting glass but improving occupancy map quality by correcting glass-induced errors.[L8]

This supports a key A2 design decision: if the stack can detect even a weak glass boundary signal, that signal should be propagated into occupancy/traversability rather than left as a discarded perception-side label.

#### 3.2.2 Reflections produce multiple plausible returns and frame-to-frame inconsistency

The 2024 reflection-plane work by Li, Zhao, and Schwertfeger (Plane Optimization / Plane SLAM) explicitly states the mechanism that is almost tailor-made for Part A: LiDAR beams near glass/mirrors may report the surface itself, an object behind the glass, or a reflected object, causing inconsistent data readings for localization, mapping, and navigation.[L10]

This gives a rigorous basis for the A1 failure hypothesis (camera detects a vehicle-like target while LiDAR support is sparse/inconsistent) and also supports the A2 failure hypothesis (glass boundary geometry is unstable or missing where traversability decisions are made).

### 3.3 Reflection as a benchmarked perception problem (not just anecdotal failure)

The **3DRef** dataset and benchmark (2024) matters because it formalizes reflection detection as a multi-modal perception problem using RGB and LiDAR, rather than treating reflections as one-off qualitative artifacts.[L9]

For this project, 3DRef is useful in two ways:

- **Mechanism evidence:** reflective surfaces persistently challenge mapping and perception.
- **Mitigation motivation:** if reflection regions can be detected/segmented or otherwise marked, they can be treated as high-risk observation zones in fusion and planning.

A limitation worth stating explicitly (to avoid overclaiming) is that 3DRef is a robotics-focused benchmark and not a highway ADS benchmark. We use it to justify sensing and mapping mechanisms, not to estimate real-world crash rates.

### 3.4 Radar multipath and ghost targets: a plausible weak-positive channel in A1

Part A should be careful with radar claims. The point is not that radar will always produce a ghost in reflective urban corridors, but that **multipath ghost targets are a real and studied phenomenon**, and therefore radar evidence in reflective scenes may be ambiguous rather than reliably disambiguating.

The paper **Detection of Ghost Targets for Automotive Radar in the Presence of Multipath** (IEEE Transactions on Signal Processing, 2024; arXiv 2023) provides the right level of support here. It explicitly models ghost-target detection under multipath conditions in automotive radar and frames ghosts as a signal-processing and hypothesis-testing problem.[L11]

This is enough to justify a conservative A1 fusion narrative:
- camera strong positive + LiDAR inconsistent support + radar weak/ambiguous return
- should not be treated as equivalent to multi-modal confirmation of a real obstacle

---

## 4. Multi-Modal Fusion Literature: Why More Sensors Help in General but Can Still Fail Here

The assignment asks for a comparison between **camera-only** and **camera+LiDAR+radar** architectures. A strong literature review should therefore acknowledge both sides:

- multi-modal fusion is genuinely effective in many settings,
- but glass/reflection scenarios are precisely where the assumptions behind fusion can break.

### 4.1 What mainstream fusion literature establishes

The modern AV fusion literature (e.g., surveys and BEV-based fusion frameworks) strongly supports the basic motivation for multi-modality:

- cameras contribute dense semantics,
- LiDAR contributes geometry,
- radar contributes robustness under certain sensing conditions,
- and fusion can improve detection and mapping performance on benchmark datasets.

A 2022 survey on multi-modal sensor fusion for autonomous driving perception summarizes this design space and explicitly discusses issues such as noisy raw data, underutilized information, and cross-modal misalignment.[L5] Representative systems like **BEVFusion** (ICRA 2023; arXiv 2022) demonstrate how much performance and efficiency can be gained when camera and LiDAR are fused effectively in a shared representation.[L6]

For the report, this matters because it prevents an unbalanced narrative. We are not arguing that multi-modal sensing is "bad"; we are arguing that **glass-related scenarios stress the reliability assumptions of fusion**, especially when disagreement is material-induced and persistent.

### 4.2 The specific gap Part A exploits: disagreement handling, not just feature fusion

Most fusion papers optimize average-case detection metrics and architectural efficiency. Part A, by contrast, tests a different question:

> What happens when the modalities disagree for physically valid reasons, and the disagreement itself is safety-critical?

This is closer to **runtime reliability / uncertainty allocation** than to benchmark mAP gains.

A useful bridge reference here is **Uncertainty-Encoded Multi-Modal Fusion for Robust Object Detection in Autonomous Driving** (ECAI 2023), which argues that fusion schemes often ignore modality quality and explicitly introduces uncertainty into fusion weighting.[L12]

That paper does not solve glass-specific corner cases. But it helps justify the design direction of Part A mitigations:

- contradiction-aware gating,
- modality-quality-aware confidence updates,
- and avoiding early collapse to a binary obstacle label.

### 4.3 Why A1 and A2 are both needed in the fusion comparison

Using only A1 would make the Part A story sound like "fusion creates false positives." Using only A2 would make it sound like "depth holes are a mapping bug." The pair is stronger because it shows two opposite failure modes under the same material family:

- **A1:** fusion can become overconfident in a non-existent obstacle.
- **A2:** fusion / occupancy can become overconfident in non-existent free space.

This directly supports the report's cross-scenario message that **the core issue is confidence management under glass-induced measurement ambiguity**, not a single model weakness.

---

## 5. Occupancy, Traversability, and the `Unknown` State (Why A2 Needs Older References)

A2 cannot be written rigorously using only recent transparent-obstacle papers. The scenario depends on a much older and broader robotics principle: **maps used for navigation must represent uncertainty explicitly, including unknown space**.

### 5.1 Foundational occupancy-grid logic (1985-1990 lineage)

The classic occupancy-grid line (Moravec & Elfes, 1985; Elfes' later occupancy-grid framework) established probabilistic map updates that distinguish free, occupied, and unknown regions under uncertain sensing.[L1][L2]

This is exactly the conceptual backbone of A2. When a transparent barrier causes depth failure, the safety-preserving move is not to guess "free" too early. It is to preserve uncertainty and defer commitment.

This may sound basic, but it is one of the most important ways to avoid overstating novelty in the report: the `depth hole -> unknown` policy is not just a heuristic patch. It is consistent with the long-standing logic of probabilistic mapping under sensor uncertainty.

### 5.2 Modern volumetric mapping keeps the same principle

**OctoMap** (Autonomous Robots, 2013) remains a useful reference because it explicitly frames probabilistic occupancy estimation as a way to deal with sensor noise and supports explicit representation of free, occupied, and unknown space.[L3] The paper is not about glass specifically, but it helps justify why A2 should be evaluated in occupancy/traversability terms rather than only object-detection terms.

**UFOMap** (2020) is also relevant because it explicitly emphasizes efficient handling of unknown space in probabilistic 3D mapping and makes the "unknown is first-class" design choice central.[L4] This is directly aligned with the A2 mitigation philosophy.

### 5.3 Transparent obstacle detection work narrows the gap from theory to implementation

Once the `unknown` principle is established, recent transparent-obstacle work provides concrete signals for implementation:

- **TOPGN (2024)** shows that LiDAR intensity and layered grid representations can be used to infer transparent obstacle boundaries in real time for navigation.[L13]
- **LiDAR-Based Glass Detection for Improved Occupancy Grid Mapping and Object Detection (2021)** shows that glass-aware processing can improve occupancy maps by reducing glass-induced mapping errors.[L8]

These papers are especially valuable for Part A because they support both the **short-term patch** and the **long-term redesign** narratives:

- short term: transparent-boundary cues + `unknown` propagation + cautious motion
- long term: glass-aware mapping and sensor trust modeling as part of the stack design

---

## 6. Safety Framing from Regulation, Protocols, and Investigations (What We Can Claim Safely)

This section is where many student reports become either too weak (only papers) or too aggressive (overclaiming from regulations). The goal here is a narrower but stronger argument.

### 6.1 FMVSS No. 127 gives a direct safety language for false activation risk (A1)

NHTSA's FMVSS No. 127 final rule is highly useful for A1 because it does three things that align with the scenario:

1. It formalizes **false activation** as something worth performance-testing.
2. It states that false activations can produce hard braking when not warranted and may create safety risk.
3. It explicitly acknowledges that test scenarios are **not comprehensive**, which supports the relevance of red-team corner cases beyond the standardized set.[L14]

This is not evidence that NHTSA studied glass-facade reflections specifically. It is evidence that the **safety class of the failure** (false obstacle -> inappropriate braking) is recognized and regulated.

### 6.2 NHTSA ODI PE 22-002 anchors the "phantom braking" risk narrative in real complaints

NHTSA's ODI Preliminary Evaluation PE 22-002 documents complaints characterized by consumers as "phantom braking" and frames unexpected brake activation / rapid deceleration as a potential safety issue at highway speeds.[L16]

This investigation is not a reflection-specific source and should not be cited as proof of glass-induced ghost vehicles. Its value for Part A is narrower and still important:

- it validates that **unexpected braking behavior** is a legitimate safety concern in real deployments,
- and it gives a real-world anchor for why false-positive obstacle logic should be treated as safety-critical rather than a comfort nuisance.

### 6.3 Euro NCAP protocol constraints support the testability argument (A1 and A2 context)

Euro NCAP's frontal collision avoidance protocol includes restrictions on track/surroundings that exclude confounding infrastructure and reflective backgrounds that may induce abnormal sensor measurements.[L15]

For this project, that supports a specific, careful claim:

- standardized tests often need controlled surroundings for repeatability;
- therefore, they may deliberately exclude some of the environmental combinations that produce corner cases in real operation.

This is an excellent discussion point for the final report and Q&A because it explains why your Part A scenarios are meaningful without implying that Euro NCAP "missed" them by mistake.

---

## 7. Reflection/Transparent-Object Methods Outside AV: Useful, but With Clear Transfer Limits

To broaden the literature base without weakening rigor, Part A can draw from adjacent robotics and vision papers, provided the transfer claim is stated correctly.

### 7.1 Transparent-object geometry/depth completion (adjacent evidence for A2)

Works such as **ClearGrasp** (ICRA 2020) and related transparent-object depth completion lines show, in a controlled but convincing way, that transparent materials systematically break standard depth sensing and often require explicit geometric priors or dedicated reconstruction logic.[L7]

For Part A, these papers are useful for:
- motivating why transparent barriers remain difficult despite modern perception models,
- suggesting possible long-term directions (depth completion / geometric priors), and
- reinforcing the idea that transparent materials deserve their own failure taxonomy.

They should **not** be used to infer AV collision frequencies, because the domains (manipulation vs on-road driving) differ substantially.

### 7.2 Reflection removal and polarization imaging (long-term direction for A1/A2)

Reflection removal and polarization-based imaging are also mostly studied outside direct AV safety evaluation, but they are highly relevant to the long-term roadmap. **PolarFree (CVPR 2025)** is a good example of a modern reflection-removal direction that exploits polarization cues to better separate reflected and transmitted content.[L17]

For this project, the right use of such work is not "we will implement this." Instead, it is to demonstrate engineering maturity in the mitigation discussion:

- short term: safer confidence handling with current sensors
- long term: improved sensing modalities and imaging pipelines that reduce ambiguity at the source

---

## 8. What the Literature Implies for Part A Scenario Design (and What It Does Not)

This section makes the transition from literature to your actual deliverables and keeps the reasoning explicit.

### 8.1 A1 (Glass facade ghost vehicle): literature-supported chain

**Well-supported by literature / official sources**
- reflective surfaces can challenge RGB/LiDAR perception and mapping ([L8]-[L11])
- radar multipath ghost targets are real and modeled ([L11])
- false activation / inappropriate braking is a recognized safety concern ([L14], [L16])

**Engineering inference (reasonable, but should be stated as inference)**
- if fusion/tracking promotes a reflection-induced hypothesis into a persistent obstacle, prediction and planning may reduce TTC and trigger braking/evasion
- the risk increases when the planner consumes a binary obstacle state without propagated uncertainty

This is a strong setup for your A1 baseline-vs-mitigation experiment because the mitigation (contradiction-aware gating + uncertainty-aware planning) follows directly from the gap identified in the fusion literature.

### 8.2 A2 (Transparent glass barrier / free-space leak): literature-supported chain

**Well-supported by literature**
- transparent materials degrade depth measurements and can require dedicated detection or reconstruction methods ([L7], [L8], [L13])
- occupancy/traversability should preserve uncertainty and unknown space under unreliable sensing ([L1]-[L4])

**Engineering inference (reasonable, but should be stated as inference)**
- if an occupancy/traversability module collapses a depth hole to `free`, planning may generate a path through a non-traversable glass barrier
- in low-speed access scenes, a conservative `unknown` policy + creep/stop strategy is a safer default

A2 is therefore not just "perception misses glass." It is a representation and policy failure, which is exactly why the older occupancy-grid references materially improve the review.

### 8.3 Why these two scenarios together improve the report

Together, A1 and A2 let you make a more serious systems claim than either scenario alone:

- **same material family (glass / reflection / transmission) -> opposite risk outcomes**
- therefore, the underlying design weakness is not a single detector class but **confidence management under sensor ambiguity**

That argument is technically stronger and less superficial than saying "glass is hard."

---

## 9. Literature Gaps (Specific to This Course Project, Not General Research Gaps)

The goal here is to define a credible gap your project can actually address.

### 9.1 What existing literature already does well

- It characterizes sensor-level phenomena (glass, reflection, multipath, transparent obstacles).
- It provides task-specific methods (reflection detection, glass detection, transparent obstacle detection).
- It provides strong benchmark performance for multi-modal perception in average settings.
- It provides safety motivation and protocol framing for false activations and controlled testing.

### 9.2 What is still missing for your Part A deliverable

What is often missing in one place (and what your Part A can deliver) is a compact, end-to-end safety analysis that connects:

1. **material-induced sensing ambiguity**,
2. **fusion / occupancy design choices**,
3. **camera-only vs multi-modal behavior**, and
4. **planning-level consequences and mitigation trade-offs**.

That is an appropriate course-project contribution because it is analytic and reproducible, without claiming to solve the full scientific problem of reflection-robust autonomous driving.

---

## 10. Verified Source Bank (Real references only; checked for existence and relevance)

The links below were selected to support Part A claims and were verified for existence on **2026-02-26**. Working tags `[L#]` are used in this draft and can be converted to IEEE style in the final report.

### Foundational mapping / uncertainty representation (time-span anchor)

- **[L1]** H. Moravec and A. Elfes, "High Resolution Maps from Wide Angle Sonar," *ICRA 1985*.
  - CMU Robotics Institute page: https://www.ri.cmu.edu/publications/high-resolution-maps-from-wide-angle-sonar/
  - DOI (via DBLP metadata): https://doi.org/10.1109/ROBOT.1985.1087316
  - Use in report: historical origin of occupancy-grid free/occupied/unknown reasoning.

- **[L2]** A. Elfes, "Occupancy Grids: A Stochastic Spatial Representation for Active Robot Perception" (arXiv reprint of classic occupancy-grid framework; notes UAI 1990 provenance).
  - https://arxiv.org/abs/1304.1098
  - Use in report: probabilistic occupancy, explicit uncertainty, multi-sensor integration logic.

- **[L3]** A. Hornung et al., "OctoMap: an efficient probabilistic 3D mapping framework based on octrees," *Autonomous Robots*, 2013.
  - https://link.springer.com/article/10.1007/s10514-012-9321-0
  - Use in report: probabilistic occupancy mapping and explicit free/occupied/unknown representation in modern 3D mapping.

- **[L4]** D. Duberg and P. Jensfelt, "UFOMap: An Efficient Probabilistic 3D Mapping Framework That Embraces the Unknown," arXiv 2020.
  - https://arxiv.org/abs/2003.04749
  - Use in report: explicit unknown-space representation as a first-class mapping concept (supports A2 policy logic).

### AV fusion context and uncertainty-aware fusion

- **[L5]** K. Huang et al., "Multi-modal Sensor Fusion for Auto Driving Perception: A Survey," arXiv 2022 (updated 2024).
  - https://arxiv.org/abs/2202.02703
  - Use in report: fusion taxonomy, common limitations (noise, misalignment, information utilization).

- **[L6]** Z. Liu et al., "BEVFusion: Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation," arXiv 2022 / ICRA 2023.
  - https://arxiv.org/abs/2205.13542
  - Use in report: representative evidence that fusion works well in benchmark settings (important contrast point).

- **[L12]** Y. Lou et al., "Uncertainty-Encoded Multi-Modal Fusion for Robust Object Detection in Autonomous Driving," ECAI 2023 (arXiv 2023).
  - https://arxiv.org/abs/2307.16121
  - Use in report: uncertainty-aware fusion direction; supports contradiction-aware gating motivation.

### Reflection / glass / transparent-obstacle sensing and mapping (Part A core)

- **[L7]** S. Sajjan et al., "ClearGrasp: 3D Shape Estimation of Transparent Objects for Manipulation," arXiv 2019 / ICRA 2020.
  - https://arxiv.org/abs/1910.02550
  - Use in report: adjacent robotics evidence that transparent objects systematically break standard depth sensing assumptions.

- **[L8]** H. Tibebu et al., "LiDAR-Based Glass Detection for Improved Occupancy Grid Mapping and Object Detection," *Sensors*, 2021.
  - https://www.mdpi.com/1424-8220/21/7/2263
  - Use in report: direct support for A2 (glass-aware occupancy mapping, error correction, boundary detection cues).

- **[L9]** X. Zhao and S. Schwertfeger, "3DRef: 3D Dataset and Benchmark for Reflection Detection in RGB and Lidar Data," arXiv 2024.
  - https://arxiv.org/abs/2403.06538
  - Use in report: reflection detection as a structured RGB+LiDAR perception problem; motivation for reflection-region handling.

- **[L10]** Y. Li, X. Zhao, and S. Schwertfeger, "Detection and Utilization of Reflections in LiDAR Scans Through Plane Optimization and Plane SLAM," arXiv 2024 (also published in *Sensors* 2024).
  - arXiv: https://arxiv.org/abs/2406.10494
  - Sensors version: https://www.mdpi.com/1424-8220/24/15/4794
  - Use in report: explicit LiDAR reflection/glass measurement inconsistency mechanism and multi-frame plane-based handling.

- **[L11]** L. Zheng et al., "Detection of Ghost Targets for Automotive Radar in the Presence of Multipath," *IEEE Transactions on Signal Processing*, 2024 (arXiv preprint 2023).
  - arXiv: https://arxiv.org/abs/2309.13585
  - DOI (IEEE TSP): https://doi.org/10.1109/TSP.2024.3384750
  - Use in report: radar multipath ghost mechanism; A1 weak-positive/ambiguous radar evidence justification.

- **[L13]** K. Weerakoon et al., "TOPGN: Real-time Transparent Obstacle Detection using Lidar Point Cloud Intensity for Autonomous Robot Navigation," arXiv 2024.
  - https://arxiv.org/abs/2408.05608
  - Use in report: transparent obstacle boundary inference using LiDAR intensity/layered grids; strong A2 mitigation reference.

### Safety standards, test protocols, and real-world risk framing

- **[L14]** NHTSA, *Final Rule: Automatic Emergency Braking Systems for Light Vehicles (FMVSS No. 127)*, 2024 web version.
  - https://www.nhtsa.gov/sites/nhtsa.gov/files/2024-04/final-rule-automatic-emergency-braking-systems-light-vehicles_web-version.pdf
  - Use in report: false activation requirement, minimum-test framing, and safety relevance of inappropriate braking.

- **[L15]** Euro NCAP, *Crash Avoidance - Frontal Collisions Protocol, Version 1.1* (Oct. 2025, implementation Jan. 2026).
  - https://www.euroncap.com/media/91710/euro-ncap-protocol-crash-avoidance-frontal-collisions-v11.pdf
  - Use in report: controlled-surroundings constraints (reflective/confounding backgrounds, structures) as motivation for corner-case relevance.

- **[L16]** NHTSA ODI, *PE 22-002 preliminary evaluation document on unexpected brake activation* (Tesla Model 3/Y; commonly described as phantom braking), 2022.
  - https://static.nhtsa.gov/odi/inv/2022/INOA-PE22002-4385.PDF
  - Use in report: real-world safety context for unexpected braking risk (not glass-specific evidence).

### Long-term sensing / imaging direction (optional but useful in mitigation discussion)

- **[L17]** M. Yao et al., "PolarFree: Polarization-based Reflection-Free Imaging," *CVPR 2025*.
  - OpenAccess page: https://openaccess.thecvf.com/content/CVPR2025/html/Yao_PolarFree_Polarization-based_Reflection-Free_Imaging_CVPR_2025_paper.html
  - PDF: https://openaccess.thecvf.com/content/CVPR2025/papers/Yao_PolarFree_Polarization-based_Reflection-Free_Imaging_CVPR_2025_paper.pdf
  - Use in report: long-term hardware+algorithm direction for reflection suppression (A1/A2 future work), not current project implementation.

---
