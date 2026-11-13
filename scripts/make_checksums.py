# scripts/make_checksums.py
"""Write SHA256SUMS: one SHA-256 per tracked file in results/, from the committed bytes.

Hashes are taken from the git blobs at HEAD, not from the working tree, so they
match a fresh clone on any platform (a Windows checkout may convert line ends).
Figures are left out: their bytes differ between platforms (font rendering),
while the data behind them is in results/. Check a copy with ``sha256sum -c
SHA256SUMS`` on a Linux or macOS clone, or with ``pytest tests/test_checksums.py``.

Run: python scripts/make_checksums.py
"""

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    files = subprocess.run(["git", "ls-files", "results"], cwd=ROOT, capture_output=True, text=True,
                           check=True).stdout.split()
    lines = []
    for f in sorted(files):
        blob = subprocess.run(["git", "cat-file", "blob", f"HEAD:{f}"], cwd=ROOT, capture_output=True,
                              check=True).stdout
        lines.append(f"{hashlib.sha256(blob).hexdigest()}  {f}")
    (ROOT / "SHA256SUMS").write_bytes(("\n".join(lines) + "\n").encode())
    print(len(lines), "files")


if __name__ == "__main__":
    main()
