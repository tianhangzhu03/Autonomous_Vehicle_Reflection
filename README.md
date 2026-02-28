# EE495 Autonomous Vehicle Reflection 项目协作说明

本 README 用于你和 teammate 的协同写作与交付对齐，重点保证：
- 场景编号统一（`A1/A2/B1/B2`）
- 文档结构统一（按课程 handout 章节）
- 图表与引用规范统一（IEEE/ACM 风格）
- 提交节奏统一（默认每天一次集中提交）

---

## 1. 项目目标（课程要求对齐）

本项目是面向自动驾驶 corner case 的 red-team 安全分析。最终交付包括：
- 一份双栏报告（建议 7–8 页，不含参考文献）
- 一次课程展示（内容与报告一致）

当前四个核心场景：
- `A1` 玻璃幕墙反射“幽灵车辆”导致误制动/误避让
- `A2` 透明玻璃门/橱窗导致深度空洞与 free-space 误判
- `B1` 可逆车道入口信号误读/车道归属错误
- `B2` 可逆车道方向切换过渡窗口状态机振荡/卡死

---

## 2. 分工与责任边界

### 2.1 Member A（Benjamin）
- 负责 `A1/A2` 场景分析与写作
- 负责 `1.3 Literature Review` 统一撰写与整合
- 负责整体文风统一与最终汇总

### 2.2 Member B（Teammate）
- 负责 `B1/B2` 场景定义、失败链、缓解方案与相关图示
- 提供 B 部分实验/案例素材与结果描述

### 2.3 共同负责
- 最终交叉检查（术语、图例、表格、引用格式）
- 口头展示内容分配与问答准备

---

## 3. 文件导航（当前有效）

### 3.1 报告主框架
- `docs/report_master_outline.md`：报告总体大纲与任务状态
- `docs/report_sections_1_1_1_3_merged.md`：已合并的 `1.1–1.3` 正文草稿（当前唯一有效版本）

### 3.2 场景文档
- `docs/part_a/part_a_scenarios.md`：A1/A2 详细分析
- `docs/scenarios/team_scenarios_draft.md`：四场景统一草稿（A1/A2/B1/B2）

### 3.3 参考文献库
- `docs/references/README.md`：文献库说明与下载状态
- `docs/references/source_catalog.tsv`：文献总目录
- `docs/references/library_status.tsv`：每篇文献是否已下载
- `docs/references/pdfs/`：已下载 PDF（优先从这里引用）

### 3.4 图表规范
- `docs/style/figure_table_legend_spec.md`：图例/配色/IEEE-ACM 表格规范

---

## 4. 写作与命名规范

### 4.1 场景编号（强制）
- 仅使用：`A1`, `A2`, `B1`, `B2`
- 不再使用旧编号（如 `S1/S3`）

### 4.2 正文写作风格
- 采用连贯段落，不写成 bullet 堆砌
- 每段聚焦一个论点：结论 -> 证据 -> 限制/含义
- 避免模糊词（如“可能很多”“大概”），尽量给出明确机制

### 4.3 引用与表述
- 引用优先级：官方标准/监管 > 顶级会议期刊 > 高质量预印本
- “文献事实”与“工程推断”需区分清楚
- 最终统一成 IEEE 参考文献格式

---

## 5. 图表与表格规范（执行摘要）

- 场景颜色固定：
  - `A1` -> `#7e8cad`
  - `A2` -> `#a5c2cd`
  - `B1` -> `#e19d92`
  - `B2` -> `#eac47c`
- 使用低饱和色，不使用高饱和红绿对抗配色
- IEEE/ACM 表格：caption 在上、无竖线、数值列右对齐
- 详细规则见：`docs/style/figure_table_legend_spec.md`

---

## 6. 协作流程与提交规则

### 6.1 日常协作
- 小改动先本地累计，不必立即 push
- 每天集中一次 commit/push（默认规则）
- 若临近截止或需要队友即时同步，可临时加一次 push

### 6.2 Commit 建议
- commit message 简洁明确，体现模块：
  - `refine section 1.3 narrative`
  - `update B1/B2 scenario analysis`
  - `add figure/table style constraints`

### 6.3 合并前检查
- 场景编号是否统一为 A1/A2/B1/B2
- 章节结构是否与大纲一致
- 图例与颜色是否符合规范
- 引用是否可追溯且格式一致

---

## 7. 当前优先级（下一步）

1. 完成 `B1/B2` 正文细化（与 A1/A2 深度对齐）
2. 补齐 `1.5 Simulation & Evaluation Setup`
3. 补齐 `1.6 Mitigation Strategies`
4. 最后统一压缩篇幅到 7–8 页双栏

