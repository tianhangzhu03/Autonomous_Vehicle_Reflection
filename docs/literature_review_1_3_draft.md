# 1.3 Literature Review (Integrated for A1, A2, B1, and B2)

This section reviews the literature most relevant to the four selected unsafe scenarios in this project: A1 and A2 (glass/reflection driven perception inconsistency), and B1 and B2 (reversible-lane rule interpretation and transition-window arbitration instability). The goal is not to provide an exhaustive survey of autonomous driving research, but to build a coherent technical foundation for the specific failure chains analyzed later in this report. The review therefore prioritizes sources that directly support one or more links in the chain from sensing and rule interpretation to planning-level unsafe behavior.

The source set was selected across a wider time horizon (1985–2025) for one reason: the two glass scenarios depend on modern multi-modal perception research, while the reversible-lane scenarios depend on traffic-control standards and operations literature that is often older but still authoritative. Foundational occupancy-grid work by Moravec and Elfes and later probabilistic mapping frameworks such as OctoMap remain necessary to explain why `unknown` should be preserved under depth ambiguity rather than silently collapsed to `free` [1]–[3]. Broad autonomous-driving fusion surveys provide the methodological context for these design choices [4]. Recent perception papers on reflection, transparent obstacles, and radar multipath then explain how the ambiguous evidence arises in the first place [5]–[10]. Finally, standards and operational guidance documents provide the rule-layer context for reversible lanes and false-activation safety concerns [11]–[16].

From the perspective of A1 and A2, the strongest pattern in the literature is that glass does not behave like random sensor noise. Reflection and transmission effects systematically weaken the alignment between appearance and geometry. Recent datasets and modeling studies show that reflective surfaces can induce persistent inconsistencies across RGB and LiDAR observations, while transparent barriers can create missing or unstable depth support exactly where traversability decisions must be made [5]–[8]. Automotive radar literature further shows that multipath can introduce ghost hypotheses in reflective geometries, which is important because multi-modal fusion may treat weak radar evidence as confirmation when it should be treated as uncertainty [9].

This body of work is technically strong at the sensing level, but its limitation is equally clear: most papers optimize detection, segmentation, or mapping quality under controlled data distributions, and only partially characterize how errors propagate into behavior-level hazards. In practical terms, the literature explains *why* A1 can produce ghost obstacles and *why* A2 can produce free-space leakage, but it is less explicit on *when* those errors trigger braking, evasive maneuvers, or deadlock under realistic planning cost structures. For this project, that gap justifies modeling A1 and A2 as system-level failures rather than isolated perception failures.

A separate but related literature stream concerns B1 and B2, where the core problem is not optics but rule interpretation under dynamic lane control. MUTCD and FHWA references establish that lane-use control signals are safety-critical control devices whose semantics must be interpreted and attributed to the correct lane with high reliability [13], [16]. Reversible-lane operations research and meta-analysis indicate that safety outcomes are highly sensitive to implementation detail, traffic demand patterns, and transition operations rather than to geometry alone [14], [15]. This is directly relevant to B1, where a system may correctly recognize a signal symbol yet bind it to the wrong lane, and to B2, where asynchronous signal updates and mixed human behavior can create temporary contradictions that destabilize a mode/state machine.

The traffic-signal perception literature supports this interpretation. Deep-learning work and public datasets show that traffic lights are small, easily occluded, and highly sensitive to illumination and viewpoint changes [17], [18]. Methods that inject HD-map priors improve robustness by constraining detection and attribution to plausible lane geometry, which is exactly the type of prior needed in B1 [19]. More recent lane-attribution formulations explicitly treat “which control belongs to which lane” as a separate estimation task, reinforcing that semantic classification accuracy alone is not sufficient [20]. The main limitation is that most benchmarks do not adequately represent reversible-lane transition windows with asynchronous overhead signals and rule conflicts, so downstream arbitration risk remains underexplored.

For B2, the relevant planning literature points to a second gap: many planning frameworks assume that upstream rule inputs are stable, while real reversible-lane transitions often present conflicting and time-varying authority signals. Rule-hierarchy receding-horizon planning demonstrates one path to embedding rule priorities directly into online planning [21], and RSS provides a formal safety envelope for conservative behavior under uncertainty [22]. However, neither line of work fully resolves oscillation caused by unstable mode arbitration inputs. In practice, B2 is less about nominal trajectory optimization and more about designing robust transition logic with hysteresis, minimum dwell-time constraints, and explicit conflict-degradation policies.

Across the four scenarios, the literature converges on one shared message: the dominant safety risk is premature confidence under conflicting evidence. In A1 and A2, the conflict is cross-modal and physics-driven (appearance suggests one interpretation, geometry suggests another). In B1 and B2, the conflict is rule-driven and temporal (signal semantics, lane attribution, and traffic-motion evidence disagree during high-load periods). Existing work is rich at the component level but thinner at the cross-layer interface where perception uncertainty, rule uncertainty, and planning authority meet. This project therefore positions its contribution at that interface: it uses a unified failure template to connect sensing and rule interpretation errors to concrete planning/control consequences, and then evaluates whether mitigation strategies that preserve uncertainty and stabilize arbitration reduce unsafe outcomes.

A final methodological note is important for scope control. This section intentionally mixes top-tier academic sources with official standards and transportation-agency documents because the four scenarios span both algorithmic and operational domains. The academic papers provide mechanism-level evidence and methodological depth; the standards and agency documents provide normative constraints and real deployment context. Neither alone is sufficient for a credible review of A1/A2/B1/B2.

## References Used in Section 1.3

[1] H. P. Moravec and A. Elfes, "High resolution maps from wide angle sonar," in *Proc. IEEE Int. Conf. Robotics and Automation (ICRA)*, 1985, pp. 116–121, doi: 10.1109/ROBOT.1985.1087316.

[2] A. Elfes, "Occupancy Grids: A Stochastic Spatial Representation for Active Robot Perception," arXiv:1304.1098, 2013.

[3] A. Hornung, K. M. Wurm, M. Bennewitz, C. Stachniss, and W. Burgard, "OctoMap: An efficient probabilistic 3D mapping framework based on octrees," *Autonomous Robots*, vol. 34, pp. 189–206, 2013.

[4] K. Huang, C. Fu, and X. Wang, "Multi-modal Sensor Fusion for Auto Driving Perception: A Survey," arXiv:2202.02703, 2022.

[5] H. Tibebu et al., "LiDAR-Based Glass Detection for Improved Occupancy Grid Mapping and Object Detection," *Sensors*, vol. 21, no. 7, p. 2263, 2021.

[6] X. Zhao and S. Schwertfeger, "3DRef: 3D Dataset and Benchmark for Reflection Detection in RGB and Lidar Data," arXiv:2403.06538, 2024.

[7] Y. Li, X. Zhao, and S. Schwertfeger, "Detection and Utilization of Reflections in LiDAR Scans Through Plane Optimization and Plane SLAM," arXiv:2406.10494, 2024.

[8] K. Weerakoon et al., "TOPGN: Real-time Transparent Obstacle Detection using Lidar Point Cloud Intensity for Autonomous Robot Navigation," arXiv:2408.05608, 2024.

[9] L. Zheng et al., "Detection of Ghost Targets for Automotive Radar in the Presence of Multipath," *IEEE Trans. Signal Process.*, vol. 72, pp. 2364–2379, 2024, doi: 10.1109/TSP.2024.3384750.

[10] M. Yao et al., "PolarFree: Polarization-based Reflection-Free Imaging," in *Proc. IEEE/CVF Conf. Computer Vision and Pattern Recognition (CVPR)*, 2025.

[11] National Highway Traffic Safety Administration, "Federal Motor Vehicle Safety Standards; Automatic Emergency Braking Systems for Light Vehicles," FMVSS No. 127 Final Rule, 2024.

[12] Euro NCAP, "Test Protocol—Crash Avoidance—Frontal Collisions," Version 11, 2025.

[13] Federal Highway Administration, *Manual on Uniform Traffic Control Devices (MUTCD), 11th Edition*, 2023.

[14] Federal Highway Administration, *Traffic Simulation Assessment of New and Reconstructed Two-Way Left-Turn Lane Lane Reversal Configurations*, FHWA-HRT-19-025, 2019.

[15] A. Manuel, A. de Barros, and R. Tay, "Traffic safety meta-analysis of reversible lanes," *Accident Analysis & Prevention*, vol. 148, p. 105751, 2020, doi: 10.1016/j.aap.2020.105751.

[16] Federal Highway Administration, *Signalized Intersections: Informational Guide* (Chapter on Variable Lane Use and Dynamic Control), 2008.

[17] K. Behrendt and L. Novak, "A deep learning approach to traffic lights: Detection, tracking, and classification," in *Proc. IEEE Int. Conf. Robotics and Automation (ICRA)*, 2017, doi: 10.1109/ICRA.2017.7989182.

[18] M. Jensen et al., "The DriveU Traffic Light Dataset: Introduction and Comparison with Existing Datasets," in *Proc. IEEE Int. Conf. Robotics and Automation (ICRA)*, 2018, doi: 10.1109/ICRA.2018.8460737.

[19] M. Hirabayashi, A. Sujiwo, A. Monrroy, S. Kato, and M. Edahiro, "Traffic light recognition using high-definition map features," *Robotics and Autonomous Systems*, vol. 111, pp. 62–72, 2019, doi: 10.1016/j.robot.2018.10.004.

[20] M. Monninger et al., "Traffic-Light-to-Lane Assignment in Structured Urban Environments," arXiv:2309.12087, 2023.

[21] S. Veer, K. Leung, R. Cosner, Y. Chen, and M. Pavone, "Receding Horizon Planning with Rule Hierarchies for Autonomous Vehicles," arXiv:2212.03323, 2022.

[22] S. Shalev-Shwartz, S. Shammah, and A. Shashua, "On a Formal Model of Safe and Scalable Self-driving Cars," arXiv:1708.06374, 2017.
