# Research question (charter amendment, 22 Oct 2026)

This file records a change to the research question in the ShellBench Project Charter. The charter PDF is kept outside this repository. The charter was reissued on 22 Oct 2026 with the revised question (storey count included) and a dated amendment note: the Claude Docs charter was edited, and a new PDF was exported as "ShellBench Project Charter (amended 22 Oct 2026).pdf". The author uploaded the new PDF to the Claude Project knowledge on 22 Oct 2026, replacing the 19 Oct PDF.

## Revised question

> How much do thin-shell floors cut the whole-building A1-A3 embodied carbon of a GB 50010 / GB 50011 RC frame across 3-8 storeys, and how does the saving change with storey count and seismic intensity once diaphragm, tie and topping needs are met?

Storey count restored by the author on 22 Oct 2026. The first revision had dropped it, but the building family (3-8 storeys) and frozen hypothesis H2 ("grows with seismic intensity and storey count") keep it. Leaving it out would make the stated question disagree with the experimental design.

Original question: how much embodied carbon do thin-shell floors save in code-designed RC frames in seismic zones, once every knock-on effect is counted?

## What changed and why

Decided by the author on 22 Oct 2026 after the stress test in [goal_stress_test.md](goal_stress_test.md).

| Change | Why (hole) |
|---|---|
| **PGA sweep**: the same building at 0.05, 0.10, 0.15, 0.20, 0.30 and 0.40 g (intensities 6 to 9). The 0.10 g anchor stays the validation case | H1: at 0.10 g the anchor columns are already at minimum detailing (baseline_spec B6), so the seismic knock-on may be close to zero. Reporting the saving against PGA turns that risk into a finding |
| **Fair baseline**: the shell saving is reported against the lowest-carbon code-compliant conventional floor on the same grid and storey height, as well as against the anchor as built | H2: beating a 120 mm beam-slab is an easy win that reviewers will discount |
| **Topping thickness as a variable, plus a diaphragm check** (in-plane stiffness, periods) | H3: a shell with loose fill may fail the rigid-floor assumption of GB 50011; a structural topping may erase much of the mass saving |

## What Paper 1 will report

1. Absolute and percentage A1-A3 saving against the best conventional floor (and against the anchor).
2. How that saving varies with PGA and with storey count (3-8).
3. The minimum topping needed for diaphragm action, and its carbon cost.

Smaller holes H4-H9 (vertical seismic action, one building, Chinese carbon factors, shell validation, storey height, buildability) are handled as sensitivity cases or in the discussion. They do not widen the scope.

## Dates (amended 26 Oct 2026)

The author approved finishing earlier on 26 Oct 2026, on the condition that no check, test or validation is dropped or weakened. Day-by-day plan in [schedule.md](schedule.md).

| Output | Date |
|---|---|
| Anchor report and release v0.1 | 31 Oct 2026 (unchanged) |
| Hypotheses and analysis plan committed | 4 Nov 2026 (unchanged; planned 3 Nov) |
| Dataset DOI on Zenodo | 17 Nov 2026 (was 20 Nov) |
| Paper 1 submitted, Journal of Building Engineering or Engineering Structures | 29 Nov 2026 (unchanged) |
| Paper 2 submitted, Automation in Construction | 8 Dec 2026 (was 12 Dec) |
| ShellBench v1.0 with software DOI | 8 Dec 2026 (was 13 Dec) |
| CV, statement of purpose draft, walkthrough video | 13 Dec 2026 (unchanged) |
| JOSS submission | from 19 Apr 2027 (unchanged) |

Why: the slack was in the gaps between outputs, not in the research. An earlier dataset DOI gives Paper 2 more time on fixed data, and v1.0 can be released with Paper 2 rather than a day after. 1 Dec was judged too tight, because it would mean cutting checks. If the go/no-go check in schedule.md fails on 1 Dec, Paper 2 and v1.0 return to 12 and 13 Dec. H1-H4 stay frozen.

## Unchanged

Anchor building, codes, A1-A3 boundary under EN 15978, two-paper plan, and gap statements G1-G4 in [gap_matrix.md](gap_matrix.md).
