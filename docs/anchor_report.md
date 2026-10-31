# Anchor report: the thesis building in ShellBench

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

Playbook Day 13, 31 Oct 2026. Draft by Claude for the author to read sentence by sentence before release v0.1. Every number comes from a file in `results/` (named under each table), from `docs/baseline_spec.md`, or from `docs/anchor_notes.md`, where the full reasoning sits. Sentences that need the author's judgement are marked [J].

## 1. Purpose

ShellBench asks how much thin-shell floors cut the A1-A3 embodied carbon of a GB 50010 / GB 50011 RC frame, and how the saving changes with storey count and seismic intensity (`docs/research_question.md`). Every later result is a comparison against a conventional frame. This report checks that the conventional frame model reproduces a building that was designed by hand: the author's undergraduate thesis building. If the model cannot reproduce the thesis where the thesis is right, nothing built on it can be trusted. Where the model and the thesis disagree, the report says which side is wrong and why.

## 2. The building

The building is a four-storey cast-in-place RC moment frame with an internal corridor (spec G1). The analysed frame is the transverse frame on axis (2): spans 7.2, 6.6 and 7.2 m, a 4.55 m ground storey and three storeys of 3.6 m (G3, G5-G7). Columns are 600 × 600 mm; frame beams are 300 × 600 mm (AB, CD) and 300 × 500 mm (BC), with the slab's contribution taken as I = 2.0 I₀. Concrete is C40 (E = 3.25 × 10⁴ MPa) and bars are HRB400. The slab is 120 mm thick (G10). The site is 7 degrees (0.10 g), site class II, Tg = 0.35 s.

The 2D anchor frame carries a 7.2 m strip, because the thesis computed every load with that width (decision B10). The whole-building model and the quantity take-off use the drawing grid instead: 38.4 × 21.0 m, bays of 6.0 and 6.6 m along the building, 28 columns, 3 225.6 m² of floor over four storeys (B11).

The model is a 2D elastic OpenSeesPy frame (`src/shellbench/anchor_frame.py`). A 3D model on the drawing grid gives the whole-building periods (`anchor_3d.py`).

## 3. The nine inconsistencies and the author's decisions

The playbook named nine places where the thesis contradicts itself. The author decided each one on 20 Oct 2026 (`docs/baseline_spec.md`, Part B):

| Item | What the thesis says | Decision |
|---|---|---|
| B1 | Slab 180 mm (§2.1) and 120 mm (load sections) | 120 mm; every load that produces a number uses it |
| B2 | "25 × 0.12 = 6.60" | A typo for 3.00; only 3.00 makes the printed floor total add up |
| B3 | Live load 2.0 (§3.2.2) and 2.5 / 3.0 kN/m² (§6.1) | 2.5 office, 3.0 corridor, the values behind the force tables |
| B4 | Four storeys, but five levels in Table 8-12; ground storey 4.55 or 4.05 m | Four storeys, 4.55 m; level 5 of Table 8-12 is an extra row |
| B5 | Site class I with Tg = 0.35 s | Keep Tg = 0.35 s; the class is II |
| B6 | Columns 4C22, below the code minimum | Reproduce 4C22 as designed and flag the shortfall |
| B7 | HRB400 written with f_y = 270 | f_y = 360 N/mm² |
| B8 | Bearing value 220, 240 or 360 kPa | 220 kPa, the lowest usable value stated |
| B9 | No T1, α1 or G_eq printed | The model computes T1 and G_i; only shears and drifts are compared |

Seven more items (B10-B16) came out of the same audit and were decided the same day. The two that matter most here are B10 (7.2 m strip for validation) and B11 (drawing grid for quantities).

## 4. Validation

Each comparison below was read with rules written down before the run, so no tolerance was set after seeing a result (`docs/anchor_notes.md`). Every difference above 10 % has a written reason in that file. The reasons fall into three kinds: the method (the hand method ignores something the frame model includes), a stated simplification, or an error in the thesis.

### 4.1 Gravity

| Case | Targets | Above 10 % | Median abs. difference | File |
|---|---|---|---|---|
| Dead load | 40 (24 beam-end moments, 16 column axial forces) | 11 | 4.2 % | `anchor_gravity_dead.csv` |
| Live load | 40 | 26 | 28.5 % | `anchor_gravity_live.csv` |
| 1.3 D + 1.5 L | 40 | 21 | 10.7 % | `anchor_gravity_combination.csv` |

For dead load, the largest difference is 36 % on the roof BC beam-end moment. The thesis moment distribution there does not balance: at joint B4 the printed final moments add to −51.81 kN·m where they should add to zero (flag D15, checked by hand by the author). The other dead-load differences above 10 % come from axial shortening of the columns, which the hand method ignores (with axially rigid columns, the AB left end falls from 11 % to 1.5-3 %), and from a missing roof BC shear in the Table 4-9 axial sums (D13).

Live load looks much worse, and most of it is in the thesis. The printed finals of table "7.2" are not the sums of their own columns at floors 2-4 (D18), three interior joints do not balance (D19), and one cell repeats the BC value in the CD column: −3.38 against a column sum of −26.66 kN·m, the 554 % row (D2). The B/C axial forces at floors 1-3 carry a running-sum error (D4): against the thesis's own sums continued without the jump, the model is 4.9-5.4 % lower. Live load also shows axial shortening more than dead load does, because the interior joint loads are 2.4 times the exterior ones. That matters later [J]: the hand method's moments are not a safe stand-in for a frame analysis.

The combination adds no new cause. Every difference above 10 % is carried from the dead and live cases. Table 8-13, the thesis's own combination table, turned out not to hold frame forces at all: its dead and wind columns are cells copied from table 6.3, and its "1.3 D" column is 1.0 D in 13 of 15 roof rows (D16, D17). It is not used as a target.

### 4.2 Wind

The pre-registered test (any storey drift more than 15 % from Table 8-2 fails) fails at all four storeys (`anchor_wind.csv`):

| Level | Δu thesis [mm] | Δu model [mm] | Difference |
|---|---|---|---|
| 1 | 0.78 | 0.425 | −45.5 % |
| 2 | 0.91 | 0.351 | −61.4 % |
| 3 | 0.51 | 0.250 | −51.1 % |
| 4 | 1.13 | 0.143 | −87.4 % |

The failure is on the thesis side. The model carries the same storey shears as the thesis (42.67, 31.93, 21.83 and 11.42 kN). Read backwards, the printed drifts imply storey stiffnesses of 54 705, 35 088, 42 804 and 10 106 N/mm, yet storeys 2-4 are identical. No single elastic frame can give those drifts, so no modelling choice can pass the test (D22, accepted by the author). Against the D-value method with D-values recomputed from the model's own sections, the model is within −16.7 % to +10.6 %, and within 3 % at levels 2-3. The test stays as written and asserts today's verdict (author's decision, 26 Oct 2026). Wind uses at most 5.4 % of the 1/550 drift limit.

### 4.3 Earthquake

With the bare-frame period, the base-shear method gives storey forces 18-20 % below Table 8-12 at every level (`anchor_seismic.csv`). The spread over the height is under 2 points, so the distribution matches and the whole difference is in the size of the base shear. The bare frame has T1 = 0.698 s and a base shear of 214.75 kN, against 264.77 kN in the thesis (four storeys, decision on Day 7). The thesis prints neither its period nor its weights (B9), so the gap cannot be split between the two (D24, accepted by the author).

The anchor uses an infill period factor ψ_T = 0.7. The source is JGJ 3-2010 cl. 4.3.17 as quoted by two secondary sources; neither the author nor Claude has opened a primary copy, so it stays [?] until one is read. It was not chosen to fit: ψ_T = 0.8 matches the thesis best, and 0.7 does not. With ψ_T = 0.7, T1 = 0.489 s and the base shear is 296.04 kN, 11.8 % above the thesis (`anchor_seismic_runs.csv`).

The response-spectrum method (three modes, 99.6 % of the mass) agrees with the base-shear method within 6.4 % at storeys 1-3. With the bare-frame period it is 15.3 % lower at the roof, because the base-shear method's top force is generous for a four-storey frame. With ψ_T = 0.7 the spectrum method is 2.0-5.5 % higher at every storey (`anchor_rsa.csv`). The largest drift is 43 % of the 1/550 limit, so drift does not govern.

The 3D model on the drawing grid gives a transverse T1 of 0.622 s against 0.698 s for the 2D frame (`anchor_3d_periods.csv`). The 2D frame is 12 % longer because it carries the mass of a 7.2 m strip, where the drawn frames carry 5.49 m on average (D25). Any period or base shear the papers quote for the real building comes from the drawing grid.

### 4.4 Design checks

The checks use GB 50010 values read in the author's translation and the thesis combinations, with the seismic demand multiplied by γ_RE = 0.75 for beam flexure (`anchor_design_check.csv`, `anchor_design_columns.csv`).

All 60 beam sections design as singly reinforced; the largest ξ is 0.147. Of the 18 thesis beam rows, 16 pass on both the printed area and the printed bars. The two that fail are at level 1, AB ends, and fail only on the bars: the printed area is 1472 mm² but the printed bars are 3C20 and 3C16. The mirrored CD ends have 3C25, so I read these as transcription errors in the bar column (D10) [J]. The margin at level 1 is thin: three rows have less than 15 % spare steel, and the flags move with where the moment is read and with which code edition sets the seismic factors.

Every column passes the axial ratio: the largest is 0.320 at the ground-storey B and C columns, against 0.85. Every column fails the minimum steel: 4C22 is 0.422 % of the section against 0.75 %. This is a thesis error under the codes it cites, not a code-version difference (B6).

The thesis's own design table (§9.2) is not internally consistent. Its A_s,req cannot be reproduced from its own moments (D26), and its roof moments for CD are not the mirror of AB on a symmetric frame (D27). Neither column is a target.

## 5. Embodied carbon

A1-A3 carbon uses one factor set, GB/T 51366-2019 Table D.0.1 (`results/anchor_carbon.csv`). C40 has no row in that table, so its factor is the mean of the C30 and C50 rows [J]. The values were read from a third-party copy, and the author is to confirm them in an official copy. The planned second set, ICE, cannot be used: its free version may not be redistributed, and ShellBench publishes its factor file openly (D29). So the playbook's "both factor sets" becomes one set here, with the factor uncertainty carried by the planned Monte Carlo band [J].

Totals are the sums of the element rows in `anchor_carbon.csv`:

| Plan | Thesis steel | Code steel |
|---|---|---|
| Grid (primary) | 128.2 kgCO₂e/m² | 129.8 kgCO₂e/m² |
| Drawn (sensitivity) | 133.0 kgCO₂e/m² | 134.7 kgCO₂e/m² |

For the grid plan with the thesis steel, the slabs carry 53.55 kgCO₂e/m², 42 % of the total and the largest single element. Columns follow with 27.90, then longitudinal beams 15.36, frame beams 14.01, footings 13.62 and secondary beams 3.73. The slabs also hold 47 % of the concrete (0.119 of 0.254 m³/m², `anchor_quantities.csv`). So the element a thin-shell floor would replace is the largest carbon item in this building.

Code-minimum column steel adds only 1.6 kgCO₂e/m² here, because the code steel for the beams is lower than the thesis steel and offsets part of it. The steel per m² is 17.9 kg (thesis) and 18.6 kg (code).

## 6. What this anchor can and cannot claim

It can claim that the frame model reproduces the thesis gravity analysis wherever the thesis arithmetic holds. The remaining differences have named causes: axial shortening, or a flagged thesis error. Two separate implementations of the design checks gave the same numbers to the digit (Claude in the app and Claude Code), so a coding error in either is unlikely [J]. The take-off and the carbon count are reproducible from the code and one factor file.

It cannot claim a validated wind drift, because the thesis drifts cannot come from any single frame. It cannot claim a validated seismic base shear either: the thesis hides its period and weights, and the anchor's ψ_T rests on a clause not yet read in a primary copy. The carbon number rests on one factor set, read from a third-party copy, with an interpolated C40 factor. The boundary is the structure only: no walls, stairs, finishes, ground slab or wastage (`anchor_notes.md`, Day 12 rule 1). The 3D model is a symmetric rectangle; the real building is E-shaped with stair cores, so torsion is not represented. And the thesis building itself is under-reinforced in its columns, so it is a model of a design as drawn, not of a code-compliant baseline. The generator must apply the code minimum, or the shell floor's saving will look too large [J].

## 7. Open items before Paper 1 cites this report

- GB/T 51366 Table D.0.1 values confirmed in an official copy (author).
- JGJ 3-2010 cl. 4.3.17 (ψ_T) and GB 50011 cl. 5.2.2 read in primary copies; f_t = 1.71 N/mm² still rests on the translation only.
- GB 50007 clause numbers behind the footing rule (D28).

## Sources

Thesis: Syed Nafiz Reja Hasib, undergraduate thesis (completed 29 May 2023), cited by section and table. Codes: GB 50010-2010 (author's English translation; Chinese 2015 edition for three values), GB 50011-2010, GB 55001-2021, GB 55002-2021, GB/T 51366-2019; clause numbers as given in `docs/anchor_notes.md`. Flags D1-D29: `validation/thesis_values/README.md` and `docs/anchor_notes.md`.

AI use: Claude drafted this report from the files named above; the author checks every sentence and number before release.

© 2026 Syed Nafiz Reja Hasib. All rights reserved.
