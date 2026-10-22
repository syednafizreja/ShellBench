# ShellBench log

## Day 0 - 18 Oct 2026
- Env 'research' uses Python 3.12 (OpenSeesPy needs python312.dll)
- Installed: gmsh, OpenSeesPy, CalculiX 2.23, numpy, scipy, pandas, matplotlib, scikit-learn, pytest
- Fixed: missing Documents folder, conda in PowerShell, Git PATH
- Claude Code connected; Project created with env research / Py 3.12

## Day 1 - 19 Oct 2026
Done: package layout, CLAUDE.md, README, 8 week issues; commit 148360f pushed.
Checked: pytest 2 passed; git ls-files thesis_source empty (thesis not on GitHub).
Problems: gh CLI not found in VS Code terminal (PATH); issues added by hand instead.
Tomorrow: Day 2, build docs/baseline_spec.md; have thesis calc sheets and GB 50010/50011 to hand.

## Day 2 - 20 Oct 2026
Day 2 done: docs/baseline_spec.md lists every model input with its thesis source and 16 inconsistencies (B1-B16), each with my decision and reason. Carried forward: Tg used in alpha1 unconfirmed (B5); T1 and Gi computed by OpenSeesPy (B9); T 8-12 row 5 spurious (B4); T 9.3 axial forces wrong; generator rounding rule for the 0.85 axial limit (B16); walls in the carbon boundary (B15).

## Day 3 - 21 Oct 2026
Day 3 done: six CSVs in validation/thesis_values/ (beam-end moments, column axial forces, D-values T 7-6, wind drift T 8-2, seismic shear and drift T 8-12, beam steel s9.2), each row with thesis source and flag; tests/test_thesis_values.py checks units in headers and no empty cells (pytest 21 passed).
Hand checks: (1) ground A/D D-value from s2.6 stiffnesses: K = 0.6315, alpha_c = 0.4300, D = 19 241 N/mm vs printed 19 302 (0.3 %). (2) T 8-12 level 1: du = 363.06e3 / 92 842 = 3.91 mm vs printed 4.04 (printed 3.3 % high); theta = 4.04 / 4550 = 0.000888 matches exactly. Typing confirmed; the differences are in the thesis arithmetic, not the typing.
Carried forward: flags D1-D12 (validation/thesis_values/README.md), notably T 7-6 K and alpha_c not reproducible (D6), T 8-2 du != V/sum_D (D7), T 8-12 du 3.3-3.9 % above V/sum_D (D9), s9.2 As_prov vs bars (D10). The anchor report must name these.
Tomorrow: Day 4, literature and the gap matrix.

## Day 4 - 22 Oct 2026
Day 4 done: docs/gap_matrix.md (20 papers, 2020-2026 only; 17 rows reviewed by me against the evidence locators; rows 1, 3, 20 not read in full) with gap statements G1-G4; docs/reading_list.md with DOI and free-copy links (all DOIs checked, no mismatches).
Stress test: docs/goal_stress_test.md. No 2020-2026 paper found that puts thin-shell floors in a seismically designed frame. Holes H1-H9; I adopted the three main fixes (PGA sweep 0.05-0.40 g, best-conventional-floor baseline, topping thickness + diaphragm check). Revised question in docs/research_question.md and README.
Carried forward: page numbers p. [?] in the gap matrix; full text for Hawkins 2020, Ismail & Mueller 2021, Fang et al. 2023; grade-dependent detailing for intensities 8-9 in the redesign loop; charter PDF to be reissued with the new question.
