# Charts

Original figures pulled from the three published studies live in `original/`; their
warm-palette cartoon versions (made by `make_cartoon.py`, composited into scenes by
`../images/integrate_charts.py`) live in `cartoon/`. Kept here as reference material
for the storybook. The storybook does not need to reproduce these exactly; it should convey
their basic message in a friendlier, painterly form. These are the source of truth for the
numbers and shapes the illustrations should echo.

Sources (paper directories in the private `papers` repo):
- Study 1: `2024-sc-adoption-erl/figures/`
- Study 2: `2025-grid-peak-shaving/eris/figs/`
- Study 3: `2025-surveydown-plos-one/figs/`

| Chart file | What it shows | Source | Story spread(s) |
|---|---|---|---|
| `study1-choice-question.png` | A real choice-experiment question: Option 1 vs Option 2 vs "Not Interested," with cash, override, and battery-threshold attributes. What a respondent actually saw. | S1 figure-1 | 07 (the choice experiment) |
| `study1-attribute-sensitivity.png` | Enrollment-rate sensitivity curves for every SMC and V2G attribute. Guaranteed Threshold is steep (matters a lot); Minimum Threshold is flat (matters little); V2G is more money-sensitive. | S1 figure-3 | 09, 10 (what each program needs) |
| `study1-enrollment-scenarios.png` | Bar chart of enrollment under Flexibility / Recurring Cash / One-time Cash scenarios. Headline: SMC flexibility alone reaches ~75%; V2G is driven harder by money (e.g. 77% at $20/4 events). | S1 figure-4 | 09, 10 (the headline findings) |
| `study2-caiso-peak-shaving.png` | CAISO daily load, 0% vs 100% SMC. The evening peak is shaved and charging slides into the overnight valley; note the green line rising after midnight, the new overnight bump from over-shifting. | S2 fig-1-caiso-avg | 13 (moving the mountain), 15 (the twist) |
| `study2-nyiso-peak-shaving.png` | NYISO daily load, 0% vs 100% SMC. Same idea, smaller and flatter than CAISO. Good for the region comparison. | S2 fig-1-nyiso-avg | 16 (place matters) |
| `study2-enrollment-vs-incentive.png` | The enrollment curve: ~30% enroll for free, ~60% at $20/month, 100% only at ~$85/month. Concave, the root of diminishing returns. | S2 fig-9-smc-monthly-incentive | 12 (borrow the answers), 14 (why the bill grows) |
| `study2-cost-efficiency.png` | CAISO cost-efficiency frontier with 30% / 50% / 100% markers across least, average, and most favorable days. Sharp diminishing returns past the moderate range. | S2 fig-4-caiso-efficiency-extreme | 14, 15 (enough, not everybody) |
| `study3-tech-stack.png` | surveydown's four building blocks: surveydown control logic, Quarto (survey design), Shiny (web framework), PostgreSQL (data storage). | S3 Fig 1 | 18 (meet surveydown) |
| `study3-survey-example.png` | A rendered surveydown page ("Welcome to our survey!" with a multiple-choice question and a Next button). What a finished survey looks like. | S3 Fig 2A | 18, 19 (plain text becomes a real survey) |
| `study3-how-it-works.png` | The logic-flow diagram: the designer edits plain-text `survey.qmd` + `app.R`, which render and serve the live survey and store responses in PostgreSQL. | S3 Fig 3 | 19 (why plain text is wonderful) |

## Notes

- These are reference figures, not final storybook art. When we lift the image hold, the
  scene illustrations should *echo* the key shape or number from the relevant chart (the
  shaved peak, the concave curve, the four hexagons) in the warm storybook style, not paste
  the chart in. If a literal chart is ever wanted on a spread, these files are ready to drop in.
- More figures are available in the source folders if a beat needs them (e.g. seasonal
  efficiency frontiers in S2, the surveydown logic map and interactive-map example in S3).
