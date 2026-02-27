# 1.3 Literature Review Draft (All Four Scenarios: A1, A2, S1, S3)

## 1.3.0 检索范围与筛选标准

为保证 1.3 小节风格统一且可直接服务四个场景，本综述采用“机制证据 + 运行规则证据 + 决策安全证据”的组合检索策略。

- 时间跨度：1985–2025（基础表示方法到近年感知/融合/规则仲裁）
- 来源类型：
  - 顶级会议/期刊论文（ICRA/CVPR/IEEE TSP/Autonomous Robots/Accident Analysis & Prevention 等）
  - 官方标准/监管/工程指南（NHTSA、Euro NCAP、FHWA、MUTCD）
  - 交通工程权威报告与手册（FHWA/NCHRP/TRB）
- 纳入原则：
  - 与四个场景存在直接机制关联（反射/透明体、车道控制信号、车道归属、过渡窗口模式仲裁）
  - 来源可追溯且可访问（论文 DOI、官方 PDF、标准官网）
  - 结论可用于“感知→预测/仲裁→规划控制”链路解释

> 说明：本小节不是系统综述（systematic review），而是课程项目所需的“问题驱动文献综述”。重点是解释**为什么这些场景会失败**，以及**哪些缓解方向最有工程可行性**。

---

## 1.3.1 主题一：反射/透明体导致的跨模态不一致（A1, A2）

### 核心共识

1. 玻璃/镜面不是“随机噪声源”，而是会系统性破坏“外观—几何一致性”。
2. 反射与透明在风险上呈现两种相反失效极性：
   - A1：假阳性障碍（ghost obstacle）导致误刹/误避让；
   - A2：假阴性可通行（free-space leak）导致撞障/卡死。
3. 多模态并不自动安全；关键在于融合是否显式处理“矛盾证据”和“unknown 传播”。

### 代表性证据与贡献

- 3DRef 与 Plane-SLAM 相关工作说明：反射会引入跨帧、跨视角不一致量测，影响建图与障碍解释（对 A1 直接相关）。
- LiDAR 玻璃检测与 TOPGN 说明：透明障碍需要专项特征工程（强度/边界）和占据层建模（对 A2 直接相关）。
- Radar multipath ghost 研究说明：在强反射几何下，雷达可出现弱阳性/幽灵目标，可能错误强化融合结果（A1 辅助证据）。

### 方法局限（批判性评估）

- 很多反射/透明研究来自机器人或受控场景，外推到城市复杂交通时仍有 domain gap。
- 数据集常聚焦感知指标（检测/分割），较少覆盖“感知错误如何传导到规划控制动作”。
- 透明障碍研究普遍强调检测精度，但对 `unknown` 策略与驾驶行为耦合的评估不足。

### 对本项目的含义

- A1 重点不应只写“相机误检”，而应写“融合在矛盾证据下的置信度管理失败”。
- A2 重点不应只写“点云空洞”，而应写“占据/可通行表示将 unknown 错判为 free”。

---

## 1.3.2 主题二：可逆车道控制与入口/过渡窗口安全（S1, S3）

### 核心共识

1. 可逆车道是“规则优先级高于常规车道语义”的场景；信号语义和车道绑定错误会直接放大为高风险动作。
2. 方向切换并非瞬时，过渡窗口天然存在信息不一致和驾驶行为混杂。
3. 工程文献（FHWA/NCHRP/TRB）长期强调：动态车道控制必须配套清晰信号、时序一致性和驾驶员可解释性。

### 代表性证据与贡献

- MUTCD 与 FHWA 文档明确 lane-use control signal 的语义规范与运行边界。
- FHWA 的双向左转/可逆车道仿真评估报告指出：几何与控制策略选择会显著影响安全冲突和驾驶行为稳定性。
- 2020 年 reversible lanes 元分析给出总体安全效应证据：在特定设计条件下可改善安全，但效果高度依赖实施细节与运行管理。

### 方法局限（批判性评估）

- 交通工程报告多以人驾行为和宏观冲突指标为主，缺少面向自动驾驶“感知-仲裁-控制”内部状态观测。
- 可逆车道研究多关注静态运行绩效，较少细化“切换过渡窗口”内多源规则冲突的机器决策稳定性。
- 旧报告（90s/00s）对现代摄像头+深度学习感知链路覆盖不足，但在人因与信号设计原则上仍有价值。

### 对本项目的含义

- S1 应突出“信号语义识别正确 ≠ 车道归属正确”。
- S3 应突出“模式仲裁滞回与时间一致性缺失”是核心风险，而非单一检测精度问题。

---

## 1.3.3 主题三：信号识别与车道归属（S1 的技术核心）

### 核心共识

1. 交通信号识别在遮挡、眩光、远距离小目标条件下波动显著。
2. lane attribution（信号到底属于哪条车道）是独立且高风险的问题，不能被“识别准确率”替代。
3. HD map / 语义地图 / 车道几何约束可显著改善归属稳定性，但依赖地图质量与定位一致性。

### 代表性证据与贡献

- Bosch/DriveU 数据集工作证明交通信号小目标检测的难度与数据稀疏性。
- 基于 HD map 的 traffic light recognition（RAS 2019）将先验几何用于过滤和归属。
- 面向 traffic-light-to-lane assignment 的语义地图学习工作把“归属”显式建模，有助于 S1 的错配分析。
- 近年 sign-lane matching 研究表明，仅靠单帧视觉在多车道复杂场景中易错，需要时序与几何联合约束。

### 方法局限（批判性评估）

- 多数方法在公开数据集上的场景受限，动态临时交通控制（可逆车道切换）样本不足。
- 对极端光照/反射与重车遮挡的鲁棒性验证不充分。
- 多数论文给的是识别指标，不直接给“误归属导致危险控制动作”的下游指标。

### 对本项目的含义

- S1 的实验指标不能只放 mAP/F1；应加入“信号-车道绑定错误率”与“错误绑定触发风险动作比例”。

---

## 1.3.4 主题四：规则冲突下的模式仲裁与规划稳定性（S3 的技术核心）

### 核心共识

1. 不确定输入下的决策安全核心不是“单次选对”，而是“避免高频规则跳变导致控制振荡”。
2. 规则层（交通控制语义）与运动层（周车轨迹证据）冲突时，需要显式仲裁机制（优先级、滞回、时间一致性）。
3. 形式化安全约束（如 RSS）与在线规划约束可提供保守下界，但不能替代场景语义正确理解。

### 代表性证据与贡献

- Rule-hierarchy 规划（ICRA 2023）展示了规则优先级在在线规划中的可实现路径。
- RSS 形式化模型给出“最小安全行为”边界，适合用作 S3 过渡窗口的安全壳参考。
- 自动驾驶运动规划综述强调：不确定性处理与行为层稳定性是落地瓶颈之一。

### 方法局限（批判性评估）

- 形式化模型常假设规则输入稳定清晰，不完全覆盖“规则源彼此冲突”的真实状态。
- 规划论文通常在较理想语义前提下评测，较少暴露“模式机振荡”带来的系统级问题。

### 对本项目的含义

- S3 的重点应是“模式机设计”（hysteresis、最小驻留时间、冲突降级策略），而不仅是感知增强。

---

## 1.3.5 跨文献模式、差异与空白（可直接写进报告）

### 主要模式（Patterns）

- 模式 P1：四个场景都属于“高层规则语义与低层观测证据不一致”引发的级联错误。
- 模式 P2：研究界普遍在感知层有较多工作，但“感知不确定性如何进入规划控制”证据较少。
- 模式 P3：官方标准/协议对误触发和可控测试环境很重视，但真实长尾组合（反射+遮挡+切换时序）覆盖不足。

### 主要差异（Differences）

- A1/A2 更偏物理感知机理（反射/透射/量测失真）。
- S1/S3 更偏规则解释与状态机稳定性（语义绑定/时序仲裁）。
- A1/A2 的关键变量是模态一致性；S1/S3 的关键变量是规则一致性。

### 关键空白（Gaps）

1. 缺少统一基准将“信号归属错误 + 规则冲突 + 控制动作”串成端到端评价。
2. 缺少针对“过渡窗口”场景的状态机稳定性指标（规则切换频率、驻留时间、卡死率）。
3. 透明/反射场景研究与交通规则场景研究仍相对割裂，缺少跨主题统一安全叙事。

---

## 1.3.6 1.3 小节写作建议（简洁版）

建议最终 1.3 用 4 个小节组织，避免堆砌文献：

1. **Safety and Evaluation Framing**：FMVSS/Euro NCAP/MUTCD/FHWA（为什么这些 corner case 合理且有现实意义）
2. **Perception and Mapping Limits under Reflection/Transparency**：A1/A2 机理和代表工作
3. **Lane-Control Signal Semantics and Lane Attribution**：S1 的核心技术难点
4. **Mode Arbitration under Rule Conflicts**：S3 的核心系统难点

每个小节末尾都加一句“对本项目四场景的直接启示”，保持叙事闭环。

---

## 1.3.7 Curated Source Set (22 references, with credibility/relevance/contribution)

> 评分规则：
> - Credibility：A=顶级期刊/会议或官方标准；B=高质量预印本/行业报告
> - Relevance：H=直接作用于四场景之一；M=提供基础方法或安全框架

| ID | Source | Type | Credibility | Relevance | 主要贡献 | 主要局限 | 场景映射 |
|---|---|---|---|---|---|---|---|
| R01 | Moravec & Elfes, ICRA 1985, High Resolution Maps from Wide Angle Sonar, [DOI](https://doi.org/10.1109/ROBOT.1985.1087316) | Conference classic | A | M | 占据栅格基础思想 | 非车载场景 | A2/S3（unknown 表示） |
| R02 | Elfes, Occupancy Grids (arXiv reprint), [link](https://arxiv.org/abs/1304.1098) | Foundational paper | A | M | 概率占据表示与多传感融合逻辑 | 年代较早 | A2 |
| R03 | Hornung et al., OctoMap, Auton. Robots 2013, [link](https://link.springer.com/article/10.1007/s10514-012-9321-0) | Journal | A | M | 3D 概率占据与 unknown 管理 | 不针对玻璃特例 | A2/S3 |
| R04 | Huang et al., Multi-modal Sensor Fusion Survey, [arXiv](https://arxiv.org/abs/2202.02703) | Survey | B | M | 多模态融合范式与局限综述 | 综述性，不给特定场景结论 | A1/A2/S1/S3 |
| R05 | Tibebu et al., LiDAR-Based Glass Detection..., Sensors 2021, [link](https://www.mdpi.com/1424-8220/21/7/2263) | Journal | A | H | 玻璃检测改善占据映射 | 场景规模有限 | A2 |
| R06 | Zhao & Schwertfeger, 3DRef 2024, [arXiv](https://arxiv.org/abs/2403.06538) | Dataset/benchmark | B | H | 反射检测基准，强调 phantom 风险 | 主要是感知层评测 | A1 |
| R07 | Li et al., Reflections in LiDAR via Plane-SLAM, [arXiv](https://arxiv.org/abs/2406.10494) | Research paper | B | H | 反射导致量测不一致机理 | 真实交通复杂度有限 | A1/A2 |
| R08 | Weerakoon et al., TOPGN 2024, [arXiv](https://arxiv.org/abs/2408.05608) | Research paper | B | H | 透明障碍边界提取（强度/分层） | 迁移到车载需验证 | A2 |
| R09 | Zheng et al., Ghost Targets for Automotive Radar, IEEE TSP 2024, [DOI](https://doi.org/10.1109/TSP.2024.3384750) | Journal | A | H | 雷达多径幽灵目标检测理论 | 与端到端规划耦合不足 | A1 |
| R10 | Yao et al., PolarFree, CVPR 2025, [PDF](https://openaccess.thecvf.com/content/CVPR2025/papers/Yao_PolarFree_Polarization-based_Reflection-Free_Imaging_CVPR_2025_paper.pdf) | Conference | A | M | 偏振反射抑制长期路线 | 工程部署成本高 | A1/A2 |
| R11 | NHTSA FMVSS 127 Final Rule 2024, [PDF](https://www.nhtsa.gov/sites/nhtsa.gov/files/2024-04/final-rule-automatic-emergency-braking-systems-light-vehicles_web-version.pdf) | Regulation | A | H | false activation 监管动机 | 非场景库文档 | A1 |
| R12 | Euro NCAP Frontal Collision Avoidance Protocol v11, [PDF](https://www.euroncap.com/media/91710/euro-ncap-protocol-crash-avoidance-frontal-collisions-v11.pdf) | Protocol | A | H | 受控场景与背景约束 | 覆盖长尾有限 | A1/S1/S3 |
| R13 | MUTCD 11th Edition resource page, [link](https://mutcd.fhwa.dot.gov/resources/11th_Edition.htm) | Standard | A | H | 车道控制信号语义权威来源 | 对 AV 实现细节不展开 | S1/S3 |
| R14 | FHWA-HRT-19-025 (Simulator Assessment), [PDF](https://www.fhwa.dot.gov/publications/research/safety/19025/19025.pdf) | Govt research report | A | H | 可逆/双向左转方案仿真安全评估 | 偏交通工程，不是 AV 内部栈 | S1/S3 |
| R15 | Tiesler et al., Traffic safety effects of reversible lanes (meta-analysis), AAP 2020, [link](https://www.sciencedirect.com/science/article/pii/S0001457519314663) | Journal | A | H | 可逆车道总体安全效应量 | 研究异质性高 | S1/S3 |
| R16 | FHWA Signalized Intersections Guide Ch12, [link](https://ops.fhwa.dot.gov/publications/fhwahop08024/chapter12.htm) | Engineering guide | A | H | variable lane use 与动态控制原则 | 年份较早 | S1/S3 |
| R17 | Behrendt et al., A deep learning approach to traffic lights, ICRA 2017, [DOI](https://doi.org/10.1109/ICRA.2017.7989182) | Conference | A | H | 小目标信号识别难题与方法 | 对 lane attribution 支持不足 | S1 |
| R18 | Jensen et al., DriveU Traffic Light Dataset, ICRA 2018, [DOI](https://doi.org/10.1109/ICRA.2018.8460737) | Dataset paper | A | H | 交通信号检测基准 | 过渡窗口样本有限 | S1/S3 |
| R19 | Seif & Hu, Traffic light recognition using HD map features, RAS 2019, [DOI](https://doi.org/10.1016/j.robot.2018.10.004) | Journal | A | H | 地图先验提升识别与归属 | 依赖定位与地图质量 | S1 |
| R20 | Monninger et al., Traffic-light-to-lane assignment, [arXiv](https://arxiv.org/abs/2309.12087) | Research preprint | B | H | 将 lane attribution 显式建模 | 工业部署验证有限 | S1 |
| R21 | Censi et al., Receding Horizon Planning with Rule Hierarchies, ICRA 2023, [arXiv](https://arxiv.org/abs/2210.07516) | Conference | A | H | 规则层级进入规划仲裁 | 规则输入冲突建模仍简化 | S3 |
| R22 | Shalev-Shwartz et al., RSS formal model, [arXiv](https://arxiv.org/abs/1708.06374) | Formal method | A | M | 安全边界形式化表达 | 语义冲突场景覆盖有限 | S3 |

---

## 1.3.8 可直接粘贴到报告中的“综述结论段”

综上，四个场景在表面上分别属于“反射/透明感知问题”和“可逆车道规则问题”，但文献显示其共性风险机制一致：系统在证据不一致时过早输出高置信决策。A1/A2 主要体现材料光学引发的跨模态不一致，S1/S3 主要体现规则语义与时序仲裁不一致。现有研究在感知层与交通工程层均有较丰富成果，但对“错误如何跨层传导至规划控制动作”覆盖不足。基于这一空白，本项目的价值在于以统一模板把感知、归属、状态机与控制后果串联，并通过 baseline-mitigation 对比验证：仅提升检测精度不足以消除风险，必须把不确定性和规则冲突显式纳入融合与决策。
