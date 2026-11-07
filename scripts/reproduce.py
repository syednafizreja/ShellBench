"""Reproduce every ShellBench result with one command, or run a fast self-test.

Usage (from the repository root, in the ``research`` environment)::

    python scripts/reproduce.py --quick   # self-test: tests + 2 buildings, a few minutes
    python scripts/reproduce.py           # every result in results/ that Paper 1 uses

Steps (full run):

1. ``pytest`` (the whole suite).
2. ``python -m shellbench.anchor_frame``: every ``results/anchor_*`` and thesis check file.
3. ``python -m shellbench.panel``: ``results/panel_day25.csv`` (needs CalculiX ``ccx``).
4. ``python -m shellbench.floorlib``: ``results/floor_library.csv`` (needs ``ccx``).
5. ``python -m shellbench.batch``: the primary conventional family
   (``results/family_rc_r14_building_v2``, preregistration.md) and its sensitivity runs.

Each family file gets a ``.provenance.json`` with package versions, the git commit
and the analysis seed (``shellbench.provenance``). After a full run, ``git status``
should show no changed result file except the provenance files, with two known
exceptions seen on 6 Nov 2026 (Linux against the Windows run that made the files):

* line endings only (CRLF against LF), e.g. ``anchor_carbon.csv``: check with
  ``git diff --ignore-cr-at-eol``;
* the last printed digit of a few CalculiX values in ``panel_day25.csv`` and
  ``floor_library.csv`` (utilisation 0.5983 against 0.5982), and Parquet floats
  differing near 1e-14 relative. Every family CSV value at 4 significant figures matched.

Anything larger is a reproducibility failure to report.

The Day 19 pilot files (``results/family_rc_pilot*``) were made before R14 and are
kept as a record; they are not rebuilt here (preregistration.md, "Deviations").
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

#: Family runs: (output stem under results/, extra batch arguments).
FAMILY_RUNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("family_rc_r14_building_v2", ("--scope", "building_v2")),
)


def run(args: list[str]) -> None:
    """Run one command from the repository root and stop on the first failure."""
    print("$", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def quick() -> None:
    """Fast self-test: the test suite and a 2-building family run to a temporary folder."""
    run([PY, "-m", "pytest", "-q"])
    with tempfile.TemporaryDirectory() as tmp:
        stem = Path(tmp) / "family_selftest"
        run([PY, "-m", "shellbench.batch", "--n", "2", "--scope", "building_v2", "--out", str(stem)])
        for suffix in (".csv", ".parquet", ".provenance.json"):
            if not stem.with_name(stem.name + suffix).exists() and not stem.with_suffix(suffix).exists():
                raise SystemExit(f"self-test failed: {stem.name}{suffix} was not written")
    print("self-test passed")


def full() -> None:
    """Rebuild every result Paper 1 uses."""
    run([PY, "-m", "pytest", "-q"])
    run([PY, "-m", "shellbench.anchor_frame"])
    run([PY, "-m", "shellbench.panel"])
    run([PY, "-m", "shellbench.floorlib"])
    for stem, extra in FAMILY_RUNS:
        run([PY, "-m", "shellbench.batch", *extra, "--out", str(ROOT / "results" / stem)])
    run(["git", "status", "--short", "results", "figures"])


def main(argv: list[str] | None = None) -> None:
    """Command line: ``--quick`` for the self-test, otherwise the full run."""
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--quick", action="store_true", help="fast self-test only")
    a = p.parse_args(argv)
    quick() if a.quick else full()


if __name__ == "__main__":
    main()
