# Prompt for Drawing AI (Slide 2: Scenario Overview + Evaluation Axes)

Use this prompt directly in your image generation tool:

---

Create a **16:9 research presentation slide graphic** (1920x1080, white background) in a **clean ACM/IEEE defense style**.

## Design goal
A single figure for Slide 2 titled **"Scenario Overview and Evaluation Axes"** that clearly shows:
1) all four scenarios (A1, A2, B1, B2), and
2) the four evaluation axes used consistently across scenarios.

## Visual style constraints (must follow)
- Minimal, academic, no decorative 3D effects.
- Flat vector style, thin clean lines, high readability.
- Font style similar to Helvetica/Arial/Source Sans Pro.
- Professional hierarchy: title, subtitle, section labels, concise bullets.
- Use low-saturation palette only:
  - A1 color: #7e8cad
  - A2 color: #a5c2cd
  - B1 color: #e19d92
  - B2 color: #eac47c
  - neutral blocks: #dbc0af, #c4c9c2, #dadae4
- Gridline/accent gray: #eaeaea.
- Do not use neon colors.

## Layout structure
- Top title area (full width):
  - Main title: "Scenario Overview and Evaluation Axes"
  - Subtitle: "Four Scenarios, One Unified Comparison Framework"

- Main body split into two columns:

### Left column (about 60% width): "Scenario Map (2x2)"
Create a 2x2 card grid with rounded rectangles:

Top-left card (A1, color #7e8cad):
- Header: "A1 — Reflective Facade Phantom Vehicle"
- Subtext: "False Positive Trajectory Commitment"

Top-right card (A2, color #a5c2cd):
- Header: "A2 — Transparent Garage Door"
- Subtext: "False Free-Space Commitment"

Bottom-left card (B1, color #e19d92):
- Header: "B1 — Reversible-Lane Signal Misread"
- Subtext: "Lane Attribution Error at Entrance"

Bottom-right card (B2, color #eac47c):
- Header: "B2 — Reversible-Lane Transition Conflict"
- Subtext: "Mode Oscillation and Deadlock"

Add a tiny legend under this 2x2 map:
- "Part A: A1/A2 (glass/reflection)"
- "Part B: B1/B2 (reversible-lane control)"

### Right column (about 40% width): "Evaluation Axes" (must be shown as real axes)
Draw **4 horizontal axis rails** (not text cards), each with:
- left endpoint circle + label (baseline side),
- right endpoint circle + label (advanced/mitigated side),
- arrow from left to right,
- small center tick labeled \"comparison focus\".

Axis 1 (title above rail): **Architecture Axis**  
Left endpoint label: `Camera-only`  
Right endpoint label: `Multi-sensor`

Axis 2 (title above rail): **Failure-Chain Axis**  
Left endpoint label: `Perception / Rule Interpretation`  
Right endpoint label: `Planning / Control Consequence`  
Center tick text: `Prediction Prior`

Axis 3 (title above rail): **Safety-Metric Axis**  
Left endpoint label: `Primary Safety Metrics`  
Right endpoint label: `Safety-Efficiency Tradeoff`  
Small metric chips near this rail: `PBS`, `EVR`, `Collision`, `Travel Time`

Axis 4 (title above rail): **Mitigation Axis**  
Left endpoint label: `Permissive Baseline`  
Right endpoint label: `Contradiction-Aware Mitigation`

Use neutral background panel (#f7f7f7 or #c4c9c2 with low alpha) behind these 4 rails.
Use consistent line color (#9b8e95), arrowheads, and thin tick marks for all axes.
This panel must visually read as an \"axes framework,\" not a bullet list.

## Bottom footer strip (small text)
Add one compact proposal-alignment sentence:
"Aligned with proposal requirements: architecture comparison, failure-chain analysis, simulation evidence, and mitigation validation."

## Typographic requirements
- Title: bold, large.
- Section headers: semi-bold.
- Body text: concise, no paragraph blocks.
- Keep everything readable at projected size.

## Output requirements
- Return one final PNG image (1920x1080).
- Leave enough margins for slide software cropping.
- No watermark, no logo, no extra decorative icons unless subtle and technical.
- Ensure the right panel clearly contains 4 axis lines with endpoints and arrows.

---

Optional variant request:
"Also generate a grayscale-safe variant where cards differ by line pattern in addition to color for accessibility."
