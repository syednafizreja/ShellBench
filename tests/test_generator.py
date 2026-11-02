"""Tests for the frame generator (Playbook Day 16).

File: tests/test_generator.py

Thesis inputs and their sources: spans 7.2/6.6/7.2 m and storey heights
4.55/3.6/3.6/3.6 m (anchor_frame.py, docs/baseline_spec.md); frame spacing
7.2 m (decision of Day 2); slab panel 3.6 m (design_rules R3); floor dead
4.05 and roof dead 4.224 kN/m^2 (baseline L1, L2); live 2.5 office / 3.0
corridor, roof 0.5 [J] (B3); alpha_max 0.08 (Table 5.1.4-1, checked 25 Oct);
Tg 0.35 s; psi_T 0.7 (anchor); E 3.25e4 MPa and 2.0 I0 (anchor_frame.py).
"""

from __future__ import annotations

import pytest

from shellbench import anchor_frame as af
from shellbench import generator as g

THESIS = g.BuildingInput(
    spans_m=af.SPANS_M, storey_heights_m=af.STOREY_HEIGHTS_M, tributary_width_m=7.2,
    slab_panel_m=3.6, floor_dead_kn_m2=4.05, roof_dead_kn_m2=4.224,
    live_kn_m2=(2.5, 3.0, 2.5), roof_live_kn_m2=0.5, alpha_max=0.08, tg_s=0.35,
    psi_t=0.7, concrete_e_mpa=3.25e4, beam_i_factor=af.BEAM_INERTIA_FACTOR)


@pytest.fixture(scope="module")
def result():
    return g.generate(THESIS)


def test_preliminary_sizes_follow_the_rules():
    """R3-R5 with code values: 120 slab, 300x600 / 300x550 beams, 500 column.

    The thesis has 600 columns (n = 5, mu = 0.75; design_rules R5) and a
    300x500 BC beam (a separate choice; R4). Both differences are decided
    (design_rules section 6, items 2 and 3).
    """
    pre = g.preliminary_sizes(THESIS)
    assert pre.slab_mm == 120
    assert pre.beams_mm == [(300, 600), (300, 550), (300, 600)]
    assert pre.column_mm == 500


def test_thesis_case_passes_all_checks(result):
    """Final frame meets drift 1/550 and the axial limit."""
    assert max(result.drift_ratios) <= g.DRIFT_LIMIT
    assert result.axial_ratio <= g.c.AXIAL_RATIO_LIMIT
    assert 0.3 < result.period_s < 1.0


def test_reports_sizes(result):
    """Day 16 key test: report final sizes against the thesis 600x600 / 300x600."""
    print("final", result.final, "history", result.history)
    assert result.final.beams_mm[0] == (300, 600)
    assert result.final.column_mm in (500, 550, 600)


def test_rounding_and_bars():
    assert g.round_up(462.8) == 500
    assert g.choose_bars(1000.0) == "5C16"
    assert g.column_bars(600)[1] == "8C22"
