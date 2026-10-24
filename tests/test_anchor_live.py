"""Tests for the live-load case of src/shellbench/anchor_frame.py (Day 6).

Validation against closed-form results and hand sums:
1. A fixed-fixed beam under the back-calculated floor loads gives back the
   printed thesis fixed-end moments 27.70 and 3.52 kN*m (Th §7.1).
2. The total applied live load equals the hand sum of the printed joint loads
   and line loads (Th §6.1), for every live-load model.

Checks of the frame model:
3. Vertical base reactions equal the applied live load.
4. The frame and its load are symmetric, so results mirror about the centre.
5. Live load has no column self-weight, so N_top = N_bottom in every storey.
6. main() writes the live, combination and thesis-check tables.
"""

import csv
import shutil
from pathlib import Path

import pytest

from shellbench import anchor_frame as af
from test_anchor_frame import fixed_beam_end_moments

REPO = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("kind, span, printed", [("side", 7.2, 27.70), ("mid", 6.6, 3.52)])
def test_back_calculated_live_loads_give_printed_fem(kind, span, printed):
    """q = 12 M / L^2 applied to a fixed beam returns the printed FEM (Th s7.1)."""
    load = af.LIVE_LOAD_MODELS["thesis_fem"].beams[("floor", kind)]
    left, right = fixed_beam_end_moments(span, load)
    assert -left == pytest.approx(printed, rel=1e-9)
    assert right == pytest.approx(printed, rel=1e-9)


def hand_total(model: af.LoadModel) -> float:
    """Hand sum of the live load in one model [kN].

    Args:
        model: A live-load model.

    Returns:
        Joint loads on all 16 joints plus the line loads integrated over every
        span (trapezoid p(L - a), triangle pL/2, uniform qL).
    """
    joints = 2 * (af.LIVE_JOINT_LOADS_KN[("exterior", "roof")] + af.LIVE_JOINT_LOADS_KN[("interior", "roof")])
    joints += 3 * 2 * (af.LIVE_JOINT_LOADS_KN[("exterior", "floor")] + af.LIVE_JOINT_LOADS_KN[("interior", "floor")])
    lines = 0.0
    for level, count in (("roof", 1), ("floor", 3)):
        for kind, span, n in (("side", 7.2, 2), ("mid", 6.6, 1)):
            b = model.beams[(level, kind)]
            shaped = {"none": 0.0, "trapezoid": b.peak_kn_m * (span - b.ramp_m),
                      "triangle": b.peak_kn_m * span / 2.0}[b.shape]
            lines += count * n * (b.uniform_kn_m * span + shaped)
    return joints + lines


@pytest.mark.parametrize("load_model", sorted(af.LIVE_LOAD_MODELS))
def test_live_total_and_equilibrium(load_model):
    """Applied load equals the hand sum, and base reactions equal the applied load."""
    res = af.run_live_load(load_model)
    assert res.applied_kn == pytest.approx(hand_total(af.LIVE_LOAD_MODELS[load_model]), rel=1e-6)
    assert res.reaction_kn == pytest.approx(res.applied_kn, rel=1e-9)


@pytest.mark.parametrize("variant", sorted(af.LIVE_VARIANTS))
def test_live_symmetry(variant):
    """Symmetric frame and load: AB mirrors CD, BC is antisymmetric, A = D, B = C."""
    res = af.run_live_load(variant=variant, **af.LIVE_VARIANTS[variant])
    for floor in ("1", "2", "3", "4"):
        m = res.moments
        assert m[(floor, "AB", "left")] == pytest.approx(-m[(floor, "CD", "right")], abs=1e-6)
        assert m[(floor, "AB", "right")] == pytest.approx(-m[(floor, "CD", "left")], abs=1e-6)
        assert m[(floor, "BC", "left")] == pytest.approx(-m[(floor, "BC", "right")], abs=1e-6)
        for end in ("top", "bottom"):
            assert res.axial[("A", floor, end)] == pytest.approx(res.axial[("D", floor, end)], abs=1e-6)
            assert res.axial[("B", floor, end)] == pytest.approx(res.axial[("C", floor, end)], abs=1e-6)


def test_live_axial_constant_over_storey():
    """No self-weight in the live case: column axial force is the same at top and bottom."""
    res = af.run_live_load("thesis_fem")
    for storey in range(1, len(af.STOREY_HEIGHTS_M) + 1):
        for ax in af.AXES:
            assert res.axial[(ax, str(storey), "top")] == pytest.approx(
                res.axial[(ax, str(storey), "bottom")], abs=1e-9)


def test_live_tables_written(tmp_path):
    """main() writes 40 live rows, 40 combination rows and the table-7.2 checks."""
    shutil.copytree(REPO / "validation", tmp_path / "validation")
    tables = af.main(tmp_path)
    assert len(tables["live"]) == 40
    assert len(tables["combination"]) == 40
    for name in ("anchor_gravity_live.csv", "anchor_gravity_live_runs.csv",
                 "anchor_gravity_combination.csv", "thesis_table_7_2_check.csv",
                 "thesis_table_7_2_joints.csv"):
        assert (tmp_path / "results" / name).exists(), name
    with open(tmp_path / "results" / "thesis_table_7_2_check.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    beam_rows = [r for r in rows if r["model_primary [kN*m]"] != "n/a"]
    assert len(beam_rows) == 24
