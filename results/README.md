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

Units are in each column header. `[mixed]` columns hold kN*m for moments and kN for axial forces; the `unit [text]` column says which.
