# Anchor notes: why the model and the thesis differ

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

One line of explanation for every difference above 10 % between the anchor model and the thesis (Playbook Day 6). Dead load was added on Day 5 (23 Oct 2026); live load and the load combinations on Day 6 (24 Oct 2026).

Status: dead-load section **reviewed by the author on 23 Oct 2026** (decisions at the end of that section). Live-load and combination sections: **draft, Day 6, for the author to review**; every explanation there is [J] until then. Numbers come from files in `results/` (written by `src/shellbench/anchor_frame.py`) or are arithmetic on printed thesis values, with the table named.

Sign convention: beam-end moments are clockwise positive on the member end, as in the thesis. Column axial forces are positive in compression.

## Dead load (Day 5)

### How the thesis applies dead load

The thesis gives the dead load three times, and the three do not agree at roof level:

| Where | Roof AB | Roof BC | Floors AB | Floors BC | Used for |
|---|---|---|---|---|---|
| Fig. 4-4 (actual shapes) | trapezoid 15.21 + beam 3.61 | triangle 13.94 + beam 3.274 | trapezoid 14.58 + beam 3.61 | triangle 13.36 + beam 3.274 | Drawing only |
| Text under Fig. 4-5 | 17.15 | 10.23 | 23.43 | 10.96 | Beam shears (Tables 4-6, 4-7), so column axial forces |
| Fixed-end row of table 6.3 | 18.48 (from FEM 79.85) | 11.19 (from FEM 40.63) | 23.43 | 10.96 | Beam-end moments |

All values are kN/m. The roof values in the last row are back-calculated from the printed fixed-end moments (FEM × 12 / L²). They equal 13.55 + 4.934 and 7.92 + 3.274, the §5.1 slab loads plus the §4.1 beam weights [J]. The floor value 23.43 equals 12.99 + 4.934 + 5.51 (slab, beam, interior wall of §4.2) [J].

The model's primary run uses the last row, because those loads produced the moment targets. The other runs change one thing each:

| Run | What changes |
|---|---|
| `primary` | Loads behind the thesis fixed-end moments; eccentric moments at A and D only (as drawn in Fig. 4-4 and 4-5); columns axially flexible |
| `roof_text_loads` | Roof loads 17.15 and 10.23, as printed under Fig. 4-5 |
| `rigid_column_axial` | Columns made axially rigid, as the hand method assumes |
| `interior_moments` | Adds the eccentric moments at B and C (31.79, 38.09 kN·m) that the distribution table lists but the figures do not show |
| `actual_load_shape` | Trapezoid and triangle shapes of Fig. 4-4 instead of equivalent uniform loads |

All five runs satisfy vertical equilibrium: the base reactions equal the applied load (`results/anchor_gravity_dead_runs.csv`).

### Two checks on the thesis itself

**1. Joint balance in table 6.3.** The two-cycle moment distribution ends with a distribution step, so the final member-end moments at each joint must add up to the external joint moment. External moments here are −20.26 or −25.16 kN·m at A (anticlockwise) and 0 at B, as drawn.

| Joint | Sum of final member-end moments (table 6.3) | Should be | Out of balance |
|---|---|---|---|
| A4 | 50.74 − 67.76 = −17.02 | −20.26 | 3.2 |
| A3 | 37.01 + 37.01 − 96.15 = −22.13 | −25.16 | 3.0 |
| A2 | 37.01 + 37.01 − 97.64 = −23.62 | −25.16 | 1.5 |
| A1 | 17.48 + 1.35 − 97.12 = −78.29 | −25.16 | 53.1 |
| B4 | 68.77 − 52.84 − 67.74 = −51.81 | 0 | 51.8 |
| B3 | 90.82 − 40.95 − 42.18 − 46.88 = −39.19 | 0 (or −38.09 if the B moment was applied) | 39.2 (or 1.1) |
| B2 | 87.18 − 61.29 − 61.29 − 44.24 = −79.64 | 0 | 79.6 |
| B1 | 89.20 − 53.16 − 37.01 − 51.33 = −52.30 | 0 | 52.3 |

Joints A2 to A4 are nearly balanced. A1 and every B joint are not, so the thesis moments at those joints contain arithmetic or copying errors [J]. B3 balances only if the interior eccentric moment (38.09) was applied there, which suggests the table and the figures used different load sets.

**2. Running sums in Table 4-9.**
- Roof, B/C column: N_top = 214.11 + 61.88 = 275.99. The 61.88 is only the AB beam shear. The BC beam shear (33.75, Table 4-7) is missing. At floors 1-3, the same column includes both shears (e.g. 83.60 + 36.16 = 119.76).
- Floor 1, both columns: N_top is 9.46 kN (A/D) and 9.15 kN (B/C) higher than the running sum. For A/D, 810.69 + 167.77 + 85.44 = 1063.90, but 1073.36 is printed. The 9.46 equals 45.32 − 35.86, the difference between the ground and typical column weights. So the ground-storey column weight was probably added twice [J].
- Global check: the thesis base axial forces add up to 2 × (1118.68 + 1558.41) = 5354.18 kN. Its own loads (text roof values) add up to 5385.81 kN in the model. That is 31.6 kN short. Most of this is the missing roof BC shears (2 × 33.75 = 67.5) minus the floor-1 excess (2 × 9.46 + 2 × 9.15 = 37.2), which leaves 30.3; the last 1.3 kN is small rounding in the running sums [J].

### Differences above 10 % (primary run)

| Quantity | Thesis | Model | Diff | Likely cause | Type |
|---|---|---|---|---|---|
| M, floor 4, BC ends | ∓67.74 | ∓43.21 | 36 % | Joint B4 is out of balance by 51.8 kN·m in the thesis. The BC end equals the AB right end almost exactly (67.74 against 68.77), which a correct distribution would not give with fixed-end moments of 79.85 and 40.63. The B4 distribution factor printed for the right beam (0.373) also does not match the relative stiffnesses (about 0.174) | Possible mistake |
| M, floor 1, BC ends | ∓51.33 | ∓43.36 | 16 % | Joint B1 is out of balance by 52.3 kN·m in the thesis | Possible mistake |
| M, floor 3, AB left / CD right | −96.15 / 97.64 | −106.65 / 106.65 | 11 % / 9 % | Mostly axial shortening of the columns. The hand method ignores it, and with rigid columns the difference falls to 1.5 %. The CD value also has the copy error D1 | Method |
| M, floor 3, BC ends | ∓46.88 | ∓41.92 | 11 % | Joint B3 balances only with the interior moment applied; with it the difference is 7 %. The rest is axial shortening | Method (load set) |
| M, floor 4, AB left / CD right | ∓67.76 | ∓74.93 | 11 % | Axial shortening (3 % with rigid columns) | Method |
| N, floor 4, B/C top / bottom | 275.99 / 311.85 | 316.65 / 352.51 | 15 % / 13 % | The roof BC beam shear (33.75 kN) is missing from the thesis sum. With it, the thesis value would be 309.74 against 316.65 (2 %) | Mistake |

### Differences below 10 % worth knowing about

- **N, floor 1, A/D (−0.1 %).** The good match hides two effects that cancel: the thesis adds about 9.46 kN too much, and the model's roof shear is larger by 4.8 kN (18.48 against 17.15 kN/m).
- **N, B/C, floors 1-3 (2-6 %).** These carry the missing roof BC shear down the column.
- **M, AB right ends (1-5 %).** These look close, but with rigid columns they move to 8-13 %. Axial shortening and the unbalanced B joints happen to offset each other here. So the closeness is not evidence that either side is right.
- **Equivalent-load method.** Replacing the trapezoid and triangle with equivalent uniform loads gives the right fixed-end moments; the closed-form test in `tests/test_anchor_frame.py` confirms this. But the equivalent loads carry 19 % (trapezoid, α = 0.25) and 25 % (triangle) more total load than the shapes they replace [J]. That changes the beam shears and the column axial forces: the `actual_load_shape` run gives axial forces 2-4 % lower than the primary run. For the carbon model, the load path should use the actual shapes, not the equivalent loads.

### Decisions by the author (23 Oct 2026)

1. **Table 4-9 findings accepted.** They become flags D13 (roof BC shear missing at B/C) and D14 (ground-column weight counted twice at floor 1) in `validation/thesis_values/README.md`.
2. **Table 6.3 joint imbalance flagged.** This is D15. The author checked B4 by hand: 68.77 − 52.84 − 67.74 = −51.81 kN·m, not 0. So the 36 % on the roof BC moment is a thesis arithmetic error, not a modelling error.
3. **Load set:** the anchor keeps the table-6.3 loads (the `primary` run: roof 18.48 / 11.19 kN/m), because they generated the later force tables.
4. **Interior eccentric moments at B and C are left out**, as in Fig. 4-4 and 4-5. The `interior_moments` run stays only as a check. Note [J]: the B3 balance (−39.19 against 38.09) is the one sign that the table may have used them. The anchor report should mention it as a possible remaining cause at B3 only.

Still open: Fig. 4-4 labels the AB beam weight 3.61 kN/m, while the fixed-end moments use 4.934 kN/m (§4.1). This is consistent with decision B13, so no action is needed.


## Live load (Day 6)

Numbers in this section come from `results/anchor_gravity_live.csv`, `results/anchor_gravity_live_runs.csv`, `results/thesis_table_7_2_check.csv` and `results/thesis_table_7_2_joints.csv`, or are arithmetic on printed thesis values with the table named.

### How the thesis applies live load

As with the dead load, the thesis gives the live load more than once, and the versions do not agree:

| Where | Roof AB | Roof BC | Floors AB | Floors BC | Used for |
|---|---|---|---|---|---|
| §6.1 slab loads (actual shapes) | trapezoid 1.80 | triangle 3.3 | trapezoid 9.00 | triangle 19.80 | Drawing only |
| §6.1 equivalent loads | 1.60 | 2.06 | 8.08 | 12.37 | Beam shears, Tables 7-2 and 7-3 (roof BC uses 0.94) |
| Fixed-end row of table "7.2" (§7.1) | 1.60 (FEM 6.91) | 0.94 (FEM 3.41) | 6.41 (from FEM 27.70) | 0.97 (from FEM 3.52) | Beam-end moments |

All values are kN/m. The floor values in the last row are back-calculated from the printed fixed-end moments (q = 12 M / L²) [J]. The text under table "7.2" also says that beam BC "does not bear the live load", and Table 7-1 sets its span moment to 0, which matches neither 12.37 nor 0.97.

Two observations [J]:
- 6.41 = 2.0 × 3.6 × (1 − 2 × 0.25² + 0.25³), the office load of §3.2.2 (2.0 kN/m²), not the 2.5 kN/m² of §6.1. So the live **moment** targets correspond to the code office value, while the **shear and axial** targets correspond to 2.5 / 3.0 kN/m² (decision B3). This does not change B3, but the anchor report should say it.
- §6.1 converts the AB trapezoid with "(1 − 2 × 0.92² + 0.92³)", but the numbers only come out (1.80 → 1.60; 9.00 → 8.01) with α = 1.8 / 7.2 = 0.25. The joint-load line uses 8.01, the shear tables 8.08.

The model's primary run uses the fixed-end-moment loads, because they produced the moment targets; this is the same choice the author made for the dead load on Day 5. Joint loads are the printed §6.1 totals (9.82, 21.07, 45.03, 108.32 kN). Eccentric moments act at A and D only (1.47 and 5.89 kN·m, §7.1), following the Day 5 decision. The other runs change one thing each:

| Run | What changes |
|---|---|
| `primary` | Loads behind the table "7.2" fixed-end moments; moments at A and D only; columns axially flexible |
| `shear_loads` | Floor loads 8.08 and 12.37, as used for the shears |
| `rigid_column_axial` | Columns axially rigid, as the hand method assumes |
| `interior_moments` | Adds the moments at B and C printed in table "7.2" (3.16 roof, 15.64 floors) |
| `actual_load_shape` | Trapezoid and triangle shapes of §6.1 instead of equivalent loads |

All five runs satisfy vertical equilibrium, and the applied load equals a hand sum of the printed loads (`tests/test_anchor_live.py`).

### Three checks on the thesis itself

**1. Column sums in table "7.2".** In a moment-distribution table, each final moment is the sum of the column above it (fixed-end moment plus every distribution and carry-over step). At floors 2-4 the printed finals do not equal those sums:

| Floor | Largest gap (printed − column sum) | Example |
|---|---|---|
| 4 (roof) | 6.20 kN·m (B, lower column) | A, right beam: printed −4.55, sum −6.66 |
| 3 | 5.24 kN·m (B, left beam) | B, left beam: printed 27.92, sum 22.68 |
| 2 | 23.28 kN·m (C, right beam) | C, right beam: printed −3.38, sum −26.66 (this is flag D2) |
| 1 | 0.06 kN·m at A, B and D; 1.74 at joint C | sums hold, except the copied C column |

Full list: `results/thesis_table_7_2_check.csv`.

**2. Joint balance in table "7.2".** With the column sums, the exterior joints balance the printed eccentric moment (A4: −1.46 against −1.47; A3: −5.87 and A2: −5.86 against −5.89). A1 is out by 1.03. The interior joints do not balance, either at 0 (no interior moment) or at +15.64 (moment applied): B4 −4.40, B3 −0.47, B2 +6.22, B1 −27.67 kN·m. At B the first distribution step is also not the distribution factor times the unbalanced moment: at B3 the step adds to −12.18, while the fixed-end moments give 27.70 − 3.52 = 24.18 (or 8.54 with the 15.64 applied) [J]. So at B3 the balance near 0 is a coincidence of the carry-overs, and the table does not show which interior moment, if any, was used. Full list: `results/thesis_table_7_2_joints.csv`.

**3. Running sums for the B/C column (Figure 7-2 table).** Flag D4 (Day 3) already notes that 30.40 + 32.77 + 108.32 = 171.49, not 409.08. The "V transfer" of 32.77 also equals the AB right shear 29.67 plus the roof BC shear 3.10. The floor BC shear in Table 7-3 is 40.82. So the axial forces use the roof BC value at every floor [J], which fits the fixed-end-moment load (0.97 kN/m), not the shear table. Continuing the thesis's own sums without the jump: 171.49 (floor 3), 171.49 + 32.78 + 108.32 = 312.59 (floor 2), 312.59 + 30.84 + 108.32 = 451.75 (floor 1).

### Differences above 10 % (primary run)

Moments are compared with the printed table "7.2" values in `results/anchor_gravity_live.csv`. "Rigid vs sum" is the `rigid_column_axial` run against the column sum, from `results/thesis_table_7_2_check.csv`; it shows what is left once the two main effects are removed.

| Quantity | Thesis | Model | Diff | Rigid vs sum | Likely cause | Type |
|---|---|---|---|---|---|---|
| M, floor 4, AB left / CD right | ∓4.55 | ∓9.86 | 117 % | 5 % | Printed final is not the column sum (−6.66), plus axial shortening. The moment is small (under 10 kN·m), so a few kN·m is a large percentage | Possible mistake + method |
| M, floor 4, AB right / CD left | ±7.98 | ±3.66 | 54 % | 32 % | Joint B4 does not balance even with the column sums (−4.40) | Possible mistake |
| M, floor 4, BC ends | ∓1.35 | ∓2.87 | 113 % | 5 % | Printed final is not the column sum (−3.50); axial shortening | Possible mistake + method |
| M, floor 3, AB left / CD right | ∓23.72 | ∓30.48 | 29 % | 2 % | Axial shortening of the columns: the interior joint loads (108.32 kN) are 2.4 times the exterior ones (45.03 kN), so B and C shorten more than A and D. The hand method ignores this | Method |
| M, floor 3, AB right / CD left | ±27.92 | ±20.58 | 26 % | 12 % | Axial shortening, and the printed final is 5.24 above its column sum; the rest is the B3 distribution step | Method + possible mistake |
| M, floor 2, AB left / CD right | ∓23.25 | ∓30.15 | 30 % | 2 % | Axial shortening | Method |
| M, floor 2, AB right | 27.92 | 22.11 | 21 % | 2 % | Axial shortening (6.5 % with rigid columns against the printed value) | Method |
| M, floor 2, BC ends | ∓3.38 | ∓4.30 | 27 % | 2 % | Printed final is not the column sum (−4.60); axial shortening | Possible mistake + method |
| M, floor 2, CD left | −3.38 | −22.11 | 554 % | 2 % | Copy error D2: the BC value was repeated; the column sum is −26.66 | Mistake |
| M, floor 1, AB right / CD left | ±17.58 | ±22.73 | 29 % | 43 % | Joint B1 is out of balance by 27.7 kN·m in the thesis | Possible mistake |
| M, floor 1, BC ends | ∓7.86 | ∓4.88 | 38 % | 36 % | Joint B1 out of balance, as above | Possible mistake |
| N, floors 3-1, B/C | 409.08 / 550.18 / 689.34 | 162.30 / 295.79 / 429.66 | 60 / 46 / 38 % | n/a | Running-sum error D4. Against the continued sums (171.49 / 312.59 / 451.75) the model is 5.4 / 5.4 / 4.9 % lower, because its AB load is 6.41 kN/m against the 8.08 used for the thesis shears | Mistake |

### Differences below 10 % worth knowing about

- **N, A/D, all floors (−6 to +9 %).** The thesis sums use the 8.08 kN/m shears; the model uses 6.41 kN/m. The roof is +9 % because the model's roof end moments differ from the printed ones (see the table above), which moves shear towards A (small numbers: 16.44 against 15.10 kN).
- **M, floor 1, AB left (2.6 %).** This is the one interior-floor beam end where the column sum, the joint balance and the model all agree.
- **Axial shortening is a larger effect for live load than for dead load.** For dead load, making the columns rigid moved the AB left ends by about 8-9 percentage points (Day 5); for live load it moves them by about 17-20 points, because the live joint loads are much larger at B and C than at A and D. For the carbon model this matters [J]: the hand method's moments are not a conservative stand-in for a frame analysis.
- **Pattern loading.** The thesis puts the full live load on every span at once, and so does the model. A reviewer may ask about chequerboard live load for beam span moments. It is not in the thesis or the charter, so it is not modelled here [J].

## Load combinations (Day 6)

Numbers come from `results/anchor_gravity_combination.csv` and `validation/thesis_values/combination_beam_roof.csv`.

### What the thesis used

§8.7 and the headers of Tables 8-13 and 8-15 give (baseline_spec S13):

1. 1.3 D + 1.5 L
2. 1.3 D + 1.5 (L ± 0.6 W)
3. 1.3 D + 1.5 (0.7 L ± W)
4. A seismic combination. The text is garbled ("Gravitational freight multiplied by1.21.3 times"); it reads as 1.2 × gravity representative value ± 1.3 × earthquake. This equals GB 50011-2010 cl. 5.4.1 and Table 5.4.1 (γG = 1.2, γEh = 1.3), the seismic code the thesis cites.

These are coded as data in `src/shellbench/combinations.py`. Combinations 2-4 need the wind (Day 8) and seismic (Day 9) cases, so they are reported as pending.

**Code clauses (checked by Claude Code, 24 Oct 2026).** Only the clause text was used; the author should still confirm it in their own copies.

| Factor set | Clause | Source text used |
|---|---|---|
| 1.3 dead, 1.5 live and wind | GB 55001-2021 cl. 3.1.13: permanent action "不应小于1.3" (item 1); other variable actions "不应小于1.5" (item 4) | Online text of GB 55001-2021 (gb55001.readthedocs.io, chapter 3) |
| 1.2 gravity, 1.3 horizontal earthquake (thesis) | GB 50011-2010 cl. 5.4.1: γG "一般情况应采用 1.2"; Table 5.4.1, horizontal only: γEh = 1.3 (γw = 1.4) | GB 50011-2010 text, PDF page 37 (csdp.edu.cn copy) |
| 1.3 gravity, 1.4 horizontal earthquake (current) | GB 55002-2021 cl. 4.3.2: Table 4.3.2-1 γG ≥ 1.3; Table 4.3.2-2, horizontal only: γEh = 1.4 (minimum, "不应低于") | Online text of GB 55002-2021 (gb55002.readthedocs.io, chapter 4) |

The thesis was completed on 29 May 2023 (cover page). Its references list GB 50009-2012, GB 50011-2010 and GB 50068-2001, not GB 55001 or GB 55002. Both general codes have been in force since 1 Jan 2022. So:
- The gravity factors 1.3/1.5 match GB 55001-2021, which the thesis does not cite.
- The seismic factors 1.2/1.3 come from GB 50011-2010. The mandatory GB 55002-2021, in force at thesis time, requires at least 1.3/1.4. This is flag D21.

A 2024 edition of GB 50011-2010 reportedly aligns with GB 55002 [?]; this was not checked.

### Decisions by the author (24 Oct 2026)

The author made these decisions and checks the work; Claude Code implemented them and cross-checked the clause texts.

1. **Flags D16-D21 accepted** as worded in `validation/thesis_values/README.md`. D16 and D17 take the wording revised by the cross-check. D16's A-support arithmetic was checked by the author.
2. **Anchor (Layer 1) keeps the thesis factors.** These are 1.3/1.5 for gravity and wind, and 1.2/1.3 for seismic (Day 9), so the model can reproduce the thesis. `THESIS_COMBINATIONS` is unchanged.
3. **Generator (Layer 2) uses the current codes.** Gravity uses GB 55001-2021 cl. 3.1.13 (1.3/1.5). Seismic uses GB 55002-2021 cl. 4.3.2 (1.3/1.4), held in `CODE_SEISMIC_COMBINATIONS`. This is the code-compliant baseline the charter asks for [J].
4. **Table 8-13 is not used as a validation target** (D17). Later checks compare the model with tables 6.3 and "7.2" and with Table 4-9, and name their flags.

### A check on Table 8-13

In 13 of the 15 roof rows of Table 8-13 the column headed "1.3 Dead load + 1.5 × live" equals **1.0 × dead + 1.5 × live** (the first draft said all 13 typed rows; see the cross-check below). For example, at the A support: −67.76 + 1.5 × (−22.18) = −101.03, as printed; 1.3 × (−67.76) + 1.5 × (−22.18) = −121.36 would be expected. The test `tests/test_combinations.py` checks every row. If this holds through the rest of the table, the thesis design forces for gravity are about 23 % low on the dead-load part [J]. (The cross-check below shows that it does not hold at level 1, and that the inputs are not frame forces, so this estimate is withdrawn.) This matters for Layer 2: a generator that applies 1.3 correctly may not reproduce the thesis member sizes, and the reason would be this, not the generator.

Two more things in Table 8-13 do not fit [J]:
- Its live-load column does not match table "7.2". At the roof A support it gives −22.18, against −4.55 in table "7.2".
- The wind columns could not be reproduced. A search over simple factor sets a × D + b × L + c × W (a, b, c from 0 to ±1.95) found no set that fits even the first four roof rows of either wind column. They are left for Day 8.

### Cross-check of Table 8-13 against the thesis (Claude Code, 24 Oct 2026)

Done on the thesis .docx (tables read in body order), not on the typed files. It changes D16 and D17:

1. **The roof block has 15 rows, not 13.** The two D-support rows (M −44.495, V 54.755) were left out of the typed file. They fit neither 1.0 D + 1.5 L (−101.03, −104.095) nor 1.3 D + 1.5 L. Both rows are now in `combination_beam_roof.csv`, as printed. So the 1.0 factor holds in 13 of 15 roof rows.
2. **The level-1 block fits neither factor set in any of its 15 rows.** Example: A support, dead −97.64, live −24.53, printed 48.31 (1.0 D + 1.5 L gives −134.44). Levels 4 to 2 are not printed in the table text.
3. **The dead and wind inputs are cells of table 6.3, not frame forces.** Every level-5 dead value is a roof-block cell of table 6.3. These come from the final row (67.76, 68.77, 52.84, 67.74), the second distribution step (25.72, 18.96) and the carry-over row (9.92). The "V" rows hold moments: A support V 68.77 is the B4 left-beam final moment, while the roof AB shear is 61.88 (Table 4-9). Every non-zero level-5 wind value is a table 6.3 cell too. These come from the roof first-step and carry-over rows (2.77, 4.08, 9.92, 1.38) and the floor-3 carry-over row (5.87, 7.74). The level-1 dead values are floor-3 and floor-2 cells of table 6.3, not floor-1 cells. They include −97.64, which is the D1 copy error.
4. **The live values (22.18, 23.55, 17.65, 25.59, 22.60, 8.22, 5.63) appear nowhere else in the thesis text** except Tables 8-14 and 8-15. Their source is unknown. Figures were not searched.

What follows [J]: Table 8-13 cannot be a validation target for combined forces. The 1.0 factor in D16 is real arithmetic, but it is applied to inputs that are not frame forces. So the "about 23 % low on the dead part" estimate above does not measure the error in the thesis design forces; that error is not known. The Layer 2 warning stands, in a stronger form: the thesis member sizes may not follow from any correct combination. The wind columns could not be reproduced (D17) partly because their inputs are table 6.3 cells.

Typed table "7.2" was checked in the same way: all 296 cells in `live_distribution_table_7_2.csv` equal the thesis cells, in reading order. Two D18/D19 numbers were redone by hand from those cells. Floor 2, C right beam: −27.70 + 2.31 − 2.18 + 0.91 = −26.66 (printed −3.38). Joint B1: 17.64 − 26.89 − 10.56 − 7.86 = −27.67.

**Seismic wording (§8.7).** Items i to v write "1.31.5" for "1.3 D + 1.5", and mark right-hand wind with a minus ("primary freight-0.6 right wind"). Read the same way, item vi ("multiplied by1.21.3 times left of collision") is 1.2 G_E + 1.3 E_h with the earthquake from the left. Item vii ("multiplied by1.2-1.3 times") is 1.2 G_E − 1.3 E_h, from the right [J]. This is what `combinations.py` holds. It matches GB 50011-2010 cl. 5.4.1 (see "Code clauses" above).

### Differences above 10 % (1.3 D + 1.5 L)

The reference is 1.3 × (thesis dead) + 1.5 × (thesis live), from the typed tables. Every difference above 10 % comes from the dead and live differences explained above; the combination adds no new cause:

| Rows | Diff | Carried from |
|---|---|---|
| M, floor 4, AB left / CD right; floor 3 and 2, AB left / CD right | 11-18 % | Axial shortening (dead and live) and the roof column-sum error (live) |
| M, floor 4, BC ends | 33 % | Dead joint B4 (D15) and the live roof column-sum error |
| M, floor 3, AB right / CD left | 11 % | Axial shortening and the live B3 column-sum gap |
| M, floor 2, CD left | 25 % | Copy errors D2 (live) |
| M, floor 1, BC ends | 19 % | Dead joint B1 (D15) and live joint B1 |
| N, floor 4, B/C | 11-13 % | D13 (dead roof BC shear missing) |
| N, floors 3-1, B/C | 12-21 % | D4 (live running sum) and D13 |

### Flags D16-D21 (accepted by the author, 24 Oct 2026; see "Decisions" above)

- **D16.** Table 8-13: the "1.3 D + 1.5 L" column is 1.0 D + 1.5 L in 13 of the 15 roof rows; the two D-support rows and all 15 level-1 rows fit neither 1.0 nor 1.3 (revised after the cross-check above). **Confirmed by the author, 24 Oct 2026,** for the first wording ("every roof row"): −67.76 + 1.5 × (−22.18) = −101.03, as printed. The revised scope was accepted by the author the same day.
- **D17.** Table 8-13: the dead and wind columns are cells copied from table 6.3, not frame forces ("V" rows hold moments); the live column matches neither table "7.2" nor any other thesis table; the wind combination columns cannot be reproduced from simple factors. So Table 8-13 is not a validation target (revised after the cross-check above).
- **D18.** Table "7.2": at floors 2-4 the printed finals are not the sums of their columns (up to 6.2 kN·m; 23.28 at the D2 cell).
- **D19.** Table "7.2": joints B4, B2 and B1 do not balance even with the column sums (−4.40, +6.22, −27.67 kN·m), and the first distribution step at B does not follow the distribution factors.
- **D20.** Live load sets: the fixed-end moments use 6.41 / 0.97 kN/m, the shears 8.08 / 12.37 kN/m, the text says BC carries no live load, and the B/C axial sums use the roof BC shear (3.10) at every floor.
- **D21.** §8.7 seismic combination: 1.2 gravity + 1.3 earthquake follows GB 50011-2010 cl. 5.4.1, but GB 55002-2021 cl. 4.3.2 (in force from 1 Jan 2022; thesis completed 29 May 2023) requires at least 1.3 and 1.4. The thesis seismic design forces are therefore below the code minimum then in force [J].

## Lateral loads: decisions made before the runs (25 Oct 2026)

The author made these decisions on Day 7, before any wind or seismic result exists, so neither can be tuned to the results.

1. **Wind drift tolerance: 15 %.** The Day 8 test fails if any storey drift differs from thesis Table 8-2 by more than 15 %. Author's reason: the D-value method is itself an approximation, and 15 % is large enough to absorb the known differences in α_c and axial flexibility without masking a real modelling error.
2. **Seismic comparison (Day 9): storey forces for levels 1-4 only.** Every shear in Table 8-12 includes the 98.29 kN level-5 force, which comes from the row judged spurious (decision B4). Day 9 compares the storey forces F_i = V_i − V_i+1 for levels 1-4 and does not add the level-5 force at the roof. Author's reason: adding it would inflate every shear and spoil the comparison with the four real storeys.
3. **α_max = 0.08** for frequent earthquakes at 7 degrees (0.10 g), confirmed by the author in GB 50011-2010 Table 5.1.4-1.

### How the wind comparison is read (written 26 Oct 2026, 03:55 UTC, before the first wind run)

Claude wrote these reading rules down before any wind result existed [J]. They apply the author's decision 1 above; they do not change it.

1. "Storey drift" in decision 1 is read as the inter-storey displacement Δu [mm] of Table 8-2, storey by storey. That is the pass/fail test, with the 15 % tolerance, and it is reported whatever it shows.
2. Two more references are reported next to it as diagnostics, never as pass/fail: (a) V/ΣD from the shears and ΣD printed in Table 8-2 (the thesis method with its own numbers, see D7); (b) V/ΣD with D-values recomputed from the model's own section stiffnesses by the same D-value formulas. Together they split any difference into thesis arithmetic, D-value method, and finite-element model.
3. The wind storey forces are the printed W_k of Table 8-2; they are not recomputed. A separate check recomputes them from the Table 8-1 inputs (baseline_spec W1-W7) only to test the typing and the thesis arithmetic.
4. Model storey displacement is the mean horizontal displacement of the four column-line nodes at each level. The drift ratio checked against 1/550 (spec S11) is Δu / h with the model storey heights (ground 4.55 m, decision B4).
5. Check runs change one thing each: columns axially rigid; floors rigid in their own plane; ground storey 4.05 m as in Tables 8-1 and 8-2. None of them can replace the primary run in the pass/fail test.
6. If the pass/fail test fails, the tolerance and the target stay as they are. The failure is written into this file and the LOG, and the author decides how the test is kept.

### How the seismic comparison is read (written 27 Oct 2026, 03:41 UTC, before the first seismic run)

Claude wrote these reading rules before any seismic result existed [J]. They apply the author's decisions 2 and 3 above and change neither. The author has set no pass/fail tolerance for Day 9, so none is invented here: every difference is reported, and every difference above 10 % gets a written reason (Playbook Day 6 rule).

1. **Comparison targets.** The storey forces F_i = V_i − V_(i+1) of Table 8-12 for levels 1-4 (31.03, 54.56, 77.62, 101.56 kN) are the primary targets (decision 2). The level-5 force is not added at the roof. Storey shears are compared with the four-storey shears the same decision implies, V_i − 98.29 kN [J], and also listed next to the printed V_i.
2. **Storey weights G_i (GB 50011 cl. 5.1.3, Table 5.1.3).** G_i = dead + 0.5 × floor live; roof live load is not included. The loads are those the thesis applied to the axis (2) frame (7.2 m strip, decision B10), summed from the model's own load description. Primary: the actual load shapes of Fig. 4-4 and §6.1, because they carry the true total load; the equivalent uniform loads of §6.2.1 and §7.1 were made to match fixed-end moments, not totals [J]. Each storey's column self-weight goes half to the level above and half to the level below; the lower half of the ground storey goes to the foundation. Check run: the loads the thesis used for beam shears and column axial forces (dead ``thesis_text``, live ``thesis_shear``).
3. **Period.** The thesis prints no period (B9). The primary T1 is the first-mode period of the bare OpenSeesPy frame, with G_i/g lumped as horizontal mass at the four column-line nodes of each level. A Rayleigh estimate from the static deflection under lateral forces equal to G_i is reported as an arithmetic check of the eigenvalue, not as a separate method.
4. **Infill period factor ψ_T.** This is the author's decision (docs/schedule.md, Day 9). Until it is made, the primary run uses ψ_T = 1.0, which needs no outside value. Runs with ψ_T = 0.9, 0.8, 0.7 and 0.6 are reported as a sensitivity only. These are trial values spanning the range the primer cites from JGJ 3-2010 cl. 4.3.17 [?]; they are not code values, and none of them becomes the primary run until the author chooses one from a source.
5. **Implied period.** The period at which the GB 50011 curve, with the model's G_eq, gives the thesis base shear (V_1 − 98.29 kN) is reported as a diagnostic. It must not be used to choose ψ_T, because that would tune the model to the target [J].
6. **Spectrum and forces.** α_max = 0.08 (decision 3), Tg = 0.35 s (B5), 5 % damping with γ = 0.9, η1 = 0.02, η2 = 1.0 (cl. 5.1.5); F_Ek = α1 × 0.85 ΣG_i (cl. 5.2.1); F_i by G_i H_i with the top additional force δ_n from Table 5.2.1 (H_i measured from the top of the footing, 4.55 m ground storey, B4). Only the four values read from the English translation of GB 50011-2010 on 26 Oct are used; they are still to be checked against the Chinese 2016 copy.
7. **Drifts.** The model's forces act at the axis-A node of each level, as for wind; storey displacement is the mean of the four column-line nodes. Model Δu is reported against the printed Δu, against V/ΣD with the printed ΣD and four-storey shears, and against the 1/550 limit (S11). A second run applies the thesis F_1-F_4 to the model, so the stiffness comparison does not depend on the forces.
8. **Minimum shear.** Every storey is checked against λ ΣG_j with λ = 0.016 (cl. 5.2.5, Table 5.2.5, 7 degrees 0.10 g, T1 < 3.5 s).
9. If a result looks wrong, these rules stay as written. Any change after the run is dated, marked as made after the run, and given a reason.

## Wind (Day 8, 26 Oct 2026)

Status: **reviewed by the author on 26 Oct 2026** (decisions at the end of this section). Explanations still marked [J] or [?] are Claude's and unverified. Numbers come from `results/anchor_wind.csv`, `anchor_wind_runs.csv`, `anchor_wind_d_values.csv` and `thesis_table_8_2_forces_check.csv`, written by `src/shellbench/anchor_wind.py` (run by `python -m shellbench.anchor_frame`), or are arithmetic on printed Table 8-2 values.

### What the model does

The printed W_k of Table 8-2 (10.74, 10.10, 10.41, 11.42 kN, levels 1-4) act from the left at the axis-A joint of each level. Nothing in the gravity model changes; the gravity results files are byte-identical to Day 7. Wind from the right is the mirror image, because the frame is symmetric.

### Verdict of the pre-registered test: fail at all four storeys

| Level | Δu Table 8-2 [mm] | Δu model [mm] | Difference | Within 15 %? |
|---|---|---|---|---|
| 1 | 0.78 | 0.425 | −45.5 % | no |
| 2 | 0.91 | 0.351 | −61.4 % | no |
| 3 | 0.51 | 0.250 | −51.1 % | no |
| 4 | 1.13 | 0.143 | −87.4 % | no |

The tolerance and the target were not changed after the run (reading rule 6). The pytest `test_preregistered_tolerance_verdict` applies decision 1 unchanged and asserts the verdict it gives today: fail at all four storeys. It is a regression check on the verdict, not on the model (the closed-form tests check the model). If the model or the typed target ever changes so that a storey passes, the test fails and the verdict has to be read again. The Playbook asked for a test that fails when a drift is outside the tolerance; written that way it would fail on every run, for a reason that sits in the thesis, and skipping or marking it as an expected failure would hide a test. The author may prefer the literal version and accept a red suite until the anchor report; that is the author's call.

### Why it fails: the target, not the model

The model and the thesis carry the same storey shears (column shears 42.67, 31.93, 21.83, 11.42 kN, equal to the printed V). So the gap sits in the drifts the thesis printed, and three things point at the thesis arithmetic:

1. The printed Δu is not V/ΣD of the thesis's own V and ΣD (flag D7). It is 1.70, 3.06, 2.51 and 10.6 times that value at levels 1-4.
2. Read backwards, the printed Δu implies storey stiffnesses V/Δu of 54 705, 35 088, 42 804 and 10 106 N/mm. Storeys 2-4 have identical columns, beams and heights, yet the implied stiffness changes by more than four times between them. No single elastic frame can do that, so no choice of modelling assumption (cracked sections, a different E, joint flexibility) can bring the model within 15 % of all four rows.
3. Against V/ΣD with the thesis numbers, the model is −7.5, +18.1, +22.9 and +34.5 % off. Against V/ΣD with D-values recomputed from the model's own sections by the same formulas as Table 7-6, it is −16.7, −2.8, +1.1 and +10.6 % off.

Item 3 splits the difference into its parts. The recomputed ΣD (83 633 N/mm ground, 88 416 N/mm above) is lower than the printed 92 842 and 107 488 N/mm, which is flag D6 again: the printed K and α_c in Table 7-6 cannot be reproduced from the §2.6 stiffnesses. Once the D-values are recomputed, the finite-element frame and the D-value method agree within 3 % at levels 2-3. The ground storey is 16.7 % stiffer in the model than the D-value formula gives, because the fixed-base α_c = (0.5 + K)/(2 + K) ignores the restraint the storey above gives to the column tops [J]. At the roof the model is 10.6 % more flexible than the D-value estimate. Checked on 26 Oct 2026 (Claude Code, `test_roof_storey_stiffness_depends_on_load_pattern`): the D-value method assumes equal joint rotations at both ends of each column, so its storey stiffness does not depend on the loads. The model's roof storey does. Under the Table 8-2 forces storey 3 carries 21.83 kN against 11.42 kN at the roof, so the level-3 joints rotate about 1.9 times as much as the roof joints, and that rotation adds drift to the roof storey. With the same 42.67 kN at the roof only (equal shear in every storey) the roof storey is 15.8 % stiffer than the estimate, because the roof beams restrain only the columns below them. With 42.67 kN at level 3 only, the roof storey drifts 0.115 mm while carrying no shear. So the 10.6 % is a limit of the D-value method at the top storey, not an error in the model or in the recomputed D-values [J]. It does not change the wind verdict.

### Check runs (one change each, Δu difference from Table 8-2)

| Run | Level 1 | Level 2 | Level 3 | Level 4 | What it shows |
|---|---|---|---|---|---|
| primary | −45.5 % | −61.4 % | −51.1 % | −87.4 % | |
| rigid_column_axial | −45.7 % | −61.8 % | −51.9 % | −87.8 % | Column axial shortening adds about 1 % to the roof displacement (1.169 against 1.155 mm). |
| rigid_floor | −45.5 % | −61.5 % | −51.1 % | −87.4 % | Beam axial strain does not matter for wind. |
| ground_4_05 | −58.8 % | −63.0 % | −51.6 % | −87.4 % | A 4.05 m ground storey (Tables 8-1, 8-2) makes level 1 stiffer and the gap wider, so B4's 4.55 m is not the cause. |

### Drift limit

Every model drift ratio meets 1/550 (spec S11) by a wide margin. The largest is θ = 9.75 × 10⁻⁵ at storey 2, which is 5.4 % of the limit. The thesis printed θ = u/h for levels 2-4 (flag D8), cumulative displacement over storey height, and that also passes. So under the stated assumptions wind does not govern the frame's drift; the seismic check on Day 9 will.

### A check on the printed wind forces

`thesis_table_8_2_forces_check.csv` recomputes W_k = β_z μ_s μ_z w₀ B h from the Table 8-1 inputs (spec W1-W6). The printed shears are exact running sums of the printed forces. Levels 1-3 reproduce to 0.01 kN with tributary heights of 3.825 m ((4.05 + 3.6)/2) and 3.60 m. The roof force 11.42 kN implies a tributary height of 3.60 m, the same as a typical floor. Table 8-1 confirms it: the roof row has h_i = 3.6 m and h_j = 3.6 m. The parapet is 1.2 m high (Th §4.2, parapet wall 1.2 × 0.24 × 5.5), so half the top storey plus the parapet gives 1.8 + 1.2 = 3.0 m and W_k = 3.173 × 3.0 = 9.52 kN [J]. The printed roof force is 20 % higher than that, and the base shear 42.67 kN is about 4.5 % higher than 40.77 kN. This is flag D23. It errs on the safe side and does not change the drift verdict.

### Proposed flags (for the author)

- **D22.** Table 8-2 Δu implies storey stiffnesses V/Δu of 54 705, 35 088, 42 804 and 10 106 N/mm; storeys 2-4 are identical, so the printed Δu cannot come from one frame. Extends D7. Effect: the pre-registered wind test fails on the thesis side; the anchor report names it.
- **D23.** Roof W_k = 11.42 kN uses h_j = 3.6 m (Table 8-1) where half the top storey plus the 1.2 m parapet (Th §4.2) gives 3.0 m, so 9.52 kN [J]. Effect: the thesis roof wind force is 20 % high and the base shear 4.5 % high, on the safe side. The anchor keeps the printed forces.

### Decisions by the author (26 Oct 2026)

- Author's check: Table 8-2 in the thesis prints Δu = 0.91 mm (storey 2) and 1.13 mm (storey 4), so D22 is not a Day 3 typing error.
- The wind test stays as written: the 15 % rule applied unchanged, with today's verdict (fail at all four storeys) asserted. Author's reason: the tolerance was fixed before any result existed, and the test records that the printed drifts cannot come from any single set of storey stiffnesses.
- D22 accepted.
- D23 accepted, on condition that Table 8-1 or the drawings confirm the roof value. Confirmed the same day from the thesis text: Table 8-1 roof row h_j = 3.6 m, parapet 1.2 m in §4.2. D23 is now a permanent flag.

### How the response-spectrum check is read (written 27 Oct 2026, 03:49 UTC, before the first response-spectrum or 3D run)

Claude wrote these before any Day 10 result existed [J]. No tolerance is set for Day 10 by the author, so none is invented; every difference above 10 % gets a written reason.

1. **Same inputs as Day 9.** Same G_i, masses, spectrum, α_max, Tg and ψ_T = 1.0 (bare frame) as the primary base-shear run. Nothing is re-chosen for the second method.
2. **Modes and combination.** First three modes of the 2D frame. For mode j, F_ji = α_j γ_j X_ji G_i with γ_j = Σ X_ji G_i / Σ X_ji² G_i (GB 50011 cl. 5.2.2 [?], to be checked in the author's copy; this is also the standard modal participation factor). Each mode's forces are applied statically; storey shears and inter-storey drifts are combined by SRSS (square root of the sum of squares) storey by storey. Displacements are not combined first and then differenced.
3. **Mass participation** of each mode = (Σ m φ)² / (Σ m φ² × Σ m), reported with the cumulative sum.
4. **Comparison.** Base shear, storey shears and drifts of the response-spectrum method against the Day 9 base-shear run, and both against Table 8-12 as read on Day 9 (four-storey shears V_i − 98.29 kN; printed Δu). The figure has storey on the y-axis and three lines per quantity: base-shear method, response spectrum, thesis.
5. **Which method governs** is read from the larger base shear and the larger drift. It is reported as found, not chosen.
6. **3D model.** Whole building on the drawing grid (spec G4 and B11: bays 6.0, 6.6, 6.6, 6.6, 6.6, 6.0 m along axes 1-7; 7.2, 6.6, 7.2 m across), same storey heights, 600 × 600 columns at every grid point, transverse beams as the 2D frame, longitudinal beams 300 × 600 (M3). Beam I factor 2.0 for interior lines and 1.5 for edge lines (M7, applied to both directions [J]). Rigid floors (one diaphragm per level). Mass per level = the 2D frame's G_i / g scaled by plan area, 38.4 × 21.0 m against 7.2 × 21.0 m, placed at the plan centre with the rotational inertia of a uniform rectangle [J]. Shear modulus 0.4 E (GB 50010 cl. 4.1.8 [?]). The first three periods are reported next to the 2D frame's first three, with each mode's direction. The E-shaped wings and stair cores are not modelled (B11 open point).
7. These rules stay as written whatever the results. Any later change is dated and marked as made after the run.

## Earthquake by the base-shear method (Day 9, 27 Oct 2026)

Status: **draft for the author's review.** Explanations marked [J] are Claude's. Numbers come from `results/anchor_seismic.csv`, `anchor_seismic_runs.csv`, `anchor_seismic_weights.csv` and `anchor_seismic_period_check.csv`, written by `src/shellbench/seismic.py` (run by `python -m shellbench.anchor_frame`), or are arithmetic on printed Table 8-12 values. The reading rules above ("How the seismic comparison is read") were committed before the first run and were not changed after it.

### What the model does

G_i comes from the loads the thesis put on the axis (2) frame, with half the floor live load and no roof live load (Table 5.1.3): 1614.6, 1595.7, 1595.7 and 1073.1 kN, so ΣG = 5879 kN and G_eq = 4997 kN. The bare frame with these masses has T1 = 0.698 s; the Rayleigh estimate gives 0.695 s, so the eigenvalue is right. With α_max = 0.08 and Tg = 0.35 s the curved branch gives α1 = 0.0430, so F_Ek = 214.75 kN. T1 is above 1.4 Tg = 0.49 s, so a top force δ_n F_Ek = 0.126 × 214.75 = 27.0 kN goes on the roof (Table 5.2.1). The forces act at the axis-A joints, as for wind, and the column shears add back to F_Ek exactly.

### Storey forces and shears against Table 8-12 (levels 1-4, decision 2)

| Level | F model [kN] | F thesis [kN] | Diff. | V model [kN] | V thesis, four storeys [kN] | Diff. |
|---|---|---|---|---|---|---|
| 1 | 24.82 | 31.03 | −20.0 % | 214.75 | 264.77 | −18.9 % |
| 2 | 43.93 | 54.56 | −19.5 % | 189.94 | 233.74 | −18.7 % |
| 3 | 63.34 | 77.62 | −18.4 % | 146.01 | 179.18 | −18.5 % |
| 4 | 82.67 | 101.56 | −18.6 % | 82.67 | 101.56 | −18.6 % |

Every force is 18-20 % below the thesis, and the spread across the four levels is under 2 points. So the way the base shear is spread up the height matches the thesis; the whole difference is in the size of the base shear, α1 × G_eq. That difference is above 10 %, so it needs a reason. I cannot give one cause, because the thesis prints neither its period nor its weights (B9). Two readings fit the numbers [J]:

1. **Period.** With the model's G_eq, the thesis base shear 264.77 kN needs α1 = 0.0530, which the curve gives at T = 0.553 s (`T_implied_by_thesis_V`). That is 0.79 times the bare-frame period. A period reduction for infill walls would do this, and the thesis building has infill walls (Th §4.2). This number is a diagnostic only (reading rule 5); it must not be used to pick ψ_T.
2. **Weights.** At the model's own T1, the same base shear needs G_eq = 6160 kN, 23 % more than the model's. The model's ΣG is 9.7 kN/m² over the 7.2 m strip (4 × 151.2 m²), a little below the 12-15 kN/m² the primer gave as a normal range [J]. So heavier thesis weights are possible too. The check run with the loads the thesis used for beam shears (`thesis_shear_weights`) adds only 3 % to ΣG and closes the gap to −17.5 %, so the beam-load model is not the cause.

Most likely both play a part [J]. The anchor report will name this as a stated assumption, not a resolved difference.

### The infill period factor (the author's decision)

| ψ_T | T1 used [s] | α1 | F_Ek [kN] | vs thesis 264.77 kN | δ_n | Largest θ / (1/550) |
|---|---|---|---|---|---|---|
| 1.0 (primary) | 0.698 | 0.0430 | 214.75 | −18.9 % | 0.126 | 0.31 |
| 0.9 | 0.628 | 0.0473 | 236.12 | −10.8 % | 0.120 | 0.34 |
| 0.8 | 0.559 | 0.0525 | 262.52 | −0.9 % | 0.115 | 0.38 |
| 0.7 | 0.489 | 0.0592 | 296.04 | +11.8 % | 0 | 0.42 |
| 0.6 | 0.419 | 0.0681 | 340.10 | +28.5 % | 0 | 0.48 |

These ψ_T are trial values (reading rule 4), not code values. Please choose ψ_T from a source you can cite (JGJ 3-2010 cl. 4.3.17 [?], or your course notes) and not from this table. The ψ_T = 0.8 row lands close to the thesis, and picking it for that reason would be tuning. One thing to know when choosing: at ψ_T ≤ 0.7 the period drops below 1.4 Tg and the top force disappears.

### Drifts

| Level | Δu model [mm] | Δu printed [mm] | Diff. | Δu = V(four storeys)/ΣD printed [mm] | Diff. | Δu model, thesis forces [mm] | Diff. vs V/ΣD |
|---|---|---|---|---|---|---|---|
| 1 | 2.223 | 4.04 | −45.0 % | 2.852 | −22.0 % | 2.740 | −3.9 % |
| 2 | 2.040 | 3.19 | −36.1 % | 2.175 | −6.2 % | 2.510 | +15.4 % |
| 3 | 1.605 | 2.67 | −39.9 % | 1.667 | −3.7 % | 1.972 | +18.3 % |
| 4 | 0.982 | 1.93 | −49.1 % | 0.945 | +4.0 % | 1.207 | +27.7 % |

The −36 to −49 % against the printed Δu has three parts, and each is already known [J]:

1. The printed shears include the spurious 98.29 kN level-5 force (B4). Taking it out lowers V by 27 % at level 1 and by 49 % at level 4.
2. The forces are 19 % lower in the model (above).
3. Under the thesis forces, the model is more flexible than V/ΣD with the printed ΣD by 4 to 28 %, growing up the height. This is the wind pattern again: the printed ΣD in Table 7-6 cannot be reproduced (D6), and the D-value method's equal-rotation assumption flatters the top storey (wind section, "Why it fails"). The printed Δu are also about 3.3 % above V/ΣD (D9).

### Code checks

Every storey drift meets 1/550. The largest is θ = 5.67 × 10⁻⁴ at storey 2, 31 % of the limit (48 % at ψ_T = 0.6). The thesis also passes (Table 8-12). So, under the stated assumptions, earthquake governs drift over wind by about six times (wind used 5.4 % of the limit), but neither comes close. Every storey shear is above λ ΣG_j with λ = 0.016; the base shear is 2.3 times the minimum.

### Proposed flag (for the author)

- **D24.** Table 8-12 base shear (four storeys, 264.77 kN) is 23 % above the model's base-shear method with the bare-frame period (214.75 kN). The thesis prints no T1, α1 or G_i (B9), so the cause cannot be split between the period (an infill factor near 0.8 would close it) and the weights (23 % heavier would close it). The distribution over the height matches within 2 points. Effect: the anchor reports the seismic forces with the author's ψ_T and names D24; the gap is not tuned away.

### Decisions by the author (27 Oct 2026)

- D24 accepted: the thesis base shear (four storeys) is 18.9 % above the bare-frame base-shear method, and the cause cannot be split because the thesis prints neither period nor weights.
- The author asked Claude to choose ψ_T from a citable source, not from the sensitivity table. **Change made after the Day 9 and Day 10 runs (reading rule 9):** the anchor value is ψ_T = 0.7 (`seismic.ANCHOR_PSI_T`). Source: JGJ 3-2010 cl. 4.3.17 gives 0.6-0.7 for frame structures with infill walls [?]. Claude did not open the clause; the range and clause number are as cited by Zhou (2024), "框架结构计算中对周期折减系数合理取值的研究", 建筑监督检测与造价, issue 9. JGJ 3 is the high-rise code, so using it for a four-storey frame borrows a design-office practice rule [J]. Within the range, 0.7 is the smaller reduction [J]. It is not the value that matches the thesis best (0.8, outside the cited range), so the choice is not tuned to the target. The author should open cl. 4.3.17 in a copy of JGJ 3-2010 and confirm the range.
- What changes: at ψ_T = 0.7, T1 = 0.489 s (below 1.4 Tg, so δ_n = 0), α1 = 0.0592, F_Ek = 296.04 kN, 11.8 % above the thesis four-storey base shear; largest θ is 42 % of 1/550 (`results/anchor_seismic_runs.csv`, row `psi_t_0.7`). The bare-frame run stays as the method comparison above; the design checks (Day 11) and the carbon inventory use ψ_T = 0.7.

## Response-spectrum check and 3D periods (Day 10, done ahead on 27 Oct 2026)

Status: **draft for the author's review.** Numbers come from `results/anchor_rsa.csv`, `anchor_rsa_modes.csv`, `anchor_3d_periods.csv` and `figures/anchor_seismic_compare.png`, written by `src/shellbench/rsa.py` and `src/shellbench/anchor_3d.py` (run by `python -m shellbench.anchor_frame`). The reading rules ("How the response-spectrum check is read") were committed before the first run and not changed after it. Inputs are the Day 9 primary run's: same G_i, spectrum and bare-frame period.

### Modes of the 2D frame

| Mode | T [s] | α | Mass share | Cumulative | Modal base shear [kN] |
|---|---|---|---|---|---|
| 1 | 0.698 | 0.0430 | 88.9 % | 88.9 % | 224.57 |
| 2 | 0.215 | 0.0800 | 8.7 % | 97.6 % | 40.95 |
| 3 | 0.115 | 0.0800 | 2.0 % | 99.6 % | 9.53 |

Three modes carry 99.6 % of the mass, so a fourth would change nothing that matters.

### The two methods side by side

| Storey | V base-shear [kN] | V spectrum [kN] | Diff. | Δu base-shear [mm] | Δu spectrum [mm] | Diff. |
|---|---|---|---|---|---|---|
| 1 | 214.75 | 228.47 | +6.4 % | 2.223 | 2.325 | +4.6 % |
| 2 | 189.94 | 194.28 | +2.3 % | 2.040 | 2.058 | +0.9 % |
| 3 | 146.01 | 142.57 | −2.4 % | 1.605 | 1.539 | −4.1 % |
| 4 | 82.67 | 70.06 | −15.3 % | 0.982 | 0.870 | −11.4 % |

The two routes agree within 6.4 % at storeys 1-3. Two things explain the pattern [J]:

1. **The base.** The base-shear method takes G_eq = 0.85 ΣG. The first mode alone has 88.9 % of the mass, so its base shear is 0.889 / 0.85 = 1.046 times larger: 224.57 against 214.75 kN. The higher modes add another 4 kN through SRSS. So the spectrum method is 6.4 % higher at the base.
2. **The roof.** The base-shear method puts δ_n F_Ek = 27.0 kN on the roof to stand in for higher modes (Table 5.2.1). For this four-storey frame that stand-in is generous: the spectrum method's roof shear is 70.06 kN against 82.67 kN. That is why storey 4 differs by more than 10 %, in shear and in drift. The difference sits on the safe side of the simpler method.

**Which governs.** The spectrum method gives the larger base shear (+6.4 %) and the larger drift at storeys 1 and 2. The base-shear method gives the larger shear and drift at storeys 3 and 4. Neither comes near the drift limit: the largest θ is 5.72 × 10⁻⁴ (spectrum, storey 2), 31 % of 1/550. Against the thesis four-storey shears the spectrum method is 14-31 % lower, for the reasons given in Day 9 (D24) and, at the roof, because it carries less top force still.

### 3D whole-building periods

| Mode | 3D period [s] | Direction | 2D frame, same mode number [s] |
|---|---|---|---|
| 1 | 0.622 | transverse (Y, the 2D frame's direction) | 0.698 |
| 2 | 0.571 | longitudinal (X) | 0.215 (2nd transverse mode) |
| 3 | 0.518 | torsion | 0.115 (3rd transverse mode) |

The comparison that matters is the transverse T1: 0.622 s in 3D against 0.698 s for the 2D frame, so the 2D model is 12 % longer. That is not a 3D effect as such. Each 2D-frame storey carries the mass of a 7.2 m strip (decision B10, the thesis calculation width), while the seven drawn transverse frames share 38.4 m, 5.49 m each. With mass alone the period would scale by √(5.49 / 7.2) = 0.873. The two edge frames have the 1.5 beam factor instead of 2.0, which makes the average frame a little softer, and the result, 0.891, sits just above 0.873 [J]. So the 2D simplification mainly changes T1 through the tributary width, and the paper should say so: the 7.2 m width is kept for validating against the thesis tables, and the drawn grid is what the whole-building model (and Layer 2) uses.

The plan is symmetric in the model, so the translational modes carry no rotation and torsion comes third. The real building is E-shaped with stair cores (B11 open point), which would add eccentricity; the simple model cannot show that, and the anchor report should say it was left out.

### With the anchor ψ_T = 0.7 (added 27 Oct 2026, after the run)

With every modal period multiplied by 0.7, the spectrum method gives 312.38, 267.47, 192.52 and 89.51 kN against the base-shear method's 296.04, 256.91, 187.63 and 87.75 kN: 5.5, 4.1, 2.6 and 2.0 % higher (`results/anchor_rsa.csv`, columns `*_anchor_psi`). The base-shear method now has no top force (T1 ≤ 1.4 Tg), so the roof difference of the bare-frame run disappears and the spectrum method governs at every storey. Its largest θ is 7.88 × 10⁻⁴ (storey 2), 43 % of 1/550.

### Decisions by the author (27 Oct 2026)

- D25 accepted: the 2D frame's T1 is 12 % longer than the whole building's transverse T1 because it carries a 7.2 m strip of mass against 5.49 m for the drawn frames.

### Code values still marked [?]

GB 50011 cl. 5.2.2 (modal forces and SRSS) and GB 50010 cl. 4.1.8 (G_c = 0.4 E_c) are cited from general knowledge and must be checked in the author's copies. The square-section torsion constant (0.1406 a⁴) is a standard textbook result [?]; it only affects member torsion in the 3D model.

### Proposed flag (for the author)

- **D25.** The 2D anchor frame's T1 (0.698 s) is 12 % longer than the whole-building transverse T1 on the drawn grid (0.622 s), because the 2D frame carries a 7.2 m strip of mass (B10) where the drawn frames carry 5.49 m on average. Effect: the anchor validates against the thesis with 7.2 m, but any period or base shear the papers quote for the real building comes from the drawn grid.

© 2026 Syed Nafiz Reja Hasib. All rights reserved.
