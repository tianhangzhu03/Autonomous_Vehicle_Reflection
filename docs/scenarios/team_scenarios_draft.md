# Team Scenarios Working Draft (A1, A2, S1, S3)

> Purpose: this working draft keeps all four scenarios in one place for report integration.
> A1/A2 remain owned by Part A, while S1/S3 are teammate-owned Part B scenarios now registered in the project baseline.

## Scenario List and Ownership

| ID | Title | Owner | Type |
|---|---|---|---|
| A1 | 玻璃幕墙反射“幽灵车辆”导致误制动/误避让 | You | Reflection / cross-modal inconsistency |
| A2 | 透明玻璃门/橱窗导致深度空洞与 free-space 误判 | You | Transparent obstacle / traversability error |
| S1 | 可逆车道入口处车道方向信号误读/车道归属错误 | Teammate | Temporary traffic control + lane attribution conflict |
| S3 | 可逆车道方向切换过渡窗口状态机错误（规则振荡/卡死） | Teammate | Transition timing + mode arbitration failure |

---

## A1 (Part A) — Glass Facade Ghost Vehicle

- 核心风险：反射造成视觉强阳性目标，跨模态证据不一致仍被融合升格，触发误刹或误避让。
- 重点失效链：Reflection -> Perception inconsistency -> Fusion ghost track -> TTC underestimation -> Aggressive planning action。
- 架构对比：
  - `camera-only`：语义误检更直接传递。
  - `camera+LiDAR+radar`：理论可抑制误检，但在玻璃场景中 LiDAR/radar 也可能产生困难样本，若融合缺乏反证门控仍可失败。

(Detail source: `/Users/benjaminzth/Desktop/Courses/EE495AutonomousVehicles/Autonomous_Vehicle_Reflection/docs/part_a/part_a_scenarios.md`)

## A2 (Part A) — Transparent Glass Barrier Free-Space Leak

- 核心风险：视觉可见背景 + 深度失效，导致不可通行区域被误判为可通行，产生撞障或卡死。
- 重点失效链：Transparent barrier -> Depth ambiguity -> Occupancy/traversability error -> Unsafe path commitment。
- 架构对比：
  - `camera-only`：依赖语义先验，泛化风险高。
  - `camera+LiDAR+radar`：若未显式建模“透明体=深度不可靠域”，多模态也可能将空洞当 free。

(Detail source: `/Users/benjaminzth/Desktop/Courses/EE495AutonomousVehicles/Autonomous_Vehicle_Reflection/docs/part_a/part_a_scenarios.md`)

---

## S1 (Part B) — 可逆车道入口信号误读 / 车道归属错误

### 场景定义

在可逆车道入口，龙门架车道方向信号（绿箭头/红X/黄箭头）是关键规则来源。高峰拥堵、重车遮挡、低太阳角眩光、雨后反光或夜间溢光会降低图案可见性；弯道、匝道分流、坡顶视角变化会增加“信号-车道绑定”难度。

### 触发条件

- 单帧图案退化：红X与绿箭头在眩光或反光下被洗白、变形。
- 遮挡导致关键信号帧缺失：识别结果断续。
- 车道归属不稳：识别本身正确，但绑定到错误车道（lane attribution error）。

### 失败链（Perception -> Prediction -> Planning/Control）

- 感知：语义误分类（绿↔红）或 lane attribution 错误。
- 预测：错误规则先验导致对周车意图解释偏差（例如将对向来车视为异常目标而非规则冲突证据）。
- 规划/控制：
  - 误入关闭/对向车道（最严重）；
  - 入口处摇摆、急刹、最后时刻横向修正（更常见）。

### 架构对比

- `camera-only`：对信号语义和车道归属的视觉依赖更强，受眩光/遮挡影响更直接。
- `camera+LiDAR+radar`：可通过运动证据部分抑制灾难性后果，但“信号语义 + lane attribution”仍主要依赖视觉，仍可能失败。

### 主要安全后果

- wrong-way / 逆行风险
- 入口急刹导致追尾风险
- 急并线导致侧碰风险

---

## S3 (Part B) — 过渡窗口状态机错误（规则振荡/卡死）

### 场景定义

可逆车道方向切换并非瞬时完成，常经历“预告 -> 清空 -> 切换 -> 稳定”过程。过渡窗口内可能出现：
- 相邻龙门架更新不同步，
- 部分信号闪烁过渡，
- 上方信号与地面残留标线/车流运动证据短时冲突，
- 人类驾驶行为不一致（晚进入、急刹、犹豫并线）。

### 触发条件

- 多源规则冲突：近端显示开放，远端仍关闭/闪烁。
- 识别置信度阈值附近波动：绿↔红反复抖动。
- 周车轨迹短时混杂，使“运动证据”与规则证据不一致。

### 失败链（Perception -> Mode Arbitration/State Machine -> Planning/Control）

- 感知：信号语义/归属不稳定，或真实不一致状态未被建模为不确定性。
- 模式仲裁（核心）：Normal 与 Reversible-lane 模式缺乏滞回和时间一致性约束，导致频繁切换（rule oscillation）。
- 规划/控制：速度抖动（加减速循环）、路径抖动（尝试进入又撤回）、入口/分流口卡死（deadlock）。

### 架构对比

- `camera-only`：更易被信号抖动直接触发模式跳变。
- `camera+LiDAR+radar`：能更稳定感知周车运动，但“信号开放 vs 运动危险”的语义冲突仍可能导致仲裁失败（卡死或过度急刹）。

### 主要安全后果

- 卡死或急刹引发追尾
- 试探并线引发侧碰
- 极端情况下误入对向

---

## Integration Notes for Report Writing

- 统一模板（每场景同结构）：Setup / Expected Safe Behavior / Failure Chain / Architecture Comparison / Risk / Mitigation。
- S1 与 S3 可共享同一组背景文献：
  - lane-use control signal 标准与可逆车道运行规则，
  - 信号识别鲁棒性与 lane attribution 方法，
  - 模式仲裁/状态机在不确定输入下的稳定性设计。
- 建议 S1 偏重“语义与归属误解”，S3 偏重“时序与仲裁振荡”，避免内容重复。

