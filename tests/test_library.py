"""Tests for the shell floor library (Playbook Day 26).

File: tests/test_library.py

Done-when: 60 or more library cases, with 5 spot checks. The library is
read from results/floor_library.csv (made by ``python -m shellbench.library``).
"""

from __future__ import annotations

import pytest

from shellbench import library as lib

ROWS = lib.read_library()
SPOT = ("SF001", "SF020", "SF044", "SF060", "SF087")  # one per span, mixed rise, live, levelling [J]


def test_at_least_60_sized_cases():
    assert len(ROWS) == 90
    assert sum(r["status"] == "ok" for r in ROWS) >= 60
    assert all(r["levelling"] for r in ROWS)


@pytest.mark.parametrize("case_id", SPOT)
def test_spot_checks(case_id):
    """Hand values against the library row: 0.5 % for statics, 10 % for the FE thrust."""
    row = next(r for r in ROWS if r["case_id"] == case_id)
    chk = lib.spot_checks(row)
    for name in ("w_uls", "h_closed", "concrete", "tie_steel"):
        assert abs(chk[name]) < 0.005, name
    assert abs(chk["h_fe_vs_closed"]) < 0.10


def test_sized_rows_pass_every_check():
    for r in ROWS:
        if r["status"] == "ok":
            assert r["passes"] == "True"
            assert float(r["util_pattern"]) <= 1.0 and float(r["buckling_factor"]) > 1.0
