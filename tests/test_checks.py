"""Tests for the GB 50010 / GB 50011 design checks (Day 11).

File: tests/test_checks.py

Closed-form section design, the code values, the load cases (G_E as one
run, mirror symmetry of wind and earthquake), and a pin of today's flags so
a later change has to be read again (docs/anchor_notes.md, "How the design
checks are read").
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import pytest

from shellbench import anchor_frame as af
from shellbench import checks as c
from shellbench import combinations as cb

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def cases() -> dict[str, c.CaseResult]:
    """Solve the anchor load cases once for the module."""
    wind, quake = c.anchor_forces(ROOT)
    return c.run_cases(wind, quake)


@pytest.fixture(scope="module")
def tables(cases) -> dict[str, list[dict]]:
    """Build the result tables once for the module."""
    return {
        "check": c.beam_check_rows(cases, c.read_thesis_beam_steel(ROOT)),
        "columns": c.column_rows(cases),
        "beams": c.beam_design_rows(cases),
    }


def test_code_values():
    """xi_b 0.518 (formula 6.2.7-1); beam minimum 0.261 % / 0.214 % (Table 11.3.6-1)."""
    assert c.xi_b() == pytest.approx(0.518, abs=5e-4)
    assert c.rho_min_beam("support") == pytest.approx(55 * 1.71 / 360 / 100)
    assert c.rho_min_beam("mid-span") == pytest.approx(45 * 1.71 / 360 / 100)
    with pytest.raises(ValueError):
        c.rho_min_beam("corner")


def test_bar_areas():
    """3C16 = 603 mm2 and 3C25 = 1473 mm2 (thesis prints 603 and 1472)."""
    assert c.bar_area_mm2("3C16") == pytest.approx(603.2, abs=0.1)
    assert c.bar_area_mm2("3C25") == pytest.approx(1472.6, abs=0.1)
    with pytest.raises(ValueError):
        c.bar_area_mm2("3C16+3C16")


def test_section_design_hand_check():
    """Level-1 AB left face, M = 236.37 kN*m, b 300, h0 550: alpha_s 0.1364,
    xi 0.1472, A_s 1288.6 mm2 (worked by hand from cl. 6.2.10)."""
    d = c.design_section(236.37, 300.0, 600.0, "support", True)
    alpha_s = 236.37e6 / (19.1 * 300 * 550**2)
    xi = 1 - math.sqrt(1 - 2 * alpha_s)
    assert d.xi == pytest.approx(xi)
    assert d.as_calc_mm2 == pytest.approx(19.1 * 300 * xi * 550 / 360)
    assert d.as_req_mm2 == pytest.approx(1288.6, abs=0.1)
    assert d.status == "ok"


def test_section_design_limits():
    """Minimum steel governs small moments; large moments need compression steel."""
    small = c.design_section(10.0, 300.0, 600.0, "mid-span", False)
    assert small.as_req_mm2 == pytest.approx(small.as_min_mm2)
    end = c.design_section(550.0, 300.0, 600.0, "support", True)
    assert end.status.startswith("needs compression steel")
    huge = c.design_section(2000.0, 300.0, 600.0, "mid-span", False)
    assert huge.status.startswith("section too small")
    assert c.design_section(0.0, 300.0, 600.0, "support", True).as_calc_mm2 == 0.0


def test_moment_diagram_matches_end_moments():
    """The sagging moment at the beam ends equals the thesis-convention end moments
    (left end as is, right end negated)."""
    fm = af.build_frame()
    af.apply_dead_load(fm, af.LOAD_MODELS["thesis_fem"])
    af.solve_static()
    diagrams = c.beam_moment_diagrams(fm)
    ends = af.beam_end_moments(fm)
    for (span, lvl), ms in diagrams.items():
        assert ms[0] == pytest.approx(ends[(str(lvl), span, "left")])
        assert ms[-1] == pytest.approx(-ends[(str(lvl), span, "right")])


def test_face_index():
    """0.3 m from the centre-line is node 3 at 10 sub-elements per metre."""
    assert c.face_index("AB", 73, True) == 3
    assert c.face_index("BC", 67, True) == 3
    assert c.face_index("AB", 73, False) == 0


def test_gravity_representative_is_dead_plus_half_floor_live(cases):
    """G_E run as one case equals D + 0.5 x (live without the roof)."""
    model, joints, moments = c.floor_live_model()
    lf = c.solve_case("Lf", lambda fm: af.apply_gravity_case(fm, model, joints, moments,
                                                              None, 0.0))
    for k, v in cases["GE"].axial.items():
        assert v == pytest.approx(cases["D"].axial[k] + 0.5 * lf.axial[k], rel=1e-9)
    ms_ge, ms_d, ms_l = (x.moments[("AB", 1)] for x in (cases["GE"], cases["D"], lf))
    assert ms_ge == pytest.approx([d + 0.5 * l for d, l in zip(ms_d, ms_l)], rel=1e-9)


def test_lateral_cases_are_mirror_images(cases):
    """Earthquake from the right gives the mirrored axial forces of the left case."""
    for st in "1234":
        left_a = cases["E_left"].axial[("A", st, "bottom")]
        right_d = cases["E_right"].axial[("D", st, "bottom")]
        assert right_d == pytest.approx(left_a, rel=1e-9)


def test_axial_ratio_hand_check(cases, tables):
    """B1: N = 1.2 G_E + 1.3 E_left; mu = N / (f_c A) = 0.320 <= 0.85."""
    k = ("B", "1", "bottom")
    n = 1.2 * cases["GE"].axial[k] + 1.3 * cases["E_left"].axial[k]
    row = next(r for r in tables["columns"] if r["axis [text]"] == "B" and r["storey [text]"] == 1)
    assert row["N_seismic [kN]"] == pytest.approx(n, abs=0.01)
    assert row["axial_ratio [-]"] == pytest.approx(n * 1e3 / (19.1 * 600 * 600), abs=1e-4)
    assert row["axial_ratio [-]"] == pytest.approx(0.3202, abs=1e-4)
    assert all(r["axial_ratio_ok [text]"] == "yes" for r in tables["columns"])


def test_seismic_combination_uses_gamma_re(cases):
    """Level-1 AB left face: 0.75 x |1.2 G_E + 1.3 E_right| is the design moment."""
    d = c.beam_demands(cases, c.PRIMARY_COMBINATIONS)[("AB", 1, "left end", "top")]
    m = 1.2 * cases["GE"].moments[("AB", 1)][3] + 1.3 * cases["E_right"].moments[("AB", 1)][3]
    assert d.combination == "1.2GE+1.3E_right"
    assert d.m_knm == pytest.approx(0.75 * -m, rel=1e-9)


def test_flags_pinned(tables):
    """Pins today's result (28 Oct 2026): two thesis beam rows short on their bars
    (level 1, AB left and right ends, D10 rows); every column below 0.75 %;
    no row fails the thesis's own numbers (check b)."""
    flagged = [(r["floor_printed [text]"], r["span [text]"], r["location [text]"])
               for r in tables["check"] if r["flag_a [text]"] == "yes"]
    assert flagged == [("1", "AB", "left end"), ("1", "AB", "right end")]
    assert all(r["flag_a_short [text]"] == "bars" for r in tables["check"]
               if r["flag_a [text]"] == "yes")
    assert not any(r["flag_b [text]"] == "yes" for r in tables["check"])
    assert all(r["flag [text]"].startswith("yes: total steel") for r in tables["columns"])
    assert len(tables["columns"]) == 16
    assert len(tables["beams"]) == 60


def test_combinations_sets():
    """Primary set is the thesis set; the sensitivity set swaps in GB 55002 factors."""
    assert c.PRIMARY_COMBINATIONS == cb.THESIS_COMBINATIONS
    assert sum(c.is_seismic(x) for x in c.CODE_SEISMIC_SET) == 2
    assert all(x.status == "code" for x in c.CODE_SEISMIC_SET if c.is_seismic(x))


def test_main_writes_tables(tmp_path):
    """main() writes the four design tables."""
    for sub in ("validation/thesis_values",):
        (tmp_path / sub).mkdir(parents=True)
    for name in ("beam_steel_areas.csv", "wind_drift.csv"):
        src = ROOT / "validation" / "thesis_values" / name
        (tmp_path / "validation" / "thesis_values" / name).write_bytes(src.read_bytes())
    t = c.main(tmp_path)
    for name in ("anchor_design_beams.csv", "anchor_design_check.csv",
                 "anchor_design_columns.csv", "anchor_design_column_bars.csv"):
        with (tmp_path / "results" / name).open(newline="", encoding="utf-8") as f:
            assert len(list(csv.DictReader(f))) > 0
    assert len(t["column_bars"]) == 3
