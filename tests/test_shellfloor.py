"""Shell floor in the generator (Day 29): variants, dead load and one row by hand."""

import pytest

from shellbench import batch as bt
from shellbench import shellfloor as sf


@pytest.fixture(scope="module")
def vs():
    """Floor variants from the committed floor library."""
    return sf.variants()


def test_variants_pair_both_spans(vs):
    """6 rises x 3 levellings x 2 meshes, each pairing a 6.0 and a 6.6 m case."""
    assert len(vs) == 36
    assert all(v["vault_span_m"] == "6/6.6" for v in vs)


def test_fill_mass_by_hand():
    """Foamed fill, 6.6 m, f/L = 1/15: 800 kg/m^3 x (6.6/15)/3 = 117.3 kg/m^2."""
    assert sf.fill_kg_m2("foamed_fill", 6.6, 1 / 15) == pytest.approx(800 * 6.6 / 15 / 3)
    assert sf.fill_kg_m2("raised_floor", 6.6, 1 / 15) == 29.0


def test_dead_load_by_hand(vs):
    """25 (t_eq + topping) + 1.05 + fill x g / 1000 [kN/m^2]."""
    v = vs[0]
    expect = 25 * (v["concrete_m3_m2"] + 0.05) + 1.05 + v["fill_kg_m2"] * 9.81 / 1000
    assert sf.floor_dead_kn_m2(v, 50) == pytest.approx(expect, rel=1e-3)


def test_anchor_row_floor_carbon_by_hand(vs):
    """The anchor building with one variant: floor carbon is the sum of its parts."""
    fac = sf.factors()
    spec = next(sp for sp in bt.family() if sp["building_id"] == "s04-p010-tg35-C40")
    v = next(x for x in vs if x["levelling"] == "recycled_fill")
    row = sf.run_shell(spec, v, 50, fac)
    assert row["status"] == "ok" and row["floor_system"] == "shell_vault" and row["slab_mm"] == 0
    expect = ((v["concrete_m3_m2"] + 0.05) * fac["concrete"] + v["mesh_kg_m2"] * fac["bar"]
              + v["tie_kg_m2"] * fac["tie"] + v["fill_kg_m2"] * fac["recycled_fill"])
    assert row["carbon_floor_kgco2e_per_m2"] == pytest.approx(expect)
    assert list(row) == list(sf.COLUMNS)
