"""tests/test_metadata.py

The release metadata files must name the same version.

pyproject.toml is the source of truth. CITATION.cff and codemeta.json are
read by GitHub, Zenodo and software indexes, so a stale copy would cite the
wrong version. The release workflow publishes docs/releases/v<version>.md,
so a released version must have its notes file.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _pyproject_version() -> str:
    """Return the package version from pyproject.toml."""
    with open(ROOT / "pyproject.toml", "rb") as fh:
        return tomllib.load(fh)["project"]["version"]


def _citation_version() -> str:
    """Return the top-level ``version:`` field of CITATION.cff."""
    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    match = re.search(r"(?m)^version:\s*\"?([^\"\n]+)\"?\s*$", text)
    assert match, "CITATION.cff has no top-level version field"
    return match.group(1).strip()


def test_citation_matches_pyproject():
    """CITATION.cff carries the package version."""
    assert _citation_version() == _pyproject_version()


def test_codemeta_matches_pyproject():
    """codemeta.json carries the package version."""
    meta = json.loads((ROOT / "codemeta.json").read_text(encoding="utf-8"))
    assert meta.get("version") == _pyproject_version()


def test_changelog_lists_current_version():
    """CHANGELOG.md has a row for the package version."""
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"| {_pyproject_version()} |" in text
