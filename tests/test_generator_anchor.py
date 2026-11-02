"""Tests for the frame generator on the thesis building (Playbook Day 16).

File: tests/test_generator_anchor.py

Thesis inputs and their sources: spans 7.2/6.6/7.2 m and storey heights
4.55/3.6/3.6/3.6 m (anchor_frame.py, docs/baseline_spec.md); frame spacing
7.2 m (B10); slab panel 3.6 m (design_rules R3); floor dead 4.05 and roof dead
4.224 kN/m^2 (baseline L1, L2); live 2.5 office / 3.0 corridor, roof 0.5 [J]
(B3); secondary beams 2.54 on floors and on roof BC, 2.78 on roof AB/CD
(Th s5.2 items 1-4); wall on the frame beam 5.51 on AB/CD (L6, placement [J]
as the anchor); exterior wall 8.37, interior wall 6.36, longitudinal beam 3.61
and parapet 2.54 kN/m (B15); alpha_max 0.08 (Table 5.1.4-1, checked 25 Oct);
Tg 0.35 s; psi_T 0.7 (anchor); E 3.25e4 MPa and 2.0 I0 (anchor_frame.py).

The columns and the BC beam differ from the thesis on purpose. Which rule
causes each difference, and which side is right, is in docs/anchor_notes.md
("Generator against the thesis (Day 16)").
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from shellbench import anchor_frame as af
from shellbench import generator as g

ROOT = Path(__file__).resolve().parents[1]

THESIS = g.BuildingInput(
    spans_m=af.SPANS_M, storey_heights_m=af.STOREY_HEIGHTS_M, tributary_width_m=7.2,
    slab_panel_m=3.6, floor_dead_kn_m2=4.05, roof_dead_kn_m2=4.224,
    live_kn_m2=(2.5, 3.0, 2.5), roof_live_kn_m2=0.5,
    floor_secondary_kn_m=(2.54, 2.54, 2.54), roof_secondary_kn_m=(2.78, 2.54, 2.78),
    floor_beam_wall_kn_m=(5.51, 0.0, 5.51), exterior_wall_kn_m=8.37,
    interior_wall_kn_m=6.36, longitudinal_beam_kn_m=3.61, parapet_kn_m=2.54,
    alpha_max=0.08, tg_s=0.35, psi_t=0.7, concrete_e_mpa=3.25e4,
    beam_i_factor=af.BEAM_INERTIA_FACTOR)

ANCHOR_SIZES = g.Sizes(600, [(300, 600), (300, 500), (300, 600)], 120)  # Th s2.3, s2.4


@pytest.fixture(scope="module")
def result():
    return g.generate(THESIS, verbose=True)


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


def test_main_beams_match_and_columns_follow_r5(result):
    """Day 16 key test: AB/CD match the thesis 300x600; columns stay at R5's 500."""
    assert result.final.beams_mm[0] == (300, 600)
    assert result.final.beams_mm[2] == (300, 600)
    assert result.final.column_mm == 500
    assert len(result.history) == 1  # one pass, no resize


def test_thesis_case_passes_all_checks(result):
    """Final frame meets drift 1/550 and the axial limit, at the values logged on Day 16."""
    assert max(result.drift_ratios) <= g.DRIFT_LIMIT
    assert result.axial_ratio <= g.c.AXIAL_RATIO_LIMIT
    assert result.period_s == pytest.approx(0.5485, abs=5e-4)
    assert 1.0 / max(result.drift_ratios) == pytest.approx(1163, abs=1)
    assert result.axial_ratio == pytest.approx(0.4385, abs=5e-4)


def test_joint_loads_leave_out_the_slab():
    """Th s5.2 wall and beam items at floor nodes A and B, without its slab shares."""
    a, b, _, _ = g.joint_dead_kn(THESIS, ANCHOR_SIZES, 1)
    assert a == pytest.approx((8.37 + 3.61) * 6.6)
    assert b == pytest.approx((6.36 + 3.61) * 6.6)


def test_anchor_sizes_stay_close_to_the_anchor_model():
    """At the anchor's sizes, sum G and bare T1 are near results/, and always below.

    The bands are not targets. The residual is itemised in docs/anchor_notes.md;
    a change outside them means a load has been lost or counted twice.
    """
    with open(ROOT / "results" / "anchor_seismic_weights.csv", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["variant [text]"] == "primary"]
    with open(ROOT / "results" / "anchor_seismic_period_check.csv", newline="") as f:
        t_anchor = float(next(csv.DictReader(f))["T_eigen [s]"])
    sum_anchor = sum(float(r["G_i [kN]"]) for r in rows)
    weights = g.storey_weights_kn(THESIS, ANCHOR_SIZES)
    assert -0.11 < sum(weights) / sum_anchor - 1.0 < 0.0
    assert -0.06 < g.period_s(THESIS, ANCHOR_SIZES, weights) / t_anchor - 1.0 < 0.0


def test_rounding_and_bars():
    assert g.round_up(462.8) == 500
    assert g.choose_bars(1000.0) == "5C16"
    assert g.column_bars(600)[1] == "8C22"
    assert g.bars_area_mm2("5C16", 0.0) == pytest.approx(1005.3, abs=0.1)
    assert g.bars_area_mm2("more than one layer needed", 12.0) == 12.0
