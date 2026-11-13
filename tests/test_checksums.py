"""The committed record in results/ matches SHA256SUMS."""

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = {".csv", ".json", ".md", ".txt"}


def _matches(path: Path, digest: str) -> bool:
    """True if the file as checked out, or with a Windows checkout's CRLF conversion undone, has ``digest``."""
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() == digest:
        return True
    return path.suffix in TEXT and hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest() == digest


def test_results_match_sha256sums():
    entries = [ln.split("  ", 1) for ln in (ROOT / "SHA256SUMS").read_text().splitlines() if ln.strip()]
    assert len(entries) > 50
    bad = [name for digest, name in entries if not _matches(ROOT / name, digest)]
    assert not bad, f"changed since SHA256SUMS was written: {bad}"
