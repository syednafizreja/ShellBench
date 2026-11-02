"""Shell benchmarks and CalculiX read-back (Playbook Day 24).

File: tests/test_benchmarks.py

The Scordelis-Lo roof and the pinched hemisphere run from
validation/benchmarks.csv at the three mesh densities of shellfe.MESH_ELEMENTS.
The finest mesh must be within 2 % of the reference. A flat strip checks the
stress and buckling read-back against closed forms; its values are chosen for
the test, not taken from a source.
"""

from __future__ import annotations

import math

import pytest

from shellbench import calculix as cx
from shellbench import shellfe as sf

needs_ccx = pytest.mark.skipif(cx.find_ccx() is None, reason="CalculiX not installed")

# Flat strip, chosen for the test, SI units.
STRIP_LENGTH_M = 1.0
STRIP_WIDTH_M = 0.1
STRIP_THICKNESS_M = 0.01
STRIP_E_PA = 30e9
STRIP_ELEMENTS = (20, 2)
STRIP_FORCE_N = 1000.0


def strip() -> tuple[sf.ShellModel, dict[tuple[int, int], int]]:
    """Flat strip along x, pinned at both ends, with no end force yet."""
    nx, ny = STRIP_ELEMENTS
    nodes, elements, grid = sf.mapped_mesh(
        lambda u, v: (u * STRIP_LENGTH_M, v * STRIP_WIDTH_M, 0.0), nx, ny)
    supports = [(grid[(0, 0)], 2, 2)]
    for (i, j), node in grid.items():
        if i == 0:
            supports.append((node, 1, 1))
        if i in (0, 2 * nx):
            supports.append((node, 3, 3))
    model = sf.ShellModel(nodes, elements, STRIP_THICKNESS_M, STRIP_E_PA, 0.0, 0.0, supports)
    return model, grid


def end_forces(grid: dict[tuple[int, int], int], total_n: float) -> list[tuple[int, int, float]]:
    """Consistent nodal forces of a quadratic edge at the free end: 1/6, 4/6, 1/6."""
    nx, ny = STRIP_ELEMENTS
    weights = [1.0] + [w for _ in range(ny) for w in (4.0, 2.0)]
    weights[-1] = 1.0
    return [(grid[(2 * nx, j)], 1, total_n * w / sum(weights)) for j, w in enumerate(weights)]


def test_benchmark_values_carry_a_page():
    """Every problem has its reference answer, and the file has a page on each line."""
    data = sf.load_benchmarks()
    assert set(data) == {"scordelis_lo", "hemisphere"}
    assert data["scordelis_lo"]["reference_displacement"] == 0.3024
    assert data["hemisphere"]["reference_displacement"] == 0.0940
    lines = sf.BENCHMARKS_CSV.read_text(encoding="utf-8").splitlines()[1:]
    assert all(line.split(",")[4].isdigit() for line in lines)


def test_closed_mesh_shares_the_seam():
    """Round a ring the last element uses the first column of nodes."""
    nodes, elements, grid = sf.mapped_mesh(
        lambda u, v: (math.cos(v * 2 * math.pi), math.sin(v * 2 * math.pi), u), 1, 4, closed_v=True)
    assert len(elements) == 4
    assert len(nodes) == 4 * 3 + 4 * 2  # j even: 3 nodes, j odd: 2 nodes; 8 columns in all
    assert elements[-1][2] == grid[(2, 0)]


def test_roof_area_load_matches_its_resultant():
    """Density x thickness x gravity is the area load of Fig. 8."""
    p = sf.load_benchmarks()["scordelis_lo"]
    model, _ = sf.scordelis_lo(p, 2)
    assert model.density * model.thickness * model.gravity[0] == pytest.approx(p["area_load"])


@needs_ccx
@pytest.mark.parametrize("problem", ["scordelis_lo", "hemisphere"])
def test_finest_mesh_is_within_tolerance(problem, tmp_path):
    """Three densities; the finest within 2 %, and the last two within 1 % of each other."""
    p = sf.load_benchmarks()[problem]
    rows = [sf.benchmark_row(problem, n, tmp_path, p) for n in sf.MESH_ELEMENTS]
    print(problem, [round(r["normalised"], 4) for r in rows])
    assert abs(rows[-1]["normalised"] - 1.0) <= sf.TOLERANCE
    assert abs(rows[-1]["normalised"] / rows[-2]["normalised"] - 1.0) <= 0.01


@needs_ccx
def test_stress_read_back_is_force_over_area(tmp_path):
    """A strip in tension has sxx = F / (b t) at every integration point."""
    model, grid = strip()
    model.forces = end_forces(grid, STRIP_FORCE_N)
    result = sf.run(model, tmp_path, "tension")
    assert len(result.stresses) > 0
    expected = STRIP_FORCE_N / (STRIP_WIDTH_M * STRIP_THICKNESS_M)
    for s in result.stresses.values():
        assert s[0] == pytest.approx(expected, rel=1e-3)
    assert result.buckling_factors == []


@needs_ccx
def test_buckling_read_back_is_euler(tmp_path):
    """A pinned strip under an end force buckles at pi^2 E I / L^2, within 2 %."""
    model, grid = strip()
    model.forces = end_forces(grid, -STRIP_FORCE_N)
    result = sf.run(model, tmp_path, "buckle", buckling_modes=2)
    i = STRIP_WIDTH_M * STRIP_THICKNESS_M ** 3 / 12
    euler = math.pi ** 2 * STRIP_E_PA * i / STRIP_LENGTH_M ** 2
    assert len(result.buckling_factors) == 2
    assert result.buckling_factors[0] * STRIP_FORCE_N == pytest.approx(euler, rel=0.02)
