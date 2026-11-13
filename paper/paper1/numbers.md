# Paper 1: numbers traceability

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

One row per number in the manuscript (academic-manuscript-writing §8). A number without a row does not go in the paper. If the manuscript and the repo disagree, the repo wins. Seeded on 5 Nov 2026 from the Methods skeleton; "Checked by Syed" stays empty until the author checks the value against the file.

Check window, 13 Nov 2026 (the AI assistant) [J]: values were read again from the working tree on main after PR #177 (results/ unchanged since v0.5.0): the results/ and data/ rows by script; the geometry, generator-column and pilot hand-check rows by reading docs/anchor_report.md, tests/test_generator_anchor.py and docs/pilot_hand_checks.md. The two rows sourced to the thesis were checked against anchor_report §2 only, not the thesis. The "[?] tag" cells were resolved with `git tag --contains`. The "Checked by the AI assistant" column records that; the author to confirm each row. Corrections made: row 2.6 (row counts were the pre-release plan) and a rounding note on the dead-load median. Rows 3.x are new: the frozen H1-H4 numbers.

| Manuscript location | Value | Source (file, function or table) | Commit or tag | Checked by Syed (date) | Checked by the AI assistant (author to confirm) |
|---|---|---|---|---|---|
| 2.2 | Spans 7.2 / 6.6 / 7.2 m; storeys 4.55 + 3 × 3.6 m | docs/baseline_spec.md G3, G5-G7; docs/anchor_report.md §2 | v0.1.0 | | The AI assistant 13 Nov 2026 |
| 2.2 | Columns 600 × 600; beams 300 × 600 (AB, CD), 300 × 500 (BC) | Thesis §2.3-2.4; docs/anchor_report.md §2 | v0.1.0 | | The AI assistant 13 Nov 2026 |
| 2.2 | Grid 38.4 × 21.0 m, 28 columns, 3 225.6 m² | docs/baseline_spec.md B11 | v0.1.0 | | The AI assistant 13 Nov 2026 |
| 2.2 | Dead load: 40 targets, 11 above 10 %, median 4.2 % (exactly 4.25 %: the middle two are 3.5 and 5.0; anchor_report §3 prints 4.2 %. Write "4.3 %" or "4.25 %" in the paper [J]) | results/anchor_gravity_dead.csv | v0.1.0 | | The AI assistant 13 Nov 2026 |
| 2.2 | Live load: 40 targets, 26 above 10 %, median 28.5 % | results/anchor_gravity_live.csv | v0.1.0 | | The AI assistant 13 Nov 2026 |
| 2.2 | Wind drift differences −45.5 to −87.4 % | results/anchor_wind.csv | v0.1.0 | | The AI assistant 13 Nov 2026 |
| 2.2 | T1 0.698 s bare 2D; base shear 214.75 kN vs 264.77 kN | results/anchor_seismic.csv | v0.1.0 | | The AI assistant 13 Nov 2026 |
| 2.2 | ψ_T = 0.7: T1 0.489 s, base shear 296.04 kN (+11.8 %) | results/anchor_seismic_runs.csv | v0.1.0 | | The AI assistant 13 Nov 2026 |
| 2.2 | 3D T1 0.622 s | results/anchor_3d_periods.csv | v0.1.0 | | The AI assistant 13 Nov 2026 |
| 2.2 | Largest column axial ratio 0.320 vs 0.85 | results/anchor_design_columns.csv | v0.1.0 | | The AI assistant 13 Nov 2026 |
| 2.3 | Generator columns 500 × 500 vs thesis 600 × 600 | tests/test_generator_anchor.py; LOG Day 16 | v0.2.0 | | The AI assistant 13 Nov 2026 |
| 2.3 | Pilot hand checks: hand/generator 1.03-1.25 | docs/pilot_hand_checks.md | v0.2.0 | | The AI assistant 13 Nov 2026 |
| 2.4 | MacNeal-Harder ratios 0.9984 (roof), 0.9965 (hemisphere), 16 elements per side | results/benchmarks_convergence.csv | floor-r2 | | The AI assistant 13 Nov 2026 |
| 2.4 | Library: 72 cases, 70-100 mm, concrete 0.071-0.104 m³/m², λ 9.0-33.2 | results/floor_library.csv; docs/floor_library.md | v0.2.0 (unchanged to v0.5.0; rebuilt 13 Nov 2026 with the shell equilibrium check, identical) | | The AI assistant 13 Nov 2026 |
| 2.6 | 36 conventional buildings; 5,184 shell rows (36 buildings × 36 floor variants × 4 toppings): 4,856 ok, 288 outside code (frame height > 24 m, GB 50011 Table 6.1.1), 40 not converged. Corrected from "up to 72 variants; up to 2,592 rows" | results/family_shell.csv; docs/data_card.md | v0.4.0 (dataset DOI 10.5281/zenodo.24194144) | | The AI assistant 13 Nov 2026 |
| 2.7 | Factors C30 295, C40 340 (interpolated), HRB400 2340, tie EAF 3030, BOF 1990, crushed stone 2.18 | data/carbon_factors.csv | v0.3.0 | Official-copy check open | The AI assistant 13 Nov 2026 |
| 2.7 | Raised floor 534.5 kgCO2e/t | data/carbon_factors.csv (Oval et al. 2023 Table 6) | v0.3.0 | 5 Nov 2026 | The AI assistant 13 Nov 2026 |
| 2.8 | Smallest exact two-sided p: n = 4 0.083, n = 5 0.017, n = 6 0.0028 | arithmetic 2/n! | n/a | | The AI assistant 13 Nov 2026 |
| 3.1 | H1 partly supported: S_b > 0 in 32 of 33 buildings (97.0 %); S_b < S_f in 27; S_b min −0.33 %, median 5.66 %, max 30.68 % | results/verdicts_summary.csv (case base) | v0.5.0 | | The AI assistant 13 Nov 2026 |
| 3.1 | H1 under C1/C2 sensitivity: verdict "partly supported" in all six cases | results/verdicts_summary.csv | v0.5.0 | | The AI assistant 13 Nov 2026 |
| 3.1 | S_b with lateral carbon × 1.3125 (strip vs plan, data_card row 4): 32 of 33 positive, median 4.13 %, min −0.29 %, max 32.36 %; verdict unchanged. Factors 1.0 and 1.3125 bracket each building's S_b; exploratory, not preregistered [J] | scripts/strip_factor_bound.py | this PR | | The AI assistant 13 Nov 2026 |
| 3.2 | H2 not supported; H3 not supported (all six cases) | results/verdicts_summary.csv | v0.5.0 | | The AI assistant 13 Nov 2026 |
| 3.4 | H4 error ratio 2.27 (RMSE 25.62 vs 11.30 kgCO2e/m², unseen storeys vs random) | results/surrogate_accuracy.csv; preregistration §3 | v0.5.0 | | The AI assistant 13 Nov 2026 |
| 3.4 | H4 conformal coverage, unseen storeys pooled 73.3 % (folds 56.1-87.1 %), nominal 90 %; random split 90.1 % | results/surrogate_coverage.csv | v0.5.0 | | The AI assistant 13 Nov 2026 |
| 3.4 | H4 decision agreement 31/33 (93.9 %), needs 80 %; always-shell baseline 32/33 (97.0 %) | results/surrogate_decision_summary.csv | v0.5.0 | | The AI assistant 13 Nov 2026 |
| 3.1 | Grade-I caveat: 7 of the 33 buildings are grade I; the two largest S_b (17.3 % s07-p030, 30.7 % s08-p030) are among them with 1300 mm conventional columns. Without grade I: max 9.6 %, median 5.65 % | results/verdicts_buildings.csv (case base); preregistration C2 | v0.5.0 | | The AI assistant 13 Nov 2026 |
