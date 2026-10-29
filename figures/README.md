# figures/

Figures for the reports and papers. Each figure is produced by a script in this repository, so it can be rebuilt from the results.

## What must be reproducible

The rule is the files in `results/`, not the images (decided 27 Oct 2026).

- Every CSV in `results/` must be byte-identical on every platform. CI and the daily sync check this.
- A PNG here is drawn from the same values the run writes to those CSVs, so the numbers in a figure are reproducible whenever `results/` is. Its bytes may still differ between Linux and Windows, even with the same matplotlib (3.11.2), because the fonts are rasterised differently. Nobody compares figure bytes.
- Committed figures come from the Linux run (the cloud or CI). A local rebuild that changes only a PNG is restored, not committed.

Current figures: `anchor_seismic_compare.png` (Day 10, the values in `results/anchor_rsa.csv`); `anchor_quantities.png` (Day 12, grid plan, the values in `results/anchor_quantities.csv`). `anchor_carbon.png` will follow once the author's carbon factors exist.
