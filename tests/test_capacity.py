"""Tests for R14 capacity design and the doubly reinforced beam end (Day 20).

File: tests/test_capacity.py

Hand values use the constants in ``shellbench.checks``: a_s = 50 mm,
f_c = 19.1 N/mm^2, f_y = 360 N/mm^2, alpha1 = 1.0 (GB 50010 cl. 4.1.4,
4.2.3, 6.2.6, as in checks.py).
"""

import math

import pytest

from shellbench import capacity as cap
from shellbench import checks as c
from shellbench import generator as g

D = g.BAR_DIAMETERS_MM


def test_column_bars_minimum_count_anchor():
    """h = 500: 3 bars a face (400/200 + 1), 8 bars; total >= (0.7 + 0.05) % of 500^2 = 1875 mm^2.

    8C16 = 1608 mm^2 is short, 8C18 = 2036 mm^2 passes (Table 11.4.12-1, grade 3).
    """
    bars = cap.column_bars(500, 0.0, 3, D)
    assert (bars.per_side, bars.label) == (3, "8C18")
    assert bars.total_min_mm2 == pytest.approx(1875.0)
    assert bars.area_mm2 == pytest.approx(8 * math.pi * 18 ** 2 / 4)


def test_column_bars_adds_bars_when_32_mm_is_not_enough():
    """h = 1600, 12 187 mm^2 a face: 9C32 = 7238 mm^2 is short; 16C32 = 12 868 mm^2 passes.

    15C32 = 12 064 mm^2 is short. Clear spacing at 16 a face: 1500/15 - 32 = 68 mm >= 50 mm
    (cl. 9.3.1 item 2). Total 4 x 15 = 60 bars, rho = 48 255 / 1600^2 = 1.88 %.
    """
    bars = cap.column_bars(1600, 12187.0, 1, D)
    assert (bars.per_side, bars.diameter_mm, bars.label) == (16, 32, "60C32")
    assert bars.rho == pytest.approx(60 * math.pi * 32 ** 2 / 4 / 1600 ** 2)
    clear = (1600 - 2 * c.A_S_MM) / (bars.per_side - 1) - bars.diameter_mm
    assert clear >= cap.COLUMN_MIN_CLEAR_MM


def test_column_bars_none_when_no_layout_fits():
    """h = 500, 5000 mm^2 a face: at 50 mm clear spacing C32 allows 5 a face (4021 mm^2)."""
    assert cap.column_bars(500, 5000.0, 3, D) is None


def test_comp_ratio_zero_is_singly_reinforced():
    """comp_ratio = 0 gives the R13 singly reinforced result unchanged."""
    a = c.design_section(300.0, 300, 600, "support", True, grade=1)
    b = c.design_section(300.0, 300, 600, "support", True, grade=1, comp_ratio=0.0)
    assert a == b


def test_doubly_reinforced_meets_cl_6_2_10():
    """b 300, h 600, M 600 kN m, A_s' = 0.5 A_s: both equations of cl. 6.2.10 hold.

    Singly reinforced, alpha_s = 600e6 / (19.1 x 300 x 550^2) = 0.346, xi = 0.446 > 0.25;
    with A_s' counted xi drops below 0.25 (grade I, cl. 11.3.1). At 800 kN m it is above.
    """
    r, b, h0 = 0.5, 300.0, 600.0 - c.A_S_MM
    d = c.design_section(600.0, b, 600, "support", True, grade=1, comp_ratio=r)
    x = d.xi * h0
    assert x >= 2 * c.A_S_MM
    assert c.ALPHA1 * c.FC_N_MM2 * b * x == pytest.approx(c.FY_N_MM2 * (1 - r) * d.as_calc_mm2)
    m = c.ALPHA1 * c.FC_N_MM2 * b * x * (h0 - x / 2) + c.FY_N_MM2 * r * d.as_calc_mm2 * (h0 - c.A_S_MM)
    assert m == pytest.approx(600.0e6)
    single = c.design_section(600.0, b, 600, "support", True, grade=1)
    assert single.status != "ok" and d.status == "ok"
    assert single.xi == pytest.approx(1 - math.sqrt(1 - 2 * 600.0e6 / (19.1 * 300 * 550 ** 2)))
    assert c.design_section(800.0, b, 600, "support", True, grade=1, comp_ratio=r).status != "ok"


def test_doubly_reinforced_small_x_uses_cl_6_2_14():
    """M 100 kN m: x < 2 a_s', so A_s = 100e6 / (360 x (550 - 50)) = 555.6 mm^2."""
    d = c.design_section(100.0, 300, 600, "support", True, grade=1, comp_ratio=0.5)
    assert d.as_calc_mm2 == pytest.approx(100.0e6 / (360.0 * 500.0))
    assert d.status == "ok"


def test_beam_end_comp_ratio_values():
    """cl. 11.3.6 item 2: 0.5 grade I, 0.3 grade II; grades III-IV not counted [J]."""
    assert c.BEAM_END_COMP_RATIO == {1: 0.5, 2: 0.3, 3: 0.0, 4: 0.0}
