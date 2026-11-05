# Data card: ShellBench building family (part 1, frozen format)

**Format frozen 4 Nov 2026 (Day 18).** From this date no column is renamed and no column changes its unit or meaning. New columns may be added at the end only (schedule.md, "ShellForm data hand-over", item 1). Part 2 (how the rows were checked, failure counts, licence, DOI) follows on Day 20 and Day 31.

Every row released before the dataset DOI (11 Nov 2026) carries `release = "pre-release, not for results"`.

## Files

| File | One row per | Written by | Status |
|---|---|---|---|
| `family_rc.parquet` | building, conventional floor (beam and slab) | `python -m shellbench.batch` | Runner done (Day 18). Sample: [../results/family_rc_sample.csv](../results/family_rc_sample.csv) |
| `family_shell.parquet` | building × floor variant × topping | the batch runner after Day 29 (shell floor in the generator) | Format below; no rows yet |

Both files use the same `building_id` for the same building (the Day 31 check needs this). The ID is built from the inputs, not from a row number, so a family dimension added later does not change an existing ID: `s{storeys:02d}-p{PGA × 100:03d}-tg{Tg × 100:02d}-{grade}`, for example `s04-p010-tg35-C40` is the anchor.

## Family definition

- Storey counts 3, 4, 5, 6, 7 and 8; PGA 0.05, 0.10, 0.15, 0.20, 0.30 and 0.40 g (preregistration 2.0). That gives 36 conventional buildings.
- Every other input is the anchor's. Spans 7.2 / 6.6 / 7.2 m, frame spacing 7.2 m, loads as in `tests/test_generator_anchor.py`, which gives the source of each.
- Storey heights: 4.55 m ground storey, then 3.6 m storeys (spec G6, G7) [J].
- Tg 0.35 s and concrete C40 for every building [J]. Both are columns, so other values can be added later without a format change.
- Run order: the 0.10 g block first (the validated case), then the other PGAs in rising order; storeys rise inside each block [J].
- **α_max.** GB 50011-2010 Table 5.1.4-1, frequent earthquake: 0.04 (6°, 0.05 g), 0.08 (7°, 0.10 g), 0.12 (7°, 0.15 g), 0.16 (8°, 0.20 g), 0.24 (8°, 0.30 g), 0.32 (9°, 0.40 g). The 7°/0.10 g value was confirmed by the author on 25 Oct 2026. The other five were checked: S. N. R. Hasib, 4 Nov 2026 in the 2016 edition (p. 33). A row whose α_max is missing still gets `status = blocked`.
- **Intensity.** 0.05 g → 6, 0.10 and 0.15 g → 7, 0.20 and 0.30 g → 8, 0.40 g → 9: GB 50011-2010 Table 3.2.2 (2016 edition, p. 6), checked: S. N. R. Hasib, 4 Nov 2026.
- **Seismic grade and axial limit.** Frame grade from Table 6.1.2 (p. 49) by intensity and height (≤ 24 m or above). The column axial-ratio limit comes from Table 6.3.6 (p. 62): 0.65, 0.75, 0.85 and 0.90 for grades 1-4. Height is the sum of storey heights [J].
- **Outside the code.** A frame taller than Table 6.1.1 allows (p. 48: 60, 50, 50, 40, 35 and 24 m for the six PGAs) gets `status = outside_code` and is not run. Only `s07-p040` and `s08-p040` are affected.

## Columns of family_rc

Units are in the column name, or in the Unit column for names without one. `[-]` means a pure number.

| # | Column | Unit | Meaning |
|---|---|---|---|
| 1 | `building_id` | text | Stable ID, see above |
| 2 | `release` | text | "pre-release, not for results" until the DOI version |
| 3 | `shellbench_version` | text | `shellbench.__version__` of the code that wrote the row |
| 4 | `takeoff_scope` | text | Which elements the quantities and carbon include. `frame_strip_v1` = one frame strip: slab, frame beams below the slab, columns, longitudinal bars only. Stirrups, footings, slab bars, longitudinal and secondary beams are not in it yet. Decision (author, 5 Nov 2026): `frame_strip_v1` is a pilot scope only. Paper 1 uses the preregistered scope (preregistration.md, Measured): C_floor = slab or vault with its bars, ties, fill, topping and secondary beams, and C_bldg = every element in the take-off, the same element set for both systems. A new scope value marks those rows |
| 5 | `storeys` | [-] | Number of storeys |
| 6 | `pga_g` | g | Design basic ground acceleration |
| 7 | `intensity` | [-] | Fortification intensity for that PGA |
| 8 | `tg_s` | s | Site characteristic period |
| 9 | `alpha_max` | [-] | Frequent-earthquake α_max used; empty if blocked |
| 10 | `concrete_grade` | text | Concrete strength grade |
| 11 | `spans_m` | m | Transverse spans, left to right, joined by "/" |
| 12 | `storey_heights_m` | m | Storey heights, ground first, joined by "/" |
| 13 | `tributary_width_m` | m | Frame spacing carried by the modelled frame |
| 14 | `floor_area_m2` | m² | Floor area of the strip: storeys × sum of spans × tributary width. Every "per_m2" column is per m² of this area |
| 15 | `floor_system` | text | `beam_slab` in family_rc |
| 16 | `status` | text | `ok` (designed, all checks pass), `failed` (generator did not converge or a check cannot be met), `blocked` (an input is not confirmed), `outside_code` (taller than GB 50011 Table 6.1.1 allows; not run) |
| 17 | `failure_reason` | text | Empty when `ok` |
| 18 | `n_passes` | [-] | Analysis passes of the generator's resize loop |
| 19 | `period_s` | s | First period, after the ψ_T reduction |
| 20 | `max_drift_ratio` | [-] | Largest storey drift ratio under frequent earthquake |
| 21 | `axial_ratio` | [-] | Largest ground-storey column axial ratio |
| 22 | `column_mm` | mm | Square column side |
| 23 | `beam_b_mm` | mm | Frame beam widths, per span, "/" |
| 24 | `beam_h_mm` | mm | Frame beam depths, per span, "/" |
| 25 | `slab_mm` | mm | Slab thickness |
| 26 | `concrete_m3_per_m2` | m³/m² | Concrete in the take-off scope |
| 27 | `bar_steel_kg_per_m2` | kg/m² | Bar steel in the take-off scope |
| 28 | `floor_concrete_m3_per_m2` | m³/m² | Concrete of the floor elements (slab; for shells: vault, topping) |
| 29 | `lateral_concrete_m3_per_m2` | m³/m² | Concrete of the lateral system (frame beams and columns), preregistration 2.2 |
| 30 | `floor_steel_kg_per_m2` | kg/m² | Steel of the floor elements (slab bars; for shells: mesh, ties). 0 in `frame_strip_v1`, which has no slab bars |
| 31 | `lateral_steel_kg_per_m2` | kg/m² | Steel of frame beams and columns |
| 32 | `carbon_floor_kgco2e_per_m2` | kgCO2e/m² | A1-A3 carbon of the floor elements (C_floor, preregistration 2.1) |
| 33 | `carbon_lateral_kgco2e_per_m2` | kgCO2e/m² | A1-A3 carbon of the lateral system |
| 34 | `carbon_building_kgco2e_per_m2` | kgCO2e/m² | Sum of the two above in this take-off scope (C_bldg once the scope is whole-building) |

Carbon factors: `data/carbon_factors.csv`, set GBT51366 (C40 340 kgCO2e/m³, HRB400 2340 kgCO2e/t; sources and open checks are in that file).

## Columns of family_shell

Columns 1-34 have the same names, units and meanings, with `floor_system = shell_vault`. Then:

| # | Column | Unit | Meaning |
|---|---|---|---|
| 35 | `floor_variant_id` | text | Case ID in the floor library ([floor_library.md](floor_library.md)) |
| 36 | `vault_span_m` | m | Vault span L |
| 37 | `rise_ratio` | [-] | f / L |
| 38 | `levelling` | text | `foamed_fill`, `recycled_fill` or `raised_floor` |
| 39 | `mesh_layers` | [-] | 1 (mid-depth) or 2 (one near each face) |
| 40 | `shell_thickness_mm` | mm | Vault thickness |
| 41 | `tie_bar_mm` | mm | Tie bar diameter |
| 42 | `tie_spacing_m` | m | Tie spacing along the vault |
| 43 | `tie_prestressed` | bool | Tie tensioned against the dead-load spread |
| 44 | `topping_mm` | mm | Structural topping: 0, 40, 50 or 60 (preregistration 2.3) |
| 45 | `diaphragm_rigid` | bool | Passes the rigid-diaphragm rule of preregistration 2.3 |
| 46 | `fill_kg_per_m2` | kg/m² | Levelling fill or raised-floor mass |
| 47 | `tie_steel_kg_per_m2` | kg/m² | Tie steel (also inside column 30) |

Columns added on 4 Nov 2026, after the freeze (adding is allowed). Both files carry them at the end, so their position differs by file. Read them by name.

| # in family_rc | # in family_shell | Column | Unit | Meaning |
|---|---|---|---|---|
| 35 | 48 | `seismic_grade` | [-] | Frame seismic grade 1-4, GB 50011-2010 Table 6.1.2 |
| 36 | 49 | `axial_ratio_limit` | [-] | Column axial-ratio limit used in design, Table 6.3.6 |

family_shell is built as family_rc columns 1-34, then shell columns 35-47, then columns 35-36 of family_rc (`batch.COLUMNS[:34] + shell + batch.COLUMNS[34:]`).

In family_shell, `slab_mm` is empty and `topping_mm` holds the topping. Floor-only factors (GB/T 51366 Table D.0.1; checked: S. N. R. Hasib, 5 Nov 2026, in the third-party copy; official-copy check open) are as follows:

- `TIE_BAR` is 2340 kgCO2e/t.
- Recycled-content cases are `TIE_STEEL_EAF` at 3030 and `TIE_STEEL_BOF` at 1990 kgCO2e/t. These are crude-steel rows, and in this table the EAF route is the higher one.
- `RECYCLED_FILL` is 2.18 kgCO2e/t, the crushed-stone row used as a proxy [J].

- `RAISED_FLOOR` (set `OVAL2023`) is 534.5 kgCO2e/t. It comes from Oval et al. (2023) Table 6, row "flooring system", stage A1: 29 kg gives 15.50 kgCO2eq per m². So the 29 kg/m² raised floor costs 15.50 kgCO2e/m². This row uses an ecoinvent background, not the GB/T 51366 set, so report it separately [J].

Foamed-concrete fill has no row in Table D.0.1 and still has no factor [?]. Hawkins et al. (2020) Table 2 takes its values from Jones and Hammond (ICE), so it is not used (D29). A factor needs an open-access 2020-2026 mix with a stated cement content near 800 kg/m³, multiplied by the Table D.0.1 cement row (735 kgCO2e/t).

## 10-row sample (`python -m shellbench.batch --n 10`)

Pre-release, not for results. Run on 4 Nov 2026. Fourteen of the 36 columns are shown; the full rows are in [../results/family_rc_sample.csv](../results/family_rc_sample.csv) and `.parquet`.

| building_id | status | alpha_max | seismic_grade | period_s | max_drift_ratio | axial_ratio | column_mm | beam_h_mm | concrete_m3_per_m2 | bar_steel_kg_per_m2 | carbon_floor_kgco2e_per_m2 | carbon_lateral_kgco2e_per_m2 | carbon_building_kgco2e_per_m2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| s03-p010-tg35-C40 | ok | 0.08 | 3 | 0.4845 | 0.0009437 | 0.3962 | 450 | 600/550/600 | 0.1603 | 4.177 | 40.8 | 23.48 | 64.28 |
| s04-p010-tg35-C40 | ok | 0.08 | 3 | 0.5485 | 0.00086 | 0.4385 | 500 | 600/550/600 | 0.1647 | 4.563 | 40.8 | 25.88 | 66.68 |
| s05-p010-tg35-C40 | ok | 0.08 | 3 | 0.6135 | 0.0008349 | 0.46 | 550 | 600/550/600 | 0.1697 | 5.049 | 40.8 | 28.7 | 69.5 |
| s06-p010-tg35-C40 | ok | 0.08 | 3 | 0.6823 | 0.0008445 | 0.4699 | 600 | 600/550/600 | 0.1751 | 5.462 | 40.8 | 31.53 | 72.33 |
| s07-p010-tg35-C40 | ok | 0.08 | 2 | 0.7248 | 0.0008094 | 0.4131 | 700 | 600/550/600 | 0.1878 | 6.172 | 40.8 | 37.48 | 78.28 |
| s08-p010-tg35-C40 | ok | 0.08 | 2 | 0.8336 | 0.0008349 | 0.4721 | 700 | 600/550/600 | 0.1876 | 6.277 | 40.8 | 37.66 | 78.46 |
| s03-p005-tg35-C40 | ok | 0.04 | 4 | 0.5771 | 0.0005927 | 0.4966 | 400 | 600/550/600 | 0.1559 | 3.95 | 40.8 | 21.46 | 62.26 |
| s04-p005-tg35-C40 | ok | 0.04 | 4 | 0.6254 | 0.0005224 | 0.5349 | 450 | 600/550/600 | 0.1599 | 4.015 | 40.8 | 22.96 | 63.76 |
| s05-p005-tg35-C40 | ok | 0.04 | 4 | 0.6135 | 0.0004175 | 0.457 | 550 | 600/550/600 | 0.1697 | 4.771 | 40.8 | 28.05 | 68.85 |
| s06-p005-tg35-C40 | ok | 0.04 | 4 | 0.6823 | 0.0004222 | 0.4673 | 600 | 600/550/600 | 0.1751 | 5.148 | 40.8 | 30.79 | 71.59 |

Checks on the sample:
- The anchor row `s04-p010-tg35-C40` gives T1 0.5485 s, drift 1/1163 and axial ratio 0.4385, the Day 16 values (LOG Day 16, `tests/test_generator_anchor.py`).
- Floor carbon 40.8 kgCO2e/m² = 0.12 m slab × 340 kgCO2e/m³ by hand, in every `ok` row.
- `s07-p010` is 26.15 m tall, so it is grade 2 with axial limit 0.75 (Tables 6.1.2 and 6.3.6). Its columns are 700 mm. Under the earlier single limit of 0.85 they were 650 mm.
- The whole family (36 buildings) was also run on 4 Nov as a check: 34 `ok`, 0 `failed`, and 2 `outside_code` (`s07-p040` and `s08-p040`, taller than 24 m at 9 degrees).
