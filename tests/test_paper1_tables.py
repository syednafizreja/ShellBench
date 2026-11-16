"""tests/test_paper1_tables.py

The committed Paper 1 tables (paper/paper1/tables/) must equal a fresh build
from results/ and data/ by scripts/paper1_tables.py, and the headline cells
must match the values recorded in paper/paper1/numbers.md.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "paper" / "paper1" / "tables"


def _builder():
    """Import scripts/paper1_tables.py as a module."""
    spec = importlib.util.spec_from_file_location("paper1_tables", ROOT / "scripts" / "paper1_tables.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_tables_rebuild_identically(tmp_path):
    """Every committed table file equals a fresh build byte for byte."""
    for p in _builder().build(tmp_path):
        committed = COMMITTED / p.name
        assert committed.exists(), f"{p.name} not committed"
        assert p.read_bytes() == committed.read_bytes().replace(b"\r\n", b"\n"), p.name


def test_headline_cells_match_numbers_md():
    """Spot values recorded in numbers.md rows 2.2, 3.1 and 3.4."""
    t1 = pd.read_csv(COMMITTED / "table1_anchor_validation.csv")
    assert t1.loc[0, "targets"] == 40 and t1.loc[0, "above_10pct"] == 11
    assert "4.25 %" in t1.loc[0, "result"]
    assert "214.75 kN vs 264.77 kN" in t1.loc[3, "result"]
    t5 = pd.read_csv(COMMITTED / "table5_verdicts.csv").set_index("hypothesis")
    assert t5.loc["H1", "verdict"] == "partly supported"
    assert t5.loc["H2", "verdict"] == "not supported"
    assert t5.loc["H3", "verdict"] == "not supported"
    assert t5.loc["H4", "verdict"] == "partly supported"
    assert "2.27" in t5.loc["H4", "evidence"] and "73.3 %" in t5.loc["H4", "evidence"]
