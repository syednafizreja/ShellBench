"""tests/test_csv_wellformed.py

Every committed CSV must parse cleanly: each row has exactly as many fields
as the header. A stray comma in an unquoted text cell shifts the columns, and
a reader such as pandas or Excel then reports or silently drops data. This
guards data/, results/, validation/ and the paper tables.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = ("data", "results", "validation", "paper")


def test_every_csv_row_matches_header():
    """No committed CSV has a row longer or shorter than its header."""
    bad = []
    for folder in FOLDERS:
        for path in sorted((ROOT / folder).rglob("*.csv")):
            with open(path, encoding="utf-8-sig", newline="") as fh:
                rows = list(csv.reader(fh))
            if not rows:
                continue
            n = len(rows[0])
            for i, row in enumerate(rows[1:], start=2):
                if row and len(row) != n:
                    bad.append(f"{path.relative_to(ROOT).as_posix()} line {i}: {len(row)} fields, header {n}")
    assert not bad, "\n".join(bad[:20])
