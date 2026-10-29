# results/

Output written by the code in [../src/shellbench/](../src/shellbench/). Do not edit by hand; rerun the code instead.

| File | Written by | What it holds |
|---|---|---|
| anchor_gravity_dead.csv | `python -m shellbench.anchor_frame` | Dead load, thesis frame on axis (2): every beam-end moment and column axial force typed from the thesis, next to the model value, the difference and the % difference (primary run), plus the % difference of four check runs. Explanations in [../docs/anchor_notes.md](../docs/anchor_notes.md). |
| anchor_gravity_dead_runs.csv | same | One row per run: load model, switches, applied vertical load and the sum of base reactions (equilibrium check). |
| anchor_gravity_live.csv | same | Live load (Day 6): the same comparison for the 40 live-load targets, primary run plus four check runs. |
| anchor_gravity_live_runs.csv | same | Equilibrium totals of the five live-load runs. |
| anchor_gravity_combination.csv | same | 1.3D + 1.5L from the primary dead and live runs against 1.3 x thesis dead + 1.5 x thesis live; also 1.0D + 1.5L, which is what thesis Table 8-13 printed in 13 of 15 roof rows (proposed flag D16). Table 8-13's own dead and wind inputs are table 6.3 cells (D17), so its printed combinations are not a target. |
| thesis_table_7_2_check.csv | same | Thesis table 7.2: every printed final moment next to the sum of its column, and, for beam ends, the primary and axially rigid model values. |
| thesis_table_7_2_joints.csv | same | Thesis table 7.2: sum of final moments at every joint, from the printed finals and from the column sums, with the printed joint moment. |
| anchor_wind.csv | same (calls `shellbench.anchor_wind.main`) | Wind (Day 8): per storey, the printed Table 8-2 forces, shears and drifts next to the model's column shears, Δu, u and θ; the % difference on Δu with the author's 15 % tolerance (pass/fail); Δu against V/ΣD with the printed and with the recomputed D-values (diagnostics); the 1/550 check; the Δu difference of each check run. Explanations in the wind section of [../docs/anchor_notes.md](../docs/anchor_notes.md). |
| anchor_wind_runs.csv | same | One row per wind run: switches, storey heights, applied load and base shear (equilibrium), roof displacement, largest θ. |
| anchor_wind_d_values.csv | same | D-value method (Th §7.3 formulas) redone with the model's own section stiffnesses: K, α_c, D for A/D and B/C columns and ΣD per storey. |
| thesis_table_8_2_forces_check.csv | same | Printed W_k against β_z μ_s μ_z w₀ B h from the Table 8-1 inputs: implied tributary heights, and printed V against the running sum of W_k. |
| anchor_seismic.csv | same (calls `shellbench.seismic.main`) | Earthquake by the GB 50011 base-shear method (Day 9), levels 1-4: G_i, H_i, model storey forces and shears next to Table 8-12 (F_i = V_i − V_i+1 and four-storey shears V_i − 98.29 kN, lateral-load decision 2); λΣG minimum-shear check; Δu against the printed Δu, against V/ΣD, and under the thesis forces; θ and the 1/550 check. Explanations in the seismic section of [../docs/anchor_notes.md](../docs/anchor_notes.md). |
| anchor_seismic_runs.csv | same | One row per seismic run (primary, thesis beam-shear weights, trial infill factors ψ_T 0.9-0.6): ΣG, G_eq, T1, α1, δ_n, F_Ek, base reaction, roof displacement, largest θ, and the period implied by the thesis base shear (diagnostic only). |
| anchor_seismic_weights.csv | same | Storey weights G_i = dead + ψ × live (GB 50011 Table 5.1.3) for the two weight models. |
| anchor_seismic_period_check.csv | same | The four modal periods of the bare frame and the Rayleigh estimate of T1. |
| anchor_rsa.csv | same (calls `shellbench.rsa.main`) | Response-spectrum check (Day 10), storeys 1-4: SRSS storey shears and drifts of the first three modes next to the Day 9 base-shear run and Table 8-12, % differences, θ and the 1/550 check, and each mode's storey shear. Explanations in the response-spectrum section of [../docs/anchor_notes.md](../docs/anchor_notes.md). |
| anchor_rsa_modes.csv | same | One row per mode: period, α, participation factor (roof-normalised shape), mass share and cumulative share, modal base shear, mode shape. |
| anchor_3d_periods.csv | same (calls `shellbench.anchor_3d`) | First three periods of the 3D whole-building model (drawn grid, rigid floors) with each mode's direction, next to the 2D frame's periods of the same mode number. |
| anchor_design_beams.csv | same (calls `shellbench.checks.main`) | Design checks (Day 11): every beam location (12 beams × left end top/bottom, mid-span bottom, right end top/bottom) with the governing thesis combination, design moment at the column face (γ_RE = 0.75 in seismic combinations), ξ, status, calculated, minimum and required steel (GB 50010 cl. 6.2.10, Table 11.3.6-1), and the required steel with centre-line moments and with the GB 55002 seismic factors. Explanations in the design-check section of [../docs/anchor_notes.md](../docs/anchor_notes.md). |
| anchor_design_check.csv | same | The 18 rows of the thesis s9.2 beam table: printed moments and steel next to the model's requirement; flag (a) on the printed A_s,prov and the printed bars; check (b) with the thesis's own γRE × M; sensitivity flags. |
| anchor_design_columns.csv | same | Every column: largest seismic and gravity axial force, axial compression ratio against 0.85 (Table 11.4.16), and the 4C22 steel ratio against the 0.75 % / 0.20 % minimum (Table 11.4.12-1). |
| anchor_design_column_bars.csv | same | The column bar sets of Th s9.3 and drawing 01 against the column minimum steel. |
| anchor_quantities.csv | same (calls `shellbench.carbon.main`) | Quantity take-off of the whole building (Day 12): concrete [m3] and steel [kg] by element (slabs, frame, longitudinal and secondary beams, columns, footings), for the grid plan (B11) and the drawn plan, with the thesis or the code beam and column steel; also per m² of floor area. Rules in the Day 12 section of [../docs/anchor_notes.md](../docs/anchor_notes.md). |
| anchor_footings.csv | same | One pad footing per column and plan: N_k (D + L), side B, thickness, bottom steel each way, concrete and steel (rule 8, proposed D28). |
| anchor_carbon.csv | same, only once `data/carbon_factors.csv` exists | A1-A3 carbon by factor set, plan, steel source and element, and per m² of floor area. Not written yet: the factors are the author's. |

Units are in each column header. `[mixed]` columns hold kN*m for moments and kN for axial forces; the `unit [text]` column says which.
