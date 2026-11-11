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


def test_commit_is_read_before_the_files_are_written(tmp_path, monkeypatch):
    """The recorded commit is the one seen before writing, so the run's own output files do not add "+dirty"."""
    calls = []

    def fake_commit(root):
        """First call (before writing) is clean; any later call would see the written files as dirty."""
        calls.append(1)
        return "abc123" if len(calls) == 1 else "abc123+dirty"

    monkeypatch.setattr(provenance, "git_commit", fake_commit)
    df = batch.run_family(1, scope="building_v2")
    batch.write(df, tmp_path / "one", scope="building_v2")
    rec = json.loads((tmp_path / "one.provenance.json").read_text())
    assert rec["git_commit"] == "abc123"
