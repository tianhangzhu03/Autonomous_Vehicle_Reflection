# 1.3 Literature Review (Condensed, for 7–8 Page Double-Column Report)

This project studies four corner scenarios under a single safety question: how does an autonomous driving stack fail when high-level decision confidence is built on conflicting evidence? Scenarios A1 and A2 focus on glass-induced sensing ambiguity (reflection and transparency), while B1 and B2 focus on reversible-lane rule interpretation and transition-window arbitration instability. The literature is therefore selected across both robotics perception and transportation operations domains, rather than from perception-only benchmarks.

For A1/A2, the central finding in recent work is that glass is not a random noise source; it systematically decouples visual appearance from geometric consistency. Reflection-oriented datasets and modeling papers show that reflective surfaces can produce stable vision hypotheses with inconsistent LiDAR support across frames and viewpoints [5], [6]. Transparent-obstacle studies and glass-aware occupancy mapping similarly show that missing or distorted depth at transparent boundaries can corrupt traversability estimation if uncertainty is not explicitly represented [4], [7]. Radar multipath research adds a complementary warning for A1: weak or ambiguous radar returns may reinforce, rather than reject, ghost hypotheses in reflective geometry [8].

These studies are methodologically strong at the sensing level, but they leave an important system-level gap. Most optimize detection, segmentation, or mapping metrics; fewer quantify how these errors propagate into planning decisions such as false braking, false evasive behavior, or deadlock. For this report, that gap motivates treating A1/A2 as cross-layer failures (perception/fusion/occupancy to planning/control), not isolated detector failures.

For B1/B2, the key evidence comes from standards and reversible-lane operations literature. MUTCD and FHWA guidance establish lane-use control signals as primary authority in dynamic lane operation and emphasize clear signal semantics and lane-level interpretability [11], [14]. Reversible-lane safety studies further indicate that outcomes are sensitive to implementation details and transition management, not just infrastructure geometry [12], [13]. This supports the B1 hypothesis that signal recognition accuracy alone is insufficient when lane attribution is unstable, and the B2 hypothesis that asynchronous updates and mixed human behavior can destabilize mode arbitration.

Traffic-light perception literature supports this interpretation from the vision side. Public datasets and detection studies show that traffic lights are small, occlusion-prone, and highly sensitive to illumination and viewpoint changes [15], [16]. Map-aided recognition and traffic-light-to-lane assignment research improves robustness by injecting lane-geometry priors and explicit attribution reasoning [9], [10]. The limitation, however, is that these datasets only partially represent reversible-lane transition windows where rule conflicts are temporally structured rather than static.

The planning and safety literature suggests that B2 is primarily an arbitration-stability problem. Rule-hierarchy planning demonstrates how rule priority can be embedded into online optimization [2], while formal safety models such as RSS provide conservative envelopes under uncertainty [1]. Yet these frameworks generally assume comparatively stable semantic inputs; they do not fully resolve oscillation caused by rapidly changing or contradictory lane-control evidence. This implies that hysteresis, minimum dwell time, and explicit conflict-degradation logic are necessary design elements in B2-like transitions.

Across all four scenarios, a common pattern emerges: the dominant risk is premature commitment under unresolved contradiction. In A1/A2, contradiction is cross-modal and physics-driven; in B1/B2, contradiction is rule-driven and temporal. Existing research is rich at component level but thinner at interfaces between sensing uncertainty, rule uncertainty, and planning authority. This report is positioned at that interface by using a unified failure template and baseline-versus-mitigation analysis to test whether uncertainty-aware fusion, robust lane attribution, and stable mode arbitration reduce unsafe actions.

## References Used in Section 1.3 (Core Set)

[1] S. Shalev-Shwartz, S. Shammah, and A. Shashua, "On a Formal Model of Safe and Scalable Self-driving Cars," arXiv:1708.06374, 2017.

[2] S. Veer, K. Leung, R. Cosner, Y. Chen, and M. Pavone, "Receding Horizon Planning with Rule Hierarchies for Autonomous Vehicles," arXiv:2212.03323, 2022.

[3] K. Huang, C. Fu, and X. Wang, "Multi-modal Sensor Fusion for Auto Driving Perception: A Survey," arXiv:2202.02703, 2022.

[4] H. Tibebu et al., "LiDAR-Based Glass Detection for Improved Occupancy Grid Mapping and Object Detection," *Sensors*, vol. 21, no. 7, p. 2263, 2021.

[5] X. Zhao and S. Schwertfeger, "3DRef: 3D Dataset and Benchmark for Reflection Detection in RGB and Lidar Data," arXiv:2403.06538, 2024.

[6] Y. Li, X. Zhao, and S. Schwertfeger, "Detection and Utilization of Reflections in LiDAR Scans Through Plane Optimization and Plane SLAM," arXiv:2406.10494, 2024.

[7] K. Weerakoon et al., "TOPGN: Real-time Transparent Obstacle Detection using Lidar Point Cloud Intensity for Autonomous Robot Navigation," arXiv:2408.05608, 2024.

[8] L. Zheng et al., "Detection of Ghost Targets for Automotive Radar in the Presence of Multipath," *IEEE Trans. Signal Process.*, vol. 72, pp. 2364–2379, 2024, doi: 10.1109/TSP.2024.3384750.

[9] M. Hirabayashi, A. Sujiwo, A. Monrroy, S. Kato, and M. Edahiro, "Traffic light recognition using high-definition map features," *Robotics and Autonomous Systems*, vol. 111, pp. 62–72, 2019, doi: 10.1016/j.robot.2018.10.004.

[10] M. Monninger et al., "Traffic-Light-to-Lane Assignment in Structured Urban Environments," arXiv:2309.12087, 2023.

[11] Federal Highway Administration, *Manual on Uniform Traffic Control Devices (MUTCD), 11th Edition*, 2023.

[12] A. Manuel, A. de Barros, and R. Tay, "Traffic safety meta-analysis of reversible lanes," *Accident Analysis & Prevention*, vol. 148, p. 105751, 2020, doi: 10.1016/j.aap.2020.105751.

[13] Federal Highway Administration, *Traffic Simulation Assessment of New and Reconstructed Two-Way Left-Turn Lane Lane Reversal Configurations*, FHWA-HRT-19-025, 2019.

[14] Federal Highway Administration, *Signalized Intersections: Informational Guide* (Chapter on Variable Lane Use and Dynamic Control), 2008.

[15] K. Behrendt and L. Novak, "A deep learning approach to traffic lights: Detection, tracking, and classification," in *Proc. IEEE Int. Conf. Robotics and Automation (ICRA)*, 2017, doi: 10.1109/ICRA.2017.7989182.

[16] M. Jensen et al., "The DriveU Traffic Light Dataset: Introduction and Comparison with Existing Datasets," in *Proc. IEEE Int. Conf. Robotics and Automation (ICRA)*, 2018, doi: 10.1109/ICRA.2018.8460737.

