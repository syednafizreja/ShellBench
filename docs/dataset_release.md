# Dataset release v0.4.0 (11 Nov 2026)

© 2026 Syed Nafiz Reja Hasib. The dataset is licensed CC BY 4.0; the code is MIT.

## What is published

One zip, built by `python scripts/make_dataset.py` (deterministic): `shellbench_dataset_v0.4.0.zip`, SHA-256 `36f00644c5d19bcf8301d5d9003b1c0f1843a60785d9047cb128a9745bae7f8e`. It holds the two family files (Parquet and CSV, with provenance), the diaphragm side table, the diaphragm and floor libraries, the Day 31 checks, `carbon_factors.csv`, the data card, a README, `SHA256SUMS.txt` and `zenodo_metadata.json`. Nothing from `thesis_source/` is included.

The zip hash changes if any packaged file changes (the data card is one of them). The hash in the Zenodo record must be the one of the file that is uploaded.

Laptop check, 11 Nov 2026 (The AI assistant, Windows, zlib 1.3.2) [J]: a build from the v0.4.0 tag gives zip SHA-256 `17b2d57541599d0e4ea39f9abace1ac3b06b67b1534efa4cc7c5ba8f4148d60e`, not the hash above. Every file inside it is byte-identical to the committed file. The zip hash can also differ because a different zlib compresses differently, so the portable check is `SHA256SUMS.txt` inside the zip, not the zip hash. Before this fix, Windows checkouts (`core.autocrlf=true`) turned LF into CRLF and changed the packed CSVs. `.gitattributes` now checks the inputs out byte for byte. Author to confirm: the uploaded zip's `SHA256SUMS.txt` matches the one from a build of the tag.

Decisions, 11 Nov 2026 (The AI assistant, with the author's standing permission) [J]: (1) the file to upload is the build of the v0.4.0 tag on the laptop (`17b2d575…`), because its every member is checked against git. The Zenodo record's hash is that file's hash. (2) `carbon_factors.csv` stays in the dataset. It is a short table of cited values (GB/T 51366-2019 Appendix D and one manuscript table), with source and page for each value, and every carbon number in the families traces to it. Author to confirm. (3) Publishing runs through the Zenodo deposit API (`C:\Users\ASUS\tools\zenodo\publish.py`, outside the repo). It needs a personal access token in `C:\Users\ASUS\.AI assistant\zenodo-token.txt`. Only the author can create that token.

## Gate (schedule.md, Day 33)

- Day 31 checks: all pass on the rebuilt files (results/day31_checks.csv).
- `python scripts/reproduce.py`: ran in full on 11 Nov 2026 (6 min). Every family result file came back identical to the committed one. Known noise only: CRLF line endings and the last printed digit of a few CalculiX values in `panel_day25.csv` and `floor_library.csv`.
- Rebuild at 0.4.0: only the columns `release` and `shellbench_version` changed in the family files (checked column by column). The H1-H3 verdicts therefore run on the same numbers as the pre-release run.
- Provenance: the git commit is now read before the result files are written, so a clean tree is recorded as clean. The old files said "+dirty" for that reason.

## Zenodo form (the author does this; Zenodo has no import for these fields)

Upload `shellbench_dataset_v0.4.0.zip`, then fill the form from `zenodo_metadata.json` (same text is in the zip): resource type Dataset; title; creator Hasib, Syed Nafiz Reja with ORCID 0009-0002-7162-7890; description; licence Creative Commons Attribution 4.0 International; version 0.4.0; publication date 2026-11-11; keywords; related identifier: "is supplement to" 10.5281/zenodo.23851675 (software concept DOI) and the repository URL. Publish. Paste the new DOI in the thread; the day thread adds it to the README, the data card and CITATION.cff.

## Tag

After the PR is merged: annotated tag `v0.4.0` on the merge commit, named "Dataset release". No GitHub release, so no second DOI is minted; the software DOI stays with v1.0 (README, "plain tags").
