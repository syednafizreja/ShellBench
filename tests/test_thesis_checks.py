"""Tests for src/shellbench/thesis_checks.py (arithmetic checks on the thesis).

The typed live-load distribution table (Th §7.2, table "7.2") is checked
against facts that can be read off it by hand:
1. Floor 1 (the ground-floor block): every printed final equals its column sum
   to within 0.1 kN*m, so the summing code and the typed cells agree.
2. Floor 2, joint C, right beam: the printed final -3.38 differs from its
   column sum -26.66 by 23.28 kN*m. This is flag D2 (Day 3) seen from the table.
3. Joints A2 and A3: the column sums balance the printed external moment
   5.89 kN*m (sum = -5.89 to within 0.05), which confirms the sign rule used
   for joint balance.
4. Every block has the same members: 14 member ends at floors 1-3, 10 at the
   roof (no upper columns).
"""

from pathlib import Path

import pytest

from shellbench import thesis_checks as tc

REPO = Path(__file__).resolve().parents[1]
TABLE_7_2 = REPO / "validation" / "thesis_values" / "live_distribution_table_7_2.csv"


@pytest.fixture(scope="module")
def cells():
    """The typed table-7.2 cells."""
    return tc.read_distribution_table(TABLE_7_2)


def test_member_count_per_floor(cells):
    """14 member ends with a final value at floors 1-3 and 10 at the roof."""
    sums = tc.column_sums(cells)
    for floor, n in (("4", 10), ("3", 14), ("2", 14), ("1", 14)):
        assert sum(1 for r in sums if r["floor"] == floor) == n


def test_floor_1_finals_equal_column_sums(cells):
    """Floor 1 block: printed finals equal the column sums within 0.1 kN*m, except at joint C."""
    for r in tc.column_sums(cells):
        if r["floor"] == "1" and r["joint"] != "C":
            assert abs(r["printed_minus_sum"]) < 0.1, r


def test_d2_seen_as_column_sum_error(cells):
    """Floor 2, C right beam: printed -3.38, column sum -26.66 (flag D2)."""
    row = next(r for r in tc.column_sums(cells)
               if (r["floor"], r["joint"], r["member_end"]) == ("2", "C", "right beam"))
    assert row["printed_final"] == -3.38
    assert row["column_sum"] == pytest.approx(-26.66, abs=0.01)


@pytest.mark.parametrize("floor", ["2", "3"])
def test_exterior_joint_balances_with_column_sums(cells, floor):
    """At A2 and A3 the column sums add to minus the printed joint moment."""
    row = next(r for r in tc.joint_balance(cells) if (r["floor"], r["joint"]) == (floor, "A"))
    assert row["sum_column_sums"] == pytest.approx(-row["external_moment_printed"], abs=0.05)
