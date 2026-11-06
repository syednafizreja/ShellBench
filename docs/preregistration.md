# Preregistration: hypotheses H1-H4

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

This file holds the four hypotheses of ShellBench, the analysis that will test each one, and, at the end of the project, the verdict on each. The hypotheses below are frozen. They are copied word for word from the ShellBench Project Charter (amended 22 Oct 2026, p. 11, "Hypotheses (frozen; never reworded)") and must never be reworded. Each verdict will be reported as it comes out, including any hypothesis that fails.

## Status

| Part | What it holds | Status |
|---|---|---|
| 1. Hypotheses | H1-H4, verbatim | Committed 25 Oct 2026, before any family result exists |
| 2. Analysis plan | Variables, comparisons and decision rules for each hypothesis | Approved by the author on 3 Nov 2026 (charter date "Hypotheses committed"), before any family row, pilot run or surrogate run |
| 3. Verdicts | One verdict per hypothesis, with the result files behind it | After Week 5 (H1-H3) and Week 7 (H4) |

The hypotheses were committed ahead of the 3 Nov date so that the public record of their wording is as early as possible. No family result, pilot run or surrogate run existed when they were committed: the repository at this point holds only the anchor building under gravity load (Days 5-6). Git history gives the timestamp.

## 1. Hypotheses (frozen)

**H1:** The whole-building saving is smaller than the floor-level saving but stays positive across the family.

**H2:** The saving grows with seismic intensity and storey count, because mass reductions compound into a smaller lateral system.

**H3:** Without a topping, the shell floor cannot be assumed to act as a rigid diaphragm. The topping it needs takes back a measurable share of the saving.

**H4:** Surrogate error on unseen storey counts is clearly larger than on random test splits. Conformal intervals restore the stated coverage, and the surrogate's choice of floor system agrees with the full analysis in most cases.

## 2. Analysis plan

**Approved by the author, 3 Nov 2026 (Day 17 gate closed).** Claude drafted this plan before any family row, pilot run or surrogate run existed, and the author approved all of it, including every threshold marked [J], on the same day. Any later change goes in the change log (2.0, "Changes"). The research question and the Option A design fixes it follows are in [research_question.md](research_question.md). Thresholds marked [J] were proposed by Claude and approved by the author.

### 2.0 Rules for all four hypotheses

- **Boundary.** A1-A3 embodied carbon under EN 15978, with the factor set in `carbon.py`, in kgCO2e per m² of floor area and in total per building.
- **Family.** Every building the generator produces from the frozen family definition: storey counts 3-8, PGA 0.05, 0.10, 0.15, 0.20, 0.30 and 0.40 g, and the floor variants of the floor library. A building whose conventional or shell design fails a code check is reported and counted, never dropped quietly.
- **Two baselines.** The primary baseline is the lowest-carbon code-compliant conventional floor for the same grid, storey height, storey count and PGA. The secondary baseline is the anchor floor as built (120 mm slab on secondary beams). Each verdict is given against the primary baseline. The secondary result is reported beside it.
- **Shell variant used.** For the verdicts, each building uses its lowest-carbon shell variant that passes every check, including the topping needed for a rigid diaphragm (H3). Results for every variant (rise, thickness, levelling option, topping) are reported as well, so a reader can see the whole spread, including the fill-to-crown cases that floor_concept §6 shows may save nothing.
- **Verdict words.** Each hypothesis gets one of three verdicts: *supported*, *partly supported* or *not supported*. The verdict is reported whatever it is.
- **Changes.** Any change to this plan after the first family row is listed in section 3, with its date and reason, and the result is shown both ways.

### 2.1 H1: whole-building against floor-level saving

- **Measured.** For each building: the floor-level saving S_f = (C_floor,conv − C_floor,shell) / C_floor,conv, and the whole-building saving S_b = (C_bldg,conv − C_bldg,shell) / C_bldg,conv. C_floor covers the floor elements (slab or vault, ties, fill, topping, secondary beams). C_bldg covers every element in the take-off.
- **Comparison.** S_b against S_f in the same building, and the sign of S_b.
- **Verdict rule [J].** *Supported* if S_b < S_f and S_b > 0 in every building of the family. *Partly supported* if S_b > 0 in at least 90 % of buildings. *Not supported* otherwise. The share of buildings with S_b > 0, and the minimum, median and maximum of S_b, are reported in every case.

### 2.2 H2: trend with seismic intensity and storey count

- **Measured.** S_b, and the absolute whole-building saving per m² of floor, for each building. To test the stated mechanism, the change in carbon of the lateral system (columns and frame beams) between the conventional and the shell design is also measured.
- **Comparison.** Spearman rank correlation of S_b with PGA at each fixed storey count, and with storey count at each fixed PGA. Significance comes from a permutation test (10 000 permutations, two-sided, α = 0.05) [J].
- **Verdict rule [J].** *Supported* if the correlation is positive and significant for both PGA and storey count in most (more than half) of the fixed slices, and the lateral-system saving also grows with PGA. *Partly supported* if this holds for only one of PGA or storey count. *Not supported* otherwise, including when the trend is negative. floor_concept §6 records that a heavy fill can reverse H2. If it does, the result is reported as found.

### 2.3 H3: diaphragm and topping

- **Measured.** For each building's shell floor with no topping: whether the floor passes the rigid-diaphragm rule. Then the minimum topping (0, 40, 50 or 60 mm) that passes it, and the topping's share of the saving, R = (S_b,no topping − S_b,min topping) / S_b,no topping.
- **Rule for "rigid".** The GB 50011 / JGJ 3 criterion. Its clause is still [?] (floor_concept §8, item 6) and must be fixed before Day 27. If the code gives no numerical rule, the default is: the floor's largest in-plane deformation is no more than twice the mean storey drift of the vertical elements below it [J; this is the usual definition of a flexible diaphragm in US practice, to be confirmed against a source before use].
- **Verdict rule [J].** *Supported* if the untopped floor fails the rule in more than half of the buildings and the median R is at least 5 %. *Partly supported* if only one of these holds. *Not supported* otherwise.

### 2.4 H4: surrogate

The pipeline follows schedule.md (Track B, Days 43-47). Its code and hyperparameters are frozen and committed before the dataset DOI, and it runs once on the published data.

- **Splits.** (a) Random split. (b) Unseen storey counts: whole storey counts are held out, so no building with a test storey count is in training.
- **Measured.** RMSE and MAE of the whole-building carbon of each of the three models on each split. Empirical coverage of split-conformal intervals at a nominal 90 % on the unseen-storey split. Agreement between the floor system the surrogate picks (lower predicted carbon) and the one the full analysis picks.
- **Verdict rule [J].** *Supported* if, for the best model on the random split, its RMSE on unseen storeys is at least 1.5 times its random-split RMSE, the conformal coverage on unseen storeys is between 88 % and 92 %, and the floor-system choice agrees in at least 80 % of test buildings. *Partly supported* if one or two of the three hold. *Not supported* if none holds. The leakage test (schedule, Day 46) must pass before any H4 verdict is given.

### 2.5 Author items (approved 3 Nov 2026)

1. The thresholds marked [J]: "every building" and 90 % (H1), the permutation test and "more than half of slices" (H2), the 5 % and the default rigidity rule (H3), and 1.5×, 88-92 % and 80 % (H4). Approved.
2. The H1 population: each building's best shell variant, with all variants reported. Approved.
3. The GB 50011 / JGJ 3 rigid-diaphragm clause (H3). Approved as written: the default rule applies unless a numerical clause is found before Day 27. Its source is still to be confirmed.

## 3. Verdicts

None yet.

### Change log

**C1, 6 Nov 2026 (author's decision 3, Paper 1 review panel finding P4): carbon-factor sensitivity added.**

- *What.* A one-at-a-time sensitivity on the carbon factors. Each bound is run alone, with every other factor at its base value:
  - concrete: the C40 factor (340, the C30/C50 mean) set to the Table D.0.1 C30 row (295) and to the C50 row (385);
  - steel: every steel factor (reinforcing bar, mesh and tie steel) set to the Table D.0.1 converter carbon steel row (1990 kgCO2e/t) and to the electric-arc carbon steel row (3030 kgCO2e/t).
  All four values are rows already in data/carbon_factors.csv or in GB/T 51366-2019 Table D.0.1. No new source is used.
- *Reported.* For each bound: S_f and S_b per building (minimum, median, maximum), the share of buildings with S_b > 0, and whether any H1-H3 verdict would read differently.
- *What it is not.* It is a sensitivity, not an uncertainty band. The bounds are tabulated extremes, not a distribution. Every verdict is given with the base factors only (section 2.0). It replaces the "Monte Carlo band" named in anchor_notes D29 and anchor_report §5, which was never part of this plan.
- *Caveat [J].* The converter and electric-arc rows are crude-steel values without rolling, while the base bar factor (2340) is the hot-rolled bar row. As bounds for bar steel they bracket the base value but are not like-for-like. Paper 1 states this.
- *When.* Added after the conventional pilot rows (pre-release) and before any shell-family row, any S_f or S_b, or any DOI-data result existed. Git history gives the timestamp.

