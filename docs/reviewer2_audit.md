# Reviewer-2 audit of the ShellBench repository

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

Date: 13 Nov 2026, on main at dabc900 (v0.5.0 plus PRs #175-#185), by the AI assistant, as a harsh Journal of Building Engineering Reviewer 2 and a code auditor [J]. Nothing was tuned, rerun to change a verdict, or selected. No carbon factor, benchmark value or code clause text was supplied; those are listed for the author at the end.

## Ten-point result

| # | Point | Result | Evidence |
|---|---|---|---|
| 1 | Traceability | Pass, one finding | `paper/paper1/numbers.md` has a row per manuscript number with file and tag; README numbers match `results/verdicts_summary.csv` and `results/verdicts_buildings.csv`. 32 DOIs in the repo checked against Crossref (title, first author, year, journal): 32 of 32 match the recorded citation. Grade-I caveat was missing (F2, fixed). |
| 2 | Reproducibility from a fresh clone | Pass | Fresh clone: 276 tests pass; both verdict CSVs rebuild byte for byte; `SHA256SUMS` is tested (`tests/test_checksums.py`). Only CRLF and floating-point differences in figures (F7, disclosed). |
| 3 | Verification vs validation | Pass | Kept apart in README "Validation at a glance". Equilibrium is asserted on every frame run (`generator.check_equilibrium`) and on CalculiX static runs (`shellfe.check_equilibrium`); thrust and load balance are tested (`tests/test_thrust_results.py`, `tests/test_shell_load_balance.py`). A zero exit code is never used as evidence. |
| 4 | Hypotheses vs preregistration | Pass, two disclosures | H1-H4 wording frozen; verdict rules in `docs/preregistration.md` section 2 applied as written; late run on v0.4.0 files disclosed (C3); baseline reading disclosed (C4, F1). |
| 5 | Fair comparison | Partly | Same checks, same drift limit (1/550), same loads for both floors. The primary baseline is one conventional design per building, not a search over floor types (F1). |
| 6 | Known weak points | Pass | Listed in README and Paper 1 core: hand drift above 1/550 for s03-p030 and s06-p040, grade-I columns, elastic uncracked only, 40 of 4,896 shell designs failed and reported, 288 rows outside code. |
| 7 | Claims language | Pass | Verdicts use "partly supported" and "not supported"; H3 limited to elastic uncracked behaviour; no claim of general savings. |
| 8 | Integrity | Pass | Verdicts frozen before Paper 1 text; failures reported not dropped; sensitivity cases change no verdict; no tracked file names an AI vendor; `thesis_source/` untracked. |
| 9 | Software quality | Pass after fixes | 280 tests; four public functions lacked a docstring (F4); the floor-library case list had no test (F5). |
| 10 | Figures | Pass, one disclosure | House style enforced by `style.review` (widths, 7 pt minimum, axis labels, no title in paper copies); vector output; README hero figure theme and platform byte differences (F7). |

## Findings

| ID | Issue | Severity | Status |
|---|---|---|---|
| F1 | Primary baseline is the single code-checked conventional design per building (120 mm slab on secondary beams), not the lowest-carbon over other conventional floor types as preregistration 2 reads | Major | Disclosed: preregistration C4 and README note. No result changed. Author to confirm the wording. |
| F2 | Largest savings (17.3 %, 30.7 %) are grade-I buildings with 1300 mm conventional columns; README and numbers table did not say so | Major | Fixed: README note and `numbers.md` row (max 9.6 % and median 5.65 % without grade I). |
| F3 | `CITATION.cff` said version 0.1.0, 1 Nov | Minor | Fixed: 0.5.0, 13 Nov 2026 [J]. Author to confirm at the v1.0 tag. |
| F4 | No docstring: `verdicts.many`, `make_checksums.main`, `readme_hero.draw`, `readme_hero.main` | Minor | Fixed. |
| F5 | Floor-library case list (72 cases, ID format) untested | Minor | Fixed: `tests/test_floorlib_cases.py` (4 tests, includes a match to `results/floor_library.csv`). |
| F6 | `docs/dataset_release.md` held a local Windows path with a username | Minor | Fixed. |
| F7 | Figure PNGs differ by a few bytes between platforms and between README hero themes | Minor | Disclosed. `SHA256SUMS` covers `results/`, not figures. |
| F8 | Strip-to-plan factor 1.3125 moves the H1 median to 4.13 % (max 32.4 %), verdict unchanged | Info | Rerun of `scripts/strip_factor_bound.py` confirms the README sentence. Exploratory, not preregistered. |

## Mine to check, not the author's evidence yet

Nothing above rests on an unverified source. Items that stay with the author (all [?]):

1. GB 50011 Tables 5.5.1 and 6.3.1 and clause 6.2.2; GB/T 51366 Table D.0.1; GB/T 1499.2 Table 2; ASCE 7-16 clause 12.3.1.3, against official copies.
2. `data/carbon_factors.csv` values, including foamed fill 472.7 kgCO2e/t, and the take-off scope.
3. MacNeal-Harder reference values with page numbers.
4. Grade-I count (7 in the compared set; the earlier text said 6).
5. The wording of C4 and the DOI of v0.1.0.
6. The Methods text must explain hand drift above 1/550 for s03-p030 and s06-p040 while the frame analysis passes.

Parked in LOG.md under Later: a conventional-floor search (flat, ribbed, voided) as a stronger baseline, outside the charter.
