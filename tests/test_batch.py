"""Tests for the batch runner and the frozen family_rc format (Playbook Day 18).

File: tests/test_batch.py

The column list is frozen on 4 Nov 2026 (docs/data_card.md): a test fails
if a column is renamed, removed or moved. Columns may only be added at the end.
"""

from __future__ import annotations

import pytest

from shellbench import batch

FROZEN_4_NOV_2026 = (
    "building_id", "release", "shellbench_version", "takeoff_scope",
    "storeys", "pga_g", "intensity", "tg_s", "alpha_max", "concrete_grade",
    "spans_m", "storey_heights_m", "tributary_width_m", "floor_area_m2", "floor_system",
    "status", "failure_reason", "n_passes", "period_s", "max_drift_ratio", "axial_ratio",
    "column_mm", "beam_b_mm", "beam_h_mm", "slab_mm",
    "concrete_m3_per_m2", "bar_steel_kg_per_m2",
    "floor_concrete_m3_per_m2", "lateral_concrete_m3_per_m2",
    "floor_steel_kg_per_m2", "lateral_steel_kg_per_m2",
    "carbon_floor_kgco2e_per_m2", "carbon_lateral_kgco2e_per_m2", "carbon_building_kgco2e_per_m2",
)


def test_columns_frozen():
    """The first 34 columns are the 4 Nov 2026 list, in order."""
    assert batch.COLUMNS[:len(FROZEN_4_NOV_2026)] == FROZEN_4_NOV_2026


def test_family_size_and_ids():
    """6 storey counts x 6 PGAs = 36 buildings, unique IDs, anchor ID as documented."""
    fam = batch.family()
    ids = [f["building_id"] for f in fam]
    assert len(fam) == 36 and len(set(ids)) == 36
    assert batch.building_id(4, 0.10, 0.35, "C40") == "s04-p010-tg35-C40"
    assert fam[0]["pga_g"] == 0.10  # validated block first


@pytest.fixture(scope="module")
def sample():
    """First eight buildings: six at 0.10 g and two blocked at 0.05 g."""
    return batch.run_family(8)


def test_anchor_row_matches_day16(sample):
    """The 4-storey 0.10 g row reproduces the Day 16 generator values."""
    r = sample.set_index("building_id").loc["s04-p010-tg35-C40"]
    assert r["status"] == "ok"
    assert r["period_s"] == pytest.approx(0.5485, abs=5e-4)
    assert 1.0 / r["max_drift_ratio"] == pytest.approx(1163, abs=1)
    assert r["axial_ratio"] == pytest.approx(0.4385, abs=5e-4)


def test_blocked_rows_are_kept(sample):
    """Unconfirmed alpha_max gives a blocked row with a reason, never a dropped one."""
    blocked = sample[sample["pga_g"] == 0.05]
    assert len(blocked) == 2
    assert (blocked["status"] == "blocked").all()
    assert blocked["failure_reason"].str.contains("not confirmed").all()
    assert blocked["carbon_building_kgco2e_per_m2"].isna().all()


def test_carbon_adds_up(sample):
    """Building carbon is floor plus lateral; floor carbon is slab x C40 factor by hand."""
    ok = sample[sample["status"] == "ok"]
    conc, _ = batch.factors()
    assert ok["carbon_building_kgco2e_per_m2"].tolist() == pytest.approx(
        (ok["carbon_floor_kgco2e_per_m2"] + ok["carbon_lateral_kgco2e_per_m2"]).tolist())
    assert ok["carbon_floor_kgco2e_per_m2"].tolist() == pytest.approx([0.12 * conc] * len(ok))
