# results/

Output written by the code in [../src/shellbench/](../src/shellbench/). Do not edit by hand; rerun the code instead.

| File | Written by | What it holds |
|---|---|---|
| anchor_gravity_dead.csv | `python -m shellbench.anchor_frame` | Dead load, thesis frame on axis (2): every beam-end moment and column axial force typed from the thesis, next to the model value, the difference and the % difference (primary run), plus the % difference of four check runs. Explanations in [../docs/anchor_notes.md](../docs/anchor_notes.md). |
| anchor_gravity_dead_runs.csv | same | One row per run: load model, switches, applied vertical load and the sum of base reactions (equilibrium check). |

Units are in each column header. `[mixed]` columns hold kN*m for moments and kN for axial forces; the `unit [text]` column says which.
