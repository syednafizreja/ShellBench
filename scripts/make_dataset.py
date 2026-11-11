"""Build the ShellBench dataset package for Zenodo (Day 33, v0.4.0).

File: scripts/make_dataset.py

What this script does
---------------------
It copies the published result files into one folder, writes a README, the
SHA-256 checksums and the Zenodo metadata, and makes one zip file. The zip is
deterministic: the same inputs give the same bytes, so the checksum in the
README can be checked by anyone who rebuilds it.

Usage (from the repository root)::

    python scripts/make_dataset.py            # writes dist/shellbench_dataset_v0.4.0.zip
    python scripts/make_dataset.py --out DIR  # another folder

Every number in the README and the metadata is read from the files themselves.
Nothing from ``thesis_source/`` is included. The licence of the dataset is
CC BY 4.0 (the code stays MIT). The DOI is added after Zenodo mints it; this
script never writes a DOI of the new record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

#: Zip entry timestamp (fixed, so the zip is reproducible): year, month, day, hour, minute, second.
ZIP_TIME: tuple[int, int, int, int, int, int] = (2026, 11, 11, 0, 0, 0)
#: Concept DOI of the ShellBench software record on Zenodo (checked on the Zenodo API, 10 Nov 2026).
SOFTWARE_CONCEPT_DOI: str = "10.5281/zenodo.23851675"
REPO_URL: str = "https://github.com/syednafizreja/ShellBench"
ORCID: str = "0009-0002-7162-7890"

#: (source path relative to the repository root, name inside the package).
FILES: tuple[tuple[str, str], ...] = (
    ("results/family_rc_r14_building_v2.parquet", "family_rc_r14_building_v2.parquet"),
    ("results/family_rc_r14_building_v2.csv", "family_rc_r14_building_v2.csv"),
    ("results/family_rc_r14_building_v2.provenance.json", "family_rc_r14_building_v2.provenance.json"),
    ("results/family_shell.parquet", "family_shell.parquet"),
    ("results/family_shell.csv", "family_shell.csv"),
    ("results/family_shell.provenance.json", "family_shell.provenance.json"),
    ("results/family_shell_diaphragm.csv", "family_shell_diaphragm.csv"),
    ("results/diaphragm_library.csv", "diaphragm_library.csv"),
    ("results/floor_library.csv", "floor_library.csv"),
    ("results/day31_checks.csv", "day31_checks.csv"),
    ("data/carbon_factors.csv", "carbon_factors.csv"),
    ("docs/data_card.md", "data_card.md"),
)


def sha256(path: Path) -> str:
    """SHA-256 of a file, as a hex string."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def family_facts(root: Path = ROOT) -> dict:
    """Counts read from the two family files: rows, buildings, statuses, version and release label."""
    rc = pd.read_parquet(root / "results" / "family_rc_r14_building_v2.parquet")
    sh = pd.read_parquet(root / "results" / "family_shell.parquet")
    return {
        "version": str(sh["shellbench_version"].iloc[0]),
        "release": str(sh["release"].iloc[0]),
        "buildings": int(rc["building_id"].nunique()),
        "rc_rows": int(len(rc)),
        "rc_status": {k: int(v) for k, v in rc["status"].value_counts().sort_index().items()},
        "shell_rows": int(len(sh)),
        "shell_status": {k: int(v) for k, v in sh["status"].value_counts().sort_index().items()},
        "storeys": sorted(int(s) for s in rc["storeys"].unique()),
        "pga_g": sorted(float(p) for p in rc["pga_g"].unique()),
    }


def counts(status: dict) -> str:
    """Status counts as plain words, e.g. ``33 ok, 2 outside the code, 1 failed``."""
    words = {"ok": "ok", "outside_code": "outside the code", "failed": "failed"}
    return ", ".join(f"{status[k]} {words[k]}" for k in ("ok", "outside_code", "failed") if k in status)


def description(f: dict) -> str:
    """Zenodo description text, with the counts from the files."""
    return (
        "Result files of ShellBench: whole-building A1-A3 embodied carbon of reinforced-concrete frames "
        "designed to GB 50010 and GB 50011, with a conventional beam-and-slab floor and with thin-shell "
        f"(vaulted) floors. The family has {f['buildings']} buildings ({f['storeys'][0]} to {f['storeys'][-1]} storeys, "
        f"peak ground acceleration {', '.join(f'{p:g}' for p in f['pga_g'])} g). Conventional file: {f['rc_rows']} rows, "
        f"{counts(f['rc_status'])}. Shell file: {f['shell_rows']} rows (floor variant x topping x building), "
        f"{counts(f['shell_status'])}. Failures and designs outside the code are counted, not dropped. "
        "Carbon is in kgCO2e per m2 of floor area, from the GB/T 51366-2019 factors in carbon_factors.csv. "
        "Screening-level, elastic, code-level analysis under the stated assumptions; it makes no claim of seismic "
        "safety. Read data_card.md for every column, unit and flag. Files carry provenance (package versions, git "
        "commit, seed). Code: " + REPO_URL + " (MIT licence)."
    )


def zenodo_metadata(f: dict) -> dict:
    """Metadata for the Zenodo deposit form (one field per form field)."""
    return {
        "upload_type": "dataset",
        "title": f"ShellBench building family v{f['version']}: embodied carbon of reinforced-concrete frames with conventional and thin-shell floors",
        "creators": [{"name": "Hasib, Syed Nafiz Reja", "orcid": ORCID}],
        "description": description(f),
        "version": f["version"],
        "publication_date": "2026-11-11",
        "access_right": "open",
        "license": "cc-by-4.0",
        "language": "eng",
        "keywords": ["embodied carbon", "thin-shell floor", "reinforced concrete", "seismic design",
                     "structural engineering", "life-cycle assessment", "benchmark dataset"],
        "related_identifiers": [
            {"relation": "isSupplementTo", "identifier": SOFTWARE_CONCEPT_DOI, "resource_type": "software", "scheme": "doi"},
            {"relation": "isSupplementTo", "identifier": REPO_URL, "resource_type": "software", "scheme": "url"},
        ],
    }


def readme(f: dict, names: list[str]) -> str:
    """README of the package."""
    lines = [
        f"# ShellBench dataset v{f['version']}", "",
        "© 2026 Syed Nafiz Reja Hasib. Licence: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). "
        "Give credit to the author and cite the Zenodo record. The code is MIT-licensed at " + REPO_URL + ".", "",
        description(f), "",
        f"Release label in the `release` column: `{f['release']}`.", "",
        "## Files", "",
        *[f"- `{n}`" for n in names], "",
        "`family_rc_r14_building_v2.*` is the conventional family (data_card.md calls it `family_rc`). "
        "`SHA256SUMS.txt` lists the checksum of every file. `zenodo_metadata.json` is the metadata of this deposit.", "",
        "## How to cite", "",
        "Hasib, S. N. R. (2026). ShellBench building family, version " + f["version"] + " [Data set]. Zenodo. "
        "Use the DOI shown on the Zenodo record page.", "",
        "## What this is not", "",
        "It is not a design tool and not a safety assessment. The numbers are screening-level and depend on the "
        "stated assumptions and on the carbon factors in `carbon_factors.csv`.", "",
    ]
    return "\n".join(lines)


def build(out_dir: Path, root: Path = ROOT) -> Path:
    """Build the package folder and the zip in ``out_dir``; return the zip path."""
    name = None
    f = family_facts(root)
    name = f"shellbench_dataset_v{f['version']}"
    pkg = out_dir / name
    if pkg.exists():
        shutil.rmtree(pkg)
    pkg.mkdir(parents=True)
    names = []
    for src, dst in FILES:
        shutil.copyfile(root / src, pkg / dst)
        names.append(dst)
    (pkg / "README.md").write_text(readme(f, sorted(names)), encoding="utf-8", newline="\n")
    (pkg / "zenodo_metadata.json").write_text(json.dumps(zenodo_metadata(f), indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    members = sorted(p.name for p in pkg.iterdir())
    sums = "".join(f"{sha256(pkg / n)}  {n}\n" for n in members)
    (pkg / "SHA256SUMS.txt").write_text(sums, encoding="utf-8", newline="\n")
    zpath = out_dir / f"{name}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(p.name for p in pkg.iterdir()):
            info = zipfile.ZipInfo(f"{name}/{n}", date_time=ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, (pkg / n).read_bytes())
    return zpath


def main(argv: list[str] | None = None) -> None:
    """Command line entry."""
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--out", type=Path, default=ROOT / "dist")
    a = p.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    z = build(a.out)
    print(z, z.stat().st_size, "bytes, sha256", sha256(z))


if __name__ == "__main__":
    main()
