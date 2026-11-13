"""Tie thrust in the committed panel results against H = w L^2 / (8 f) (no CalculiX needed).

File: tests/test_thrust_results.py

The CalculiX tests in test_panel.py check the Day 25 Done-when only when ccx is
installed, so they are skipped in CI. These tests read the committed result
files instead and check three things on every row:

1. ``h_closed_n_m`` is the closed-form parabolic thrust w L^2 / (8 f) of the
   row's own ULS load, span and rise.
2. ``h_ratio`` is ``h_rigid_n_m / h_closed_n_m``.
3. Rows under uniform load meet the Day 25 Done-when: the rigid-tie thrust from
   CalculiX is within ``DONE_WHEN_TOLERANCE`` of the closed form. Rows with a
   true (shaped) fill carry a non-uniform load, so for them the ratio is only
   reported (``panel.size_row``: ``done_when_ok = shaped or ...``).
"""

from __future__ import annotations

import pandas as pd
import pytest

from shellbench import panel as pn
from shellbench.formfind import parabolic_thrust

PANEL_CSV = pn.ROOT / "results" / "panel_day25.csv"
LIBRARY_CSV = pn.ROOT / "results" / "floor_library.csv"
# Writers round every float to 4 significant figures (panel.write_rows, "{v:.4g}"),
# so each stored value is off by up to 5e-4 relative; a quotient or product of
# two rounded values by up to 1e-3. 1.5e-3 covers that with margin [J].
REL_TOL: float = 1.5e-3


def _panel() -> pd.DataFrame:
    """Day 25 rows with span [m] and rise [m] of the Day 25 vault added."""
    df = pd.read_csv(PANEL_CSV)
    df["span_m"] = pn.SPAN_M
    df["rise_m"] = pn.RISE_RATIO * pn.SPAN_M
    return df


def _library() -> pd.DataFrame:
    """Floor library rows with rise [m] = rise ratio x span."""
    df = pd.read_csv(LIBRARY_CSV)
    df["rise_m"] = df["rise_ratio"] * df["span_m"]
    return df


@pytest.mark.parametrize("load", [_panel, _library], ids=["panel_day25", "floor_library"])
def test_closed_form_thrust_and_ratio(load):
    """Every row's h_closed is w L^2 / (8 f) and h_ratio is h_rigid / h_closed."""
    df = load()
    assert len(df) > 0
    for r in df.itertuples():
        h = parabolic_thrust(r.w_uls_pa, r.span_m, r.rise_m)
        assert r.h_closed_n_m == pytest.approx(h, rel=REL_TOL), r.Index
        assert r.h_ratio == pytest.approx(r.h_rigid_n_m / r.h_closed_n_m, rel=REL_TOL), r.Index


def test_day25_rows_meet_done_when():
    """All Day 25 rows: CalculiX rigid-tie thrust within 10 % of the closed form."""
    df = _panel()
    bad = df[(df["h_ratio"] - 1.0).abs() > pn.DONE_WHEN_TOLERANCE]
    assert bad.empty, bad[["thickness_m", "levelling", "h_ratio"]].to_string()


def test_library_uniform_rows_meet_done_when():
    """Floor library rows without a shaped fill meet the Done-when; fill rows are report-only."""
    df = _library()
    uniform = df[~df["levelling"].map(pn.is_fill)]
    assert len(uniform) > 0
    bad = uniform[(uniform["h_ratio"] - 1.0).abs() > pn.DONE_WHEN_TOLERANCE]
    assert bad.empty, bad[["variant_id", "h_ratio"]].to_string()


def test_passing_rows_meet_done_when_or_are_shaped():
    """A row marked as passing is either within the band or a shaped-fill row."""
    df = _library()
    ok = df["passes"].astype(bool)
    within = (df["h_ratio"] - 1.0).abs() <= pn.DONE_WHEN_TOLERANCE
    shaped = df["levelling"].map(pn.is_fill)
    assert (~ok | within | shaped).all()
