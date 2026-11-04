# Data card: ShellBench building family

© 2026 Syed Nafiz Reja Hasib. Code MIT; the dataset will be CC BY 4.0 when published with its DOI.

**Part 1, the frozen data format (Day 18, 4 Nov 2026).** From this date a column is never renamed or given new units. Columns may only be added at the end. Part 2 (how the rows were made, checks, failure counts and known limits) follows on Day 20 and Day 31.

**Status of the rows.** Every file before the dataset DOI (11 Nov) is **pre-release, not for results** (schedule.md, "ShellForm data hand-over"). The 10-row sample in `results/family_sample/` exists only to show the format.

## Files

| File | Rows | Made by |
|---|---|---|
| `family_rc.csv` / `family_rc.parquet` | One per building, conventional floor | `python -m shellbench.family --n N --out DIR` |
| `family_shell.csv` / `family_shell.parquet` | One per building and shell floor variant, same `building_id`s | Day 29 onwards; same columns, `floor_system` names the variant |

The CSV is always written. The parquet copy is written when pyarrow is installed, with the same columns in the same order.

## Columns

| Column | Unit | Meaning |
|---|---|---|
| building_id | text | `RC` + 5 digits; the same building has the same id in both files |
| status | text | `ok`, `failed` (the generator could not size it) or `not_run` (an input value is not yet confirmed) |
| reason | text | Why a row is `failed` or `not_run`; empty when `ok` |
| storeys | - | Number of storeys, 3-8 |
| pga_g | g | Design basic acceleration: 0.05, 0.10, 0.15, 0.20, 0.30 or 0.40 |
| intensity | degree | Seismic intensity for that PGA (GB 50011 Table 3.2.2 [?]) |
| side_span_m | m | Span of the two outer bays of the three-bay transverse frame |
| middle_span_m | m | Span of the middle bay |
| frame_spacing_m | m | Spacing of the transverse frames (tributary width) |
| ground_storey_m | m | Ground storey height, base to level 1 |
| upper_storey_m | m | Height of every other storey |
| office_live_kn_m2 | kN/m² | Live load on the outer bays; the middle bay is 3.0 |
| floor_system | text | `rc_slab` for the conventional floor; shell variants from Day 29 |
| slab_mm | mm | Slab thickness (R3) |
| column_mm | mm | Side of the square columns, the same for every column (R5, R11, R12) |
| side_beam_b_mm, side_beam_h_mm | mm | Outer-bay frame beam width and depth |
| middle_beam_b_mm, middle_beam_h_mm | mm | Middle-bay frame beam width and depth |
| period_s | s | First-mode period after ψ_T |
| max_drift_ratio | - | Largest elastic storey drift ratio under frequent earthquake (limit 1/550) |
| axial_ratio | - | Largest column axial ratio, seismic combination (limit 0.85) |
| resizes | - | Number of resizes the generator made |
| concrete_m3_per_m2 | m³/m² | Frame-strip concrete (slab, beam webs, columns) per m² of floor |
| bar_steel_kg_per_m2 | kg/m² | Frame-strip longitudinal bars at the chosen bar areas, per m² of floor |
| carbon_kgco2e_per_m2 | kgCO2e/m² | A1-A3 of the two quantities above, with `factor_set` |
| factor_set | text | Carbon factor set in `data/carbon_factors.csv` (D29: `GBT51366`) |
| generator_version | text | `shellbench.__version__` of the code that made the row |
| git_commit | text | Short commit of the repository when the row was made |

**What the carbon column does not yet hold.** It covers the frame strip only: no stirrups, footings, longitudinal or secondary beams. So it is lower than the anchor's whole-building 128.2 kgCO2e/m² (anchor_report.md). The whole-building columns will be added (not renamed) before Day 20 [J].

## The family definition (frozen 4 Nov 2026) [J]

Storeys 3-8 and the six PGA levels are the charter's. Every storey-PGA cell gets an equal share of the buildings. The other inputs are drawn by Latin hypercube with seed 20261104, on these grids:

| Input | Range | Step |
|---|---|---|
| side_span_m | 6.0-8.4 | 0.3 |
| middle_span_m | 5.4-7.8 | 0.3 |
| frame_spacing_m | 6.0-8.4 | 0.3 |
| ground_storey_m | 3.9-4.8 | 0.15 |
| upper_storey_m | 3.3-3.9 | 0.15 |
| office_live_kn_m2 | 2.0-3.5 | 0.5 |

Every range contains the anchor's value. Dead loads, walls, Tg 0.35 s, ψ_T 0.7, C40 and the beam stiffness factor stay at the anchor's (`family.FIXED`, sources in `tests/test_generator_anchor.py`). The Latin hypercube depends on n, so a 10-row sample is not the first 10 rows of the full family.

**Rows that cannot run yet.** Only α_max at 0.10 g is confirmed from GB 50011 Table 5.1.4-1. Every other PGA level is written as `not_run`, with the reason, until its value is confirmed.
