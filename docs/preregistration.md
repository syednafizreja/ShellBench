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

**H1 to H3, run 13 Nov 2026 on the v0.4.0 files** (code `src/shellbench/verdicts.py`; results `results/verdicts_summary.csv`, `verdicts_buildings.csv`, `verdicts_slices.csv`; seed `provenance.SEED`; the rules of 2.1 to 2.3 applied as written). 33 of the 36 buildings are compared. The other three (s05-p040, s07-p040, s08-p040) have no `ok` conventional design (one failed, two are outside the code). Base carbon factors, every valid row, grade I included (2.0).

| Hypothesis | Verdict | The numbers behind it |
|---|---|---|
| H1 | **Partly supported** | S_b > 0 in 32 of 33 buildings (97.0 %), so the 90 % rule holds but "every building" does not. S_b is below S_f in 27 of 33. S_b: minimum -0.3 % (s05-p030), median 5.7 %, maximum 30.7 %. S_f: minimum -62.9 % (s07-p030), median 14.3 %, maximum 17.8 %. |
| H2 | **Not supported** | S_b against PGA is positive and significant in 0 of 6 storey-count slices; against storey count in 1 of 6 PGA slices (0.05 g). The lateral-system saving against PGA: 0 of 6. Median rank correlations are -0.14 for PGA and -0.14 for storeys. |
| H3 | **Not supported** | The untopped floor passes the rule in all 33 buildings (0 failures; 0 of 1180 untopped variants fail), so the minimum topping is 0 mm and R is 0 in every building. Neither condition of the rule holds. |

Sensitivities (C1 four factor bounds, C2 grade-I rows dropped): **no verdict changes in any of the five cases.** S_b > 0 in 32 (C30), 33 (C50), 32 (converter steel), 33 (electric-arc steel) of 33 buildings, and in 25 of the 26 buildings left when the grade-I rows are dropped. Median S_b ranges from 4.95 % to 6.24 % across the cases.

Reading, my judgement [J], for the author to confirm: the whole-building saving is small and positive in most buildings, with a median near 6 %. The floor-level saving is not a reliable guide to it, because the lateral system does not get lighter in the median (lateral-system saving: median -2.5 kgCO2e/m², range -5.3 to 83.2). The two largest S_b values (17.3 % at 7 storeys and 30.7 % at 8 storeys, both 0.30 g) are grade-I buildings whose conventional design has 1300 mm columns (850 mm at 6 storeys, 0.30 g). Change C2 explains the mechanism: the generator grows grade-I columns because no bar layout fits, so those two values may partly reflect a generator limit and not the floor [J]. Without the grade-I rows (7 buildings with an `ok` conventional design; C2 says 6 rows, a count to reconcile) the maximum S_b is 9.6 %. H3 is "not supported" for a reason that depends on the model: elastic, uncracked, fully bonded shell, transverse load only, and the largest ratio of deformation to limit is 0.011 (88 times margin). Paper 1 must state this and must not claim that thin-shell floors are rigid diaphragms in general.

Checked by Claude, 13 Nov 2026 [J]: every number in the table and in the sensitivity line above was compared with `results/verdicts_summary.csv` and `verdicts_slices.csv` (rounded as shown) and agrees; the one significant H2 slice is S_b against storeys at 0.05 g (rho 0.94, p 0.017). The lateral-system range (-5.3 to 83.2 kgCO2e/m²) and the grade-I S_b values (s07-p030 17.3 %, s08-p030 30.7 %) agree with `verdicts_buildings.csv`. Author to confirm.

**H4, run once on 13 Nov 2026 on the published data** (Zenodo 10.5281/zenodo.24194144; the family files in the repository are byte-identical to those in the zip, docs/dataset_release.md). Code `src/shellbench/ml/` as frozen at commit 5c11ce8 (`python -m shellbench.ml.conformal`, then `python -m shellbench.ml.decision`); no model, grid, split rule or threshold changed. Results: `results/surrogate_accuracy.csv`, `surrogate_coverage.csv`, `surrogate_leakage.csv`, `surrogate_decision.csv`, `surrogate_decision_summary.csv`. The leakage test passed first: 36 of 36 checks on the unseen-storeys split. Best model on the random split: gradient boosting (HGB).

| Hypothesis | Verdict | The numbers behind it |
|---|---|---|
| H4 | **Partly supported** (two of three conditions hold) | (1) Error ratio: RMSE of whole-building carbon 25.62 kgCO2e/m² on unseen storey counts against 11.30 on the random split, ratio 2.27 (needs at least 1.5): **holds**. (2) Conformal coverage on unseen storey counts, pooled: 73.3 % (needs 88 to 92 %): **fails**; by held-out storey count it runs from 56.1 % (7 storeys) to 87.1 % (6 storeys), and on the random split it is 90.1 %. (3) Floor-system choice agrees with the full analysis in 31 of 33 buildings, 93.9 % (needs 80 %): **holds**. |

Reading, my judgement [J], for the author to confirm: the surrogate is much worse on storey counts it has not seen, so the first half of H4 is supported. Conformal intervals do not restore the stated coverage there, because the calibration rows come from storey counts the model was trained on (docs/surrogate_notes.md, "When it fails"). The 93.9 % agreement is below the 97.0 % reached by always choosing the shell, and the full analysis picks the slab in one building only (s05-p030, saving -0.3 %). One of the two disagreements is a near tie (under 1 % saving). The surrogate picks the same shell variant as the full analysis in 5 of 33 buildings (15 %), with mean regret 5.5 kgCO2e/m² (3.7 % of the best shell carbon). Paper 2 must report the baseline next to the agreement and must not call 93.9 % evidence that the surrogate decides well. The numbers are the same as in the pre-release reading, as expected: the family files differ only in the `release` and `shellbench_version` columns.

Checked by Claude, 13 Nov 2026 [J]: the ratio, the coverage figures and the agreement were read from `surrogate_accuracy.csv`, `surrogate_coverage.csv` and `surrogate_decision_summary.csv` after the run. The three result CSVs were byte-identical to the committed pre-release files (the pipeline is deterministic). Author to confirm.

Transparency note on timing (change C3 below): these verdicts were run on the committed v0.4.0 family files before the Zenodo record exists.

Transparency note (6 Nov 2026, before any verdict). R14 capacity design was added to the generator after the plan was approved (design_rules.md R14). The analysis plan is unchanged, but the design rules that make the family rows changed:
- R14 sizes the column bars and the frame stirrups.
- R13 counts compression steel at grade I-II beam ends.
- Column steel (`bar_steel_kg_per_m2`) changes in every scope, including `frame_strip_v1`.
- Frame stirrups enter `building_v2` only.
The Day 19 pilot files were made without R14 and are kept as they are. `generate(..., capacity_design=False)` reproduces them. Results for H1-H4 use the R14 rows (results/family_rc_r14_building_v2.*).

### Change log

**C1, 6 Nov 2026 (author's decision 3, Paper 1 review panel finding P4): carbon-factor sensitivity added.**

- *What.* A one-at-a-time sensitivity on the carbon factors. Each bound is run alone, with every other factor at its base value:
  - concrete: the C40 factor (340, the C30/C50 mean) set to the Table D.0.1 C30 row (295) and to the C50 row (385);
  - steel: every steel factor (reinforcing bar, mesh and tie steel) set to the Table D.0.1 converter carbon steel row (1990 kgCO2e/t) and to the electric-arc carbon steel row (3030 kgCO2e/t).
  All four values are rows already in data/carbon_factors.csv or in GB/T 51366-2019 Table D.0.1. No new source is used.
- *Reported.* For each bound: S_f and S_b per building (minimum, median, maximum), the share of buildings with S_b > 0, and whether any H1-H3 verdict would read differently.
- *What it is not.* It is a sensitivity, not an uncertainty band. The bounds are tabulated extremes, not a distribution. Every verdict is given with the base factors only (section 2.0). It replaces the "Monte Carlo band" named in anchor_notes D29 and anchor_report §5, which was never part of this plan.
- *Caveat [J].* The converter and electric-arc rows are crude-steel values without rolling, while the base bar factor (2340) is the hot-rolled bar row. As bounds for bar steel they bracket the base value but are not like-for-like. Paper 1 states this.
- *When.* Added after the conventional pilot and the R14 conventional family rows (both pre-release) and before any shell-family row, any S_f or S_b, or any DOI-data result existed. Git history gives the timestamp.

**C2, 7 Nov 2026 (direction review P1; author's decision A, then Claude's choice [J] under the author's 7 Nov rule to take the recommended option): grade-I rows.**

- *What changed in the generator.* At grade I the strong-column check now uses 1.2 ΣM_bua, the actual flexural capacity of the beams (GB 50011 cl. 6.2.2), and no longer η_c = 1.7 times the analysis moments. M_bua uses f_yk and the bars actually chosen, without the slab bars [J]. Beam growth keeps cl. 6.3.1 (h/b ≤ 4, clear span/h ≥ 4).
- *Result.* The grade-I rows hardly moved (largest change 0.3 kgCO2e/m²). s07-p030 still has 1750 mm columns. Its history shows why: the column grows because no bar layout fits the magnified moments (cl. 9.3.1, 11.4.13), after the beams have grown deep for shear. The strong-column factor is not the driver.
- *Choice [J].* The primary analysis stays as approved: every valid row, grade I included. A sensitivity case drops the grade-I rows (6 ok rows at 0.20-0.40 g), and every H1-H3 verdict is shown both ways (section 2.0, "Changes"). Excluding them from the primary analysis would drop rows because of their result, which the plan forbids.
- *Why the grade-I rows are flagged.* The bar-layout growth is a generator limitation (one bar set for all columns; no beam redesign to cut the demand) [J]. Paper 1 Methods states it and lists the grade-I rows.
- *When.* Before any shell-family row, S_f, S_b or DOI-data result.
- *Count, corrected 13 Nov 2026 (checked by Claude from git) [J].* "6 ok rows" was right when C2 was written (commit ea58baa): s08-p030 had failed. The Day 21 rerun the same day (commit 3f925b5, 36 and 40 mm column bars) made it converge, so the v0.4.0 file has 7 ok grade-I rows (7 and 8 storeys at 0.20 and 0.30 g; 3, 4 and 6 storeys at 0.40 g). The drop-grade-I case therefore removes 7 of the 33 compared buildings (26 left), as section 3 reports. The same rerun cut s07-p030's columns from 1750 to 1300 mm. Nothing in the rule or the analysis changes. Author to confirm.

**C3, 13 Nov 2026 (schedule.md slip rule, no change to any rule): verdicts run on the v0.4.0 files before the dataset DOI exists.**

- *What.* Section 2.4 and the schedule say the verdicts run on the published dataset. The Zenodo record was not published by 13 Nov (it waits on the author's Zenodo token). schedule.md ("If the dataset DOI slips past 12 Nov") says the H1-H3 verdicts and the Paper 1 figures still come before the check window. I ran H1-H3 on the family files committed at tag v0.4.0.
- *Why this is the same data.* The files in the dataset zip are byte-identical to those committed at v0.4.0 (docs/dataset_release.md; checked by VS Code Claude on 11 Nov). Only the DOI is missing, not any byte. The pre-release run and the v0.4.0 files differ only in the columns `release` and `shellbench_version`.
- *Not changed.* No threshold, rule, hypothesis wording, factor or row. The rules are applied as written in 2.1-2.3 and C1-C2. Two details the plan left open are marked [J] in `verdicts.py`: slices with fewer than 4 buildings count as not significant, and "the lateral-system saving also grows with PGA" uses the same rule as S_b.
- *When.* After the dataset files were final (11 Nov) and before any Paper 1 text uses a result.
