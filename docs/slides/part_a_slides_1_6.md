# Slides 1–6 (Opening to End of Part A)

## Slide 1
**Title**: From Sensor Signals to Safety-Critical Decisions: AV Corner Cases Under Contradiction  
**Subtitle**: Red-Team Analysis of Four Unsafe Scenarios  
**Purpose**: Establish the research problem, thesis, and team scope.

**Content (put on slide):**
- Autonomous driving can perform well on average but still fail in long-tail corner cases.
- We analyze four unsafe scenarios where contradictory evidence is prematurely converted into deterministic decisions.
- Core thesis: **unsafe behavior is caused by premature commitment under unresolved contradiction**.
- Team split: Part A (A1/A2) by Member A; Part B (B1/B2) by Member B.

**Visual suggestion:**
- One horizontal pipeline: Perception -> Fusion -> Planning -> Control.
- Red marker above "Premature Commitment" at Fusion/Planning boundary.

**Speaker note (1 sentence):**
- "Our contribution is a unified failure mechanism and mitigation logic across heterogeneous corner cases."

**中文对照：**
- **中文标题**：从传感器信号到安全关键决策：矛盾证据下的自动驾驶边缘场景  
- **中文副标题**：四类不安全场景的红队分析  
- **中文目的**：交代研究问题、核心观点和两位成员分工。  
- **中文内容（可放PPT）**：
  - 自动驾驶在平均场景下表现良好，但在长尾边缘场景仍可能出现危险失效。  
  - 我们研究四类场景：系统在证据冲突时过早做出确定性决策。  
  - 核心观点：**不安全行为的根因是“在矛盾未消解时过早承诺”**。  
  - 分工：Part A（A1/A2）由成员A负责；Part B（B1/B2）由成员B负责。  
- **中文讲稿提示（一句）**：
  - “我们的贡献是提出一个跨场景统一的失效机理与缓解逻辑，而不只是列举案例。”  

---

## Slide 2
**Title**: Scenario Overview and Evaluation Axes  
**Subtitle**: Four Scenarios, One Unified Comparison Framework  
**Purpose**: Define all scenarios and explain how every scenario is evaluated using the same dimensions.

**Scenario labels (use exactly):**
- **A1 — Reflective Facade Phantom Vehicle**: False Positive Trajectory Commitment.
- **A2 — Transparent Garage Door**: False Free-Space Commitment.
- **B1 — Reversible-Lane Signal Misread**: Lane Attribution Error at Entrance.
- **B2 — Reversible-Lane Transition Conflict**: Mode Oscillation and Deadlock.

**Evaluation axes (explain clearly on slide):**
- **Axis 1: Architecture**
  camera-only vs multi-sensor.
- **Axis 2: Failure Chain**
  perception/rule interpretation -> prediction prior -> planning/control action.
- **Axis 3: Safety Metrics**
  PBS, EVR, collision rate, travel time (safety-efficiency tradeoff).
- **Axis 4: Mitigation Validation**
  permissive baseline vs contradiction-aware mitigation.

**Proposal alignment sentence (add as small footer):**
- "This directly matches proposal requirements: architecture comparison, failure-chain explanation, simulation evidence, and mitigation validation."

**Speaker note (1 sentence):**
- "Evaluation axes means shared comparison coordinates applied consistently to all four scenarios."

**中文对照：**
- **中文标题**：场景总览与统一评估轴  
- **中文副标题**：四个场景使用同一套比较框架  
- **中文目的**：先把四个场景讲清，再说明“我们如何统一评估”。  
- **中文内容（可放PPT）**：
  - A1：玻璃幕墙反射幽灵车（假阳性障碍物）。  
  - A2：透明车库门可通行误判（假阴性自由空间）。  
  - B1：可逆车道信号误读（车道归属错误）。  
  - B2：可逆车道切换窗口冲突（模式振荡/卡死）。  
  - 统一评估轴：  
    - 架构轴：camera-only vs multi-sensor  
    - 失效链轴：感知/规则解释 -> 预测先验 -> 规划控制  
    - 指标轴：PBS、EVR、碰撞率、通行时间  
    - 缓解轴：permissive baseline vs contradiction-aware mitigation  
- **中文讲稿提示（一句）**：
  - “这里的 axes 就是统一比较坐标，四个场景都按同一框架评估，保证结论可横向对比。”  

---

## Slide 3
**Title**: A1 Definition — Reflective Facade Ghost Vehicle  
**Subtitle**: A Real Car Is Beside Us, but the System Thinks It Is in Front  
**Purpose**: Explain scenario setup and risk mechanism.

**Content (put on slide):**
- Urban 3-lane road canyon; ego speed 35-45 km/h.
- Long reflective glass facade along roadside.
- Real vehicle in adjacent lane; reflected image projected into ego lane view.
- Camera output: stable \"front vehicle\" across multiple frames.
- Tracker effect: ghost target promoted; virtual TTC drops.
- Planning effect: unnecessary hard braking / evasive steering.
- Safety outcome: rear-end risk + lateral conflict risk.

**Visual suggestion:**
- Use `docs/part_a/A1_part_a_locked.png`.
- Add one short callout: "appearance-geometric inconsistency".

**Speaker note (1 sentence):**
- "In A1, the dangerous part is not the reflection itself, but the system committing to it as a real obstacle."

**中文对照：**
- **中文标题**：A1 场景定义——玻璃幕墙幽灵车辆  
- **中文副标题**：真实车辆在旁侧，但系统误以为前方有车  
- **中文目的**：说明 A1 的具体环境、触发过程和风险后果。  
- **中文内容（可放PPT）**：
  - 城市三车道路峡谷环境；自车 35-45 km/h。  
  - 路侧大面积玻璃幕墙。  
  - 相邻车道真实车辆；反射投影进入自车前向视野。  
  - 相机输出：连续多帧“前车”稳定检测。  
  - 跟踪结果：幽灵目标被升格；虚拟 TTC 下降。  
  - 规划结果：不必要急刹 / 规避转向。  
  - 安全后果：后车追尾风险 + 侧向冲突风险。  
- **中文讲稿提示（一句）**：
  - “A1 的关键不是看到了反射，而是系统把反射升级成了要立即处理的真实障碍。”  

---

## Slide 4
**Title**: A1 Comparison + Mitigation  
**Subtitle**: Why Two Baselines Fail and What Our Fix Changes  
**Purpose**: Compare architectures and present mitigation effect.

**Content (put on slide):**
- Camera-only failure chain:
  - reflected box stable for 8-12 frames;
  - virtual TTC < brake threshold;
  - hard deceleration on physically empty lane center.
- Multi-sensor (permissive) failure chain:
  - LiDAR support sparse/inconsistent near glass;
  - weak radar multipath at similar range;
  - additive fusion still crosses confirmation threshold.
- Mitigation (plain):
  - unconfirmed if camera-positive but geometry-weak;
  - keep unconfirmed + gentle slowdown + re-check.
- Figure signals (single seed): longitudinal accel, TTC$_{virtual}$.
- 100-seed result:
  - PBS: 1.933 -> 1.188
  - Reduction: **38.5%**
  - Significance: **p = 1.08e-13**

**Visual suggestion:**
- Left: small formula block (penalized fusion).
- Right: number card with PBS reduction and p-value.
- Optional mini chart: `results/part_a_simulation_100/a1_three_modes_timeline.png` (y-axes: accel, TTC$_{virtual}$).

**Speaker note (1 sentence):**
- "If sensors disagree, we delay confirmation and slow down smoothly instead of committing to a hard brake."

**中文对照：**
- **中文标题**：A1 架构对比与缓解效果  
- **中文副标题**：为什么两个基线都会失败，以及我们的修复点  
- **中文目的**：讲清 camera-only 与 multi-sensor 基线的失效差异，并给出 mitigation 的量化收益。  
- **中文内容（可放PPT）**：
  - camera-only 失效链：  
    - 反射框连续 8-12 帧稳定；  
    - 虚拟 TTC 低于制动阈值；  
    - 前方物理空车道仍触发急减速。  
  - multi-sensor（宽松融合）失效链：  
    - 玻璃附近 LiDAR 支持稀疏/不连续；  
    - 雷达同距离弱多径回波；  
    - 加和融合仍越过确认阈值。  
  - mitigation（通俗版）：  
    - 相机阳性但几何证据弱 -> 不确认为真障碍；  
    - 先不确认 -> 轻减速 -> 复核后续帧。  
  - 图中变量（单次时序）：纵向加速度、虚拟 TTC。  
  - 100 次随机实验：  
    - PBS：1.933 -> 1.188  
    - 下降：38.5%  
    - 显著性：p = 1.08e-13  
- **中文讲稿提示（一句）**：
  - “一句话：证据对不上时，先慢下来再确认，不要把反射直接当成必须急刹的真车。”  

---

## Slide 5
**Title**: A2 Definition — Transparent Garage Door False Free-Space  
**Subtitle**: The Exit Looks Open, but a Closed Glass Door Is Actually There  
**Purpose**: Explain A2 physical setup and failure origin.

**Content (put on slide):**
- Underground garage ramp exit -> bright outdoor street.
- Closed transparent glass door at boundary.
- Camera cue: continuous outdoor scene through glass.
- Depth cue: missing/unstable return at door plane.
- Map effect: unknown region collapsed into free-space.
- Planning outcome: forward commit into physical barrier.
- Safety risk: low-speed impact + exit blockage.

**Visual suggestion:**
- Use `docs/part_a/A2_part_a_locked.png`.
- Add one equation chip: `m(O) + m(F) + m(Omega) = 1`.

**Speaker note (1 sentence):**
- "A2 is dangerous because missing depth is mistaken as free space, not because the door is invisible."

**中文对照：**
- **中文标题**：A2 场景定义——透明车库门自由空间误判  
- **中文副标题**：视觉看起来可通行，但物理上是关闭的玻璃门  
- **中文目的**：说明 A2 的物理环境、证据错配和碰撞来源。  
- **中文内容（可放PPT）**：
  - 地库坡道出口 -> 外部强光街道。  
  - 边界：关闭的透明玻璃门。  
  - 相机线索：可看到门外连续街景。  
  - 深度线索：门平面回波缺失/不稳定。  
  - 地图结果：unknown 被折叠成 free-space。  
  - 规划结果：轨迹继续前推，直穿门体。  
  - 风险后果：低速碰撞 + 出口阻塞。  
- **中文讲稿提示（一句）**：
  - “A2 的本质是把‘未知深度’误当成‘可通行空间’，不是单纯看不见门。”  

---

## Slide 6
**Title**: A2 Comparison + Mitigation  
**Subtitle**: Why Both Baselines Fail, and How Mitigation Stops Collision  
**Purpose**: Show mitigation mechanism and safety-efficiency tradeoff.

**Content (put on slide):**
- Camera-only failure:
  - visual continuity through glass -> strong free-space prior;
  - no geometric veto channel;
  - unknown collapses to free-space -> collision.
- Multi-sensor (permissive) failure:
  - LiDAR depth void treated as \"no evidence\" (not risk evidence);
  - radar gives little/no reliable door boundary support;
  - permissive fusion still commits to free-space -> collision.
- Key message:
  - both architectures fail, but for different reasons;
  - this is the motivation for contradiction-aware mitigation.
- Mitigation: keep unknown when depth support is weak.
- Control logic (simple):
  - high uncertainty zone -> creeping speed;
  - stopping distance exceeded -> forced full stop.
- 100-seed results:
  - EVR: 0.942 -> 0.104
  - Collision rate: 1.000 -> 0.000
  - Travel time: 6.09 s -> 19.63 s
- Figure vs results:
  - timeline (single seed): speed, unknown mass $m(\\Omega)$;
  - summary (100 seeds): EVR, collision rate, travel time.
- Interpretation (2D -> 3D): 2D results show a clear safety-efficiency tradeoff; deployment-level confidence still needs 3D validation under latency, friction/slope uncertainty, weather/glare, calibration drift, and richer multipath, typically with uncertainty-aware fusion, temporal checks, RSS-like safety envelopes, and domain-randomized tests.

**Visual suggestion:**
- Main figure: `results/part_a_simulation_100/a2_three_modes_timeline.png` (y-axes: speed, unknown mass $m(\\Omega)$).
- Small table: PBS / EVR / collision / travel time.

**Speaker note (1 sentence):**
- "In 2D we show the mechanism clearly; in 3D we still need latency, friction, and weather robustness before claiming deployment-level safety."

**中文对照：**
- **中文标题**：A2 架构对比与缓解效果  
- **中文副标题**：两种基线为何都失败，以及 mitigation 如何止碰  
- **中文目的**：讲清 mitigation 如何避免穿门，并说明安全-效率权衡。  
- **中文内容（可放PPT）**：
  - camera-only 失效：  
    - 玻璃后连续街景 -> 强 free-space 语义先验；  
    - 缺少几何否决通道；  
    - unknown 被折叠为 free -> 碰撞。  
  - multi-sensor（宽松融合）失效：  
    - LiDAR 深度空洞被当作“没证据”，而不是“风险证据”；  
    - 雷达对门边界支持弱/不稳定；  
    - 宽松融合仍提交 free-space 轨迹 -> 碰撞。  
  - 核心结论：  
    - 两种架构都会失败，但失败机制不同；  
    - 这正是我们做 mitigation 的研究动机。  
  - mitigation 原则：深度不可靠时，保留 unknown。  
  - 控制逻辑（简版）：  
    - 高不确定区域：低速爬行；  
    - 小于安全停车距离：强制刹停。  
  - 100 次随机实验：  
    - EVR：0.942 -> 0.104  
    - 碰撞率：1.000 -> 0.000  
    - 通行时间：6.09s -> 19.63s  
  - 图与结果口径：  
    - 时序图（单次）：speed、unknown mass $m(\\Omega)$；  
    - 汇总指标（100 次）：EVR、碰撞率、通行时间。  
  - 结果解读（2D -> 3D）：2D 结果清楚显示“安全提升-效率下降”的权衡；要到可部署级结论，还需在 3D 中覆盖时延、摩擦/坡度不确定、天气眩光、标定漂移和复杂多径，并结合不确定性感知融合、时间一致性检查、RSS 类安全包络与域随机化测试。  
- **中文讲稿提示（一句）**：
  - “2D 结果证明机制有效，但到 3D 落地还要把时延、摩擦和天气这些现实因素一起并入安全验证。”  
