"""Tests for the response-spectrum check and the 3D periods (Day 10).

File: tests/test_rsa.py

Closed-form checks (SRSS, participation, torsion constant, a one-storey 3D
period), consistency with the Day 9 base-shear run, and a pin of today's
results so a later change has to be read again (docs/anchor_notes.md,
response-spectrum section).
"""

from __future__ import annotations

import math

import pytest

from shellbench import anchor_3d as a3
from shellbench import anchor_frame as af
from shellbench import rsa
from shellbench import seismic as s


def weights() -> list[float]:
    """Return the primary G_i of Day 9 [kN]."""
    return [w.g_kn for w in s.storey_weights()]


def test_srss_closed_form():
    """sqrt(3^2 + 4^2) = 5, level by level."""
    assert rsa.srss([[3.0, 0.0], [4.0, 2.0]]) == pytest.approx([5.0, 2.0])


def test_mass_ratios_sum_to_one_over_all_modes():
    """Effective mass ratios over all four modes add to 1 (four lumped masses).

    Not exactly 1: the level shape is the mean of four nodes, which differ
    very slightly because the beams shorten axially (about 2e-6 here)."""
    ms = rsa.modes(weights(), 4)
    assert sum(m.mass_ratio for m in ms) == pytest.approx(1.0, abs=1e-4)
    assert [m.period_s for m in ms] == sorted((m.period_s for m in ms), reverse=True)


def test_first_period_matches_day_9():
    """Same masses and frame as the base-shear run, so the same T1."""
    assert rsa.modes(weights(), 1)[0].period_s == pytest.approx(s.run_base_shear().t1_bare_s, rel=1e-6)


def test_modal_base_shear_closed_form():
    """Mode base shear = alpha gamma sum(X G) = alpha x effective weight."""
    g = weights()
    a_max = s.alpha_max_frequent(7, 0.10)
    for m in rsa.modes(g, 3):
        f = rsa.modal_forces(m, g, a_max, s.TG_ANCHOR_S)
        alpha = s.alpha_spectrum(m.period_s, a_max, s.TG_ANCHOR_S)
        assert abs(sum(f)) == pytest.approx(alpha * m.mass_ratio * sum(g), rel=1e-9)


def test_rsa_shears_equal_column_shears_and_drift_limit():
    """Each mode's column shears add to its applied forces; SRSS drifts meet 1/550."""
    r = rsa.run_rsa()
    for f, v in zip(r.forces_kn, r.shears_kn):
        assert v == pytest.approx([sum(f[i:]) for i in range(len(f))], rel=1e-6, abs=1e-6)
    assert max(r.theta_srss) <= s.DRIFT_LIMIT


def test_rsa_result_pinned():
    """Pins today's results (27 Oct 2026, results/anchor_rsa*.csv)."""
    r = rsa.run_rsa()
    assert r.shear_srss_kn[0] == pytest.approx(228.47, abs=0.05)
    assert r.shear_srss_kn[3] == pytest.approx(70.06, abs=0.05)
    assert r.du_srss_mm[1] == pytest.approx(2.058, abs=0.002)
    assert sum(m.mass_ratio for m in r.modes) == pytest.approx(0.9962, abs=5e-4)


def test_torsion_constant_square():
    """A square of side a has J = 0.1406 a^4 (standard result); the series
    approximation gives 0.1408 a^4."""
    assert a3.torsion_constant(0.6, 0.6) == pytest.approx(0.1406 * 0.6**4, rel=0.005)


def test_plan_matches_the_drawing_grid():
    """Spec G4 and G3: 38.4 m along axes 1-7, 21.0 m along A-D."""
    xs, ys = a3.plan_coordinates()
    assert xs[-1] == pytest.approx(38.4)
    assert ys[-1] == pytest.approx(21.0)


def test_3d_masses_scaled_by_plan_length():
    """Level mass = 2D G_i x 38.4 / 7.2 / g."""
    g = weights()
    m = a3.level_masses_t(g)
    assert m[0] == pytest.approx(g[0] * 38.4 / 7.2 / s.G_ACCEL_M_S2)


def test_3d_periods_pinned_and_directions():
    """Pins today's 3D result: transverse, longitudinal, torsion; the plan is
    symmetric, so the translational modes carry no rotation."""
    p = a3.periods_3d(weights(), 3)
    assert [m["direction"] for m in p] == ["Y (transverse)", "X (longitudinal)", "torsion"]
    assert p[0]["T"] == pytest.approx(0.6222, abs=5e-4)
    assert p[1]["T"] == pytest.approx(0.5713, abs=5e-4)
    assert p[2]["T"] == pytest.approx(0.5175, abs=5e-4)
    assert abs(p[0]["torsion"]) < 1e-6 and abs(p[1]["torsion"]) < 1e-6


def test_3d_transverse_period_shorter_than_2d():
    """Each 3D transverse frame carries 38.4 / 7 = 5.49 m of mass against the
    2D frame's 7.2 m, so the 3D period is shorter (docs/anchor_notes.md)."""
    g = weights()
    assert a3.periods_3d(g, 1)[0]["T"] < rsa.modes(g, 1)[0].period_s


def test_main_writes_tables_and_figure(tmp_path):
    """main() writes the comparison, the modes, the 3D periods and the figure."""
    root = af.Path(__file__).resolve().parents[1]
    (tmp_path / "validation" / "thesis_values").mkdir(parents=True)
    src = root / "validation" / "thesis_values" / "seismic_storey_shear_drift.csv"
    (tmp_path / "validation" / "thesis_values" / src.name).write_bytes(src.read_bytes())
    tables = rsa.main(tmp_path)
    assert len(tables["rsa"]) == 4
    assert len(tables["modes"]) == 3
    assert len(tables["periods_3d"]) == 3
    assert (tmp_path / "figures" / "anchor_seismic_compare.png").stat().st_size > 0
    assert (tmp_path / "results" / "anchor_3d_periods.csv").exists()
    assert math.isfinite(tables["rsa"][0]["V_rsa [kN]"])
