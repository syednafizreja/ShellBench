"""Tests of the ``building_v2`` take-off scope (data_card row 4, 5 Nov 2026).

File: tests/test_batch_scope.py

The size-independent elements must equal the anchor's committed take-off
(results/anchor_quantities.csv, grid plan, code steel), and the v2 row must
differ from the v1 row by exactly those elements times their factors.
"""
import csv
from pathlib import Path

import pytest

from shellbench import batch as bt
from shellbench import carbon as cb

ROOT = Path(__file__).resolve().parents[1]


def _anchor_rows() -> dict[tuple[str, str], float]:
    """Per-floor-area rows of the grid plan, code steel, from the committed CSV."""
    with open(ROOT / "results" / "anchor_quantities.csv", encoding="utf-8") as fh:
        return {(r["element [text]"], r["material [text]"]): float(r["per_floor_area [unit/m2]"])
                for r in csv.DictReader(fh)
                if r["plan [text]"] == "grid" and r["steel_source [text]"] == "code"}


def test_fixed_elements_match_anchor_takeoff():
    """Slab bars, secondary and longitudinal beams equal the anchor rows (5 d.p. in the CSV)."""
    fixed, anchor = cb.family_fixed_per_m2(), _anchor_rows()
    assert set(fixed) == set(cb.FAMILY_FIXED_ELEMENTS)
    for key, v in fixed.items():
        assert v == pytest.approx(anchor[key], abs=6e-6), key


def test_v2_adds_exactly_the_fixed_elements():
    """v2 minus v1 is the fixed elements plus the R14 frame stirrups (lateral steel)."""
    conc, steel = bt.factors()
    spec = bt.family()[0]  # first building (0.10 g block)
    v1 = bt.run_building(spec, conc, steel)
    v2 = bt.run_building(spec, conc, steel, scope="building_v2")
    assert v1["status"] == v2["status"] == "ok"
    assert (v1["takeoff_scope"], v2["takeoff_scope"]) == ("frame_strip_v1", "building_v2")
    fixed = cb.family_fixed_per_m2()

    def part(where: str, concrete: bool) -> float:
        return sum(v for k, v in fixed.items()
                   if cb.FAMILY_FIXED_ELEMENTS[k] == where and (k[1] == cb.CONCRETE_GRADE) == concrete)

    assert v2["floor_concrete_m3_per_m2"] - v1["floor_concrete_m3_per_m2"] == pytest.approx(part("floor", True))
    assert v2["floor_steel_kg_per_m2"] - v1["floor_steel_kg_per_m2"] == pytest.approx(part("floor", False))
    assert v2["lateral_concrete_m3_per_m2"] - v1["lateral_concrete_m3_per_m2"] == pytest.approx(part("lateral", True))
    stirrups = v2["beam_stirrup_kg_per_m2"] + v2["column_stirrup_kg_per_m2"]
    assert stirrups > 0.0
    assert v2["lateral_steel_kg_per_m2"] - v1["lateral_steel_kg_per_m2"] == pytest.approx(part("lateral", False) + stirrups)
    extra = ((part("floor", True) + part("lateral", True)) * conc
             + (part("floor", False) + part("lateral", False) + stirrups) * steel)
    assert v2["carbon_building_kgco2e_per_m2"] - v1["carbon_building_kgco2e_per_m2"] == pytest.approx(extra)
    assert v2["column_mm"] == v1["column_mm"]  # the scope does not change the design


def test_unknown_scope_raises():
    """A misspelt scope is an error, not a silent v1 row."""
    conc, steel = bt.factors()
    with pytest.raises(ValueError):
        bt.run_building(bt.family()[0], conc, steel, scope="whole")
