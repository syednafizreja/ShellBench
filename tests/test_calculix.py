"""CalculiX smoke test (Day 22): the solver runs and a shell cantilever matches PL^3/3EI.

File: tests/test_calculix.py

Skipped where CalculiX is not installed. The tolerance (0.5 %) is Claude's
choice for a smoke test [J]; the shell benchmark with the author's values is
Day 24.
"""

from __future__ import annotations

import pytest

from shellbench import calculix as cx


def test_deck_has_expected_mesh():
    """20 x 2 S8R elements: 41 x 5 grid less the 40 element centres = 165 nodes."""
    deck, tip = cx.cantilever_deck()
    nodes = deck.split("*NODE\n")[1].split("\n*ELEMENT")[0].splitlines()
    assert len(nodes) == 41 * 5 - 20 * 2
    assert len(tip) == 5


@pytest.mark.skipif(cx.find_ccx() is None, reason="CalculiX not installed")
def test_cantilever_matches_closed_form(tmp_path):
    """Tip deflection within 0.5 % of P L^3 / (3 E I) = 13.333 mm."""
    r = cx.cantilever_smoke(tmp_path)
    assert "Version" in r.version
    assert r.tip_closed_m == pytest.approx(0.013333, abs=1e-6)
    assert abs(r.error) < 0.005
