"""tests/test_docs_links.py

Every relative link in the tracked Markdown files must point to a file or
folder that exists in the repository, so a reader following the README or
the docs never lands on a missing page. Web links (http, https, mailto,
doi) are not fetched; only repository paths are checked.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def _tracked_markdown() -> list[Path]:
    """Return the Markdown files tracked by git (all *.md if git is absent)."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True,
            text=True, check=True,
        ).stdout.split("\n")
        files = [ROOT / f for f in out if f.strip()]
        if files:
            return files
    except (OSError, subprocess.CalledProcessError):
        pass
    return [p for p in ROOT.rglob("*.md") if ".git" not in p.parts]


def test_relative_links_resolve():
    """No tracked Markdown file links to a missing repository path."""
    broken = []
    for md in _tracked_markdown():
        text = md.read_text(encoding="utf-8")
        for match in LINK.finditer(text):
            target = match.group(1)
            if SCHEME.match(target):
                continue
            if not (md.parent / unquote(target)).exists():
                broken.append(f"{md.relative_to(ROOT).as_posix()} -> {target}")
    assert not broken, "broken links:\n" + "\n".join(broken)
