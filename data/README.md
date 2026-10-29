# data/

Input data for the models. Every file here must name its source: a thesis section or table, a code clause, or a published dataset.

The thesis results used for validation live in [../validation/thesis_values/](../validation/thesis_values/).

## carbon_factors.csv

On 29 Oct 2026, with the author's permission, Claude filled in the GB/T 51366 set from Table D.0.1. Each row's source column says how its value was read; the author confirms them in an official copy. The ICE set is not in the file yet.

The carbon step of `shellbench.carbon` (Day 12) reads `data/carbon_factors.csv`. The author copies every value from the primary source; Claude writes none (charter, playbook Day 12). Start from [carbon_factors_template.csv](carbon_factors_template.csv): fill each empty cell, delete any row you have no value for, and save it as `carbon_factors.csv`.

- `set [text]`: the factor set, e.g. `GBT51366` or `ICE`. Every set must cover every material the take-off uses: `C40` (all concrete today), `HRB400` (bars) and `HPB300` (stirrups). C30 and C35 rows are welcome for later runs.
- `value` and `unit [text]`: the unit must be one of `kgCO2e/m3`, `kgCO2e/kg` or `kgCO2e/t`. Concrete must be per m³ (the take-off gives volumes).
- `source [text]` and `page [text]`: document, version, and table or page. A row without them stops the run.
- If a source gives no separate HPB300 value, copy the HRB400 value into the HPB300 row and say so in `source [text]` (this is decision D28 (e)).

Until the file exists, `python -m shellbench.anchor_frame` writes the quantities and reports the carbon as pending.
