"""CalculiX shell analysis: write the deck, run ccx, read the results.

File: src/shellbench/shellfe.py

What this module does
---------------------
Playbook Day 24. ``ShellModel`` holds a mesh of 8-node S8R shells with its
material, supports and loads. ``deck`` writes it as a CalculiX input file,
``run`` runs ccx, and the result holds nodal displacements, integration-point
stresses and buckling factors.

The two benchmarks are the Scordelis-Lo roof and the pinched hemisphere of
MacNeal and Harder (1985). Their geometry, loads and reference answers are read
from validation/benchmarks.csv, where each value carries its page. The paper
gives no units, so those two problems are in consistent units.

Whole structures, no rotational supports
----------------------------------------
Both benchmarks are drawn as symmetric parts, but they are modelled whole.
CalculiX expands S8R shells to solids, and rotational supports along a symmetry
line made the shell far too stiff: the quarter roof settled at 0.13 of the
reference however fine the mesh, while the whole roof reaches 0.998. So
``ShellModel`` has translational supports only, and n means elements per side
of the patch the paper meshes, to compare with its N x N.

Units: N, m, Pa everywhere else.
"""

from __future__ import annotations

import csv
import math
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from shellbench.calculix import find_ccx, read_displacements

ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS_CSV = ROOT / "validation" / "benchmarks.csv"
CONVERGENCE_CSV = ROOT / "results" / "benchmarks_convergence.csv"
CONVERGENCE_PNG = ROOT / "figures" / "benchmarks_convergence.png"

#: Elements per side of the modelled patch, coarse to fine [J].
MESH_ELEMENTS: tuple[int, ...] = (4, 8, 16)
#: Playbook Day 24: finest mesh within this fraction of the reference.
TOLERANCE: float = 0.02
#: Gravity used only to turn an area load into a CalculiX GRAV load. Any value
#: works, because the density is set from it (``scordelis_lo``).
LOAD_GRAVITY: float = 1.0
CCX_TIMEOUT_S: int = 900

Surface = Callable[[float, float], tuple[float, float, float]]


@dataclass
class ShellModel:
    """One S8R shell model.

    Attributes:
        nodes: Node number to (x, y, z).
        elements: Eight node numbers per element, corners then midsides.
        thickness: Shell thickness.
        e: Young's modulus.
        nu: Poisson's ratio.
        density: Mass density; needed only with ``gravity``.
        supports: (node, first dof, last dof), all zero. Translations only,
            dof 1-3 (see the module note).
        forces: (node, dof, force).
        gravity: (acceleration, dx, dy, dz) on all elements, or None.
    """

    nodes: dict[int, tuple[float, float, float]]
    elements: list[tuple[int, ...]]
    thickness: float
    e: float
    nu: float
    density: float = 0.0
    supports: list[tuple[int, int, int]] = field(default_factory=list)
    forces: list[tuple[int, int, float]] = field(default_factory=list)
    gravity: tuple[float, float, float, float] | None = None


@dataclass
class ShellResult:
    """Output of one CalculiX run.

    Attributes:
        displacements: Node to (ux, uy, uz). For a buckling step, the last mode.
        stresses: (element, integration point) to (sxx, syy, szz, sxy, sxz, syz).
        buckling_factors: Load factors in mode order; empty for a static step.
    """

    displacements: dict[int, tuple[float, float, float]]
    stresses: dict[tuple[int, int], tuple[float, ...]]
    buckling_factors: list[float]


def mapped_mesh(surface: Surface, nu: int, nv: int, closed_v: bool = False) -> tuple[
        dict[int, tuple[float, float, float]], list[tuple[int, ...]], dict[tuple[int, int], int]]:
    """Mesh a mapped surface with nu x nv 8-node elements.

    Args:
        surface: Maps (u, v) in [0, 1] x [0, 1] to (x, y, z).
        nu: Elements along u.
        nv: Elements along v.
        closed_v: True if v = 1 meets v = 0, as round a ring; the seam shares nodes.

    Returns:
        Nodes, elements, and the node at each (i, j) of the 2nu x 2nv grid.
        Element centres are not on the grid, as S8R has no centre node.
    """
    grid: dict[tuple[int, int], int] = {}
    nodes: dict[int, tuple[float, float, float]] = {}
    for j in range(2 * nv + (0 if closed_v else 1)):
        for i in range(2 * nu + 1):
            if i % 2 and j % 2:
                continue
            grid[(i, j)] = len(grid) + 1
            nodes[grid[(i, j)]] = surface(i / (2 * nu), j / (2 * nv))
    elements = []
    for jj in range(nv):
        for ii in range(nu):
            i, j = 2 * ii, 2 * jj
            top = (j + 2) % (2 * nv) if closed_v else j + 2
            elements.append(tuple(grid[c] for c in (
                (i, j), (i + 2, j), (i + 2, top), (i, top),
                (i + 1, j), (i + 2, j + 1), (i + 1, top), (i, j + 1))))
    return nodes, elements, grid


def deck(model: ShellModel, buckling_modes: int = 0) -> str:
    """Write the model as a CalculiX input deck.

    Args:
        model: The shell model.
        buckling_modes: Number of buckling factors wanted; 0 for a static step.

    Returns:
        The deck as text.
    """
    lines = ["*NODE"]
    lines += [f"{n},{x:.10g},{y:.10g},{z:.10g}" for n, (x, y, z) in model.nodes.items()]
    lines.append("*ELEMENT,TYPE=S8R,ELSET=SHELL")
    lines += [f"{k}," + ",".join(map(str, e)) for k, e in enumerate(model.elements, start=1)]
    lines += ["*NSET,NSET=OUT"]  # ccx prints nothing for its own NALL with shells
    numbers = list(model.nodes)
    lines += [",".join(map(str, numbers[k:k + 12])) for k in range(0, len(numbers), 12)]
    lines += ["*MATERIAL,NAME=MAT", "*ELASTIC", f"{model.e},{model.nu}"]
    if model.density:
        lines += ["*DENSITY", f"{model.density}"]
    lines += ["*SHELL SECTION,ELSET=SHELL,MATERIAL=MAT", f"{model.thickness}", "*BOUNDARY"]
    lines += [f"{n},{first},{last},0" for n, first, last in model.supports]
    lines += ["*STEP", "*BUCKLE", f"{buckling_modes}"] if buckling_modes else ["*STEP", "*STATIC"]
    if model.forces:
        lines.append("*CLOAD")
        lines += [f"{n},{dof},{p}" for n, dof, p in model.forces]
    if model.gravity:
        g, dx, dy, dz = model.gravity
        lines += ["*DLOAD", f"SHELL,GRAV,{g},{dx},{dy},{dz}"]
    lines += ["*NODE PRINT,NSET=OUT", "U"]
    if not buckling_modes:
        lines += ["*EL PRINT,ELSET=SHELL", "S"]
    lines += ["*END STEP", ""]
    return "\n".join(lines)


def read_stresses(dat: Path) -> dict[tuple[int, int], tuple[float, ...]]:
    """Read integration-point stresses from a CalculiX ``.dat`` file."""
    out = {}
    reading = False
    for line in dat.read_text().splitlines():
        if "stresses" in line:
            reading = True
            continue
        parts = line.split()
        if reading and len(parts) >= 8:  # shell rows end with an element-set name
            out[(int(parts[0]), int(parts[1]))] = tuple(float(x) for x in parts[2:8])
    return out


def read_buckling_factors(dat: Path) -> list[float]:
    """Read the buckling factors, in mode order, from a CalculiX ``.dat`` file."""
    out = []
    reading = False
    for line in dat.read_text().splitlines():
        if "B U C K L I N G" in line:
            reading = True
            continue
        parts = line.split()
        if reading and len(parts) == 2 and parts[0].isdigit():
            out.append(float(parts[1]))
        elif reading and out:
            break
    return out


def run(model: ShellModel, workdir: Path, name: str = "shell", buckling_modes: int = 0,
        ccx: str | None = None) -> ShellResult:
    """Write the deck, run ccx in ``workdir`` and read the results.

    Args:
        model: The shell model.
        workdir: Folder for the deck and the CalculiX output.
        name: Job name.
        buckling_modes: Number of buckling factors wanted; 0 for a static step.
        ccx: Path of the executable; found with ``find_ccx`` if None.

    Returns:
        Displacements, stresses and buckling factors.

    Raises:
        FileNotFoundError: If CalculiX is not installed.
    """
    ccx = ccx or find_ccx()
    if ccx is None:
        raise FileNotFoundError("CalculiX (ccx) not found on PATH")
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / f"{name}.inp").write_text(deck(model, buckling_modes))
    subprocess.run([ccx, name], cwd=workdir, capture_output=True, check=True,
                   timeout=CCX_TIMEOUT_S)
    dat = workdir / f"{name}.dat"
    return ShellResult(read_displacements(dat), read_stresses(dat), read_buckling_factors(dat))


def load_benchmarks(path: Path = BENCHMARKS_CSV) -> dict[str, dict[str, float]]:
    """Read validation/benchmarks.csv as {problem: {quantity: value}}."""
    out: dict[str, dict[str, float]] = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            out.setdefault(row["problem"], {})[row["quantity"]] = float(row["value"])
    return out


def scordelis_lo(p: dict[str, float], n: int) -> tuple[ShellModel, int]:
    """Build the whole Scordelis-Lo roof (Fig. 8), 2n x 2n elements.

    The cylinder axis is y, as in the figure. Curved edges: ux = uz = 0. The
    roof then needs one more support, against sliding along y: uy = 0 at the
    centre, which carries nothing because the load is symmetric.

    Args:
        p: The ``scordelis_lo`` values of ``load_benchmarks``.
        n: Elements per side of the shaded quarter.

    Returns:
        The model, and the node at the midpoint of a free edge.
    """
    r, half_angle = p["radius"], math.radians(p["half_angle"])

    def surface(u: float, v: float) -> tuple[float, float, float]:
        a = (2.0 * v - 1.0) * half_angle
        return r * math.sin(a), (u - 0.5) * p["length"], r * math.cos(a)

    nodes, elements, grid = mapped_mesh(surface, 2 * n, 2 * n)
    supports = [(grid[(2 * n, 2 * n)], 2, 2)]
    for (i, _), node in grid.items():
        if i in (0, 4 * n):
            supports += [(node, 1, 1), (node, 3, 3)]
    density = p["area_load"] / (p["thickness"] * LOAD_GRAVITY)
    model = ShellModel(nodes, elements, p["thickness"], p["e"], p["nu"], density, supports,
                       gravity=(LOAD_GRAVITY, 0.0, 0.0, -1.0))
    return model, grid[(2 * n, 4 * n)]


def pinched_hemisphere(p: dict[str, float], n: int, force: float) -> tuple[ShellModel, int]:
    """Build the whole spherical shell (Fig. 9), n x 4n elements.

    u runs from the hole to the equator and v round the axis. Four forces
    alternate in sign on the equator, outward on the X axis. Both edges are free.
    Fig. 9 prints F = 2.0 (on quadrant). That is the force at each point of the
    whole shell [J]: it gives the paper's 0.094, and half of it on each of the
    two quadrants that share a point is what a symmetric model would carry.
    The supports only stop rigid movement. Each lies on a symmetry plane or is
    matched by its mirror images, so each carries nothing [J].

    Args:
        p: The ``hemisphere`` values of ``load_benchmarks``.
        n: Elements per side of one quadrant.
        force: Force at each of the four points of the whole shell.

    Returns:
        The model, and the node under the force at +X.
    """
    r, hole = p["radius"], math.radians(p["hole_angle"])

    def surface(u: float, v: float) -> tuple[float, float, float]:
        polar = hole + u * (math.pi / 2.0 - hole)
        azimuth = v * 2.0 * math.pi
        return (r * math.sin(polar) * math.cos(azimuth), r * math.sin(polar) * math.sin(azimuth),
                r * math.cos(polar))

    nodes, elements, grid = mapped_mesh(surface, n, 4 * n, closed_v=True)
    east, north, west, south = (grid[(2 * n, k * 2 * n)] for k in range(4))
    supports = [(east, 2, 2), (west, 2, 2), (north, 1, 1), (south, 1, 1)]
    supports += [(grid[(2 * n, (2 * k + 1) * n)], 3, 3) for k in range(4)]
    forces = [(east, 1, force), (north, 2, -force), (west, 1, -force), (south, 2, force)]
    return ShellModel(nodes, elements, p["thickness"], p["e"], p["nu"], 0.0, supports, forces), east


def benchmark_row(problem: str, n: int, workdir: Path, p: dict[str, float]) -> dict[str, float]:
    """Run one benchmark at one mesh density.

    Args:
        problem: "scordelis_lo" or "hemisphere".
        n: Elements per side.
        workdir: Folder for the CalculiX files.
        p: The problem's values of ``load_benchmarks``.

    Returns:
        Elements per side, displacement and normalised displacement.
    """
    if problem == "scordelis_lo":
        model, node = scordelis_lo(p, n)
        u = -run(model, workdir, f"{problem}_{n}").displacements[node][2]
    else:
        model, node = pinched_hemisphere(p, n, p["point_force"])
        u = run(model, workdir, f"{problem}_{n}").displacements[node][0]
    return {"n": n, "u": u, "normalised": u / p["reference_displacement"]}


def write_convergence(rows: list[dict], path: Path = CONVERGENCE_CSV) -> None:
    """Save the convergence rows, one line per problem and mesh."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        out = csv.writer(f)
        out.writerow(["problem [text]", "elements_per_side [-]", "displacement [consistent]",
                      "reference [consistent]", "normalised [-]"])
        for r in rows:
            out.writerow([r["problem"], r["n"], f"{r['u']:.6f}", r["reference"],
                          f"{r['normalised']:.4f}"])


def plot_convergence(rows: list[dict], path: Path = CONVERGENCE_PNG) -> None:
    """Plot normalised displacement against elements per side, with the 2 % band."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = {"scordelis_lo": "Scordelis-Lo roof", "hemisphere": "Pinched hemisphere"}
    fig, ax = plt.subplots(figsize=(5.5, 3.8))
    ax.axhspan(1.0 - TOLERANCE, 1.0 + TOLERANCE, color="0.9", label="Within 2 %")
    ax.axhline(1.0, color="0.4", lw=0.8)
    for (problem, label), marker in zip(labels.items(), ("o", "s")):
        part = [r for r in rows if r["problem"] == problem]
        ax.plot([r["n"] for r in part], [r["normalised"] for r in part], marker=marker,
                label=label)
    ax.set_xscale("log", base=2)
    ax.set_xticks(MESH_ELEMENTS, [str(n) for n in MESH_ELEMENTS])
    ax.minorticks_off()
    ax.set_xlabel("Elements per side of the patch")
    ax.set_ylabel("Normalised displacement [-]")
    ax.legend(frameon=False)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    import tempfile

    data = load_benchmarks()
    table = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, values in data.items():
            for n in MESH_ELEMENTS:
                row = benchmark_row(name, n, Path(tmp), values)
                table.append({"problem": name, "reference": values["reference_displacement"],
                              **row})
                print(name, n, f"{row['u']:.6f}", f"{row['normalised']:.4f}")
    write_convergence(table)
    plot_convergence(table)
