"""Tests for force density form-finding (Playbook Day 23).

File: tests/test_formfind.py

The 1 % tolerances are the playbook's (Day 23). The bay values are test
inputs: the 6.6 m span is the layout-A vault span (docs/floor_concept.md),
f = L/12 sits inside the author's 1/8 to 1/20 range, and w = 5 kN/m^2 is
a round load, not a design value.
"""

from __future__ import annotations

import numpy as np
import pytest

from shellbench import formfind as ff

L, F, W = 6.6, 6.6 / 12, 5.0e3


@pytest.fixture(scope="module")
def strip():
    """A long strip: Ly = 10 Lx, so mid-bay the y-direction carries almost nothing."""
    return ff.form_find(L, 10 * L, F, W, nx=40, ny=60, qy_ratio=1.0)


def test_long_strip_section_is_parabola(strip):
    """Mid-length section within 1 % of z = 4 f x (L - x) / L^2 (playbook Day 23)."""
    j = strip.z.shape[0] // 2
    x, z = strip.x[j], strip.z[j]
    target = ff.parabola(x, L, F)
    inner = slice(1, -1)  # the support nodes are 0 on both
    assert np.max(np.abs(z[inner] / target[inner] - 1)) < 0.01


def test_long_strip_thrust(strip):
    """Horizontal force per unit width within 1 % of H = w L^2 / (8 f)."""
    assert strip.thrust_per_width() == pytest.approx(ff.parabolic_thrust(W, L, F), rel=0.01)


def test_independent_arches_are_exact():
    """With no y-branches every x-line is the discrete parabola, exactly."""
    v = ff.form_find(L, 3.0, F, W, nx=20, ny=4, qy_ratio=0.0)
    assert np.allclose(v.z[2], ff.parabola(v.x[2], L, F), rtol=1e-10, atol=1e-12)
    assert v.thrust_per_width() == pytest.approx(ff.parabolic_thrust(W, L, F), rel=1e-10)


def test_rise_and_equilibrium():
    """A square bay reaches the target rise, and the reactions carry the load."""
    v = ff.form_find(6.0, 6.0, 0.5, W, nx=24, ny=24)
    assert v.z.max() == pytest.approx(0.5)
    free_area = (6.0 - v.dx) * (6.0 - v.dy)  # tributary area of the free nodes
    assert v.vertical_reactions() == pytest.approx(W * free_area, rel=1e-9)
    assert np.allclose(v.z, v.z[::-1, ::-1])  # symmetric


def test_msh_file(tmp_path):
    """The mesh file has (nx+1)(ny+1) nodes and nx*ny quadrilaterals."""
    v = ff.form_find(6.6, 7.2, 0.55, W, nx=6, ny=8)
    text = ff.write_msh(v, tmp_path / "vault.msh").read_text().splitlines()
    assert text[text.index("$Nodes") + 1] == str(7 * 9)
    assert text[text.index("$Elements") + 1] == str(6 * 8)


def test_bad_input():
    """Non-positive geometry is refused."""
    with pytest.raises(ValueError):
        ff.form_find(6.6, 7.2, 0.0, W)
