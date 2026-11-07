# Paper 1: numbers traceability

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

One row per number in the manuscript (academic-manuscript-writing §8). A number without a row does not go in the paper. If the manuscript and the repo disagree, the repo wins. Seeded on 5 Nov 2026 from the Methods skeleton; "Checked by Syed" stays empty until the author checks the value against the file.

| Manuscript location | Value | Source (file, function or table) | Commit or tag | Checked by Syed (date) |
|---|---|---|---|---|
| 2.2 | Spans 7.2 / 6.6 / 7.2 m; storeys 4.55 + 3 × 3.6 m | docs/baseline_spec.md G3, G5-G7; docs/anchor_report.md §2 | v0.1.0 | |
| 2.2 | Columns 600 × 600; beams 300 × 600 (AB, CD), 300 × 500 (BC) | Thesis §2.3-2.4; docs/anchor_report.md §2 | v0.1.0 | |
| 2.2 | Grid 38.4 × 21.0 m, 28 columns, 3 225.6 m² | docs/baseline_spec.md B11 | v0.1.0 | |
| 2.2 | Dead load: 40 targets, 11 above 10 %, median 4.2 % | results/anchor_gravity_dead.csv | v0.1.0 | |
| 2.2 | Live load: 40 targets, 26 above 10 %, median 28.5 % | results/anchor_gravity_live.csv | v0.1.0 | |
| 2.2 | Wind drift differences −45.5 to −87.4 % | results/anchor_wind.csv | v0.1.0 | |
| 2.2 | T1 0.698 s bare 2D; base shear 214.75 kN vs 264.77 kN | results/anchor_seismic.csv | v0.1.0 | |
| 2.2 | ψ_T = 0.7: T1 0.489 s, base shear 296.04 kN (+11.8 %) | results/anchor_seismic_runs.csv | v0.1.0 | |
| 2.2 | 3D T1 0.622 s | results/anchor_3d_periods.csv | v0.1.0 | |
| 2.2 | Largest column axial ratio 0.320 vs 0.85 | results/anchor_design_columns.csv | v0.1.0 | |
| 2.3 | Generator columns 500 × 500 vs thesis 600 × 600 | tests/test_generator_anchor.py; LOG Day 16 | [?] tag | |
| 2.3 | Pilot hand checks: hand/generator 1.03-1.25 | docs/pilot_hand_checks.md | [?] tag | |
| 2.4 | MacNeal-Harder ratios 0.9984 (roof), 0.9965 (hemisphere), 16 elements per side | results/benchmarks_convergence.csv | floor-r2 | |
| 2.4 | Library: 72 cases, 70-100 mm, concrete 0.071-0.104 m³/m², λ 9.0-33.2 | results/floor_library.csv; docs/floor_library.md | v0.3 [?] | |
| 2.6 | 36 conventional buildings; up to 72 variants; up to 2,592 rows | docs/data_card.md; docs/schedule.md (family size note) | [?] tag | |
| 2.7 | Factors C30 295, C40 340 (interpolated), HRB400 2340, tie EAF 3030, BOF 1990, crushed stone 2.18 | data/carbon_factors.csv | [?] tag | Official-copy check open |
| 2.7 | Raised floor 534.5 kgCO2e/t | data/carbon_factors.csv (Oval et al. 2023 Table 6) | [?] tag | 5 Nov 2026 |
| 2.8 | Smallest exact two-sided p: n = 4 0.083, n = 5 0.017, n = 6 0.0028 | arithmetic 2/n! | n/a | |
