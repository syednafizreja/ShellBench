# The GB 50011 base-shear method, worked on the thesis building

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

Learning note for Day 9 (27 Oct 2026), written on Day 7 (25 Oct 2026). It is a study aid, not a validation result. Every clause number below must be checked in your own copy of GB 50011-2010 (2016 edition) before `src/shellbench/seismic.py` cites it. Values I give from memory of the code are marked [?] until you confirm them; my judgement is marked [J].

## Why this method applies to the anchor

The base-shear method (底部剪力法) replaces the earthquake with one static force at the base, spread up the height. GB 50011 allows it for buildings up to 40 m tall whose deformation is mainly shear and whose mass and stiffness are fairly even over the height (cl. 5.1.2). The anchor is a regular four-storey frame about 15.35 m tall (4.55 + 3 × 3.6 m, baseline_spec G-rows), so it qualifies. The clause wording was cross-checked against a web transcription of GB 50011-2010 on 25 Oct 2026; the author should still read it in their copy. Day 10's response-spectrum run is the independent check.

## The six steps

**1. Representative gravity load G_E (cl. 5.1.3 [?]).** For each storey, take all dead load plus a fraction of the variable load. From memory, Table 5.1.3 gives 0.5 for floor live load in ordinary civil buildings, 0.5 for snow, and 0 for roof live load [?]. So storey i has G_i = dead_i + 0.5 × live_i, with roof live left out. This is why the live-load choice from Day 6 (2.0 against 2.5/3.0 kN/m², flag D20) reaches the seismic forces.

**2. Fundamental period T1.** The thesis prints no period (baseline_spec S7, decision B9), so Day 9 will report the OpenSeesPy modal period. A bare-frame model leaves out the stiffness of the infill walls, so its period is longer than the real building's. Design practice reduces the computed period for infilled frames by a factor of about 0.6-0.7 (JGJ 3-2010 cl. 4.3.17 [?]). Whether the anchor applies that factor is your decision on Day 9, and it changes α1 directly.

**3. Seismic influence coefficient α1 (cl. 5.1.4 and 5.1.5 [?]).** Read α_max from Table 5.1.4-1 for frequent earthquakes at 7 degrees, 0.10 g; the value is 0.08 (confirmed by the author in Table 5.1.4-1, 25 Oct 2026). Tg = 0.35 s is fixed by your decision B5 (site class II, group 1). With 5 % damping the curve has four parts: a rise from 0.45 α_max at T = 0 to α_max at 0.1 s; a plateau at α_max up to Tg; a curved fall α = (Tg/T)^0.9 α_max from Tg to 5Tg; and a straight fall after 5Tg [?].

**4. Base shear F_Ek (cl. 5.2.1 [?]).** F_Ek = α1 G_eq, with G_eq = 0.85 ΣG_i for a multi-storey building.

**5. Storey forces (cl. 5.2.1 [?]).** F_i = G_i H_i / Σ(G_j H_j) × F_Ek (1 − δ_n), where H_i is the height of level i above the base. A top additional force ΔF_n = δ_n F_Ek is added at the roof. From memory, Table 5.2.1 gives δ_n = 0.08 T1 + 0.07 when Tg ≤ 0.35 s and T1 > 1.4 Tg, and δ_n = 0 when T1 ≤ 1.4 Tg [?]. For the anchor, 1.4 Tg = 0.49 s, so whether ΔF_n exists depends on which side of 0.49 s the period lands.

**6. Checks that follow.** Minimum shear coefficient λ (cl. 5.2.5 [?]; I recall 0.016 at 7 degrees, 0.10 g [?]). Elastic drift limit 1/550 for frames (cl. 5.5.1, Table 5.5.1; already baseline_spec S11). Load combination 1.2 G_E + 1.3 E_h for the anchor (cl. 5.4.1, confirmed 24 Oct) and 1.3/1.4 for the generator (GB 55002-2021 cl. 4.3.2, flag D21).

## What Table 8-12 already tells us

The thesis prints storey shears but not the steps behind them. Subtracting consecutive shears in Table 8-12 gives the storey forces, and dividing by height shows the pattern the thesis used. Heights assume 4.55 m then 3.6 m per level; level 5 is the row you judged spurious (B4).

| Level | V_i (kN, T 8-12) | F_i = V_i − V_i+1 (kN) | H_i (m) | F_i / H_i (kN/m) |
|---|---|---|---|---|
| 1 | 363.06 | 31.03 | 4.55 | 6.82 |
| 2 | 332.03 | 54.56 | 8.15 | 6.69 |
| 3 | 277.47 | 77.62 | 11.75 | 6.61 |
| 4 | 199.85 | 101.56 | 15.35 | 6.62 |
| 5 | 98.29 | 98.29 | 18.95 | 5.19 |

For levels 1-4, F_i/H_i stays between 6.61 and 6.82 kN/m. That is what step 5 gives when the storey weights G_i are nearly equal, so the thesis almost certainly used the base-shear distribution with similar floor weights [J]. Level 4 shows no jump that a ΔF_n would cause, unless it was put on level 5 [J]. This is a reading of the numbers, not something the thesis states.

## A sense of scale, before Day 9

Because F_Ek = α1 G_eq, the printed base shear of 363.06 kN implies a G_eq for each trial period. These rows use the step-3 curve with α_max = 0.08 (confirmed) and Tg = 0.35 s. They are illustrations, not results.

| Trial T1 (s) | α1 | Implied G_eq (kN) | Implied ΣG_i = G_eq/0.85 (kN) |
|---|---|---|---|
| 0.35 | 0.0800 | 4 538 | 5 339 |
| 0.45 | 0.0638 | 5 690 | 6 694 |
| 0.55 | 0.0533 | 6 816 | 8 019 |
| 0.65 | 0.0458 | 7 922 | 9 320 |
| 0.75 | 0.0403 | 9 011 | 10 601 |

The 7.2 m strip of one transverse frame covers about 7.2 × 21.0 = 151 m² per floor (baseline_spec G4 and B10), or about 605 m² over four floors. A total of 7 000-9 000 kN would be roughly 12-15 kN/m², which is a normal range for an RC frame with infill walls [J]. So a period near 0.55-0.65 s would be consistent with the printed shears. If Day 9 finds T1 well outside that, the cause is more likely the period (infill factor) or the weights than the method.

## Clauses to read before Monday evening

1. GB 50011-2010 cl. 5.1.2 (when the base-shear method may be used).
2. Cl. 5.1.3 and Table 5.1.3 (combination coefficients for G_E).
3. Cl. 5.1.4, Tables 5.1.4-1 and 5.1.4-2 (α_max and Tg).
4. Cl. 5.1.5 and Fig. 5.1.5 (the design spectrum curve, damping factors).
5. Cl. 5.2.1 and Table 5.2.1 (F_Ek, F_i and δ_n).
6. Cl. 5.2.5 (minimum seismic shear coefficient).
7. JGJ 3-2010 cl. 4.3.17, or the period-reduction rule in your own course notes, for the infill factor.

Still open on 25 Oct 2026: Table 5.1.3 coefficients, the cl. 5.1.5 curve shape, Table 5.2.1 δ_n and Table 5.2.5 λ. The web transcription shows these tables only as images, so they need the author's copy. Write the confirmed value next to each [?] above. Seismic.py will only use values you have confirmed.

© 2026 Syed Nafiz Reja Hasib. All rights reserved.
