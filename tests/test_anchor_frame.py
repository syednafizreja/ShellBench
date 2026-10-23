"""Tests for src/shellbench/anchor_frame.py (anchor frame, dead load).

Validation against closed-form results:
1. A fixed-fixed beam under uniform load gives end moments qL^2/12 in the
   thesis sign convention (-M left, +M right).
2. A fixed-fixed beam under a symmetric trapezoidal or triangular load gives the
   fixed-end moments of the equivalent uniform load used in the thesis
   (Th s5.1): (1 - 2a^2 + a^3) p L^2 / 12 and (5/8) p L^2 / 12. This checks both
   the piecewise load application and the thesis conversion formula.

Checks of the frame model:
3. Vertical base reactions equal the applied load for every load model.
4. The frame and its load are symmetric, so results mirror about the centre.
5. Column axial force grows down each storey by the column self-weight.
6. The comparison table has one row per dead-load thesis target.
"""

import csv
import shutil
from pathlib import Path

import openseespy.opensees as ops
import pytest

from shellbench import anchor_frame as af

REPO = Path(__file__).resolve().parents[1]

#: Closed-form tolerance: piecewise-constant loading on 0.1 m sub-elements
#: approximates the ramps; 0.5 % is ample for that error [J].
REL_TOL = 5e-3


def fixed_beam_end_moments(span_m: float, load: af.BeamLoad) -> tuple[float, float]:
    """Solve one fixed-fixed beam with the module's loading and extraction.

    Args:
        span_m: Beam length [m].
        load: The BeamLoad to apply.

    Returns:
        (left, right) end moments in the thesis sign convention [kN*m].
    """
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    ops.geomTransf("Linear", 1)
    n_sub = round(span_m * af.BEAM_SUBELEMENTS_PER_M)
    for k in range(n_sub + 1):
        ops.node(k + 1, span_m * k / n_sub, 0.0)
    ops.fix(1, 1, 1, 1)
    ops.fix(n_sub + 1, 1, 1, 1)
    fm = af.FrameModel()
    fm.beam[("AB", 1)] = []
    for k in range(n_sub):
        ops.element("elasticBeamColumn", k + 1, k + 1, k + 2, 0.18, af.E_KN_M2, 0.0108, 1)
        fm.beam[("AB", 1)].append(k + 1)
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)
    seg = span_m / n_sub
    for k, ele in enumerate(fm.beam[("AB", 1)]):
        ops.eleLoad("-ele", ele, "-type", "-beamUniform", -load.intensity((k + 0.5) * seg, span_m), 0.0)
    af.solve_static()
    m = af.beam_end_moments(fm)
    ops.wipe()
    return m[("1", "AB", "left")], m[("1", "AB", "right")]


def test_fixed_beam_uniform_load_matches_ql2_over_12():
    """Uniform load: end moments are -qL^2/12 (left) and +qL^2/12 (right)."""
    q, span = 23.43, 7.2
    left, right = fixed_beam_end_moments(span, af.BeamLoad(q))
    expected = q * span**2 / 12.0
    assert left == pytest.approx(-expected, rel=1e-9)
    assert right == pytest.approx(expected, rel=1e-9)


def test_fixed_beam_trapezoid_matches_thesis_equivalent_load():
    """Trapezoid (ramp 1.8 m on 7.2 m, alpha = 0.25): FEM of (1-2a^2+a^3) p."""
    p, span, ramp = 14.58, 7.2, 1.8
    alpha = ramp / span
    left, right = fixed_beam_end_moments(span, af.BeamLoad(0.0, "trapezoid", p, ramp))
    expected = (1 - 2 * alpha**2 + alpha**3) * p * span**2 / 12.0
    assert -left == pytest.approx(expected, rel=REL_TOL)
    assert right == pytest.approx(expected, rel=REL_TOL)


def test_fixed_beam_triangle_matches_five_eighths_rule():
    """Symmetric triangle: FEM of (5/8) p uniform, i.e. 5 p L^2 / 96."""
    p, span = 13.36, 6.6
    left, right = fixed_beam_end_moments(span, af.BeamLoad(0.0, "triangle", p))
    expected = 5.0 / 8.0 * p * span**2 / 12.0
    assert -left == pytest.approx(expected, rel=REL_TOL)
    assert right == pytest.approx(expected, rel=REL_TOL)


def test_beam_load_totals():
    """Trapezoid total p(L - a) and triangle total pL/2 by midpoint integration."""
    span, n = 7.2, 72
    seg = span / n
    trap = af.BeamLoad(0.0, "trapezoid", 10.0, 1.8)
    assert sum(trap.intensity((k + 0.5) * seg, span) * seg for k in range(n)) == pytest.approx(10.0 * (7.2 - 1.8))
    span, n = 6.6, 66
    seg = span / n
    tri = af.BeamLoad(0.0, "triangle", 10.0)
    assert sum(tri.intensity((k + 0.5) * seg, span) * seg for k in range(n)) == pytest.approx(10.0 * 6.6 / 2)


@pytest.mark.parametrize("load_model", sorted(af.LOAD_MODELS))
def test_vertical_equilibrium(load_model):
    """Sum of vertical base reactions equals the total applied load."""
    res = af.run_dead_load(load_model)
    assert res.reaction_kn == pytest.approx(res.applied_kn, rel=1e-9)


@pytest.mark.parametrize("variant", sorted(af.VARIANTS))
def test_symmetry(variant):
    """Symmetric frame and load: AB mirrors CD, BC is antisymmetric, A = D, B = C."""
    res = af.run_dead_load(variant=variant, **af.VARIANTS[variant])
    for floor in ("1", "2", "3", "4"):
        m = res.moments
        assert m[(floor, "AB", "left")] == pytest.approx(-m[(floor, "CD", "right")], abs=1e-6)
        assert m[(floor, "AB", "right")] == pytest.approx(-m[(floor, "CD", "left")], abs=1e-6)
        assert m[(floor, "BC", "left")] == pytest.approx(-m[(floor, "BC", "right")], abs=1e-6)
        for end in ("top", "bottom"):
            assert res.axial[("A", floor, end)] == pytest.approx(res.axial[("D", floor, end)], abs=1e-6)
            assert res.axial[("B", floor, end)] == pytest.approx(res.axial[("C", floor, end)], abs=1e-6)


def test_column_self_weight_increment():
    """N_bottom - N_top in each storey equals 9.96 kN/m times the storey height."""
    res = af.run_dead_load("thesis_fem")
    for storey, h in enumerate(af.STOREY_HEIGHTS_M, start=1):
        for ax in af.AXES:
            diff = res.axial[(ax, str(storey), "bottom")] - res.axial[(ax, str(storey), "top")]
            assert diff == pytest.approx(af.COLUMN_SELF_WEIGHT_KN_M * h, rel=1e-9)


def test_hogging_moments_have_thesis_signs():
    """Under gravity every beam end hogs: negative at left ends, positive at right."""
    res = af.run_dead_load("thesis_fem")
    for (floor, span, end), m in res.moments.items():
        assert (m < 0) if end == "left" else (m > 0)


def test_comparison_table_written(tmp_path):
    """main() writes one comparison row per dead-load target (24 moments + 16 axial)."""
    shutil.copytree(REPO / "validation", tmp_path / "validation")
    rows = af.main(tmp_path)
    assert len(rows) == 40
    out = tmp_path / "results" / "anchor_gravity_dead.csv"
    with open(out, newline="", encoding="utf-8") as fh:
        table = list(csv.DictReader(fh))
    assert len(table) == 40
    assert all(r["difference_pct [%]"] != "" for r in table)
    assert (tmp_path / "results" / "anchor_gravity_dead_runs.csv").exists()
