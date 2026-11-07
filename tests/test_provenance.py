"""Provenance sidecar: versions, commit and seed are recorded with every family file."""

import json

from shellbench import batch, provenance


def test_seed_is_fixed():
    """The analysis seed is a fixed integer (preregistration 2.1)."""
    assert provenance.SEED == 20261103


def test_versions_recorded():
    """Python and every listed package appear in the record."""
    v = provenance.versions()
    assert "python" in v and set(provenance.PACKAGES) <= set(v)


def test_write_adds_sidecar(tmp_path):
    """batch.write puts a provenance file next to the CSV and Parquet."""
    df = batch.run_family(1, scope="building_v2")
    stem = tmp_path / "one"
    batch.write(df, stem, scope="building_v2")
    rec = json.loads((tmp_path / "one.provenance.json").read_text())
    assert rec["seed"] == provenance.SEED and rec["rows"] == 1 and rec["scope"] == "building_v2"
    assert rec["versions"]["pandas"] != "not installed"
