"""Tests for the batch runner and the frozen data format (Playbook Day 18).

File: tests/test_family.py
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

from shellbench import family as f

ROOT = Path(__file__).resolve().parents[1]


def test_columns_match_the_data_card():
    """Every column in COLUMNS is documented in docs/data_card.md (the frozen format)."""
    card = (ROOT / "docs" / "data_card.md").read_text(encoding="utf-8")
    documented = set(re.findall(r"^\| ([a-z0-9_, ]+) \|", card, flags=re.M))
    names = {n.strip() for row in documented for n in row.split(",")}
    assert set(f.COLUMNS) <= names


def test_sample_is_seeded_and_covers_every_cell():
    a, b = f.sample_family(72), f.sample_family(72)
    assert a == b
    cells = {(x.storeys, x.pga_g) for x in a}
    assert len(cells) == 36
    assert all(f.FAMILY["side_span_m"][0] <= x.side_span_m <= f.FAMILY["side_span_m"][1] for x in a)


def test_rows_never_dropped(tmp_path):
    """n rows in, n rows out; unconfirmed PGA levels are not_run with a reason."""
    rows = f.run_family(8, tmp_path)
    assert len(rows) == 8
    with (tmp_path / "family_rc.csv").open() as fh:
        header = next(csv.reader(fh))
    assert tuple(header) == f.COLUMNS
    for r in rows:
        assert r["status"] in ("ok", "failed", "not_run")
        assert (r["status"] == "ok") == (r["reason"] == "")
        if r["pga_g"] == 0.10:
            assert r["status"] == "ok" and r["carbon_kgco2e_per_m2"] > 0
