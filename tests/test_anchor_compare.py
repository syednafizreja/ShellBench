"""Anchor slab against shell (Day 30): the weight hand check and the waterfall sum."""

import pytest

from shellbench import anchor_compare as ac
from shellbench import shellfloor as sf


@pytest.fixture(scope="module")
def variant():
    """The first recycled-fill variant of the library."""
    return next(v for v in sf.variants() if v["levelling"] == "recycled_fill")


def test_weight_change_matches_hand_sum(variant):
    """Playbook Day 30: floor load change x floor area = reported change of seismic weight.

    With the sizes fixed, three storeys change by (q_shell - 4.05) x 7.2 x 21.0 - 2.54 x 21.0 kN
    (secondary beams 2.54 kN/m on 7.2 + 6.6 + 7.2 m); the roof does not change.
    """
    chk = ac.floor_weight_check(variant, 50)
    q = sf.floor_dead_kn_m2(variant, 50)
    expect = 3 * ((q - 4.05) * 7.2 * 21.0 - 2.54 * 21.0)
    assert chk["hand_kn"] == pytest.approx(expect)
    assert chk["code_kn"] == pytest.approx(chk["hand_kn"], rel=1e-9)


def test_waterfall_sums_to_shell_building(variant):
    """The steps add up to the whole-building carbon of the shell row (the function asserts it)."""
    both = ac.run_both(variant, 50)
    steps = ac.waterfall(both, variant, 50)
    deltas = sum(s["kgco2e_per_m2"] for s in steps if s["kind"] == "delta")
    assert steps[0]["kgco2e_per_m2"] + deltas == pytest.approx(steps[-1]["kgco2e_per_m2"], abs=1e-6)
