# EE495 CAV Course Project — Report Plan (Current Snapshot)

## 1. Report Structure (IEEE/ACM double-column)

### 1.1 Abstract
- Project objective (red-team AV corner cases)
- 4 scenarios overview
- Key findings and contributions
- Team contribution statement (required for 2-person team)

### 1.2 Introduction
- Why corner cases matter for AV safety
- Scope of this project (2 glass/reflection + 2 non-glass)
- Camera-only vs camera+LiDAR+radar comparison scope
- Paper organization

### 1.3 Literature Review
- Safety/regulation framing (FMVSS 127, Euro NCAP, NHTSA investigations)
- Perception/fusion foundations and uncertainty handling
- Reflection/transparent-glass sensing mechanisms
- Part B-related literature (construction/gate-like obstacles)

### 1.4 Unsafe Scenarios
- A1: Glass facade ghost vehicle
- A2: Transparent glass barrier free-space error
- B1: Work-zone temporary traffic control conflict
- B2: Gate-like barrier (chain/arm) detection/planning failure
- For each scenario: setup, expected safe behavior, failure chain, architecture comparison, risk

### 1.5 Simulation & Evaluation Setup (recommended section)
- Platform/setup assumptions
- Baseline vs mitigation experiment design
- Unified metrics and logging format
- Reproducibility notes

### 1.6 Mitigation Strategies
- Cross-scenario principles
- Scenario-specific short-term patches
- Longer-term system redesign directions

### 1.7 Conclusion
- Main safety insights
- Limits of current study
- Future work

---

## 2. Completed So Far

- [x] Part A literature review (major revised version, verified references, wider time span)
  - `/Users/benjaminzth/Desktop/Courses/EE495AutonomousVehicles/Autonomous_Vehicle_Reflection/docs/part_a/part_a_literature_review.md`
- [x] Part A unsafe scenarios detailed draft (A1 + A2, refined writing, evidence-vs-inference boundary)
  - `/Users/benjaminzth/Desktop/Courses/EE495AutonomousVehicles/Autonomous_Vehicle_Reflection/docs/part_a/part_a_scenarios.md`
- [x] All above pushed to `main` branch

---

## 3. Team Division of Work

| Module | Owner | Scope |
|---|---|---|
| Part A scenario 1 | You | A1 Glass facade reflection ghost vehicle |
| Part A scenario 2 | You | A2 Transparent glass barrier / free-space error |
| Part A writing core | You | Part A literature + Part A unsafe scenarios + Part A mitigation/evaluation text integration |
| Part B scenario 1 | Teammate | B1 Work-zone temporary guidance conflict |
| Part B scenario 2 | Teammate | B2 Gate-like barrier (chain/arm) corner case |
| Team merge | Both | Unified report structure, references, figures, final proofreading |

---

## 4. Pending Items (To Be Implemented)

### 4.1 Your pending items (Part A)
- [ ] Convert current `[L#]` working tags to final IEEE citation format
- [ ] Write Part A subsection for `Mitigation Strategies` in final report tone
- [ ] Write Part A subsection for `Simulation & Evaluation Setup`
- [ ] Define final metric formulas and thresholds used in Part A plots
- [ ] Produce Part A figures (setup/failure-chain/results) and captions

### 4.2 Teammate pending items (Part B)
- [ ] Part B literature subsection draft
- [ ] B1/B2 unsafe scenario detailed write-up (same template depth as Part A)
- [ ] Part B mitigation and evaluation plan
- [ ] Part B figures and result placeholders

### 4.3 Joint pending items (final integration)
- [ ] Merge Part A + Part B into single report file
- [ ] Unify terminology across sections (ghost/phantom/unknown/free-space, etc.)
- [ ] Add explicit team contribution paragraph in Abstract
- [ ] Ensure required sections are all present per course handout
- [ ] Final formatting pass (IEEE/ACM double-column) and reference consistency check
