# Anchor notes: why the model and the thesis differ

One line of explanation for every difference above 10 % between the anchor model and the thesis (Playbook Day 6). This file starts with the dead-load case (Day 5, 23 Oct 2026). The live-load case is added on Day 6.

Status: **draft by Claude, to be confirmed by the author.** Every explanation is [J] until the author has checked it against the thesis. Numbers come from `results/anchor_gravity_dead.csv` (written by `src/shellbench/anchor_frame.py`) or are arithmetic on printed thesis values, with the table named.

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

### Open for the author

1. Confirm or correct the two thesis-arithmetic findings: the missing roof BC shear, and the floor-1 column weight counted twice. If you agree, they become flags D13 and D14 in `validation/thesis_values/README.md`.
2. Decide which load set the anchor keeps for Day 6 onwards: the table-6.3 loads (primary) or the text loads.
3. Decide whether the interior eccentric moments at B and C belong in the load case. The figures leave them out, while the table and the B3 balance suggest they were used.
4. Note that Fig. 4-4 labels the AB beam weight 3.61 kN/m, but the fixed-end moments use 4.934 kN/m (§4.1). Decision B13 kept the printed 4.934 for frame beams, which agrees with the table.
