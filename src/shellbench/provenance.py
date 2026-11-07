"""Provenance for every result file: package versions, git commit and the analysis seed.

``batch.write`` calls ``write_sidecar`` so each ``stem.csv``/``stem.parquet`` gets a
``stem.provenance.json`` next to it (paper/paper1/00_core.md section 10).
"""

from __future__ import annotations

import json
import platform
import subprocess
from importlib import metadata
from pathlib import Path

#: Seed for every random step of the analysis: the H2 permutation test and the
#: 2,000-resample bootstrap (preregistration.md 2.1). The value is the
#: preregistration approval date, 3 Nov 2026 [J]; it has no other meaning.
SEED: int = 20261103

#: Packages whose versions are recorded (environment.yml).
PACKAGES: tuple[str, ...] = ("numpy", "pandas", "pyarrow", "openseespy", "matplotlib", "pytest")


def versions() -> dict[str, str]:
    """Return the Python version and the installed version of each of ``PACKAGES``."""
    out = {"python": platform.python_version()}
    for name in PACKAGES:
        try:
            out[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            out[name] = "not installed"
    return out


def git_commit(root: Path) -> str:
    """Return the current git commit of ``root``, with "+dirty" if files changed, or "unknown"."""
    try:
        sha = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                             text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
                               capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return sha + ("+dirty" if dirty else "")


def record(root: Path, **extra) -> dict:
    """Return the provenance record: shellbench version, git commit, seed, versions and ``extra``."""
    import shellbench
    return {"shellbench_version": shellbench.__version__, "git_commit": git_commit(root),
            "seed": SEED, "versions": versions(), **extra}


def write_sidecar(stem: Path, root: Path, **extra) -> Path:
    """Write ``stem.provenance.json`` and return its path."""
    path = stem.with_name(stem.name + ".provenance.json")
    path.write_text(json.dumps(record(root, **extra), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
