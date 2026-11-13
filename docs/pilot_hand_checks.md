# Pilot hand checks (Day 19, 5 Nov 2026)

Checked: S. N. R. Hasib, 5 Nov 2026.

Buildings: s04-p010 (the anchor case), s03-p030 and s06-p040. Values are from `results/family_rc_pilot.csv` after the R11 best_ratio rerun (PR #112).
Script: `scripts/hand_check_pilot.py`. It calls no generator function and imports only cited constants.

## Method

| Quantity | Hand method | Simplifications [J] |
|---|---|---|
| Gravity load G_E | Take-down by tributary length from the anchor input loads; live load × 0.5 | Walls at every level; half a column above and below each level |
| T1 | Rayleigh, with the D-value (Muto) storey stiffness, × psi_t = 0.7 | Shear-building model; beam I × 2.0 as in the generator |
| F_Ek | alpha1 × 0.85 G_E (cl. 5.2.1); spectrum constants from `seismic.py` (cl. 5.1.5) | No top additional force; no minimum shear check |
| Storey drift | V_i / ΣD_i, with D = α·12i_c/h² | Centreline dimensions; no rigid joint zones |
| Axial ratio | (1.3 N_GE + 1.4 N_E)/(f_c A); N_E from the cantilever method | Equal column areas |

## Results

| Building | Quantity | Hand | Generator | Hand / generator |
|---|---|---|---|---|
| s04-p010 | T1 [s] | 0.597 | 0.549 | 1.09 |
| | Max drift [-] | 1/1012 | 1/1163 | 1.15 |
| | Axial ratio [-] | 0.459 | 0.439 | 1.05 |
| s03-p030 | T1 [s] | 0.368 | 0.326 | 1.13 |
| | Max drift [-] | 1/508 | 1/637 | 1.25 |
| | Axial ratio [-] | 0.257 | 0.235 | 1.09 |
| s06-p040 | T1 [s] | 0.393 | 0.378 | 1.04 |
| | Max drift [-] | 1/526 | 1/606 | 1.15 |
| | Axial ratio [-] | 0.448 | 0.437 | 1.03 |

## Reading

- All nine values agree within 25 %. Every hand value is higher than the generator's. This is the expected direction: a shear-building D-value model with no rigid joint zones is softer than the frame analysis [J].
- The tolerances (period ±20 %, drift ±30 %, axial ratio ±20 %) were set after the run, not before. Read them as judgement, not as a preset pass mark [J].
- **Open point.** For s03-p030 and s06-p040, the hand drift is above the 1/550 limit (Table 5.5.1), while the generator's drift is below it, with margins of 14 % and 9 %. The hand method is approximate, so this does not show a fault. It does mean that the drift pass at 0.30-0.40 g depends on the frame analysis and is not robust to model choice [J]. Proposed follow-up: a sensitivity run with the beam I factor at 1.5 instead of 2.0 (spec M7), before Paper 1 Methods. This run is done; see below.

## Sensitivity: beam I factor 1.5 (5 Nov 2026)

Run: `python -m shellbench.batch --beam-i-factor 1.5 --out results/family_rc_pilot_beam_i15`. Hand check: `python scripts/hand_check_pilot.py results/family_rc_pilot_beam_i15.csv 1.5`. The hand and generator runs use the same factor.

- The status counts are unchanged: 34 ok and 2 outside_code.
- The generator redesigns 11 buildings with beams 50-100 mm deeper; columns are unchanged.
  - Every ok row still passes 1/550, at a worst drift of 0.001805.
  - Building carbon changes by -1.6 % to +0.3 % (median -0.4 %).

| Building | Period hand / gen | Drift hand / gen | Axial hand / gen |
|---|---|---|---|
| s04-p010 | 0.637 / 0.582 (1.09) | 1/980 / 1/1123 (1.15) | 0.459 / 0.436 (1.05) |
| s03-p030 | 0.394 / 0.348 (1.13) | 1/492 / 1/573 (1.16) | 0.256 / 0.233 (1.10) |
| s06-p040 | 0.419 / 0.400 (1.05) | 1/512 / 1/561 (1.10) | 0.435 / 0.404 (1.08) |

**Finding [J].** The hand-to-generator drift gap narrows from 1.15-1.25 to 1.10-1.16. But the hand drift for s03-p030 and s06-p040 is still above 1/550. So the beam factor does not explain the gap. The hand D-value method stays higher than the matrix frame analysis, by much the same margin, under both factors. It looks like a method difference, not an error in the generator.

**Decision (the AI assistant).**

- Keep 2.0 as the primary value, as set by spec M7 (Th §2.6).
- Report 1.5 as a sensitivity row; carbon moves by less than 2 %.
- State in Paper 1 Methods that the drift pass at 0.30-0.40 g rests on the frame analysis, and that a D-value hand check gives drifts 10-25 % higher.
- No result file was changed by this check.
