# Part A Presentation Script (Slides 1-6, Bilingual, 6-Min Version)

This is the expanded script for **Member A**.
Target duration: **about 6 minutes**.

---

## Slide 1 - Opening

### English Script
Good afternoon. I will present Part A of our project, which includes two glass-induced corner cases: A1 and A2.  
Our central finding is this: many unsafe behaviors come from **early commitment under conflicting evidence**, not from one isolated detector error.  
A1 is a false-positive obstacle case. A2 is a false-free-space case.  
These two cases are opposite in outcome, but they share the same root cause in contradiction handling.  
In the next slide, I will place them in the full four-scenario map.

### 中文口播
大家好。我负责汇报 Part A，也就是两个玻璃相关场景：A1 和 A2。  
我们的核心发现是：很多危险行为来自**证据冲突下的过早承诺**，而不是单一检测器错误。  
A1 是假阳性障碍物问题，A2 是假自由空间问题。  
这两个场景结果相反，但根因一致，都是矛盾证据处理失败。  
下一页我先把它们放到四场景总览里。

---

## Slide 2 - Overview and Axes

### English Script
This slide shows the full scope. I focus on A1 and A2; my teammate covers B1 and B2.  
We use one shared comparison frame for all scenarios: architecture, failure chain, safety metrics, and mitigation effect.  
Three labels used repeatedly in my part are: PBS, EVR, and TTC.  
PBS means unnecessary braking severity. EVR means wrong free-space belief on true barrier cells. TTC is time-to-collision estimate, and lower values mean more immediate risk.  
With this frame fixed, I will now start with A1.

### 中文口播
这一页是总体范围。我负责 A1 和 A2，队友负责 B1 和 B2。  
四个场景统一按同一框架比较：架构、失效链、指标、缓解效果。  
我这部分会反复用到三个标签：PBS、EVR、TTC。  
PBS 是不必要制动强度，EVR 是真实障碍区域被误判为可通行的程度，TTC 是碰撞时间估计，越低表示风险越紧迫。  
有了这套口径，下面进入 A1。

---

## Slide 3 - A1 Scenario Setup

### English Script
A1 occurs on an urban multi-lane road with a reflective facade.  
A real vehicle in an adjacent lane produces a reflected target in the ego forward view.  
Camera can keep this reflected box stable across frames. Tracking then promotes it, and virtual TTC drops.  
Planning may respond with hard braking or unnecessary avoidance, even though the lane center is physically empty.  
So the safety impact is secondary but serious: rear-end risk and side-conflict risk.  
Next, I compare how camera-only, permissive multi-sensor, and mitigation behave differently.

### 中文口播
A1 发生在城市多车道路段，路侧有强反射玻璃幕墙。  
相邻车道的真实车辆会在自车前向视野里形成反射目标。  
相机可能连续多帧稳定检测这个反射框，跟踪会把它升格，虚拟 TTC 随之下降。  
即使前方物理空车道，规划也可能触发急刹或不必要规避。  
所以它的安全后果是次生但严重的：追尾风险和侧向冲突风险。  
下一页我对比三种架构表现。

---

## Slide 4 - A1 Comparison + Figure + Result (Focus)

### English Script
This is the main A1 comparison slide.  
Camera-only failure is direct: reflected box stays stable, TTC goes below trigger, then the car brakes hard in an actually empty lane.  
Permissive multi-sensor fails in a different way: LiDAR support near glass is sparse, radar may give weak multipath echoes, but additive fusion can still confirm the obstacle.  
Now read the timeline figure first. Each curve is one pipeline.  
Top panel is longitudinal acceleration. A sudden negative spike means unnecessary hard braking.  
Bottom panel is virtual TTC. Lower TTC means the system thinks collision is close.  
In both baselines, TTC drops early, then braking spikes appear.  
Small pre-spike oscillations mean policy hesitation: brake/hold speed switching under conflicting evidence.  
In mitigation, we first treat cross-sensor mismatch as a contradiction signal.  
Then we delay hard obstacle confirmation for extra frames instead of committing immediately.  
During that window, we use gentle speed reduction, so TTC and acceleration stay much smoother.  
Across 100 seeds, PBS drops from 1.933 to 1.188, a 38.5% reduction, with p = 1.08e-13.  
So in A1, mitigation suppresses false hard-brake behavior without pretending contradiction does not exist.  
A1 is a false-positive case. Next, A2 shows the opposite error: false free-space.

### 中文口播
这一页是 A1 最关键的对比。  
camera-only 的失效很直接：反射框稳定，TTC 触发阈值，然后在实际空车道上急刹。  
宽松 multi-sensor 的失效机制不同：玻璃附近 LiDAR 支持稀疏，雷达会有弱多径回波，但加和融合还是可能把目标确认下来。  
先读图。每条曲线对应一个 pipeline。  
上图是纵向加速度，向下尖峰就是不必要急刹。  
下图是虚拟 TTC，越低说明系统越相信“马上会撞”。  
两个基线里，先出现 TTC 下探，再出现急刹尖峰。  
急刹前的小波动表示系统在“要不要刹”之间来回切换。  
mitigation 的逻辑是连贯三步：先把跨传感器不一致当成矛盾信号。  
然后不立刻做硬确认，先多看几帧。  
在这段窗口里先平顺降速，所以 TTC 和加速度曲线都会更稳定。  
100 次随机实验里，PBS 从 1.933 降到 1.188，下降 38.5%，p = 1.08e-13。  
所以在 A1，mitigation 的作用是抑制假阳性引发的高强度误制动，而不是忽略矛盾。  
A1 是假阳性场景。下面 A2 是相反方向的错误：假自由空间。

---

## Slide 5 - A2 Scenario Setup

### English Script
A2 is an underground garage exit with a closed transparent glass door.  
Camera still sees a continuous outdoor scene through the door, so semantics suggest traversability.  
Depth support near the boundary is missing or unstable, so geometric evidence is weak.  
If unknown is collapsed into free-space too early, planning commits a path into the physical barrier.  
Now I show how this appears in the timeline curves and metrics.

### 中文口播
A2 是地下车库出口，边界处有关闭的透明玻璃门。  
相机仍能看到门外连续场景，所以语义上看起来可通行。  
但门边界深度支持缺失或不稳定，几何证据很弱。  
如果系统过早把 unknown 折叠为 free-space，规划就会提交穿门轨迹。  
下一页我用时序曲线和指标把这个过程讲清楚。

---

## Slide 6 - A2 Comparison + Figure + Result (Focus)

### English Script
In A2, both baselines fail, again for different reasons.  
Camera-only mainly trusts the image continuity and has no reliable distance cross-check.  
Permissive multi-sensor also fails, because it treats missing depth as “nothing wrong” instead of a warning sign.  
Read the figure first. Each curve is one pipeline.  
Top panel is speed. Bottom panel is unknown mass m(Omega).  
In baseline runs, unknown mass is quickly pushed toward zero, because unknown gets forced into free-space.  
Speed stays near nominal, so the car keeps moving into danger.  
In mitigation, unknown mass stays high near the door, then speed drops and the car stops before impact.  
Small wiggles on speed or unknown come from frame noise and control update delay.  
This follows our mitigation chain: keep uncertainty, switch to cautious speed logic, then hard-stop if stopping distance is not enough.  
For metrics: EVR is the average “free-space belief” on real door cells, so lower is safer; collision rate is crash frequency; travel time shows the efficiency cost.  
Across 100 seeds, EVR drops from 0.942 to 0.104 and collision rate drops from 1.000 to 0.000, but travel time increases from 6.09 s to 19.63 s.  
This “safer but slower” tradeoff is not unique to our simulator. Similar blocking behavior was publicly reported in complex urban robotaxi operation, including Cruise in San Francisco.  
So the takeaway is simple: mitigation gives much better safety, but with clear efficiency cost.  
Also, this is still 2D evidence. Before claiming deployment readiness, we still need 3D validation with latency, friction and slope uncertainty, weather, calibration drift, and richer multipath.

### 中文口播
在 A2 里，两个基线同样失败，但原因仍然不同。  
camera-only 主要是太相信画面连续，没有稳定的距离交叉验证。  
宽松 multi-sensor 也会失败，因为它把深度缺失当成“没事”，而不是“危险信号”。  
先读图。每条曲线对应一个 pipeline。  
上图是速度，下图是 unknown mass m(Omega)。  
基线会很快把 unknown 压到接近 0，因为它把 unknown 强行折叠成 free-space。  
速度基本维持标称值，所以车辆会继续往风险区域开。  
mitigation 则在门前保持较高 unknown，然后主动降速并在撞击前停车。  
图里的小幅波动，主要来自逐帧噪声和控制更新延迟。  
这和 mitigation 的逻辑链一致：先保留不确定性，再进入谨慎速度策略，最后在停车距离不够时强制刹停。  
指标上，EVR 是真实门区域被判成 free 的平均置信度，越低越安全；碰撞率是直接撞击频率；通行时间反映效率代价。  
100 次随机实验中，EVR 从 0.942 降到 0.104，碰撞率从 1.000 降到 0.000，但通行时间从 6.09 秒增加到 19.63 秒。  
这种“更安全但更慢”的模式并不只在我们仿真里出现。复杂城市场景下，行业里也有公开报道的 robotaxi 长时间停车或阻塞现象，例如 Cruise 在旧金山。  
所以结论很直接：mitigation 显著提升安全，但效率代价很明确。  
最后强调边界：这仍是 2D 机制证据。若要形成部署级结论，还需要 3D 条件下的完整验证。

---

## Transition to Part B

### English
That concludes Part A. I now hand over to my teammate for Part B on reversible-lane control conflicts.

### 中文
我的 Part A 到这里结束，下面交给队友汇报 Part B 的可逆车道控制冲突场景。
