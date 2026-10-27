"""Tests for the GB 50011 base-shear method on the anchor frame (Day 9).

File: tests/test_seismic.py

Closed-form checks of the code functions (spectrum, delta_n, force
distribution), consistency checks against the gravity model, a Rayleigh check
of the eigenvalue, and a pin of today's primary result so that any later
change to it has to be read again (docs/anchor_notes.md, seismic section).
"""

from __future__ import annotations

import math

import pytest

from shellbench import anchor_frame as af
from shellbench import seismic as s

A_MAX = 0.08
TG = 0.35


def test_spectrum_branch_end_points():
    """Fig. 5.1.5: 0.45 a_max at T = 0, a_max on the plateau, continuity at 5 Tg."""
    assert s.alpha_spectrum(0.0, A_MAX, TG) == pytest.approx(0.45 * A_MAX)
    assert s.alpha_spectrum(0.1, A_MAX, TG) == pytest.approx(A_MAX)
    assert s.alpha_spectrum(TG, A_MAX, TG) == pytest.approx(A_MAX)
    curved = (TG / (5 * TG)) ** 0.9 * A_MAX
    assert s.alpha_spectrum(5 * TG, A_MAX, TG) == pytest.approx(curved)
    assert s.alpha_spectrum(5 * TG + 1e-9, A_MAX, TG) == pytest.approx(curved, rel=1e-6)
    straight_end = (0.2 ** 0.9 - 0.02 * (6.0 - 5 * TG)) * A_MAX
    assert s.alpha_spectrum(6.0, A_MAX, TG) == pytest.approx(straight_end)


def test_spectrum_refuses_unconfirmed_inputs():
    """Only 5 % damping, 0-6 s and the confirmed alpha_max entry are allowed."""
    with pytest.raises(ValueError):
        s.alpha_spectrum(0.5, A_MAX, TG, damping_ratio=0.02)
    with pytest.raises(ValueError):
        s.alpha_spectrum(6.5, A_MAX, TG)
    with pytest.raises(KeyError):
        s.alpha_max_frequent(8, 0.20)
    assert s.alpha_max_frequent(7, 0.10) == 0.08


def test_period_for_alpha_inverts_the_spectrum():
    """The implied-period diagnostic returns the period that gives the alpha."""
    for t in (0.5, 1.0, 2.0, 4.0):
        a = s.alpha_spectrum(t, A_MAX, TG)
        assert s.period_for_alpha(a, A_MAX, TG) == pytest.approx(t, abs=1e-6)
    assert s.period_for_alpha(0.09, A_MAX, TG) is None


def test_top_additional_factor_table_5_2_1():
    """Table 5.2.1: zero up to 1.4 Tg, then the three Tg branches."""
    assert s.top_additional_factor(0.49, 0.35) == 0.0
    assert s.top_additional_factor(0.70, 0.35) == pytest.approx(0.08 * 0.70 + 0.07)
    assert s.top_additional_factor(0.80, 0.45) == pytest.approx(0.08 * 0.80 + 0.01)
    assert s.top_additional_factor(1.00, 0.65) == pytest.approx(0.08 * 1.00 - 0.02)


def test_storey_forces_sum_and_shape():
    """Forces sum to F_Ek; with equal weights and no delta_n they follow H_i."""
    f = s.storey_forces([1.0, 1.0, 1.0], [3.0, 6.0, 9.0], 60.0, 0.0)
    assert f == pytest.approx([10.0, 20.0, 30.0])
    f = s.storey_forces([2.0, 1.0, 1.5], [4.0, 7.0, 10.0], 100.0, 0.12)
    assert sum(f) == pytest.approx(100.0)
    rest = [x for x in f[:-1]]
    gh = [8.0, 7.0, 15.0]
    assert rest == pytest.approx([88.0 * x / 30.0 for x in gh[:-1]])
    assert f[-1] == pytest.approx(88.0 * 15.0 / 30.0 + 12.0)


def test_minimum_shear_coefficient():
    """Table 5.2.5, 7 degrees 0.10 g: 0.016 below 3.5 s; longer periods refused."""
    assert s.minimum_shear_coefficient(0.7) == 0.016
    with pytest.raises(ValueError):
        s.minimum_shear_coefficient(4.0)


def test_dead_weights_match_the_gravity_model():
    """Sum of dead G_i equals the load the frame carries, less the lower half
    of the ground-storey columns, which goes to the foundation."""
    fm = af.build_frame()
    applied = af.apply_dead_load(fm, af.LOAD_MODELS["actual_shape"])
    af.ops.wipe()
    dead = sum(w.dead_kn for w in s.storey_weights())
    to_foundation = af.COLUMN_SELF_WEIGHT_KN_M * len(af.AXES) * af.STOREY_HEIGHTS_M[0] / 2.0
    assert dead == pytest.approx(applied - to_foundation)


def test_live_combination_coefficients():
    """Table 5.1.3: half the floor live load, none of the roof live load."""
    w = s.storey_weights()
    for floor in w[:-1]:
        assert floor.g_kn == pytest.approx(floor.dead_kn + 0.5 * floor.live_kn)
    assert w[-1].g_kn == pytest.approx(w[-1].dead_kn)


def test_eigen_period_matches_rayleigh():
    """The Rayleigh estimate from the static deflection under G_i agrees with
    the first eigenvalue within 2 % (it is an upper bound on frequency, so it
    can only be slightly shorter in period here)."""
    g = [w.g_kn for w in s.storey_weights()]
    t_eig = s.modal_periods(g, 1)[0]
    t_ray = s.rayleigh_period(g)
    assert t_ray == pytest.approx(t_eig, rel=0.02)


def test_single_storey_period_closed_form():
    """A rigid-beam frame of one storey has T = 2 pi sqrt(m / k) with
    k = sum 12 E I / h^3 over the four columns."""
    h = 4.0
    fm = af.build_frame(storey_heights_m=(h,), beam_inertia_factor=1.0e6)
    weight = 1000.0
    for ax in af.AXES:
        af.ops.mass(fm.node[(ax, 1)], weight / s.G_ACCEL_M_S2 / 4.0, 0.0, 0.0)
    lam = af.ops.eigen(1)[0]
    af.ops.wipe()
    b, d = af.COLUMN_BH_M
    k = 4 * 12.0 * af.E_KN_M2 * (b * d**3 / 12.0) / h**3
    t_exact = 2.0 * math.pi * math.sqrt(weight / s.G_ACCEL_M_S2 / k)
    assert 2.0 * math.pi / math.sqrt(lam) == pytest.approx(t_exact, rel=0.01)


def test_primary_run_equilibrium_and_checks():
    """Base reaction equals F_Ek, column shears equal the storey shears, and
    the drift limit and minimum shear are met."""
    r = s.run_base_shear()
    assert -r.lateral.base_shear_kn == pytest.approx(r.f_ek_kn, rel=1e-6)
    assert r.lateral.column_shear_kn == pytest.approx(r.shears_kn, rel=1e-6)
    assert max(r.lateral.theta) <= s.DRIFT_LIMIT
    sum_g = [sum(w.g_kn for w in r.weights[i:]) for i in range(len(r.weights))]
    assert all(v >= r.lam * g for v, g in zip(r.shears_kn, sum_g))


def test_primary_result_pinned():
    """Pins today's primary result (27 Oct 2026, results/anchor_seismic_runs.csv).
    A change here means the seismic verdict in docs/anchor_notes.md must be
    read again; it is not a tolerance on the thesis."""
    r = s.run_base_shear()
    assert r.t1_s == pytest.approx(0.6981, abs=5e-4)
    assert r.alpha1 == pytest.approx(0.04298, abs=5e-5)
    assert r.f_ek_kn == pytest.approx(214.75, abs=0.05)
    assert r.delta_n == pytest.approx(0.1258, abs=5e-4)


def test_thesis_storey_forces_levels_1_to_4():
    """Decision 2: F_i = V_i - V_(i+1) for levels 1-4 of Table 8-12."""
    root = af.Path(__file__).resolve().parents[1]
    f = s.thesis_storey_forces(s.read_thesis_seismic(root))
    assert f == pytest.approx([31.03, 54.56, 77.62, 101.56], abs=1e-9)
