# Using ShellBench in the long term

© 2026 Syed Nafiz Reja Hasib.

This note is for a researcher who finds ShellBench years from now, when the software it uses may have changed or gone. It says what is archived, how to rerun it, and what to do if rerunning is no longer possible.

## 1. Where the permanent copies are

| What | Where | Why it lasts |
|---|---|---|
| Software, every release | Zenodo, concept DOI [10.5281/zenodo.23851675](https://doi.org/10.5281/zenodo.23851675) | CERN-hosted archive; a DOI resolves even if GitHub moves |
| Dataset v0.4.0 | Zenodo, [10.5281/zenodo.24194144](https://doi.org/10.5281/zenodo.24194144) (CC BY 4.0) | Same; the zip is checked by SHA-256 ([dataset_release.md](dataset_release.md)) |
| Source history | GitHub (this repository) | Working copy; may move, so cite the DOIs |

## 2. The results do not need the software

You can use every result without running any code.

- **Plain-text formats.** Every table is UTF-8 CSV with the unit in each header, e.g. `M_end [kN*m]`. The parquet files are copies of their CSV twins, kept for speed.
- **Column meanings.** They are in [data_card.md](data_card.md).
- **Provenance.** The main family files (`family_rc_r14_building_v2`, `family_shell`) have a `.provenance.json` with the commit and the inputs.
- **Traced numbers.** Every number in Paper 1 is traced in [../paper/paper1/numbers.md](../paper/paper1/numbers.md).
- **Inputs.** The design rules and their code clauses are in [design_rules.md](design_rules.md). The anchor inputs are in [baseline_spec.md](baseline_spec.md). Carbon factors are in `data/`.

## 3. Rerunning: the exact environment

The environment of record (13 Nov 2026) is pinned in two files.

- `environment.yml` gives exact versions and works on any platform: Python 3.12, CalculiX 2.23 (conda-forge), numpy 2.5.4, scipy 1.18.1, pandas 3.0.6, pyarrow 26.0.1, matplotlib 3.11.2, scikit-learn 1.9.1, gmsh 4.15.2, openseespy 3.8.0.0, pytest 9.1.1.
- `environment.lock.yml` is the full export of the working environment on Windows 11, every package included. Use it to trace a difference down to a library.

Check a rebuilt environment with `pytest` (275 tests on 13 Nov 2026), then `python scripts/reproduce.py --quick`. `python scripts/reproduce.py` rebuilds every Paper 1 result. Compare its output with `results/` by content. A difference in the last digits (about 1e-14) between platforms is rounding noise; anything larger is a real change.

If conda-forge or PyPI no longer serve these versions, rebuild in a container with an archived Python 3.12 image. The Zenodo releases hold the source of every version.

## 4. If a solver is no longer available

ShellBench needs nothing that cannot be redone by hand or with another program.

- **Frame analysis** (OpenSeesPy) is linear-elastic 2D and 3D frame analysis. Any frame program can repeat it. Global equilibrium is asserted on every run, and the closed-form tests in `tests/` give targets to check a new solver against.
- **Shell analysis** (CalculiX) writes plain-text `.inp` input decks; `src/shellbench/calculix.py` shows the format. Other FE programs can read or translate them. `validation/benchmarks.csv` holds the MacNeal-Harder benchmark problems and their reference answers, so a new solver can be qualified the same way.
- **Code checks and carbon** are plain arithmetic on clauses of GB 50010-2010, GB 50011-2010 and GB/T 51366-2019. The constants in the source name their clauses. If a code is revised, the design rules list every clause the results depend on.

## 5. What the results mean, and their limits

- **Scope.** The study is screening-level, elastic and code-level. It makes no claim of seismic safety.
- **Hypotheses.** H1-H4 were preregistered before any family row existed. They and their verdicts are in [preregistration.md](preregistration.md). The change log there records every later decision.
- **Anchor.** The anchor building's thesis is not public. Its inputs are typed in [baseline_spec.md](baseline_spec.md), and the thesis values used as targets are in `validation/thesis_values/`.

## 6. Citing

Cite the concept DOI for the software and the dataset DOI for the data (see the README).
