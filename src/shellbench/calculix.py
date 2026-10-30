"""Run CalculiX (ccx) from Python, with a smoke test against a closed form.

File: src/shellbench/calculix.py

What this module does
---------------------
Playbook Day 22 asks that CalculiX runs before the shell floor work starts.
This module finds the ``ccx`` executable, writes an input deck, runs it, and
reads nodal displacements from the ``.dat`` file. The smoke test is a
cantilever plate of S8R shell elements under a tip line load, compared with
the Euler-Bernoulli tip deflection P L^3 / (3 E I). Poisson's ratio is 0 so
that plate action does not stiffen the strip.

This is not the shell benchmark of Day 24 (MacNeal-Harder, with the
author's values); it only shows that the solver is installed and that the
deck, run and read-back chain works.

Units: N, m, Pa.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

# Smoke-test cantilever (all chosen for the test, not taken from a source).
SMOKE_LENGTH_M = 1.0
SMOKE_WIDTH_M = 0.1
SMOKE_THICKNESS_M = 0.01
SMOKE_E_PA = 30e9
SMOKE_LOAD_N = 10.0
SMOKE_ELEMENTS = (20, 2)  # along the length, across the width


def find_ccx() -> str | None:
    """Return the path of the CalculiX executable, or None if not installed.

    Looks for ``ccx`` and then for the versioned names some packages use.
    """
    for name in ("ccx", "ccx_2.23", "ccx_2.22", "ccx_2.21"):
        path = shutil.which(name)
        if path:
            return path
    return None


def ccx_version(ccx: str) -> str:
    """Return the version line printed by ``ccx -v`` (e.g. "This is Version 2.21")."""
    out = subprocess.run([ccx, "-v"], capture_output=True, text=True, timeout=60)
    return next((ln.strip() for ln in (out.stdout + out.stderr).splitlines()
                 if "Version" in ln), "")


def cantilever_deck() -> tuple[str, list[int]]:
    """Write the S8R cantilever deck as text.

    Returns:
        (input deck, node numbers on the loaded tip edge).
    """
    nx, ny = SMOKE_ELEMENTS
    dx, dy = SMOKE_LENGTH_M / (2 * nx), SMOKE_WIDTH_M / (2 * ny)
    nid: dict[tuple[int, int], int] = {}
    nodes = []
    for j in range(2 * ny + 1):
        for i in range(2 * nx + 1):
            if i % 2 and j % 2:
                continue  # 8-node elements have no centre node
            nid[(i, j)] = len(nid) + 1
            nodes.append(f"{nid[(i, j)]},{i * dx:.6f},{j * dy:.6f},0")
    elements = []
    for jj in range(ny):
        for ii in range(nx):
            i, j = 2 * ii, 2 * jj
            corners = [(i, j), (i + 2, j), (i + 2, j + 2), (i, j + 2),
                       (i + 1, j), (i + 2, j + 1), (i + 1, j + 2), (i, j + 1)]
            elements.append(f"{len(elements) + 1}," + ",".join(str(nid[c]) for c in corners))
    fixed = [nid[(0, j)] for j in range(2 * ny + 1)]
    tip = [nid[(2 * nx, j)] for j in range(2 * ny + 1)]
    # Consistent nodal loads of a quadratic edge: 1/6, 4/6, 1/6 per element edge.
    weights = [1.0] + [w for _ in range(ny) for w in (4.0, 2.0)]
    weights[-1] = 1.0
    total = sum(weights)
    deck = ["*NODE", *nodes,
            "*ELEMENT,TYPE=S8R,ELSET=PLATE", *elements,
            "*NSET,NSET=FIX", ",".join(map(str, fixed)),
            "*NSET,NSET=TIP", ",".join(map(str, tip)),
            "*MATERIAL,NAME=CONC", "*ELASTIC", f"{SMOKE_E_PA},0.0",
            "*SHELL SECTION,ELSET=PLATE,MATERIAL=CONC", f"{SMOKE_THICKNESS_M}",
            "*BOUNDARY", "FIX,1,6,0",
            "*STEP", "*STATIC", "*CLOAD",
            *[f"{n},3,{SMOKE_LOAD_N * w / total}" for n, w in zip(tip, weights)],
            "*NODE PRINT,NSET=TIP", "U", "*END STEP", ""]
    return "\n".join(deck), tip


def read_displacements(dat: Path) -> dict[int, tuple[float, float, float]]:
    """Read the nodal displacements printed in a CalculiX ``.dat`` file."""
    out = {}
    reading = False
    for line in dat.read_text().splitlines():
        if "displacements" in line:
            reading = True
            continue
        parts = line.split()
        if reading and len(parts) == 4:
            out[int(parts[0])] = tuple(float(x) for x in parts[1:])
    return out


@dataclass
class SmokeResult:
    """Outcome of the cantilever smoke test.

    Attributes:
        version: The ``ccx -v`` version line.
        tip_fe_m: Mean vertical tip displacement from CalculiX [m].
        tip_closed_m: P L^3 / (3 E I) [m].
    """

    version: str
    tip_fe_m: float
    tip_closed_m: float

    @property
    def error(self) -> float:
        """Relative difference of the finite-element tip deflection [-]."""
        return self.tip_fe_m / self.tip_closed_m - 1.0


def cantilever_smoke(workdir: Path, ccx: str | None = None) -> SmokeResult:
    """Run the cantilever smoke test in ``workdir``.

    Args:
        workdir: Folder for the deck and the CalculiX output.
        ccx: Path of the executable; found with ``find_ccx`` if None.

    Returns:
        The tip deflection from CalculiX and from the closed form.

    Raises:
        FileNotFoundError: If CalculiX is not installed.
    """
    ccx = ccx or find_ccx()
    if ccx is None:
        raise FileNotFoundError("CalculiX (ccx) not found on PATH")
    workdir.mkdir(parents=True, exist_ok=True)
    deck, tip = cantilever_deck()
    (workdir / "cantilever.inp").write_text(deck)
    subprocess.run([ccx, "cantilever"], cwd=workdir, capture_output=True, check=True,
                   timeout=300)
    u = read_displacements(workdir / "cantilever.dat")
    tip_fe = sum(u[n][2] for n in tip) / len(tip)
    i = SMOKE_WIDTH_M * SMOKE_THICKNESS_M ** 3 / 12
    closed = SMOKE_LOAD_N * SMOKE_LENGTH_M ** 3 / (3 * SMOKE_E_PA * i)
    return SmokeResult(ccx_version(ccx), tip_fe, closed)


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        r = cantilever_smoke(Path(tmp))
    print(f"{r.version}: tip {r.tip_fe_m:.6e} m, closed form {r.tip_closed_m:.6e} m, "
          f"difference {100 * r.error:.3f} %")
