"""Dataset package (Day 33): contents, checksums, metadata, reproducible zip, no thesis files."""

import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("make_dataset", ROOT / "scripts" / "make_dataset.py")
md = importlib.util.module_from_spec(spec)
spec.loader.exec_module(md)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """Build the package once into a temporary folder."""
    out = tmp_path_factory.mktemp("dist")
    return out, md.build(out)


def test_every_listed_file_is_in_the_zip(built):
    """The zip holds every file of FILES plus README, checksums and metadata."""
    _, z = built
    names = {Path(n).name for n in zipfile.ZipFile(z).namelist()}
    assert {dst for _, dst in md.FILES} <= names
    assert {"README.md", "SHA256SUMS.txt", "zenodo_metadata.json"} <= names


def test_checksums_match_the_zip_contents(built):
    """SHA256SUMS.txt matches the bytes inside the zip."""
    _, z = built
    zf = zipfile.ZipFile(z)
    root = zf.namelist()[0].split("/")[0]
    for line in zf.read(f"{root}/SHA256SUMS.txt").decode().splitlines():
        digest, name = line.split("  ")
        assert hashlib.sha256(zf.read(f"{root}/{name}")).hexdigest() == digest


def test_zip_is_reproducible(built, tmp_path):
    """Two builds give the same bytes."""
    _, z = built
    again = md.build(tmp_path)
    assert md.sha256(z) == md.sha256(again)


def test_metadata_licence_and_creator(built):
    """CC BY 4.0, the author's ORCID, a dataset upload type, and no DOI of the new record."""
    out, z = built
    meta = json.loads(zipfile.ZipFile(z).read(f"{z.stem}/zenodo_metadata.json"))
    assert meta["license"] == "cc-by-4.0" and meta["upload_type"] == "dataset"
    assert meta["creators"][0]["orcid"] == md.ORCID
    assert "doi" not in meta


def test_published_rows_are_not_labelled_pre_release():
    """The files that go into the dataset carry the final release label and version."""
    f = md.family_facts()
    assert "pre-release" not in f["release"] and f["version"] == "0.4.0"


def test_no_thesis_files_in_the_package(built):
    """Nothing from thesis_source/ or the validation folder is packaged."""
    _, z = built
    assert not [n for n in zipfile.ZipFile(z).namelist() if "thesis" in n.lower()]
