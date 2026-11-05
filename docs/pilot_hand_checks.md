# Pilot hand checks (Day 19, 5 Nov 2026)

Checked by the AI assistant on 5 Nov 2026. **Author to confirm.**

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
- The tolerances (period ±20 %, drift ±30 %, axial ratio ±20 %) were set by the AI assistant after the run, not before. Read them as judgement, not as a preset pass mark [J].
- **Open point.** For s03-p030 and s06-p040, the hand drift is above the 1/550 limit (Table 5.5.1), while the generator's drift is below it, with margins of 14 % and 9 %. The hand method is approximate, so this does not show a fault. It does mean that the drift pass at 0.30-0.40 g depends on the frame analysis and is not robust to model choice [J]. Proposed follow-up: a sensitivity run with the beam I factor at 1.5 instead of 2.0 (spec M7), before Paper 1 Methods.
- No result file was changed by this check.
