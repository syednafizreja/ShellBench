"""Tests for the whole-building quantity take-off and the carbon step (Day 12).

File: tests/test_carbon.py

Plan geometry (column counts, areas), the rule-11 checks of the take-off
(slab volume, footing hand check), the factor file reader, and a pin of
today's totals so a later change has to be read again (docs/anchor_notes.md,
"How the take-off is read"). The factor values used here are test inputs
(1.0 and 2.0), not carbon factors.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from shellbench import carbon as cb
from shellbench import checks as c

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def cases() -> dict[str, c.CaseResult]:
    """Solve the anchor load cases once for the module."""
    wind, quake = c.anchor_forces(ROOT)
    return c.run_cases(wind, quake)


@pytest.fixture(scope="module")
def quantities(cases) -> list[dict]:
    """Take off the grid plan with both steel sources."""
    plan = cb.make_plan("grid")
    pads = cb.footings(plan, cases)
    steel = {"thesis": cb.thesis_frame_beam_steel(ROOT),
             "code": cb.code_frame_beam_steel(c.beam_design_rows(cases))}
    return [r for s in ("thesis", "code") for r in cb.take_off(plan, s, steel[s], pads)]


def _qty(rows, source, element, material):
    return next(r["quantity"] for r in rows if r["steel_source [text]"] == source
                and r["element [text]"] == element and r["material [text]"] == material)


def test_plans():
    """Grid: 28 columns, 806.4 m2 a level (B11). Drawn: 27 columns, notch 13.2 x 7.2 m."""
    grid, drawn = cb.make_plan("grid"), cb.make_plan("drawn")
    assert len(grid.columns()) == 28
    assert grid.area_m2() == pytest.approx(38.4 * 21.0)
    assert cb.N_SLAB_LEVELS * grid.area_m2() == pytest.approx(3225.6)
    assert len(drawn.columns()) == 27
    assert (3, 0) not in drawn.columns()
    assert drawn.area_m2() == pytest.approx(38.4 * 21.0 - 13.2 * 7.2)
    assert len(grid.transverse_beams()) == 21 and len(grid.longitudinal_beams()) == 24
    assert len(drawn.transverse_beams()) == 20 and len(drawn.longitudinal_beams()) == 22
    assert len(grid.secondary_beams()) == 6
    with pytest.raises(ValueError):
        cb.make_plan("E-shape")


def test_edge_beams_have_one_panel():
    """Beams on the building edge, and next to the notch, have slab on one side only."""
    grid, drawn = cb.make_plan("grid"), cb.make_plan("drawn")
    sides = {(k, j): s for k, j, s in grid.transverse_beams()}
    assert sides[(0, 0)] == 1 and sides[(6, 1)] == 1 and sides[(3, 1)] == 2
    long_drawn = {(m, i): s for m, i, s in drawn.longitudinal_beams()}
    assert long_drawn[(1, 2)] == 1 and (0, 2) not in long_drawn


def test_slab_volume(quantities):
    """Rule 11: slab = 4 x (plan area - column footprints inside it) x 0.12 m."""
    inside = 4 * 0.25 + 14 * 0.5 + 10 * 1.0  # corner, edge and interior columns
    expected = 4 * (38.4 * 21.0 - inside * 0.36) * 0.12
    assert _qty(quantities, "thesis", "slabs", "C40") == pytest.approx(expected, abs=1e-3)


def test_column_quantities(quantities):
    """28 columns x 0.36 m2 x 15.35 m; steel 4C22 (thesis) or 0.75 % (code)."""
    height = 4.55 + 3 * 3.6
    assert _qty(quantities, "code", "columns", "C40") == pytest.approx(28 * 0.36 * height,
                                                                       abs=1e-3)
    thesis = 28 * c.bar_area_mm2("4C22") * 1e-6 * height * 7850
    code = 28 * 2700 * 1e-6 * height * 7850
    assert _qty(quantities, "thesis", "columns", "HRB400") == pytest.approx(thesis, abs=1e-2)
    assert _qty(quantities, "code", "columns", "HRB400") == pytest.approx(code, abs=1e-2)


def test_frame_beam_steel_rule():
    """Bottom over the span, ends over l_n / 3, 2C14 over the middle third."""
    s = cb.FrameBeamSteel(top_left=900.0, top_right=600.0, bottom=500.0)
    ln = 6.6
    area_length = 1500.0 * ln / 3 + c.bar_area_mm2("2C14") * ln / 3 + 500.0 * ln
    assert s.mass_kg(ln) == pytest.approx(area_length * 1e-6 * 7850)


def test_thesis_beam_steel_uses_printed_areas():
    """Levels 1-3 take the floor-1 rows, the roof the floor-5 rows (B4, D10)."""
    steel = cb.thesis_frame_beam_steel(ROOT)
    assert steel[("AB", 2)].top_left == 1472.0 and steel[("AB", 2)].bottom == 603.0
    assert steel[("AB", 4)].top_left == 603.0


def test_footing_hand_check(cases):
    """Rule 11: grid axis 3, line B. N_k = (D + L) x 6.6 x 6.9 / (7.2 x 6.9)."""
    k = ("B", "1", "bottom")
    n2d = cases["D"].axial[k] + cases["L"].axial[k]
    n_k = n2d * (6.6 * (7.2 + 6.6) / 2) / (7.2 * (7.2 + 6.6) / 2)
    pad = cb.size_footing((2, 1), n_k)
    b = math.ceil(math.sqrt(n_k / (220 - 20 * 1.1)) * 10) / 10
    assert pad.b_m == pytest.approx(b)
    m = (b - 0.6) ** 2 * (2 * b + 0.6) * 1.35 * n_k / b ** 2 / 24
    assert pad.as_mm2 == pytest.approx(max(m * 1e6 / (0.9 * 360 * 550), 0.0015 * b * 0.6e6))
    grid = cb.footings(cb.make_plan("grid"), cases)
    assert next(p for p in grid if p.node == (2, 1)).n_k_kn == pytest.approx(n_k)


def _write_factors(path: Path, rows: list[str]) -> Path:
    header = ",".join(cb.FACTOR_FIELDS)
    path.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")
    return path


def test_carbon_with_test_factors(quantities, tmp_path):
    """With factor 1.0 per m3 and 2.0 per t, carbon = m3 + 0.002 x kg."""
    f = _write_factors(tmp_path / "f.csv", [
        "T,C40,1.0,kgCO2e/m3,test,1", "T,HRB400,2.0,kgCO2e/t,test,1",
        "T,HPB300,2.0,kgCO2e/t,test,1"])
    rows = cb.carbon_rows(quantities, cb.read_factors(f))
    slab = next(r for r in rows if r["steel_source [text]"] == "thesis"
                and r["element [text]"] == "slabs")
    expected = (_qty(quantities, "thesis", "slabs", "C40")
                + 0.002 * _qty(quantities, "thesis", "slabs", "HRB400"))
    assert slab["A1-A3 [kgCO2e]"] == pytest.approx(expected, abs=0.1)
    assert len(rows) == 2 * len(cb.ELEMENTS)


def test_factor_errors(quantities, tmp_path):
    """A missing material, source or unknown unit stops the run (rule 10)."""
    missing = _write_factors(tmp_path / "m.csv", ["T,C40,1.0,kgCO2e/m3,test,1"])
    with pytest.raises(KeyError):
        cb.carbon_rows(quantities, cb.read_factors(missing))
    no_source = _write_factors(tmp_path / "s.csv", ["T,C40,1.0,kgCO2e/m3,,1"])
    with pytest.raises(ValueError):
        cb.read_factors(no_source)
    bad_unit = _write_factors(tmp_path / "u.csv", ["T,C40,1.0,kgCO2/ft3,test,1"])
    with pytest.raises(ValueError):
        cb.read_factors(bad_unit)


def test_totals_pinned(quantities):
    """Pins today's grid totals (29 Oct 2026): concrete 819.2 m3; slabs carry
    the most concrete (47 %) and the most bar steel."""
    conc = {e: _qty(quantities, "thesis", e, "C40") for e in cb.ELEMENTS}
    assert sum(conc.values()) == pytest.approx(819.15, abs=0.05)
    assert max(conc, key=conc.get) == "slabs"
    assert conc["slabs"] / sum(conc.values()) == pytest.approx(0.469, abs=1e-3)
    bars = {e: _qty(quantities, "code", e, "HRB400") for e in cb.ELEMENTS}
    assert max(bars, key=bars.get) == "slabs"
