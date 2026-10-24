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

### Decisions (24 Oct 2026, made by Claude on the author's instruction)

The author asked Claude to settle the open Day 6 items without asking. These are Claude's decisions, not the author's checks. The author must read them before the anchor report cites them (R3, R4).

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

### Flags D16-D21 (accepted 24 Oct 2026 by Claude on the author's instruction; see "Decisions" above)

- **D16.** Table 8-13: the "1.3 D + 1.5 L" column is 1.0 D + 1.5 L in 13 of the 15 roof rows; the two D-support rows and all 15 level-1 rows fit neither 1.0 nor 1.3 (revised after the cross-check above). **Confirmed by the author, 24 Oct 2026,** for the first wording ("every roof row"): −67.76 + 1.5 × (−22.18) = −101.03, as printed. The revised scope was accepted by Claude on the author's instruction.
- **D17.** Table 8-13: the dead and wind columns are cells copied from table 6.3, not frame forces ("V" rows hold moments); the live column matches neither table "7.2" nor any other thesis table; the wind combination columns cannot be reproduced from simple factors. So Table 8-13 is not a validation target (revised after the cross-check above).
- **D18.** Table "7.2": at floors 2-4 the printed finals are not the sums of their columns (up to 6.2 kN·m; 23.28 at the D2 cell).
- **D19.** Table "7.2": joints B4, B2 and B1 do not balance even with the column sums (−4.40, +6.22, −27.67 kN·m), and the first distribution step at B does not follow the distribution factors.
- **D20.** Live load sets: the fixed-end moments use 6.41 / 0.97 kN/m, the shears 8.08 / 12.37 kN/m, the text says BC carries no live load, and the B/C axial sums use the roof BC shear (3.10) at every floor.
- **D21.** §8.7 seismic combination: 1.2 gravity + 1.3 earthquake follows GB 50011-2010 cl. 5.4.1, but GB 55002-2021 cl. 4.3.2 (in force from 1 Jan 2022; thesis completed 29 May 2023) requires at least 1.3 and 1.4. The thesis seismic design forces are therefore below the code minimum then in force [J].

© 2026 Syed Nafiz Reja Hasib. All rights reserved.
