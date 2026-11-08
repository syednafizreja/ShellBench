"""Day 31 checks on the committed family files."""

import pytest

from shellbench import family_checks as fc


def test_all_checks_pass():
    """No check line fails: same IDs, 144 shell rows per building, sums, three hand-checked pairs."""
    rows = fc.run_checks()
    assert not [r for r in rows if r["result"] == "FAIL"]
    assert sum(r["check"].startswith("pair ") for r in rows) == fc.N_PAIRS


def test_factor_reads_the_file():
    """C40 340 kgCO2e/m3 and HRB400 2340 kgCO2e/t, which is 2.34 per kg (data/carbon_factors.csv)."""
    assert fc.factor("GBT51366", "C40") == pytest.approx(340.0)
    assert fc.factor("GBT51366", "HRB400") == pytest.approx(2.34)


def test_shell_floor_by_hand_one_row():
    """0.0975 m3 x 340 + (8.533 - 5.261) x 2.34 + 5.261 x 2.34 + 85.5 x 0.4727 / 1 = 93.5 for foamed fill, 0 topping."""
    import pandas as pd
    s = pd.Series({"floor_concrete_m3_per_m2": 0.09754, "floor_steel_kg_per_m2": 8.533,
                   "tie_steel_kg_per_m2": 5.261, "fill_kg_per_m2": 85.5, "levelling": "foamed_fill"})
    assert fc.shell_floor_by_hand(s) == pytest.approx(0.09754 * 340 + 8.533 * 2.34 + 85.5 * 0.4727, rel=2e-3)
