# Thesis validation targets

Values typed from the author's thesis (Day 3, 21 Oct 2026). Each file is a
validation target for the anchor model (Layer 1) or the generator (Layer 2).
Every row gives its thesis section and table in `source`. Values are copied
exactly as printed, including printed precision; nothing has been corrected.
Where a value looks wrong, the row says so in `flag` and the value is left as
printed.

Header rule: every column is `name [unit]`. `[text]` marks a label,
`[-]` a dimensionless number. Units: kN, kN*m, N/mm, mm, mm2.
`tests/test_thesis_values.py` checks this rule and that no cell is empty.
In the two Day 6 files, `[mixed]` columns hold distribution factors [-] or
moments [kN*m] (table 7.2, by `row`), and moments [kN*m] or shears [kN]
(Table 8-13, by `force`).

| File | Thesis source | Rows |
|---|---|---|
| gravity_beam_end_moments.csv | s6.2.1 table "6.3" (dead), s7.2 table "7.2" (live): final row of each floor block | 48 |
| gravity_column_axial_forces.csv | s6.2.1 Table 4-9 (dead); s7.3 unnumbered table after Table 7-4 (live) | 16 |
| lateral_stiffness_d_values.csv | s7.3 Table 7-6 | 4 |
| wind_drift.csv | s8.2 Table 8-2 (sum_D also in Table 7-7) | 4 |
| seismic_storey_shear_drift.csv | s8.4 Table 8-12 | 5 |
| beam_steel_areas.csv | s9.2 unnumbered beam reinforcement table | 18 |
| live_distribution_table_7_2.csv | s7.2 table "7.2", every cell (factors, joint moments, fixed-end moments, steps, finals); added Day 6 | 296 |
| combination_beam_roof.csv | s8.7 Table 8-13, level-5 (roof) rows: dead, live, wind and the first combination column; added Day 6 (D-support rows added in the Day 6 cross-check) | 15 |

## Reading notes

- Floor labels in the moment-distribution tables are not printed. Blocks are
  read top to bottom as floors 4, 3, 2, 1; the distribution factors (0.666 /
  0.333 top, 0.436 / 0.345 ground) and the labelled mid-span tables confirm
  the order.
- Beam-end moments keep the thesis sign convention: the fixed-end row shows
  -ql^2/12 at the left end of each span and +ql^2/12 at the right.
- Beam-end moments are centre-line values before any reduction to the column
  face or amplitude modulation (that comes later, in Table 8-13).
- Day 2 decisions apply: 4 storeys, ground column 4.55 m (B4); level 5 in
  Table 8-12 and floor "5" in s9.2 are kept as printed and flagged.

## Flags found while typing (D-numbers)

Computed checks are marked [J]; they are arithmetic on printed values, not
corrections.

- D1. Dead, floor 3: CD right end 97.64 breaks symmetry with AB left -96.15.
- D2. Live, floor 2: CD left end -3.38 repeats the BC value; symmetry gives -27.92.
- D3. Live, floor 2: Table 7-1 and Table 7-2 use 27.58 for the AB right end; the distribution table gives 27.92.
- D4. Live axial, B/C floor 3: 30.40 + 32.77 + 108.32 = 171.49, printed 409.08; floors 2 and 1 carry the error.
- D5. D-value hand check, ground A/D column (see below): about 0.3 to 1.0 % from the printed 19302.
- D6. Table 7-6 K and alpha_c are not reproducible from the s2.6 line stiffnesses for three of four rows (alpha_c = 1.02 > 1 is impossible). Recomputed D [J]: ground B/C 25553 (printed 27120), typical A/D 18056 (19621), typical B/C 33591 (34123). The printed sums still hold: 2 x (19621 + 34123) = 107488; 2 x (19302 + 27120) = 92844 against 92842 printed.
- D7. Table 8-2 du does not equal V / sum_D: level 1 gives 0.46 mm, printed 0.78.
- D8. Table 8-2 theta for levels 2-4 is u / h (cumulative), not du / h.
- D9. Table 8-12 du is 3.3 to 3.9 % above V / sum_D at every level; theta = du / h holds exactly.
- D10. s9.2 As_prov does not match the bar designation in 6 rows (e.g. 3C20 = 942 mm2, printed 603).
- D11. s9.2 floor 1 CD middle: As_req 2030.66 > As_prov 603.
- D12. s9.2 column "gammaRE x M" is printed in N.mm but equals 0.3 x M in kN*m (e.g. 0.3 x 119.78 = 35.934), while s9.1 states gammaRE = 0.75. Header here says kN*m [J].
- D13. Dead, Table 4-9, B/C roof: N_top = 214.11 + 61.88 = 275.99 includes only the AB beam shear; the BC beam shear (33.75, Table 4-7) is missing. Floors 3-1 carry the omission down. Found Day 5 (anchor model), confirmed by the author 23 Oct 2026.
- D14. Dead, Table 4-9, floor 1: N_top exceeds the running sum by 9.46 kN (A/D: 810.69 + 167.77 + 85.44 = 1063.90, printed 1073.36) and 9.15 kN (B/C). 9.46 = 45.32 - 35.86, so the ground-column weight is counted twice [J]. Confirmed by the author 23 Oct 2026.
- D15. Dead, s6.2.1 table 6.3: final member-end moments do not balance at joints A1 and B1-B4 (out by 39-80 kN*m; e.g. B4: 68.77 - 52.84 - 67.74 = -51.81, should be 0). Beam ends at those joints are arithmetic errors in the hand distribution, not model targets to match. Confirmed by the author 23 Oct 2026 (B4 checked by hand). Details in docs/anchor_notes.md.

Found on Day 6 (24 Oct 2026). **Accepted by the author on 24 Oct 2026**
(D16 and D17 in their revised wording); Claude Code cross-checked. Details and
arithmetic in docs/anchor_notes.md (live-load and combination sections);
the checks are coded in `src/shellbench/thesis_checks.py`.

- D16. Table 8-13: the column headed "1.3 Dead load + 1.5 x live" equals 1.0 x dead + 1.5 x live in 13 of the 15 roof rows (e.g. -67.76 + 1.5 x -22.18 = -101.03). The two D-support rows (-44.495, 54.755) and all 15 level-1 rows fit neither 1.0 nor 1.3. The author checked the A-support arithmetic by hand on 24 Oct 2026.
- D17. Table 8-13: the dead and wind columns are cells of table 6.3, not frame forces (roof A support "V" 68.77 is the B4 left-beam final moment; the roof AB shear is 61.88, Table 4-9); the live column matches neither table 7.2 (roof A support -22.18 against -4.55) nor any other thesis table; the wind combination columns cannot be reproduced from simple factors a x D + b x L + c x W. Table 8-13 is therefore not a validation target.
- D18. Table 7.2, floors 2-4: printed finals are not the sums of their columns (up to 6.20 kN*m; 23.28 at floor 2, C right beam, which is D2).
- D19. Table 7.2: joints B4, B2, B1 do not balance even with the column sums (-4.40, +6.22, -27.67 kN*m), and the first distribution step at B is not factor x unbalanced moment.
- D20. Live load sets disagree: fixed-end moments imply AB 6.41 and BC 0.97 kN/m (6.41 = 2.0 kN/m2 office load x 3.6 x 0.8906 [J]); shears use 8.08 and 12.37; the text says BC carries no live load; the B/C axial sums use the roof BC shear 3.10 at every floor instead of 40.82 (Table 7-3).
- D21. Th s8.7 seismic combination: 1.2 x gravity + 1.3 x earthquake follows GB 50011-2010 cl. 5.4.1 and Table 5.4.1, but GB 55002-2021 cl. 4.3.2 (Tables 4.3.2-1 and 4.3.2-2; in force from 1 Jan 2022; thesis completed 29 May 2023) requires at least 1.3 and 1.4. Clause texts checked by Claude Code; the author to confirm them in their copies.
- D22 (accepted by the author 26 Oct 2026). Table 8-2 du implies storey stiffnesses V / du of 54 705, 35 088, 42 804 and 10 106 N/mm at levels 1-4. Storeys 2-4 are identical, so the printed du cannot come from one elastic frame. Extends D7. The pre-registered wind test fails on this (docs/anchor_notes.md, wind section).
- D23 (accepted by the author 26 Oct 2026). Roof W_k = 11.42 kN uses hj = 3.6 m in Table 8-1, as if a full storey stood above the roof. Half the top storey plus the 1.2 m parapet (Th s4.2) gives 3.0 m and 9.52 kN [J], so the roof force is 20 % high and the base shear 4.5 % high (safe side). The anchor keeps the printed forces.

D16 and D17 were revised on 24 Oct 2026 after Claude Code cross-checked
Table 8-13 against the thesis .docx (docs/anchor_notes.md, "Cross-check of
Table 8-13"). The same check found all 296 typed cells of table 7.2 equal
to the thesis.

## Hand checks (Day 3)

1. D-value, ground-storey A/D column (Table 7-6, 19302 N/mm).
   Inputs from s2.6 / Table 1: i_b(AB) = 4.875e10 N*mm, i_c(ground) = 7.72e10 N*mm, h = 4550 mm.
   K = i_b / i_c; alpha_c = (0.5 + K) / (2 + K); D = alpha_c x 12 i_c / h^2.
2. Seismic storey drift, level 1 (Table 8-12).
   du = V / sum_D = 363.06e3 N / 92842 N/mm; theta = du / h with h = 4550 mm.

Results are recorded by the author in LOG.md.
