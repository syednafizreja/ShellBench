# GB 50010-2010 design values for Day 11 (design checks)

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

Read on 27 Oct 2026 by Claude from the English translation of GB 50010-2010 that the author uploaded ("Code for Design of Concrete Structures", China Architecture & Building Press, 2010; the translation itself says the Chinese text rules where they differ). Page numbers are the printed page numbers of that translation, located from the page markers in its text, so treat them as ±1 page. The file is not committed. Two limits, as for GB 50011 on 26 Oct: it is a translation, and it is the 2010 issue, not the 2015 revision. Whether the 2015 revision changed any value below is not known [?]. Values computed from the code's own formulas are marked "computed".

Materials of the anchor: C40 concrete (spec X4), HRB400 bars (spec X5), seismic grade three (spec S5), frame structure.

## Materials

| Quantity | Value | Source |
|---|---|---|
| f_c, C40 | 19.1 N/mm² | Table 4.1.4-1, p. 18 |
| f_t, C40 | 1.71 N/mm² | Table 4.1.4-2, p. 18 |
| E_c, C40 | 3.25 × 10⁴ N/mm² | Table 4.1.5, p. 19 (matches spec X4) |
| G_c | 0.4 E_c | cl. 4.1.5, p. 19 |
| ν_c | 0.2 | cl. 4.1.5, p. 19 |
| f_y = f'_y, HRB400 | 360 N/mm² | Table 4.2.3-1, p. 21 (matches spec X5) |
| E_s, HRB400 | 2.00 × 10⁵ N/mm² | Table 4.2.5, p. 22 |

## Flexure (rectangular stress block)

| Quantity | Value | Source |
|---|---|---|
| α1 | 1.0 (grade ≤ C50) | cl. 6.2.6, p. 34 |
| β1 | 0.80 (grade ≤ C50) | cl. 6.2.6, p. 34 |
| ε_cu | 0.0033 (formula gives 0.0034 for f_cu,k = 40, capped at 0.0033) | cl. 6.2.1, formula 6.2.1-5, p. 32-33 |
| ξ_b | 0.518 = β1 / (1 + f_y / (E_s ε_cu)) = 0.80 / (1 + 360 / 660) | computed, formula 6.2.7-1, p. 34 |

## Minimum longitudinal steel

| Member | Value for C40 / HRB400 | Source |
|---|---|---|
| Flexural member, tension side (non-seismic) | max(0.20 %, 45 f_t / f_y) = 0.214 % (computed) | Table 8.5.1, p. 101 |
| Compression member, all bars (non-seismic) | 0.55 % (400 MPa bars); one side 0.20 % | Table 8.5.1, p. 101 |
| Frame beam, seismic grade III, support | max(0.25 %, 55 f_t / f_y) = 0.261 % (computed) | Table 11.3.6-1, p. 156 |
| Frame beam, seismic grade III, mid-span | max(0.20 %, 45 f_t / f_y) = 0.214 % (computed) | Table 11.3.6-1, p. 156 |
| Frame column, grade III, middle and side, frame structure | 0.7 % + 0.05 % for 400 MPa bars = 0.75 %; each side ≥ 0.2 % | Table 11.4.12-1 and notes 1-2, cl. 11.4.12, p. 163 |
| Frame column, grade III, corner | 0.8 % + 0.05 % = 0.85 %; each side ≥ 0.2 % | Table 11.4.12-1 and note 2, p. 163 |

## Seismic checks

| Quantity | Value | Source |
|---|---|---|
| Axial compression ratio limit, frame structure, grade III | 0.85 (shear span ratio > 2, ≤ C60) | Table 11.4.16, p. 164 (matches baseline_spec) |
| γ_RE, flexural members | 0.75 | Table 11.1.6, p. 152 |
| γ_RE, columns, axial ratio < 0.15 / ≥ 0.15 | 0.75 / 0.80 | Table 11.1.6, p. 152 |
| γ_RE, shear (inclined section) | 0.85 | Table 11.1.6, p. 152 |

## What this already tells us

The thesis columns have 4C22 = 1520 mm² on 600 × 600 mm (spec R1), which is 0.42 % of the gross section. That is below the 0.75 % of Table 11.4.12-1 for a grade-three frame column with 400 MPa bars (computed). This is flag B6 from 20 Oct, now with a code value behind it. Day 11 will list it with the other members.

Correction to an earlier [?]: the shear modulus G_c = 0.4 E_c is cl. 4.1.5, not cl. 4.1.8 as written in `src/shellbench/anchor_3d.py` on Day 10. The value was right; the clause number was wrong (fixed on the Day 10 branch).

© 2026 Syed Nafiz Reja Hasib. All rights reserved.
