# Figure/Legend and Table Style Guide (IEEE/ACM)

## 1. Scope

This guide defines a unified visual style for the course project report and slides, with emphasis on:
- low-saturation figures,
- consistent legend semantics across A1/A2/B1/B2,
- IEEE/ACM-compliant table formatting.

Use this guide for all charts in Sections 1.4–1.6 and appendix visuals.

---

## 2. Approved Low-Saturation Palette

Use only the following colors unless there is a strong reason to add one more neutral gray.

| Color ID | HEX | RGB | Recommended Use |
|---|---|---|---|
| C1 | `#e19d92` | (225, 157, 146) | B1 primary, warning bars |
| C2 | `#eac47c` | (234, 196, 124) | B2 primary, transition markers |
| C3 | `#dbc0af` | (219, 192, 175) | secondary fill, grouped box background |
| C4 | `#c4c9c2` | (196, 201, 194) | neutral background blocks |
| C5 | `#7e8cad` | (126, 140, 173) | A1 primary curve/bar |
| C6 | `#a5c2cd` | (165, 194, 205) | A2 primary curve/bar |
| C7 | `#dadae4` | (218, 218, 228) | uncertainty bands / CI area |
| C8 | `#9b8e95` | (155, 142, 149) | baseline / reference / ablation |

### Fixed Scenario Color Mapping

- `A1` -> `C5` (`#7e8cad`)
- `A2` -> `C6` (`#a5c2cd`)
- `B1` -> `C1` (`#e19d92`)
- `B2` -> `C2` (`#eac47c`)

Do not remap scenario colors between figures.

---

## 3. Figure and Legend Rules

## 3.1 Core Figure Style

- Prefer white background (`#ffffff`) and light grid (`#eaeaea`).
- Use line width `1.4–1.8 pt`; marker size `4–5 pt`.
- Use font size `8–9 pt` for axis/legend in double-column figures.
- Keep axis labels short and include units (e.g., `Peak decel (m/s^2)`).
- For uncertainty, use shaded area with `C7` and alpha `0.25–0.35`.

## 3.2 Legend Style

- Legend position: upper-right inside plot unless data overlap; then move outside-right.
- Legend order must be consistent: `Baseline -> Mitigation-1 -> Mitigation-2`.
- Use sentence case labels; avoid abbreviations without first definition.
- Do not encode meaning by color only: pair color with line style/marker.
  - Example: Baseline `solid + circle`, Mitigation `dash + square`.

## 3.3 Visual Consistency Constraints

- For any cross-scenario comparison figure, show all four scenario colors in fixed mapping.
- If figure includes fewer than four scenarios, keep unused colors reserved (do not repurpose).
- Avoid highly saturated red/green to reduce perceptual bias and color-vision issues.

---

## 4. IEEE/ACM Table Formatting Rules

## 4.1 Structure

- Table caption is above table (`TABLE I`, `TABLE II`, ... for IEEE style).
- No vertical lines.
- Use minimal horizontal rules (top/header/bottom only).
- Header text should include units where applicable.
- Numerical columns should be right-aligned; decimal precision consistent by column.

## 4.2 Width and Placement

- Prefer single-column table if readable.
- Use two-column (`table*`) only when necessary.
- Break wide content into two smaller tables instead of shrinking font below readability.

## 4.3 Content Style

- Keep metric names consistent with main text.
- Define abbreviations in caption or footnote at first use.
- Report central value and variability when available (e.g., mean ± std).
- Highlight best values conservatively (bold only; avoid color in print tables).

---

## 5. Ready-to-Use LaTeX Table Template (IEEE/ACM Friendly)

```latex
\begin{table}[t]
\caption{Baseline vs mitigation results across four scenarios.}
\label{tab:main_results}
\centering
\begin{tabular}{lcccc}
\toprule
Scenario & False Brakes (/100) & Min TTC (s) & Peak Decel (m/s$^2$) & Collision Rate (\%) \\
\midrule
A1 & 12.4 & 1.18 & 5.6 & 0.0 \\
A2 & 0.8 & 2.41 & 2.1 & 4.0 \\
B1 & 3.2 & 1.36 & 4.2 & 1.0 \\
B2 & 1.9 & 1.52 & 3.8 & 0.0 \\
\bottomrule
\end{tabular}
\end{table}
```

Notes:
- Uses `booktabs` style (`\toprule`, `\midrule`, `\bottomrule`).
- If your venue template disallows `booktabs`, keep the same structure with standard `\hline` but no vertical bars.

---

## 6. Recommended Matplotlib Color Dictionary

```python
PALETTE = {
    "A1": "#7e8cad",
    "A2": "#a5c2cd",
    "B1": "#e19d92",
    "B2": "#eac47c",
    "baseline": "#9b8e95",
    "uncertainty": "#dadae4",
    "bg_neutral_1": "#dbc0af",
    "bg_neutral_2": "#c4c9c2",
}
```

---

## 7. Checklist Before Final Export

- Scenario colors follow fixed mapping (A1/A2/B1/B2).
- Legend order is consistent and labels are unambiguous.
- Axis labels include units.
- Fonts and line widths remain readable in two-column PDF.
- Tables have caption-above, no vertical lines, consistent decimals.
- Figures/tables are understandable in grayscale print (line style or marker redundancy).

