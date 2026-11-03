"""Tests for one sized shell panel (Playbook Day 25, floor-r3).

File: tests/test_floorpanel.py
"""

from __future__ import annotations

import pytest

from shellbench import floorpanel as fp
from shellbench.calculix import find_ccx

P = fp.DAY25_PANEL


def test_closed_form_statics():
    """H = w L^2 / (8 f) and A_t = H s / f_y, by hand."""
    c = fp.closed_form(P)
    w = P.design_load()
    assert c.thrust_per_m == pytest.approx(w * 6.6 ** 2 / (8 * 0.44))
    assert c.tie_area_mm2 == pytest.approx(c.thrust_per_m * 1.2 / 360e6 * 1e6)


@pytest.mark.skipif(find_ccx() is None, reason="CalculiX not installed")
def test_fe_thrust_within_10_percent(tmp_path):
    """Day 25 Done-when: FE thrust within 10 % of the closed form; panel stable."""
    c = fp.closed_form(P)
    r = fp.fe_panel(P, tmp_path)
    assert r.thrust_per_m == pytest.approx(c.thrust_per_m, rel=fp.TOLERANCE)
    assert r.buckling_factor > 1.0
    assert r.max_abs_stress < 19.1e6  # f_c of C40, GB 50010 Table 4.1.4-1


def test_quantities_positive():
    q = fp.quantities(P, fp.closed_form(P))
    assert q["concrete_m3_per_m2"] == pytest.approx(0.06 * P.arc_factor())
    assert all(v > 0 for v in q.values())
