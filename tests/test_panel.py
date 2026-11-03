"""Tests for the Day 25 panel: statics, section rules and the tie-force Done-when.

File: tests/test_panel.py

The statics tests need no solver. The CalculiX test is skipped when ccx is not
installed and writes only to pytest's temporary folder.
"""

from __future__ import annotations

import numpy as np
import pytest

from shellbench import calculix as cx
from shellbench import panel as pn
from shellbench.formfind import parabolic_thrust

needs_ccx = pytest.mark.skipif(cx.find_ccx() is None, reason="CalculiX not installed")

LOAD_PA = 8.0e3  # any uniform plan load for the statics tests


def test_funicular_load_gives_no_moment():
    """Uniform plan load with H = w L^2 / (8 f): M = 0 and N = H at the crown."""
    p = np.full(pn.STATICS_POINTS, LOAD_PA)
    h = parabolic_thrust(LOAD_PA, pn.SPAN_M, pn.rise_m())
    x, m, n = pn.arch_forces(p, h)
    assert np.max(np.abs(m)) < 1e-6 * LOAD_PA * pn.SPAN_M**2
    assert n[len(x) // 2] == pytest.approx(h, rel=1e-9)


def test_half_span_load_moment():
    """Half-span load q with the two-pinned thrust q L^2 / (16 f): |M| max = q L^2 / 64."""
    x = np.linspace(0.0, pn.SPAN_M, pn.STATICS_POINTS)
    p = LOAD_PA * (x < pn.SPAN_M / 2.0)
    h = LOAD_PA * pn.SPAN_M**2 / (16.0 * pn.rise_m())
    _, m, _ = pn.arch_forces(p, h)
    # 1 %: the load step at L/2 is smeared over one statics interval (0.5 % high)
    assert np.max(np.abs(m)) == pytest.approx(LOAD_PA * pn.SPAN_M**2 / 64.0, rel=1e-2)


def test_minimum_steel_is_the_ft_rule():
    """45 f_t / f_y = 45 x 1.71 / 360 % = 0.214 % governs over 0.15 % (floor_concept 4.2)."""
    assert pn.min_steel_ratio() == pytest.approx(0.0021375)


def test_tie_bar_is_smallest_that_carries_the_force():
    """A 20 mm bar carries 314 mm^2 x 360 MPa = 113 kN; just over that needs 22 mm."""
    f20 = pn.bar_area_m2(20) * pn.FY_PA
    assert pn.tie_bar(f20) == 20
    assert pn.tie_bar(f20 * 1.01) == 22
    assert pn.tie_bar(1.0e9) is None


@needs_ccx
def test_tie_force_within_ten_percent_of_closed_form(tmp_path):
    """Playbook Day 25 Done-when, at the sized panel (60 mm, recycled fill)."""
    rows = pn.size_panel(tmp_path, thicknesses=(0.060,), levellings=("recycled_fill",))
    for r in rows:
        assert abs(r.h_ratio - 1.0) <= pn.DONE_WHEN_TOLERANCE
        assert r.buckling_factor > 1.0
    assert [r.passes for r in rows if r.prestressed] == [True]
