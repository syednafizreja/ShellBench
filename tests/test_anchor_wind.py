"""Tests for src/shellbench/anchor_wind.py (anchor frame, wind, Day 8).

Validation against closed-form results:
1. With rigid beams and axially rigid columns, each storey of the frame drifts
   by V / (n 12 EI / h^3), the closed-form stiffness of n fixed-fixed columns.
2. The D-value method redone from the model's sections gives the Day 3 hand
   check of the ground exterior column (LOG Day 3: K = 0.6315,
   alpha_c = 0.4300, D = 19 241 N/mm).

Checks of the thesis values and of the frame model:
3. The printed storey shears of Table 8-2 are the running sums of the
   printed W_k, and W_k at levels 1-3 follow from the Table 8-1 inputs.
4. Horizontal base reaction and column shears balance the applied wind.
5. Every model drift ratio meets the 1/550 limit (spec S11).
6. The author's pre-registered test: every storey drift within 15 % of
   Table 8-2 (docs/anchor_notes.md, decision 1 of 25 Oct 2026).
7. main() writes the four wind tables.
"""

import csv
import shutil
from pathlib import Path

import pytest

from shellbench import anchor_frame as af
from shellbench import anchor_wind as aw

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def thesis():
    """Table 8-2 as typed on Day 3."""
    return aw.read_thesis_wind(REPO)


@pytest.fixture(scope="module")
def primary(thesis):
    """The primary wind run with the printed Table 8-2 forces."""
    return aw.run_wind([t.w_kn for t in thesis])


def test_rigid_beam_storey_drift_is_closed_form(thesis):
    """Rigid beams + rigid column axial: du = V h^3 / (4 x 12 EI) per storey."""
    forces = [t.w_kn for t in thesis]
    res = aw.run_wind(forces, axially_rigid_columns=True, beam_inertia_factor=1.0e6)
    b, h = af.COLUMN_BH_M
    ei = af.E_KN_M2 * b * h**3 / 12.0
    for i, hs in enumerate(af.STOREY_HEIGHTS_M):
        v = sum(forces[i:])
        expected_mm = 1000.0 * v * hs**3 / (len(af.AXES) * 12.0 * ei)
        assert res.du_mm[i] == pytest.approx(expected_mm, rel=1e-4)


def test_d_value_method_matches_day3_hand_check():
    """Ground A/D column: K, alpha_c and D as hand-checked on Day 3 (LOG.md)."""
    ground = aw.d_value_method()[0]
    assert ground["K_A/D [-]"] == pytest.approx(0.6315, rel=1e-3)
    assert ground["alpha_c_A/D [-]"] == pytest.approx(0.4300, rel=1e-3)
    assert ground["D_A/D [N/mm]"] == pytest.approx(19241, rel=1e-3)


def test_table_8_2_shears_are_running_sums(thesis):
    """V_i = sum of W_k at and above level i (Table 8-2), to the printed 0.01 kN."""
    for row in aw.wind_force_check_rows(thesis):
        assert row["sum_W_above [kN]"] == pytest.approx(row["V_printed [kN]"], abs=0.011)


def test_table_8_2_forces_follow_table_8_1_inputs(thesis):
    """W_k at levels 1-3 equals beta_z mu_s mu_z w0 B h_trib within print rounding."""
    for row in aw.wind_force_check_rows(thesis)[:3]:
        assert row["W_k_from_expected [kN]"] == pytest.approx(row["W_k_printed [kN]"], abs=0.02)


def test_wind_equilibrium(primary, thesis):
    """Base reaction and storey column shears balance the applied wind."""
    assert primary.applied_kn == pytest.approx(sum(t.w_kn for t in thesis), rel=1e-12)
    assert -primary.base_shear_kn == pytest.approx(primary.applied_kn, rel=1e-9)
    for shear, t in zip(primary.column_shear_kn, thesis):
        assert shear == pytest.approx(t.v_kn, abs=0.011)


def test_model_drifts_meet_limit(primary):
    """Every storey drift ratio is within 1/550 (spec S11, Th s8.2)."""
    assert all(theta <= aw.DRIFT_LIMIT for theta in primary.theta)


@pytest.mark.xfail(
    strict=True, raises=AssertionError,
    reason=("Pre-registered test fails at all four storeys (model 45-87 % below the printed "
            "du). Printed Table 8-2 du is not V/sum_D of its own V and sum_D (flag D7) and implies "
            "a stiffness V/du that varies more than four times across the identical storeys 2-4, so no "
            "single elastic frame reproduces it. Kept strict: if the target or the model changes and the "
            "test passes, the suite fails and the verdict must be re-read. Author to confirm "
            "how this test is kept (docs/anchor_notes.md, wind section)."))
def test_storey_drifts_within_preregistered_tolerance(primary, thesis):
    """Every storey drift within 15 % of thesis Table 8-2 (author, 25 Oct 2026)."""
    for du, t in zip(primary.du_mm, thesis):
        pct = aw.percent_difference(du, t.du_mm)
        assert abs(pct) <= aw.WIND_DRIFT_TOLERANCE_PCT, f"level {t.level}: {pct:+.1f} %"


def test_wind_tables_written(tmp_path):
    """main() writes the wind comparison, the runs, the D-values and the force check."""
    shutil.copytree(REPO / "validation", tmp_path / "validation")
    tables = aw.main(tmp_path)
    assert len(tables["wind"]) == 4
    assert len(tables["runs"]) == len(aw.WIND_VARIANTS)
    for name in ("anchor_wind.csv", "anchor_wind_runs.csv", "anchor_wind_d_values.csv",
                 "thesis_table_8_2_forces_check.csv"):
        assert (tmp_path / "results" / name).exists(), name
    with open(tmp_path / "results" / "anchor_wind.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert [r["level [text]"] for r in rows] == ["1", "2", "3", "4"]
