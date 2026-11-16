# Paper 1 drafts

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

Paper 1: whole-building embodied carbon of thin-shell floors in GB-code RC frames. Target: Journal of Building Engineering (author to confirm). Drafting schedule: in the project files (paper_kit/paper1/drafting_schedule.md); it follows docs/schedule.md.

## Materials for the manuscript (16 Nov 2026)

Everything the manuscript needs is built from the frozen record; nothing below has to be re-run or remade.

| Material | Where | How it is made and checked |
|---|---|---|
| Numbers, each with its source file and version | [numbers.md](numbers.md) | one row per manuscript number |
| Tables 1-5 (CSV and booktabs LaTeX) | [tables/](tables/) | `python scripts/paper1_tables.py`; tests/test_paper1_tables.py |
| Figures 3-8 and S1-S4 (600 dpi PNG, PDF, SVG) | [../../figures/paper/](../../figures/paper/) | `python -m shellbench.figures`; list and status in [00_core.md](00_core.md) section 9 |
| Hypotheses, rules, changes C1-C4, frozen verdicts | [../../docs/preregistration.md](../../docs/preregistration.md) | results/verdicts_*.csv; tests/test_verdicts.py |
| Validation against the thesis and benchmarks | [../../docs/anchor_report.md](../../docs/anchor_report.md) | results/anchor_*.csv, results/benchmarks_convergence.csv |
| Data and code availability statement | Zenodo software 10.5281/zenodo.23851675, dataset 10.5281/zenodo.24194144 | [../../CITATION.cff](../../CITATION.cff) |
| Generative-AI declaration | [../../docs/ai_use.md](../../docs/ai_use.md) | Elsevier back matter |
| References | [references.md](references.md); gap papers in [../../docs/gap_matrix.md](../../docs/gap_matrix.md) | each DOI checked against Crossref at step 10 |

## Working files

| File | What | Status |
|---|---|---|
| 00_core.md | Contribution, gap, narrative, Reviewer 2 objection, journal shortlist, frozen names, figure and table list, verification gaps | 6 Nov 2026; section 9 updated 16 Nov 2026 |
| 02_methods_skeleton.md | Methods outline: what each subsection must say, sources, open items | Skeleton, 5 Nov 2026 |
| reviews/02_methods_skeleton.md | Review panel findings on the skeleton | 5 Nov 2026 |
| numbers.md | One row per manuscript number | Sourced rows |
| references.md | One row per reference | Seeded |

## What is left (docs/finishing_path.md)

Steps 1 (core) and 2 (tables and figures) are done. Left, in order: 3 Methods, 4 Results, 5 Discussion, 6 literature search and Introduction, 7 Abstract, highlights and Conclusions, 8 optional checks, 9 LaTeX assembly, 10 self-review, 11 author check, 12 submission. Two schematics (Fig. 1 workflow, Fig. 2 floor build-up) are still to draw. The target journal is the author's choice.

Rules: follow `docs/finishing_path.md` (from 14 Nov 2026: the AI assistant drafts the prose in the author's voice, the author owns it; this replaces "prose only from the author's rough sentences"); every section passes the review panel before it goes to the author; Results only after the frozen verdicts; no em dashes; British English; Elsevier back matter including the generative-AI declaration.
