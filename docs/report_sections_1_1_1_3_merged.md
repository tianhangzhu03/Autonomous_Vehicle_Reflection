# 1.1 Abstract

This project conducts a red-team analysis of autonomous driving corner cases where nominal modules fail under conflicting evidence. We study four scenarios: A1 (reflective-facade ghost vehicle), A2 (transparent-glass free-space misclassification), B1 (reversible-lane signal misread and lane-attribution error), and B2 (transition-window mode oscillation under unsynchronized lane-control signals). For each scenario, we analyze the failure chain from perception/rule interpretation to prediction, planning, and control, and compare camera-only against camera+LiDAR+radar architectures.

Three findings are consistent across scenarios. First, unsafe behavior is usually caused by premature commitment under contradiction, rather than by a single detector error. Second, multi-modal sensing improves average robustness but does not guarantee safety when fusion and arbitration do not explicitly represent uncertainty and authority conflicts. Third, mitigation is most effective at cross-module interfaces: contradiction-aware fusion, conservative unknown handling, robust lane attribution, and stable transition-state arbitration with hysteresis and dwell-time constraints.

This report contributes a unified failure-analysis template across all four scenarios, an architecture-level safety comparison, and an implementation-oriented mitigation framework aligned with corner-case validation.

**Team contribution statement:** Member A (Benjamin Zhu) is responsible for Part A (A1/A2), including literature synthesis and scenario-level analysis of reflection/transparent-glass failures. Member B is responsible for Part B (B1/B2), including reversible-lane signal and transition-window scenario design and analysis. Final integration, cross-scenario synthesis, and presentation preparation are completed jointly.

# 1.2 Introduction

Autonomous driving performance has improved substantially on benchmark tasks, yet deployment risk remains dominated by long-tail conditions where sensing and traffic-control evidence become inconsistent. These failures are difficult to detect with average-case metrics because they emerge from cross-module coupling: a plausible perception hypothesis can be over-trusted by fusion, temporary rule conflicts can destabilize mode arbitration, and local uncertainty can escalate into high-authority control actions.

This project targets four representative corner cases in two risk families. A1 and A2 capture physics-driven inconsistency caused by glass (reflection and transparency). B1 and B2 capture rule-driven inconsistency in reversible-lane operation (signal semantics/lane attribution and transition-window arbitration). This design is intentional: together, the scenarios cover both overreaction failures (false obstacle commitment, false emergency response) and underreaction failures (false free-space commitment, delayed conflict resolution).

A core project objective is to compare two architecture classes: camera-only and camera+LiDAR+radar. The comparison is framed as a safety-logic question, not a pure accuracy question. Camera-only pipelines are generally more exposed to semantic ambiguity under glare, occlusion, and reflection. Multi-modal stacks add geometric and motion evidence [3], but still fail when contradictory observations are fused as confirmation or when rule arbitration is unstable. Therefore, the key question is whether the full stack handles contradiction before issuing control actions.

Within this scope, the paper makes three practical contributions. First, it introduces a scenario-consistent failure-chain decomposition (perception/rule interpretation -> prediction or arbitration -> planning/control). Second, it integrates sensing literature and transportation standards into one evidence base for both physical and rule-driven corner cases. Third, it proposes mitigation at the module interfaces where escalation actually occurs.

The remainder is organized as follows. Section 1.3 reviews related work and identifies gaps directly relevant to A1/A2/B1/B2. Section 1.4 details the four scenarios and architecture-specific failure chains. Section 1.5 defines simulation/evaluation setup and unified metrics. Section 1.6 discusses mitigation strategies. Section 1.7 concludes with limitations and next steps.

# 1.3 Literature Review

## 1.3.1 Safety Framing and Evaluation Context

Regulatory and protocol documents establish that false or context-inappropriate activation is a safety issue, not only a comfort issue. FMVSS No. 127 explicitly includes false-activation considerations for AEB behavior [1]. Euro NCAP frontal crash-avoidance protocol similarly constrains test conditions to preserve signal reliability and repeatability [2]. For this project, these sources justify a corner-case perspective: standardized tests are necessary but do not exhaust real operating combinations that produce contradiction across sensing and rule layers.

## 1.3.2 Reflection/Transparency and Cross-Modal Inconsistency (A1, A2)

Recent literature consistently shows that glass decouples appearance from geometry. Reflection-focused work (e.g., 3DRef and LiDAR reflection modeling) shows that reflective surfaces can produce stable visual hypotheses while geometric support is frame-dependent or inconsistent [4], [5]. Transparent-obstacle and glass-detection studies show the complementary failure mode: missing or distorted depth near transparent boundaries can corrupt occupancy/traversability if uncertainty is collapsed too early [6], [7]. Radar multipath studies add a relevant risk for A1: weak radar evidence in reflective geometry can reinforce ghost hypotheses instead of rejecting them [8].

A limitation in this literature is scope. Most studies report perception or mapping metrics, while fewer quantify propagation into planning-level outcomes such as false braking, evasive oscillation, or deadlock. This motivates the project’s system-level treatment of A1/A2: not as isolated detector failures, but as cross-layer failures driven by unresolved contradiction.

## 1.3.3 Reversible-Lane Semantics, Attribution, and Transition Risk (B1, B2)

For B1 and B2, standards and transportation operations literature are primary evidence. MUTCD defines lane-use control semantics and authority at a level directly relevant to reversible-lane entry and operation [9]. FHWA guidance and lane-reversal assessment reports show that safety outcomes are sensitive to implementation and transition operations, not only geometry [10], [11]. Meta-analytic evidence on reversible lanes supports the same conclusion: effects depend strongly on context and control quality [12].

From the perception side, traffic-light research shows persistent vulnerability to small-object scale, occlusion, and adverse illumination [13], [14]. Map-aided recognition and explicit traffic-light-to-lane assignment improve robustness by constraining detection to lane geometry [15], [16]. The remaining gap is representation of transition windows: most datasets underrepresent asynchronous lane-control updates and mixed human behavior, which are central to B2.

## 1.3.4 Planning and Arbitration Under Rule Conflict

Planning literature indicates that B2 is mainly an arbitration-stability problem. Rule-hierarchy planning provides a principled mechanism to encode rule priorities in online optimization [17], and RSS provides conservative safety envelopes under uncertainty [18]. However, both lines typically assume more stable semantic inputs than those observed in reversible-lane switch windows. In practice, robust behavior requires explicit hysteresis, minimum dwell-time constraints, and conflict-degradation policies when rule and motion evidence disagree.

## 1.3.5 Synthesis and Gap

Across A1–B2, one pattern is consistent: the dominant risk is premature commitment under unresolved contradiction. In A1/A2, contradiction is primarily cross-modal and physics-driven. In B1/B2, contradiction is rule-driven and temporal. Existing work is strong at component level but weaker at cross-layer interfaces between sensing uncertainty, rule uncertainty, and planning authority. This report is positioned at that interface by applying a unified failure template and baseline-versus-mitigation evaluation across all four scenarios.

## References (for Sections 1.1–1.3)

[1] National Highway Traffic Safety Administration, "Federal Motor Vehicle Safety Standards; Automatic Emergency Braking Systems for Light Vehicles," FMVSS No. 127 Final Rule, 2024.

[2] Euro NCAP, "Test Protocol—Crash Avoidance—Frontal Collisions," Version 11, 2025.

[3] K. Huang, C. Fu, and X. Wang, "Multi-modal Sensor Fusion for Auto Driving Perception: A Survey," arXiv:2202.02703, 2022.

[4] X. Zhao and S. Schwertfeger, "3DRef: 3D Dataset and Benchmark for Reflection Detection in RGB and Lidar Data," arXiv:2403.06538, 2024.

[5] Y. Li, X. Zhao, and S. Schwertfeger, "Detection and Utilization of Reflections in LiDAR Scans Through Plane Optimization and Plane SLAM," arXiv:2406.10494, 2024.

[6] H. Tibebu et al., "LiDAR-Based Glass Detection for Improved Occupancy Grid Mapping and Object Detection," *Sensors*, vol. 21, no. 7, p. 2263, 2021.

[7] K. Weerakoon et al., "TOPGN: Real-time Transparent Obstacle Detection using Lidar Point Cloud Intensity for Autonomous Robot Navigation," arXiv:2408.05608, 2024.

[8] L. Zheng et al., "Detection of Ghost Targets for Automotive Radar in the Presence of Multipath," *IEEE Trans. Signal Process.*, vol. 72, pp. 2364–2379, 2024, doi: 10.1109/TSP.2024.3384750.

[9] Federal Highway Administration, *Manual on Uniform Traffic Control Devices (MUTCD), 11th Edition*, 2023.

[10] Federal Highway Administration, *Traffic Simulation Assessment of New and Reconstructed Two-Way Left-Turn Lane Lane Reversal Configurations*, FHWA-HRT-19-025, 2019.

[11] Federal Highway Administration, *Signalized Intersections: Informational Guide* (chapter on variable lane use and dynamic control), FHWA-HRT-04-091, 2008.

[12] A. Manuel, A. de Barros, and R. Tay, "Traffic safety meta-analysis of reversible lanes," *Accident Analysis & Prevention*, vol. 148, p. 105751, 2020, doi: 10.1016/j.aap.2020.105751.

[13] K. Behrendt and L. Novak, "A deep learning approach to traffic lights: Detection, tracking, and classification," in *Proc. IEEE Int. Conf. Robotics and Automation (ICRA)*, 2017, doi: 10.1109/ICRA.2017.7989182.

[14] M. Jensen et al., "The DriveU Traffic Light Dataset: Introduction and Comparison with Existing Datasets," in *Proc. IEEE Int. Conf. Robotics and Automation (ICRA)*, 2018, doi: 10.1109/ICRA.2018.8460737.

[15] M. Hirabayashi, A. Sujiwo, A. Monrroy, S. Kato, and M. Edahiro, "Traffic light recognition using high-definition map features," *Robotics and Autonomous Systems*, vol. 111, pp. 62–72, 2019, doi: 10.1016/j.robot.2018.10.004.

[16] M. Monninger et al., "Traffic-Light-to-Lane Assignment in Structured Urban Environments," arXiv:2309.12087, 2023.

[17] S. Veer, K. Leung, R. Cosner, Y. Chen, and M. Pavone, "Receding Horizon Planning with Rule Hierarchies for Autonomous Vehicles," arXiv:2212.03323, 2022.

[18] S. Shalev-Shwartz, S. Shammah, and A. Shashua, "On a Formal Model of Safe and Scalable Self-driving Cars," arXiv:1708.06374, 2017.
