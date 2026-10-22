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

## Unchanged

Anchor building, codes, A1-A3 boundary under EN 15978, two-paper plan, and gap statements G1-G4 in [gap_matrix.md](gap_matrix.md).
