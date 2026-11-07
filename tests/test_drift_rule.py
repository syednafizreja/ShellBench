"""Tests for the R11 drift-fix rules (decision card 2, 5 Nov 2026).

File: tests/test_drift_rule.py

The "columns_first" rule must still give the Day 19 pilot values, so the
change of default moved nothing else. The "best_ratio" rule must meet the same
drift limit with no more frame concrete, and must keep GB 50011 cl. 6.3.1.
"""

import pytest

from shellbench import batch as bt
from shellbench import generator as g

SPEC = next(sp for sp in bt.family() if sp["building_id"] == "s07-p030-tg35-C40")


def _row(rule: str) -> dict:
    """Run s07-p030 (the building of Day 19 finding 2) with ``rule``, R14 off.

    The Day 19 pilot had no capacity design; R14 (Day 20) changes the sizes,
    so these tests pin the R11 rules alone.
    """
    conc, steel = bt.factors()
    return bt.run_building(SPEC, conc, steel, drift_rule=rule, capacity_design=False)


def test_columns_first_reproduces_day19_pilot():
    """Old rule: 1100 mm columns and beams 850/750/850 mm (LOG.md, Day 19, finding 2)."""
    row = _row("columns_first")
    assert row["status"] == "ok"
    assert row["column_mm"] == 1100
    assert row["beam_h_mm"] == "850/750/850"


def test_best_ratio_meets_drift_with_less_concrete():
    """New rule: drift within 1/550 and no more concrete than the old rule."""
    new, old = _row("best_ratio"), _row("columns_first")
    assert new["max_drift_ratio"] <= g.DRIFT_LIMIT
    assert new["concrete_m3_per_m2"] <= old["concrete_m3_per_m2"]
    assert new["column_mm"] < old["column_mm"]


def test_beam_proportions_631():
    """cl. 6.3.1: h/b above 4 or clear span/h below 4 fails."""
    b = bt.ANCHOR
    ok = g.Sizes(600, [(300, 700)] * 3, 120)
    assert g.beams_meet_631(b, ok)
    assert not g.beams_meet_631(b, g.Sizes(600, [(300, 1250)] * 3, 120))  # h/b = 4.17
    assert not g.beams_meet_631(b, g.Sizes(600, [(450, 1700)] * 3, 120))  # (6600 - 600)/1700 = 3.5


def test_unknown_rule_raises():
    """Only the rules in DRIFT_RULES are accepted."""
    with pytest.raises(ValueError):
        g.generate(bt.ANCHOR, drift_rule="beams_only")
