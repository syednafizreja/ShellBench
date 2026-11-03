"""Size one shell-floor panel at the thesis span: thickness, tie, buckling, quantities.

File: src/shellbench/panel.py

What this module does
---------------------
Playbook Day 25 (floor-r3). One parabolic barrel vault of layout A spans
L = 6.6 m between two frame beams (docs/floor_concept.md, sections 2-4 and 8).
The model is one tie bay: a strip of vault of width s = 1.2 m with one tie.
CalculiX (``shellfe``, API unchanged) gives the thrust; statics gives the
moment; a section check gives the thickness.

How the tie force is found
--------------------------
The ``shellfe`` deck prints displacements only, so reactions are not read.
Instead, springing A is pinned (ux = uz = 0) and springing B is on a roller
(uz = 0). Each load case gives the spread delta_0 of B; a unit inward force
on B gives the flexibility c_1. Compatibility then gives the tie force T:

- rigid tie: T = delta_0 / c_1 (this is the value checked against the
  closed form w L^2 / (8 f), the Day 25 Done-when);
- elastic tie of area A: T = delta_0 / (c_1 + L / (E_s A)).

The spread is the work-conjugate mean of ux along edge B, using the same
consistent weights as the unit edge load, so it is exact for the linear model.

How the moment is found
-----------------------
For vertical loads on an arch pinned at both springings the bending moment is
M(x) = M_0(x) - H z(x) and the axial force is N(x) = H cos(theta) + V_0(x)
sin(theta), where M_0 and V_0 belong to a simply supported beam with the same
plan load. H comes from CalculiX, so this needs no stress output [J].

Loads
-----
Self-weight per m^2 of shell surface (CalculiX gravity). Fill, finishes and
live load per m^2 of plan (consistent nodal loads). The fill is taken as a
uniform plan load of density x g x f / 3, as in floor_concept section 5; its
true depth (f - z) is a refinement left for Day 26 [J].

Section check
-------------
One mesh layer at mid-depth (floor_concept 4.2). Rectangular stress block
alpha_1 f_c over depth x, with C = N + A_s f_y when the mesh yields
(x <= xi_b d, d = t / 2), else C = N and the mesh is ignored. Moment capacity
about mid-depth: M_R = C (t - x) / 2. This is mechanics, not the GB 50010
eccentric-compression procedure; the additional eccentricity and slenderness
rules of that code are not applied (author item) [J].

Units: N, m, Pa throughout.
"""

from __future__ import annotations

import csv
import math
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from shellbench.carbon import STEEL_DENSITY_KG_M3
from shellbench.combinations import GAMMA_G, GAMMA_Q
from shellbench.formfind import parabola, parabolic_thrust
from shellbench.generator import BAR_DIAMETERS_MM
from shellbench.shellfe import LOAD_GRAVITY, ShellModel, mapped_mesh, run

ROOT = Path(__file__).resolve().parents[2]
RESULTS_CSV = ROOT / "results" / "panel_day25.csv"

# Geometry
SPAN_M: float = 6.6  # spec G4, layout A (floor_concept decision 2)
RISE_RATIO: float = 1.0 / 15.0  # [J] floor_concept section 7 and decision 4
TIE_SPACING_M: float = 1.2  # [J] floor_concept 4.1; the modelled strip width
TRIAL_THICKNESSES_M: tuple[float, ...] = (0.050, 0.060, 0.070, 0.080)  # floor_concept 4.1 range

# Materials
E_CONCRETE_PA: float = 3.25e10  # spec X4, C40
NU_CONCRETE: float = 0.2  # [J] no source in the repo yet (author item)
CONCRETE_N_M3: float = 25.0e3  # spec X7
FC_PA: float = 19.1e6  # spec X2
FT_PA: float = 1.71e6  # spec X3
FY_PA: float = 360.0e6  # spec X5, HRB400; GB 50010 Table 4.2.3-1
E_STEEL_PA: float = 2.0e11  # [J] no source in the repo yet (author item)
ALPHA_1: float = 1.0  # [J] stress-block factor for C40 (author item)
XI_B: float = 0.518  # [J] balanced depth ratio for HRB400 (author item)
MIN_STEEL_FLOOR: float = 0.0015  # GB 50010 Table 8.5.1 note 2 (floor_concept 4.2)
MIN_STEEL_FT_FACTOR: float = 45.0  # same note: 45 f_t / f_y, in per cent
COVER_M: float = 0.015  # GB 50010 Table 8.2.1, shells, category I (floor_concept 4.2)
MESH_BAR_M: float = 0.006  # [J] mesh bar diameter, for the cover check only

# Loads [Pa] or densities [kg/m^3]
G_ACCEL: float = 9.81  # [J] no source in the repo yet (author item)
FINISHES_PA: float = 1.05e3  # Th s4.1 via floor_concept section 5
LIVE_PA: float = 2.5e3  # spec L9, office floor
LEVELLING: dict[str, tuple[str, float]] = {
    # name: (kind, value); fill density [kg/m^3] or raised-floor mass [kg/m^2]
    "foamed_fill": ("fill", 800.0),  # Hawkins (2018) s4.3
    "recycled_fill": ("fill", 1400.0),  # Hawkins et al. (2020) Table 2
    "raised_floor": ("mass", 29.0),  # Oval et al. (2023) Table 6
}

# Model
ELEMENTS_ALONG_SPAN: int = 16  # [J]
ELEMENTS_ACROSS: int = 4  # [J]
STATICS_POINTS: int = 801
UNIT_FORCE_N: float = 1.0e3
BUCKLING_MODES: int = 2
DONE_WHEN_TOLERANCE: float = 0.10  # Playbook Day 25: tie force within 10 % of closed form


@dataclass
class PanelRow:
    """One thickness and levelling option, all checks.

    Attributes:
        thickness_m: Shell thickness.
        levelling: Key of ``LEVELLING``.
        prestressed: Tie tensioned against the dead-load spread (see ``size_row``).
        w_uls_pa: Total ULS load per m^2 of plan, as applied in the model.
        h_closed_n_m: w L^2 / (8 f).
        h_rigid_n_m: Thrust per metre from CalculiX with a rigid tie.
        h_ratio: h_rigid / h_closed.
        tie_bar_mm: Tie bar diameter: the smallest that carries the rigid-tie
            force and is stiff enough for the shell to pass (largest tried if none).
        h_elastic_n_m: Thrust per metre with that tie elastic.
        buckling_factor: First linear buckling factor under the ULS load,
            rigid tie, no imperfection knock-down [J].
        membrane_stress_pa: Largest N / t under the uniform ULS load.
        util_uniform: M / M_R, uniform ULS load, elastic tie.
        util_pattern: M / M_R, dead load plus live load on half the span.
        concrete_m3_m2: Shell concrete per m^2 of floor.
        mesh_kg_m2: Mesh steel per m^2 of floor, both directions.
        tie_kg_m2: Tie steel per m^2 of floor.
        passes: All checks pass.
    """

    thickness_m: float
    levelling: str
    prestressed: bool
    w_uls_pa: float
    h_closed_n_m: float
    h_rigid_n_m: float
    h_ratio: float
    tie_bar_mm: int
    h_elastic_n_m: float
    buckling_factor: float
    membrane_stress_pa: float
    util_uniform: float
    util_pattern: float
    concrete_m3_m2: float
    mesh_kg_m2: float
    tie_kg_m2: float
    passes: bool


def rise_m() -> float:
    """Rise f of the vault [m]."""
    return RISE_RATIO * SPAN_M


def slope(x: np.ndarray) -> np.ndarray:
    """dz/dx of the parabola z = 4 f x (L - x) / L^2."""
    return 4.0 * rise_m() * (SPAN_M - 2.0 * x) / SPAN_M**2


def arc_factor() -> float:
    """Arc length of the vault divided by its span."""
    x = np.linspace(0.0, SPAN_M, STATICS_POINTS)
    return float(np.trapezoid(np.sqrt(1.0 + slope(x) ** 2), x) / SPAN_M)


def levelling_pa(name: str) -> float:
    """Plan load of the levelling option [Pa]: fill to the crown or raised floor."""
    kind, value = LEVELLING[name]
    return value * G_ACCEL * (rise_m() / 3.0 if kind == "fill" else 1.0)


def min_steel_ratio() -> float:
    """Minimum mesh ratio, max(0.15 %, 45 f_t / f_y %) (floor_concept 4.2)."""
    return max(MIN_STEEL_FLOOR, MIN_STEEL_FT_FACTOR * FT_PA / FY_PA / 100.0)


def bar_area_m2(d_mm: int) -> float:
    """Area of one bar [m^2]."""
    return math.pi * (d_mm * 1.0e-3) ** 2 / 4.0


def tie_bar(force_n: float) -> int | None:
    """Smallest bar of ``BAR_DIAMETERS_MM`` with A f_y >= force; None if none is enough."""
    for d in BAR_DIAMETERS_MM:
        if bar_area_m2(d) * FY_PA >= force_n:
            return d
    return None


# --- CalculiX model -------------------------------------------------------

def strip(thickness: float, rigid_tie: bool):
    """Mesh one tie bay of the vault and set its supports.

    Args:
        thickness: Shell thickness [m].
        rigid_tie: True pins both springings; False puts B on a roller.

    Returns:
        The model (no loads yet) and the mesh grid.
    """
    f = rise_m()

    def surface(u: float, v: float) -> tuple[float, float, float]:
        """Point of the vault: u along the span, v across the strip."""
        x = u * SPAN_M
        return x, v * TIE_SPACING_M, float(parabola(np.array(x), SPAN_M, f))

    nu, nv = ELEMENTS_ALONG_SPAN, ELEMENTS_ACROSS
    nodes, elements, grid = mapped_mesh(surface, nu, nv)
    supports = []
    for (i, j), node in grid.items():
        if i == 0 or (i == 2 * nu and rigid_tie):
            supports.append((node, 1, 1))
        if i in (0, 2 * nu):
            supports.append((node, 3, 3))
        if j in (0, 2 * nv):  # strip continues along the vault: no uy [J]
            supports.append((node, 2, 2))
    model = ShellModel(nodes, elements, thickness, E_CONCRETE_PA, NU_CONCRETE)
    model.supports = supports
    return model, grid


def plan_loads(model: ShellModel, pressure_pa: float, x_max: float) -> list[tuple[int, int, float]]:
    """Consistent nodal forces of a downward plan pressure on elements with centre x < x_max.

    For an 8-node element under uniform pressure the corner nodes take -1/12
    and the midside nodes 1/3 of the element load.
    """
    dx = SPAN_M / ELEMENTS_ALONG_SPAN
    dy = TIE_SPACING_M / ELEMENTS_ACROSS
    out: dict[int, float] = {}
    for el in model.elements:
        xc = sum(model.nodes[n][0] for n in el[:4]) / 4.0
        if xc >= x_max:
            continue
        load = pressure_pa * dx * dy
        for k, n in enumerate(el):
            out[n] = out.get(n, 0.0) + load * (-1.0 / 12.0 if k < 4 else 1.0 / 3.0)
    return [(n, 3, -p) for n, p in out.items()]


def edge_weights(grid: dict[tuple[int, int], int]) -> dict[int, float]:
    """Consistent weights (sum 1) of the nodes on springing B for a uniform edge load."""
    nu, nv = ELEMENTS_ALONG_SPAN, ELEMENTS_ACROSS
    w: dict[int, float] = {}
    for jj in range(nv):
        for dj, share in ((0, 1.0 / 6.0), (1, 2.0 / 3.0), (2, 1.0 / 6.0)):
            n = grid[(2 * nu, 2 * jj + dj)]
            w[n] = w.get(n, 0.0) + share / nv
    return w


def spread(displacements: dict[int, tuple[float, float, float]], weights: dict[int, float]) -> float:
    """Work-conjugate outward movement of springing B [m]."""
    return sum(wt * displacements[n][0] for n, wt in weights.items())


@dataclass
class Flexibility:
    """Spreads of springing B from the four unit cases of one thickness [m]."""

    self_weight: float  # concrete self-weight, unfactored
    plan_full: float  # 1 Pa on the whole plan
    plan_half: float  # 1 Pa on the plan for x < L/2
    unit_force: float  # inward movement per 1 N of total tie force [m/N]


def flexibility(thickness: float, workdir: Path) -> Flexibility:
    """Run the four linear cases with springing B on a roller."""
    out = []
    for case in ("self", "full", "half", "unit"):
        model, grid = strip(thickness, rigid_tie=False)
        w = edge_weights(grid)
        if case == "self":
            model.density = CONCRETE_N_M3 / LOAD_GRAVITY
            model.gravity = (LOAD_GRAVITY, 0.0, 0.0, -1.0)
        elif case in ("full", "half"):
            model.forces = plan_loads(model, 1.0, SPAN_M if case == "full" else SPAN_M / 2.0)
        else:
            model.forces = [(n, 1, -UNIT_FORCE_N * wt) for n, wt in w.items()]
        res = run(model, workdir / f"t{thickness * 1e3:.0f}_{case}", name=case)
        out.append(spread(res.displacements, w))
    return Flexibility(out[0], out[1], out[2], -out[3] / UNIT_FORCE_N)


def buckling_factor(thickness: float, sd_pa: float, workdir: Path, tag: str) -> float:
    """First linear buckling factor under the uniform ULS load, rigid tie."""
    model, _ = strip(thickness, rigid_tie=True)
    model.density = GAMMA_G * CONCRETE_N_M3 / LOAD_GRAVITY
    model.gravity = (LOAD_GRAVITY, 0.0, 0.0, -1.0)
    model.forces = plan_loads(model, GAMMA_G * sd_pa + GAMMA_Q * LIVE_PA, SPAN_M)
    res = run(model, workdir / f"t{thickness * 1e3:.0f}_buckle_{tag}", name="buckle",
              buckling_modes=BUCKLING_MODES)
    return res.buckling_factors[0]


# --- statics and section ---------------------------------------------------

def arch_forces(p_plan: np.ndarray, h: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Moment and axial force along a two-pinned parabolic arch under vertical plan load.

    Args:
        p_plan: Plan load [N/m per m width] at ``STATICS_POINTS`` points from 0 to L.
        h: Horizontal thrust [N/m].

    Returns:
        x [m], M [N m/m] (positive sagging), N [N/m] (positive compression).
    """
    x = np.linspace(0.0, SPAN_M, STATICS_POINTS)
    moment_about_b = np.trapezoid(p_plan * (SPAN_M - x), x)
    r_a = moment_about_b / SPAN_M
    cum = np.concatenate(([0.0], np.cumsum((p_plan[1:] + p_plan[:-1]) / 2.0 * np.diff(x))))
    v0 = r_a - cum
    m0 = np.concatenate(([0.0], np.cumsum((v0[1:] + v0[:-1]) / 2.0 * np.diff(x))))
    theta = np.arctan(slope(x))
    z = parabola(x, SPAN_M, rise_m())
    return x, m0 - h * z, h * np.cos(theta) + v0 * np.sin(theta)


def moment_capacity(n: float, t: float, as_m2_m: float) -> float:
    """M_R of a 1 m strip with one mesh layer at mid-depth (see module note) [N m/m]."""
    c = n + as_m2_m * FY_PA
    x = c / (ALPHA_1 * FC_PA)
    if x > XI_B * t / 2.0:  # mesh does not yield: ignore it
        c = n
        x = c / (ALPHA_1 * FC_PA)
    return max(c * (t - x) / 2.0, 0.0)


def utilisation(p_plan: np.ndarray, h: float, t: float, as_m2_m: float) -> float:
    """Largest |M| / M_R along the arch."""
    _, m, n = arch_forces(p_plan, h)
    return float(max(abs(mi) / max(moment_capacity(ni, t, as_m2_m), 1e-9) for mi, ni in zip(m, n)))


# --- one panel -------------------------------------------------------------

def size_row(t: float, levelling: str, fl: Flexibility, buckle: float,
             prestressed: bool = False) -> PanelRow:
    """All checks for one thickness and levelling option, by superposition.

    Args:
        t: Shell thickness [m].
        levelling: Key of ``LEVELLING``.
        fl: Spreads of the four unit cases at this thickness.
        buckle: First buckling factor at this thickness and levelling.
        prestressed: True if the tie is tensioned (turnbuckle) until the
            springings do not spread under the dead load, so only the live
            load stretches it [J]; False for an unstressed bar.
    """
    sd = FINISHES_PA + levelling_pa(levelling)
    b = TIE_SPACING_M
    x = np.linspace(0.0, SPAN_M, STATICS_POINTS)
    self_plan = CONCRETE_N_M3 * t * np.sqrt(1.0 + slope(x) ** 2)  # per m^2 of plan
    k = arc_factor()
    w_uls = GAMMA_G * (CONCRETE_N_M3 * t * k + sd) + GAMMA_Q * LIVE_PA
    h_closed = parabolic_thrust(w_uls, SPAN_M, rise_m())

    d_dead = GAMMA_G * (fl.self_weight + sd * fl.plan_full)
    d_uniform = d_dead + GAMMA_Q * LIVE_PA * fl.plan_full
    d_pattern = d_dead + GAMMA_Q * LIVE_PA * fl.plan_half
    t_rigid = d_uniform / fl.unit_force
    d_fixed = d_dead if prestressed else 0.0  # spread the prestress takes out
    strength_bar = tie_bar(t_rigid)

    p_dead = GAMMA_G * (self_plan + sd)
    p_uniform = p_dead + GAMMA_Q * LIVE_PA
    p_pattern = p_dead + GAMMA_Q * LIVE_PA * (x < SPAN_M / 2.0)
    rho = min_steel_ratio()
    as_m = rho * t

    # Tie stretch lowers the thrust and adds sagging moment, so the bar is
    # stepped up from the strength size until the shell passes (stiffness).
    bar = None
    for d in (BAR_DIAMETERS_MM[BAR_DIAMETERS_MM.index(strength_bar):] if strength_bar else ()):
        c_tie = SPAN_M / (E_STEEL_PA * bar_area_m2(d))
        h_el_uniform = (d_fixed / fl.unit_force + (d_uniform - d_fixed) / (fl.unit_force + c_tie)) / b
        h_el_pattern = (d_fixed / fl.unit_force + (d_pattern - d_fixed) / (fl.unit_force + c_tie)) / b
        u_uni = utilisation(p_uniform, h_el_uniform, t, as_m)
        u_pat = utilisation(p_pattern, h_el_pattern, t, as_m)
        bar = d
        if max(u_uni, u_pat) <= 1.0:
            break
    a_tie = bar_area_m2(bar) if bar else float("nan")
    if not bar:
        h_el_uniform = u_uni = u_pat = float("nan")
    _, _, n_rigid = arch_forces(p_uniform, t_rigid / b)
    sigma = float(n_rigid.max()) / t
    h_rigid = t_rigid / b
    cover_ok = t >= 2.0 * COVER_M + MESH_BAR_M
    passes = bool(bar and cover_ok and max(u_uni, u_pat) <= 1.0 and sigma <= FC_PA
                  and buckle > 1.0 and abs(h_rigid / h_closed - 1.0) <= DONE_WHEN_TOLERANCE)
    return PanelRow(
        thickness_m=t, levelling=levelling, prestressed=prestressed, w_uls_pa=w_uls, h_closed_n_m=h_closed,
        h_rigid_n_m=h_rigid, h_ratio=h_rigid / h_closed, tie_bar_mm=bar or 0,
        h_elastic_n_m=h_el_uniform, buckling_factor=buckle, membrane_stress_pa=sigma,
        util_uniform=u_uni, util_pattern=u_pat, concrete_m3_m2=t * k,
        mesh_kg_m2=2.0 * rho * t * k * STEEL_DENSITY_KG_M3,
        tie_kg_m2=a_tie * STEEL_DENSITY_KG_M3 / b if bar else float("nan"), passes=passes)


def size_panel(workdir: Path, thicknesses: tuple[float, ...] = TRIAL_THICKNESSES_M,
               levellings: tuple[str, ...] = tuple(LEVELLING)) -> list[PanelRow]:
    """Run every trial thickness and levelling option.

    Args:
        workdir: Folder for the CalculiX runs.
        thicknesses: Shell thicknesses to try [m].
        levellings: Keys of ``LEVELLING``.

    Returns:
        One row per thickness and levelling option.
    """
    rows = []
    for t in thicknesses:
        fl = flexibility(t, workdir)
        for lev in levellings:
            sd = FINISHES_PA + levelling_pa(lev)
            buckle = buckling_factor(t, sd, workdir, lev)
            rows += [size_row(t, lev, fl, buckle, ps) for ps in (False, True)]
    return rows


def write_rows(rows: list[PanelRow], path: Path = RESULTS_CSV) -> None:
    """Write the rows to CSV, numbers to 4 significant figures."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(asdict(rows[0])))
        writer.writeheader()
        for r in rows:
            writer.writerow({k: (f"{v:.4g}" if isinstance(v, float) else v)
                             for k, v in asdict(r).items()})


def main() -> None:
    """Size the panel, write results/panel_day25.csv and print a summary."""
    with tempfile.TemporaryDirectory() as tmp:
        rows = size_panel(Path(tmp))
    write_rows(rows)
    for r in rows:
        print(f"t={r.thickness_m * 1e3:.0f} mm {r.levelling:14s} ps={r.prestressed:d} H/Hcf={r.h_ratio:.3f} "
              f"tie {r.tie_bar_mm} mm Hel/Hrig={r.h_elastic_n_m / r.h_rigid_n_m:.3f} "
              f"buckle={r.buckling_factor:.1f} u_uni={r.util_uniform:.2f} "
              f"u_pat={r.util_pattern:.2f} pass={r.passes}")


if __name__ == "__main__":
    main()
