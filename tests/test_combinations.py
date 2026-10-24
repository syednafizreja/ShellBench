"""Tests for src/shellbench/combinations.py (load combinations, Day 6).

1. The factors match the printed headers of thesis Tables 8-13 and 8-15
   (1.3 D + 1.5 L; 1.3 D + 1.5 (L + 0.6 W); 1.3 D + 1.5 (0.7 L + W)).
2. ``combine`` is the linear sum of factor x effect and refuses missing cases
   or mismatched effect keys.
3. With only dead and live solved, one combination is evaluated and the wind
   and seismic ones are reported as pending.
4. Thesis Table 8-13 (roof rows): the column headed "1.3 D + 1.5 L" equals
   1.0 D + 1.5 L in every row (proposed flag D16).
"""

from pathlib import Path

import pytest

from shellbench import combinations as cb
from shellbench import thesis_checks as tc

REPO = Path(__file__).resolve().parents[1]
TABLE_8_13 = REPO / "validation" / "thesis_values" / "combination_beam_roof.csv"


def by_name(name: str) -> cb.Combination:
    """Return the thesis combination with this name.

    Args:
        name: Combination label.

    Returns:
        The matching Combination.
    """
    return next(c for c in cb.THESIS_COMBINATIONS if c.name == name)


def test_factors_match_thesis_headers():
    """Expanded factors equal the products in the Table 8-13 / 8-15 headers."""
    assert by_name("1.3D+1.5L").factors == {"D": 1.3, "L": 1.5}
    c2 = by_name("1.3D+1.5(L+0.6W_left)").factors
    assert c2["D"] == 1.3 and c2["L"] == 1.5 and c2["W_left"] == pytest.approx(0.9)
    c3 = by_name("1.3D+1.5(0.7L+W_right)").factors
    assert c3["D"] == 1.3 and c3["L"] == pytest.approx(1.05) and c3["W_right"] == 1.5


def test_seismic_combinations_marked_unverified():
    """The seismic factors come from garbled text, so they carry status 'unverified'."""
    for c in cb.THESIS_COMBINATIONS:
        assert c.status == ("unverified" if "E_" in c.name else "thesis")


def test_combine_is_linear():
    """1.3 D + 1.5 L on two keys, by hand."""
    cases = {"D": {"a": 10.0, "b": -2.0}, "L": {"a": 4.0, "b": 1.0}}
    out = cb.combine(cases, by_name("1.3D+1.5L"))
    assert out["a"] == pytest.approx(1.3 * 10.0 + 1.5 * 4.0)
    assert out["b"] == pytest.approx(1.3 * -2.0 + 1.5 * 1.0)


def test_combine_refuses_missing_case_and_key_mismatch():
    """A missing case raises KeyError; different effect keys raise ValueError."""
    with pytest.raises(KeyError):
        cb.combine({"D": {"a": 1.0}}, by_name("1.3D+1.5L"))
    with pytest.raises(ValueError):
        cb.combine({"D": {"a": 1.0}, "L": {"b": 1.0}}, by_name("1.3D+1.5L"))


def test_only_gravity_combination_available_on_day_6():
    """With D and L solved, 1.3D+1.5L is evaluated and six combinations are pending."""
    results, pending = cb.evaluate_all({"D": {"a": 1.0}, "L": {"a": 1.0}})
    assert list(results) == ["1.3D+1.5L"]
    assert len(pending) == 6


def test_table_8_13_used_1_0_dead_not_1_3():
    """Every roof row of Table 8-13 equals 1.0 D + 1.5 L (D16), and none equals 1.3 D + 1.5 L."""
    rows = tc.read_combination_table(TABLE_8_13)
    assert len(rows) == 13
    as_printed = tc.combination_factor_check(rows, 1.0, cb.GAMMA_Q)
    assert all(abs(r["printed_minus_recomputed"]) < 0.01 for r in as_printed)
    as_headed = tc.combination_factor_check(rows, cb.GAMMA_G, cb.GAMMA_Q)
    assert all(abs(r["printed_minus_recomputed"]) > 1.0 for r in as_headed)
