# v1.0 gate (software DOI)

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

v1.0 mints the software DOI (GitHub release, Zenodo). A DOI cannot be withdrawn, so v1.0 waits for the author's check window, 14-17 Nov 2026 (docs/schedule.md). Prepared by Claude Code on 13 Nov 2026 [J].

## Release step (one PR, after every box below is ticked)

1. `pyproject.toml`: `version = "1.0.0"`.
2. `CITATION.cff`: `version: 1.0.0`, `date-released` the merge date (it still says 0.1.0, 2026-11-01).
3. README status line: v1.0 and, after Zenodo answers, the software DOI.
4. Rerun pytest and update the test count in `docs/releases/v1.0.0.md` (275 on 13 Nov).
5. Merge to main. `.github/workflows/release.yml` sees `docs/releases/v1.0.0.md` (already written) and makes the release; Zenodo mints the DOI.

Until step 1, pushing to main cannot make a v1.0 release: the workflow only looks for the notes file of the current package version.

## Checks (author ticks each)

| # | Check | Claude's check (13 Nov 2026, author to confirm) | Author |
|---|---|---|---|
| 1 | Anchor report | Values in paper/paper1/numbers.md rows 2.2 read again from results/anchor_*.csv: all match. Dead-load median is exactly 4.25 % (report prints 4.2 %) | |
| 2 | Dataset | DOI 10.5281/zenodo.24194144 published 13 Nov; 5,184 shell rows (4,856 ok, 288 outside code, 40 not converged); floor library rebuilt 13 Nov with the shell equilibrium check: identical to the committed file | |
| 3 | H1-H3 verdicts | preregistration section 3 table checked against verdicts_summary.csv (13 Nov). New [J]: S_b bound for the strip-vs-plan lateral gap (data_card row 4): median 5.66 % at factor 1.0, 4.13 % at 1.3125 (the two bracket each building), verdict unchanged (scripts/strip_factor_bound.py) | |
| 4 | H4 verdict | Ratio 2.27, coverage 73.3 %, agreement 31/33 rechecked on the laptop (preregistration section 3 note) | |
| 5 | Paper 1 numbers | numbers.md: every row has a source and a tag; column "Checked by Claude" filled; "Checked by Syed" empty | |
| 6 | Equilibrium | Frame: `generator.check_equilibrium` on every analysis. Shell: reactions vs nodal forces on every static run without gravity (PR #177); thrust and load-balance tests | |
| 7 | Open "author to confirm" lines | baseline_spec S12 (γRE); design_rules capacity constants; floor_concept topping clause reading; preregistration section 3 readings for H1-H4; GB/T 51366 official-copy check of the carbon factors | |
| 8 | Tests | pytest 275 passed on the laptop with CalculiX (13 Nov) | |

Not part of v1.0 (schedule.md): the JOSS documentation and the two tutorials (v1.0.x), and Paper 1 prose (the author writes it).
