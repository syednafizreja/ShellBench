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

Later on 22 Oct: all sources now legal open copies (Hawkins 2020 read via Bath accepted manuscript; Ismail & Mueller 2021 dropped, no open copy). Fang et al. 2023 review still unread: its only open copy (MIT repository) refuses automated downloads; a retry is scheduled. Further open-access search added four papers read in full (gap matrix rows 21-24): Abd-Elhamed 2023 (floor system changes low-rise base shear coefficient 0.102-0.312), Zhang L. 2026 (GB 50011 frames redesigned with dampers, GB/T 51366 factors, -17.4% carbon), Mutlu 2025 (CLT vs RC, base shear about one-third), NIST SP 1324 (2024 review; lowest-carbon system may change in seismic regions). Rows 21-24 await my review. New docs/q1_standards.md: journal and COPE rules we follow daily (JOBE confirmed Q1, SJR 2025).
Compliance: sources - 4 new DOIs checked on OpenAlex, all open access (CC BY, CC BY-NC-ND, US government). AI use - Claude searched, read and summarised the papers, drafted rows 21-24 and q1_standards.md; I review. Numbers - every number in rows 21-24 quoted from the paper with a section locator. Data - nothing confidential committed; thesis_source/ not tracked.

Later still on 22 Oct (closing Day 4 carry-overs, on my instruction): Fang et al. 2023 read in full. The MIT bitstream URL returned 429, but the same file came through the DSpace REST content endpoint (CC BY-NC-ND manuscript). Its version is unclear: the cover sheet says "author's final manuscript", while OpenAlex says "submittedVersion" [?]. Gap matrix row 20 filled: it treats seismic risk only as a caveat to load reduction, and says floor systems are one of the most decisive EC variables. The cloud retry routine is now disabled. Claude checked rows 20-24 against the PDFs and marked them [x]ᶜ (Claude-checked, not yet read by me). Corrections:
- Row 21: designed to ASCE 7-16, not 7-10. The buildings have eight RC shear walls. Its Conclusions (p. 19) contradict its Results (p. 12) on the height trend.
- Row 22: only the typical 3.6 m storey matches our anchor (theirs 4.6/4.2 m below that). Its carbon boundary includes transport and construction energy.
- Row 23: the RC scheme is all shear walls, and the foundation design is not reported.
- q1_standards R14: the "33%" was wrong. NIST counts 33 review articles and prints no percentage.
Page numbers were added for rows 20-24.
Compliance: sources - no new references; row 20 now read from a legal open copy. AI use - Claude downloaded, read and checked the papers and edited gap_matrix.md, reading_list.md and q1_standards.md; I still need to read rows 20-24 myself before citing them (R4). Numbers - every new number is quoted from the paper with a page. Data - nothing confidential committed; thesis_source/ not tracked. Repo - branch day04-review-rows, PR merged, Week 1 issue updated.
Update, 22 Oct: I have read and reviewed rows 20-24 myself; Claude's PDF check was a cross-check of my reading. All 23 rows in the gap matrix are now ticked [x] (the [x]ᶜ marker is removed). This meets R4.
