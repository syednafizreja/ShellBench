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

| File | Thesis source | Rows |
|---|---|---|
| gravity_beam_end_moments.csv | s6.2.1 table "6.3" (dead), s7.2 table "7.2" (live): final row of each floor block | 48 |
| gravity_column_axial_forces.csv | s6.2.1 Table 4-9 (dead); s7.3 unnumbered table after Table 7-4 (live) | 16 |
| lateral_stiffness_d_values.csv | s7.3 Table 7-6 | 4 |
| wind_drift.csv | s8.2 Table 8-2 (sum_D also in Table 7-7) | 4 |
| seismic_storey_shear_drift.csv | s8.4 Table 8-12 | 5 |
| beam_steel_areas.csv | s9.2 unnumbered beam reinforcement table | 18 |

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

## Hand checks (Day 3)

1. D-value, ground-storey A/D column (Table 7-6, 19302 N/mm).
   Inputs from s2.6 / Table 1: i_b(AB) = 4.875e10 N*mm, i_c(ground) = 7.72e10 N*mm, h = 4550 mm.
   K = i_b / i_c; alpha_c = (0.5 + K) / (2 + K); D = alpha_c x 12 i_c / h^2.
2. Seismic storey drift, level 1 (Table 8-12).
   du = V / sum_D = 363.06e3 N / 92842 N/mm; theta = du / h with h = 4550 mm.

Results are recorded by the author in LOG.md.
