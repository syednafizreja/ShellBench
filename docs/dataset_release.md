# Dataset release v0.4.0 (11 Nov 2026)

© 2026 Syed Nafiz Reja Hasib. The dataset is licensed CC BY 4.0; the code is MIT.

## What is published

One zip, built by `python scripts/make_dataset.py` (deterministic): `shellbench_dataset_v0.4.0.zip`, SHA-256 `36f00644c5d19bcf8301d5d9003b1c0f1843a60785d9047cb128a9745bae7f8e`. It holds the two family files (Parquet and CSV, with provenance), the diaphragm side table, the diaphragm and floor libraries, the Day 31 checks, `carbon_factors.csv`, the data card, a README, `SHA256SUMS.txt` and `zenodo_metadata.json`. Nothing from `thesis_source/` is included.

The zip hash changes if any packaged file changes (the data card is one of them). The hash in the Zenodo record must be the one of the file that is uploaded.

## Gate (schedule.md, Day 33)

- Day 31 checks: all pass on the rebuilt files (results/day31_checks.csv).
- `python scripts/reproduce.py`: ran in full on 11 Nov 2026 (6 min). Every family result file came back identical to the committed one. Known noise only: CRLF line endings and the last printed digit of a few CalculiX values in `panel_day25.csv` and `floor_library.csv`.
- Rebuild at 0.4.0: only the columns `release` and `shellbench_version` changed in the family files (checked column by column). The H1-H3 verdicts therefore run on the same numbers as the pre-release run.
- Provenance: the git commit is now read before the result files are written, so a clean tree is recorded as clean. The old files said "+dirty" for that reason.

## Zenodo form (the author does this; Zenodo has no import for these fields)

Upload `shellbench_dataset_v0.4.0.zip`, then fill the form from `zenodo_metadata.json` (same text is in the zip): resource type Dataset; title; creator Hasib, Syed Nafiz Reja with ORCID 0009-0002-7162-7890; description; licence Creative Commons Attribution 4.0 International; version 0.4.0; publication date 2026-11-11; keywords; related identifier: "is supplement to" 10.5281/zenodo.23851675 (software concept DOI) and the repository URL. Publish. Paste the new DOI in the thread; the day thread adds it to the README, the data card and CITATION.cff.

## Tag

After the PR is merged: annotated tag `v0.4.0` on the merge commit, named "Dataset release". No GitHub release, so no second DOI is minted; the software DOI stays with v1.0 (README, "plain tags").
