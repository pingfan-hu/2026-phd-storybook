# Source Facts — Ground Truth for the Storybook

Every number and claim in the storybook must trace back to this file, which is distilled
from `2026-phd-defense/paper.qmd`. If the story and this file disagree, this file wins.

The dissertation is one connected arc:
**consumer preference (Study 1) → grid value + economics (Study 2) → the open tool that
made the research possible (Study 3).**

---

## The shared setup (the "why")

- Electric cars (battery electric vehicles, BEVs) cut transportation emissions, but the
  climate benefit depends on **when** they charge.
- Left alone, people charge when they get home in the evening. Unmanaged BEV charging
  piles onto the existing **evening peak** (~6–9 PM), straining the grid and sometimes
  firing up dirtier "peaker" plants.
- The fix is **smart charging**: coordinate charging so it moves off the peak. The
  overnight hours have a demand **valley** with room to absorb it.

---

## Study 1 — Measuring BEV owners' willingness to participate
(Chapter 2; published in *Environmental Research Letters*)

**The question:** Will BEV owners actually opt in to smart charging, and under what terms?

**Two smart charging techniques studied:**
- **Supplier-Managed Charging (SMC):** the utility controls the *timing* of charging but
  guarantees the car is charged by a set time.
- **Vehicle-to-Grid (V2G):** the car also sends power *back* to the grid (bidirectional);
  a bigger ask, with battery-wear concerns.

**Who was asked (the differentiator):** **1,356 current, real BEV owners** in the U.S.,
not the general car-owning public. Prior studies mostly sampled people with little or no
BEV experience. A model-year screener (BEVs were only 4.4% of options, 77 of 1,748 models)
made it very unlikely non-owners slipped through.
- 1,356 completed the SMC section; 682 completed the optional V2G section.
- Recruited via Meta ads (803) and Dynata (553), 2024.
- Sample skews male (73%), wealthier, older; 83% live in detached single-family homes;
  93% charge at home.

**Method:** a discrete choice experiment (people pick option A, option B, or "not
interested"), 6 SMC questions then 6 V2G questions. Attributes varied: one-time
*Enrollment Cash*, *Monthly Cash* (SMC) / *Occurrence Cash* (V2G), override/occurrence
flexibility, and battery thresholds (minimum, guaranteed, lower). Modeled with logit.

**Key findings:**
- **SMC people value flexibility + modest recurring payments.** Offering only flexibility
  (guaranteed thresholds + override options) with **no money** still reaches **at least
  50% enrollment**.
- **V2G people are more sensitive to money**, reflecting the bigger, more active ask.
  High occurrence pay ($20/event, 4 events/month) reaches 82% enrollment.
- **Recurring beats one-time:** a small **$2–$3/month** payment moves enrollment as much
  as **$65 (SMC)** or **$46 (V2G)** of one-time cash. Roughly a 20-to-1 ratio.
- For SMC, the **guaranteed** end-of-charge threshold matters far more than the minimum
  (range certainty is what people care about).
- **Deliverable:** an interactive enrollment simulator for utilities/policymakers:
  https://gwuvehicle.shinyapps.io/enrollment_simulator/
- Code/data: https://github.com/jhelvy/smart-charging-preferences-2025

---

## Study 2 — Peak-shaving potential AND cost efficiency (the economy)
(Chapter 3; submitted to *Joule*, Cell Press)

**The question (extends Study 1):** If people enroll, does smart charging actually shave
the peak, and **does the money make sense**? This study's heart is the **economics**, not
just the engineering.

**The move:** take the **real enrollment curves from Study 1** and feed them into a
grid simulation. Compare two structurally contrasting grids:
- **CAISO (California):** solar-heavy, deep midday and overnight valleys, steep evening
  ramp ("duck curve"). 7.69 million detached single-family households.
- **NYISO (New York):** flatter profile, no solar valley, cold winters with heating load.
  3.16 million such households.

**How it works:** shift BEV charging from the evening "normal" window into the overnight
"valley" window, protecting drivers' state-of-charge and next-day travel. Swept five
time-of-use windows, BEV adoption levels, seasons, and 0%–100% enrollment. The 11 PM
valley start performed best. Unmanaged charging peaks at 7 PM.

**Peak-shaving findings:**
- **CAISO:** annual-average peak shaved **3.7 GW (12.1%)**; up to **5.6 GW** on the most
  favorable day (Feb 23).
- **NYISO:** annual-average **1.6 GW (7.5%)**; up to 2.4 GW best day. Smaller, because
  fewer households and lower daily variability.

**The economics (the core of this study):**
- Utilities pay enrollees a monthly incentive. The enrollment-to-incentive curve is
  **concave**: ~**30% enroll for free**; **$20/month → ~60%**; reaching **100% costs
  ~$85/month per household**.
- Because every enrollee gets the **same** payment, total cost scales **non-linearly**.
  Each extra percentage point of enrollment is disproportionately expensive.
- **Diminishing returns:** **moderate 30–50% enrollment captures most of the achievable
  peak reduction at a fraction of the cost** of near-full enrollment.
- **The twist:** pushing enrollment too high backfires. On ~**15% of CAISO days**,
  over-enrollment concentrates charging and **reconstitutes a new overnight peak**.
- **Region/season:** cost efficiency is **season-invariant in CAISO** (solar keeps the
  valley wide year-round) but **deteriorates in NYISO winters** (space heating fills the
  overnight valley, leaving less room to shift charging into).
- Real-world pilots (PCE, MCE Sync) sit at only **4–10% enrollment** today, i.e. the
  cheap left-hand part of the curve, well below the 30–50% sweet spot.

**Takeaway:** smart charging works and can pay off, but **moderate, region-tuned
enrollment** is the smart target. More is not better.
- Code/data: https://github.com/pingfan-hu/2025-grid-peak-shaving-public

---

## Study 3 — surveydown: a free, open-source survey tool
(Chapter 4; published in *PLOS ONE*)

**The need:** doing rigorous surveys (like the 1,356-owner study) meant fighting survey
platforms that were clunky, expensive (Qualtrics), or not reproducible (Google Forms).
So the team built their own.

**What it is:** **surveydown**, an **open-source, text-based** survey platform in the R
language. You write the survey as **plain text (markdown + R code)** instead of clicking
through a GUI. Built on three mature open-source technologies:
- **Quarto** for the survey document, **Shiny** for the interactive web app, **PostgreSQL**
  for data storage. The `surveydown` R package ties them together.

**Why it's different / better:**
- **Reproducible & version-controlled:** the whole survey lives in plain-text files you can
  track in Git and share without proprietary software.
- **Programmable:** real code runs during the survey, enabling skip logic, conditional
  display, reactive questions, and complex randomization.
- **You own your data:** a disaggregated design separates the survey app, the hosting, and
  the data store, so researchers keep full control (e.g. their own Supabase/PostgreSQL).
- **Free & open:** on **CRAN** under an **MIT license**; install with
  `install.packages("surveydown")`.

**Who it's for:** the team itself (it was the instrument behind Study 1) **and any other
research team** that wants free, reproducible, programmable surveys, across social science,
public health, economics, education, policy, and beyond. Basic R knowledge is enough.

**Adoption (at time of writing):** 118 GitHub stars, 38 issues addressed, 52 discussions,
**3,703 CRAN downloads**, contributor-added six-language support. A companion GUI tool,
**sdstudio**, is in development to lower the entry barrier while keeping reproducibility.
- Site: https://surveydown.org

---

## How the three connect (the spine)

1. **Study 1** asks people: *will you join, and on what terms?* → real enrollment behavior.
2. **Study 2** uses that to ask the grid and the wallet: *does it shave the peak, and is it
   worth the money?* → moderate, region-tuned enrollment wins.
3. **Study 3** is the open tool that made asking 1,356 people rigorously possible, and gives
   the same power to everyone else.

Together: design smart charging around how consumers actually behave, implement it to fit
the local grid and economics, and keep the research tools open so others can build on it.
