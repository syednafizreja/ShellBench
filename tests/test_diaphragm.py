"""Rigid-diaphragm test (Day 27, H3): method check, hand calculation, topping rule."""

import math

import pandas as pd
import pytest

from shellbench import diaphragm as dp
from shellbench import panel
from shellbench import shellfloor as sf
from shellbench.shellfe import find_ccx

needs_ccx = pytest.mark.skipif(find_ccx() is None, reason="CalculiX not installed")


@needs_ccx
def test_flat_plate_shear_factor_is_one():
    """Method check: a flat plate in this model has K = G t exactly (deep beam, shear only)."""
    assert dp.shear_factor(6.6, 0.0, 0.06) == pytest.approx(1.0, abs=1e-3)


@needs_ccx
def test_vault_is_softer_than_a_flat_plate():
    """A vault of rise 1/15 has k below 1 (its shear path is longer than the plan) but above 0.7."""
    k = dp.shear_factor(6.6, 1.0 / 15.0, 0.06)
    assert 0.7 < k < 1.0


def test_library_factors_cover_all_cases():
    """results/diaphragm_library.csv has one factor per floor-library case, all between 0.7 and 1."""
    k = dp.library_factors()
    assert len(k) == 72
    assert all(0.7 < x < 1.0 for x in k.values())


def test_shear_modulus_by_hand():
    """G = 3.25e10 / (2 x 1.2) = 1.354e10 Pa."""
    assert dp.shear_modulus_pa() == pytest.approx(3.25e10 / 2.4)


def test_check_storey_by_hand():
    """F = 200 kN on 151.2 m^2, L = 6.6 m, t = 0.06 m, k = 0.84, no topping, drift 5 mm.

    p = 1.3228 kN/m^2; K = 1.3542e7 kPa x 0.84 x 0.06 = 6.825e5 kN/m;
    delta = p L^2 / (8 K) = 1.3228 x 43.56 / (8 x 6.825e5) = 1.0553e-5 m.
    """
    k = dp.bay_stiffness_kn_m(0.84, 0.06, 0)
    assert k == pytest.approx(1.3542e7 * 0.84 * 0.06, rel=1e-3)
    c = dp.check_storey(200.0, 151.2, 0.005, 6.6, k, 0.06, 0)
    p = 200.0 / 151.2
    assert c["delta_m"] == pytest.approx(p * 6.6**2 / (8 * k))
    assert c["delta_m"] == pytest.approx(1.055e-5, rel=2e-2)
    assert c["ratio"] == pytest.approx(c["delta_m"] / 0.010)
    assert c["stiffness_ratio"] == pytest.approx(0.005 / c["delta_m"])


def test_topping_adds_stiffness():
    """A 50 mm topping on a 60 mm shell raises K by G x 0.05 m, and lowers the ratio."""
    k0 = dp.bay_stiffness_kn_m(0.84, 0.06, 0)
    k50 = dp.bay_stiffness_kn_m(0.84, 0.06, 50)
    assert k50 - k0 == pytest.approx(dp.shear_modulus_pa() / 1e3 * 0.05)


def test_flexible_when_stiffness_is_tiny():
    """The criterion bites: with K cut by a factor 3000 the same floor is flexible."""
    k = dp.bay_stiffness_kn_m(0.84, 0.06, 0)
    c = dp.check_storey(200.0, 151.2, 0.005, 6.6, k / 3000.0, 0.06, 0)
    assert c["ratio"] > 1.0


def test_topping_rule_picks_smallest_rigid_topping():
    """Rigid from 40 mm up gives 40; never rigid gives NaN; rigid at 0 gives 0."""
    rows = []
    for vid, rigid in (("a", [False, True, True, True]), ("b", [False] * 4), ("c", [True] * 4)):
        for t, r in zip((0, 40, 50, 60), rigid):
            rows.append({"building_id": "s04", "floor_variant_id": vid, "topping_mm": t, "rigid": r})
    out = sf.topping_rule(pd.DataFrame(rows)).set_index("floor_variant_id")["min_topping_mm"]
    assert out["a"] == 40 and out["c"] == 0 and math.isnan(out["b"])


def test_ft_is_the_spec_value():
    """tau / f_t uses f_t = 1.71 MPa (spec X3, GB 50010 Table 4.1.4-1 [?])."""
    assert panel.FT_PA == pytest.approx(1.71e6)
