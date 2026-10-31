"""Force density form-finding of a vault over a rectangular bay.

File: src/shellbench/formfind.py

What this module does
---------------------
Playbook Day 23. The bay is Lx by Ly in plan, supported on all four
edges, under a uniform load w per unit plan area. A grid of nx by ny
cells is laid over the plan. Every grid line between two neighbouring
nodes is a branch with a force density q (force divided by length).
Plan positions stay fixed; only the heights z are unknown.

For a free node i, vertical equilibrium is

    sum over branches ij of q_ij (z_i - z_j) = P_i,

with P_i = w times the node's tributary plan area. This is one linear
system, D z = P. The branch force densities are set from membrane
forces per unit width: n_x in x and n_y = ``qy_ratio`` times n_x in y,
so an x-branch has q = n_x dy / dx and a y-branch q = n_y dx / dy. With
these, the result does not depend on the grid spacing. Because z scales
with 1/n_x, the module solves once with n_x = 1 N/m and then picks n_x
so that the highest node sits at the target rise f.

Why the result is a parabola for a long strip: when the y-branches
carry nothing (or the bay is long, so mid-bay y-curvature vanishes),
each x-line is a string under equal nodal loads, and the force density
equation is the finite-difference form of H z'' = -w. Its exact
solution at the nodes is z = 4 f x (L - x) / L^2, and the horizontal
force per unit width is H = w L^2 / (8 f).

The mesh for shell elements is written as gmsh MSH 2.2 text (4-node
quadrilaterals), so no gmsh install is needed to create it; gmsh and
CalculiX can read it.

Units: N, m, Pa (N/m^2 for w).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class Vault:
    """Result of a form-finding run.

    Attributes:
        x, y, z: Node coordinates [m], arrays of shape (ny + 1, nx + 1).
        q_x: Force density of the x-branches [N/m].
        q_y: Force density of the y-branches [N/m].
        dx, dy: Grid spacing [m].
        w: Load per unit plan area [N/m^2].
    """

    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    q_x: float
    q_y: float
    dx: float
    dy: float
    w: float

    def thrust_per_width(self) -> float:
        """Horizontal force per unit width carried by an x-line [N/m].

        The force in an x-branch is q times its length; its horizontal
        part is q times dx, the same in every branch of the line. Each
        x-line stands for a strip dy wide.
        """
        return self.q_x * self.dx / self.dy

    def vertical_reactions(self) -> float:
        """Sum of the vertical support reactions [N].

        Each branch from a free node to a support node pushes down on the
        support with q times the height difference.
        """
        z, total = self.z, 0.0
        ny, nx = z.shape[0] - 1, z.shape[1] - 1
        total += self.q_x * (z[1:ny, 1].sum() + z[1:ny, nx - 1].sum())
        total += self.q_y * (z[1, 1:nx].sum() + z[ny - 1, 1:nx].sum())
        return total


def form_find(lx: float, ly: float, rise: float, w: float,
              nx: int = 40, ny: int = 40, qy_ratio: float = 1.0) -> Vault:
    """Find the vault shape over a bay supported on four edges.

    Args:
        lx, ly: Plan dimensions [m].
        rise: Target height of the highest node above the supports [m].
        w: Uniform load per unit plan area [N/m^2].
        nx, ny: Number of grid cells in x and y.
        qy_ratio: Membrane force per unit width in y over that in x [-].
            0 makes every x-line an independent arch.

    Returns:
        The vault, with q chosen so that max(z) equals ``rise``.
    """
    if min(lx, ly, rise, w) <= 0 or nx < 2 or ny < 2 or qy_ratio < 0:
        raise ValueError("lx, ly, rise, w must be positive; nx, ny >= 2; qy_ratio >= 0")
    dx, dy = lx / nx, ly / ny
    xs, ys = np.linspace(0.0, lx, nx + 1), np.linspace(0.0, ly, ny + 1)
    x, y = np.meshgrid(xs, ys)
    nfx, nfy = nx - 1, ny - 1  # free nodes; all edge nodes are supports at z = 0
    n = nfx * nfy
    idx = lambda i, j: (j - 1) * nfx + (i - 1)  # noqa: E731
    # Branch force densities for a membrane force of 1 N/m in x: each
    # x-branch stands for a strip dy wide over a length dx, so q = dy/dx.
    cx, cy = dy / dx, qy_ratio * dx / dy
    d = np.zeros((n, n))
    for j in range(1, ny):
        for i in range(1, nx):
            k = idx(i, j)
            for di, dj, q in ((1, 0, cx), (-1, 0, cx), (0, 1, cy), (0, -1, cy)):
                if q == 0:
                    continue
                d[k, k] += q
                ii, jj = i + di, j + dj
                if 0 < ii < nx and 0 < jj < ny:
                    d[k, idx(ii, jj)] -= q
    p = np.full(n, w * dx * dy)
    z_free = np.linalg.solve(d, p)  # heights for a membrane force of 1 N/m
    scale = z_free.max() / rise  # membrane force n_x [N/m] for the target rise
    z = np.zeros_like(x)
    z[1:ny, 1:nx] = (z_free / scale).reshape(nfy, nfx)
    return Vault(x, y, z, scale * cx, scale * cy, dx, dy, w)


def write_msh(vault: Vault, path: Path) -> Path:
    """Write the vault as a gmsh MSH 2.2 ASCII mesh of 4-node quadrilaterals.

    Args:
        vault: Result of ``form_find``.
        path: File to write.

    Returns:
        The path written.
    """
    ny1, nx1 = vault.z.shape
    lines = ["$MeshFormat", "2.2 0 8", "$EndMeshFormat", "$Nodes", str(nx1 * ny1)]
    for j in range(ny1):
        for i in range(nx1):
            lines.append(f"{j * nx1 + i + 1} {vault.x[j, i]:.6f} {vault.y[j, i]:.6f} {vault.z[j, i]:.6f}")
    quads = [(j * nx1 + i + 1, j * nx1 + i + 2, (j + 1) * nx1 + i + 2, (j + 1) * nx1 + i + 1)
             for j in range(ny1 - 1) for i in range(nx1 - 1)]
    lines += ["$EndNodes", "$Elements", str(len(quads))]
    # element type 3 = 4-node quadrangle; 2 tags: physical 1, elementary 1
    lines += [f"{e + 1} 3 2 1 1 {a} {b} {c} {d}" for e, (a, b, c, d) in enumerate(quads)]
    lines.append("$EndElements")
    path.write_text("\n".join(lines) + "\n")
    return path


def parabola(x: np.ndarray, span: float, rise: float) -> np.ndarray:
    """Funicular of a uniform load: z = 4 f x (L - x) / L^2 [m]."""
    return 4.0 * rise * x * (span - x) / span**2


def parabolic_thrust(w: float, span: float, rise: float) -> float:
    """Horizontal thrust per unit width of a parabolic arch, H = w L^2 / (8 f) [N/m]."""
    return w * span**2 / (8.0 * rise)
