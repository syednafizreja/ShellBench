# figures/

Figures for the reports and papers. Each figure is produced by a script in this repository, so it can be rebuilt from the results.

## What must be reproducible

The rule is the files in `results/`, not the images (decided 27 Oct 2026).

- Every CSV in `results/` must be byte-identical on every platform. CI and the daily sync check this.
- A PNG here is drawn from the same values the run writes to those CSVs, so the numbers in a figure are reproducible whenever `results/` is. Its bytes may still differ between Linux and Windows, even with the same matplotlib (3.11.2), because the fonts are rasterised differently. Nobody compares figure bytes.
- Committed figures come from the Linux run (the cloud or CI). A local rebuild that changes only a PNG is restored, not committed.

## House style

Every figure is drawn by `src/shellbench/figures.py` in the house style (`src/shellbench/style.py`, `shellbench.mplstyle`) and must pass the review in `docs/visual_standard.md`. Each is written three times: `.png` (600 dpi preview, shown below and in the reports), `.pdf` and `.svg` (vector masters). Redraw all of them from `results/` with `python -m shellbench.figures`; add `--paper` for footer-free copies in `figures/paper/`. No analysis runs when figures are redrawn.

## Current figures

| File | Shows | Data |
|---|---|---|
| `anchor_waterfall` | Anchor building, slab to shell floor: each step of A1-A3 carbon per m² of floor, and the whole-building saving. Pre-release, screening-level; footings out of scope. | `results/anchor_waterfall.csv` |
| `anchor_seismic_compare` | (a) storey shear and (b) inter-storey drift by storey: base-shear method, response spectrum (3 modes, SRSS) and thesis Table 8-12. | `results/anchor_rsa.csv` |
| `anchor_quantities` | (a) concrete and (b) steel per m² of floor by element, grid plan, thesis and code-minimum steel. | `results/anchor_quantities.csv` |
| `anchor_carbon` | A1-A3 per m² of floor by element, per factor set and steel source, grid plan. | `results/anchor_carbon.csv` |
| `benchmarks_convergence` | Shell benchmarks: computed over reference displacement against mesh density, with the 2 % band. | `results/benchmarks_convergence.csv` |
| `surrogate_coverage` | Empirical coverage of the 90 % split-conformal intervals for each held-out storey count and pooled, against the H4 band 88-92 %. Pre-release pipeline test. | `results/surrogate_coverage.csv` |
| `surrogate_parity` | Surrogate against full analysis, whole-building carbon, one panel per model and split, with RMSE, R² and n. Pre-release pipeline test. | `results/surrogate_predictions.csv` |
