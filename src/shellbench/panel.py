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
true depth (f - z) is an option from Day 26 (`true_fill`) [J].

Section check
-------------
One mesh layer at mid-depth (floor_concept 4.2). JGJ 22-2012 3.2.1 sends the
resistance of shell sections to GB 50010, so the check is GB 50010-2010 6.2.17
for a rectangular eccentric-compression section with A_s' = 0 and the bar at
mid-depth (h_0 = a = t / 2, so e = e_i). The additional eccentricity e_a of 6.2.5
is added, and the first-order moment is amplified by 1 / (1 - 1 / lambda) for
second-order effects (6.2.3 does not allow them to be ignored) [J]. Each clause
was read in a third-party copy of the code; confirm it in your own copy.

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
TRIAL_THICKNESSES_M: tuple[float, ...] = (0.050, 0.060, 0.070, 0.080, 0.090, 0.100, 0.120)  # floor_concept 4.1 range, widened [J]

# Materials
E_CONCRETE_PA: float = 3.25e10  # spec X4, C40
NU_CONCRETE: float = 0.2  # GB 50010-2010 4.1.5
CONCRETE_N_M3: float = 25.0e3  # spec X7
FC_PA: float = 19.1e6  # spec X2
FT_PA: float = 1.71e6  # spec X3
FY_PA: float = 360.0e6  # spec X5, HRB400; GB 50010 Table 4.2.3-1
FCU_K_PA: float = 40.0e6  # C40: cube strength grade, GB 50010-2010 4.1.1
E_STEEL_PA: float = 2.0e11  # GB 50010-2010 Table 4.2.5, HRB400
ALPHA_1: float = 1.0  # GB 50010-2010 6.2.6, grade not above C50
BETA_1: float = 0.8  # GB 50010-2010 6.2.6, grade not above C50
EPS_CU_MAX: float = 0.0033  # GB 50010-2010 6.2.1-5 and its cap
EPS_CU_SLOPE: float = 1.0e-5 / 1.0e6  # 6.2.1-5: (f_cu,k - 50 N/mm^2) x 10^-5, per Pa
EPS_CU_REF_PA: float = 50.0e6  # 6.2.1-5
EA_MIN_M: float = 0.020  # GB 50010-2010 6.2.5: e_a = max(20 mm, h / 30)
EA_DEPTH_DIVISOR: float = 30.0  # same clause
MIN_STEEL_FLOOR: float = 0.0015  # GB 50010 Table 8.5.1 note 2 (floor_concept 4.2)
MIN_STEEL_FT_FACTOR: float = 45.0  # same note: 45 f_t / f_y, in per cent
COVER_M: float = 0.015  # GB 50010 Table 8.2.1, shells, category I (floor_concept 4.2)
MESH_BAR_M: float = 0.006  # [J] mesh bar diameter, for the cover check only

# Loads [Pa] or densities [kg/m^3]
G_ACCEL: float = 9.81  # standard gravity 9.80665 (3rd CGPM 1901, Declaration 2), rounded [J]
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


@dataclass(frozen=True)
class Vault:
    """Geometry of one vault (Day 26). The defaults are the Day 25 panel.

    Attributes:
        span_m: Span L between the two frame beams [m].
        rise_ratio: f / L [-].
    """

    span_m: float = SPAN_M
    rise_ratio: float = RISE_RATIO


DAY25_VAULT = Vault()


def rise_m(vault: Vault | None = None) -> float:
    """Rise f of the vault [m]."""
    v = vault or DAY25_VAULT
    return v.rise_ratio * v.span_m


def slope(x: np.ndarray, vault: Vault | None = None) -> np.ndarray:
    """dz/dx of the parabola z = 4 f x (L - x) / L^2."""
    span = (vault or DAY25_VAULT).span_m
    return 4.0 * rise_m(vault) * (span - 2.0 * x) / span**2


def arc_factor(vault: Vault | None = None) -> float:
    """Arc length of the vault divided by its span."""
    span = (vault or DAY25_VAULT).span_m
    x = np.linspace(0.0, span, STATICS_POINTS)
    return float(np.trapezoid(np.sqrt(1.0 + slope(x, vault) ** 2), x) / span)


def is_fill(name: str) -> bool:
    """True if the levelling option is a fill (load depends on depth), not a raised floor."""
    return LEVELLING[name][0] == "fill"


def fill_unit_weight(name: str) -> float:
    """Unit weight of a fill [N/m^3]; 0 for a raised floor."""
    kind, value = LEVELLING[name]
    return value * G_ACCEL if kind == "fill" else 0.0


def levelling_pa(name: str, vault: Vault | None = None) -> float:
    """Mean plan load of the levelling option [Pa]: fill to the crown or raised floor.

    For a fill this is the mean depth f / 3 times the unit weight; the true
    depth f - z(x) is used when ``true_fill`` is set (Day 26).
    """
    kind, value = LEVELLING[name]
    return value * G_ACCEL * (rise_m(vault) / 3.0 if kind == "fill" else 1.0)


def fill_depth(x: np.ndarray, vault: Vault | None = None) -> np.ndarray:
    """Depth of fill from the shell up to the crown level, f - z(x) [m]."""
    span = (vault or DAY25_VAULT).span_m
    return rise_m(vault) - parabola(x, span, rise_m(vault))


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

def strip(thickness: float, rigid_tie: bool, vault: Vault | None = None):
    """Mesh one tie bay of the vault and set its supports.

    Args:
        thickness: Shell thickness [m].
        rigid_tie: True pins both springings; False puts B on a roller.
        vault: Geometry; the Day 25 vault if None.

    Returns:
        The model (no loads yet) and the mesh grid.
    """
    span = (vault or DAY25_VAULT).span_m
    f = rise_m(vault)

    def surface(u: float, v: float) -> tuple[float, float, float]:
        """Point of the vault: u along the span, v across the strip."""
        x = u * span
        return x, v * TIE_SPACING_M, float(parabola(np.array(x), span, f))

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


def plan_loads(model: ShellModel, pressure_pa: float, x_max: float, vault: Vault | None = None,
               shape=None) -> list[tuple[int, int, float]]:
    """Consistent nodal forces of a downward plan pressure on elements with centre x < x_max.

    For an 8-node element under uniform pressure the corner nodes take -1/12
    and the midside nodes 1/3 of the element load. With ``shape`` (a function
    of x), the pressure on each element is ``pressure_pa * shape(x_centre)``,
    a mid-point rule over the element [J].
    """
    span = (vault or DAY25_VAULT).span_m
    dx = span / ELEMENTS_ALONG_SPAN
    dy = TIE_SPACING_M / ELEMENTS_ACROSS
    out: dict[int, float] = {}
    for el in model.elements:
        xc = sum(model.nodes[n][0] for n in el[:4]) / 4.0
        if xc >= x_max:
            continue
        load = pressure_pa * dx * dy * (float(shape(np.array(xc))) if shape else 1.0)
        for k, n in enumerate(el):
            out[n] = out.get(n, 0.0) + load * (-1.0 / 12.0 if k < 4 else 1.0 / 3.0)
    if shape:  # ccx rejects number fields over 20 characters, e.g. 5.4931640624999995E-05
        return [(n, 3, -float(f"{p:.12g}")) for n, p in out.items()]
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
    """Spreads of springing B from the unit cases of one thickness [m]."""

    self_weight: float  # concrete self-weight, unfactored
    plan_full: float  # 1 Pa on the whole plan
    plan_half: float  # 1 Pa on the plan for x < L/2
    unit_force: float  # inward movement per 1 N of total tie force [m/N]
    plan_fill: float = float("nan")  # fill of unit weight 1 N/m^3 to the crown, depth f - z (Day 26)


def flexibility(thickness: float, workdir: Path, vault: Vault | None = None,
                fill_shape: bool = False) -> Flexibility:
    """Run the linear unit cases with springing B on a roller.

    Four cases always; with ``fill_shape`` a fifth, the true-depth fill case.
    """
    span = (vault or DAY25_VAULT).span_m
    cases = ("self", "full", "half", "unit") + (("fill",) if fill_shape else ())
    out = []
    for case in cases:
        model, grid = strip(thickness, rigid_tie=False, vault=vault)
        w = edge_weights(grid)
        if case == "self":
            model.density = CONCRETE_N_M3 / LOAD_GRAVITY
            model.gravity = (LOAD_GRAVITY, 0.0, 0.0, -1.0)
        elif case in ("full", "half"):
            model.forces = plan_loads(model, 1.0, span if case == "full" else span / 2.0, vault)
        elif case == "fill":
            model.forces = plan_loads(model, 1.0, span, vault, shape=lambda x: fill_depth(x, vault))
        else:
            model.forces = [(n, 1, -UNIT_FORCE_N * wt) for n, wt in w.items()]
        res = run(model, workdir / f"t{thickness * 1e3:.0f}_{case}", name=case)
        out.append(spread(res.displacements, w))
    return Flexibility(out[0], out[1], out[2], -out[3] / UNIT_FORCE_N,
                       out[4] if fill_shape else float("nan"))


def buckling_factor(thickness: float, sd_pa: float, workdir: Path, tag: str,
                    vault: Vault | None = None, fill_n_m3: float = 0.0) -> float:
    """First linear buckling factor under the uniform ULS load, rigid tie.

    ``sd_pa`` is the uniform superimposed dead load; ``fill_n_m3`` adds a fill
    of that unit weight at its true depth f - z (Day 26).
    """
    span = (vault or DAY25_VAULT).span_m
    model, _ = strip(thickness, rigid_tie=True, vault=vault)
    model.density = GAMMA_G * CONCRETE_N_M3 / LOAD_GRAVITY
    model.gravity = (LOAD_GRAVITY, 0.0, 0.0, -1.0)
    model.forces = plan_loads(model, GAMMA_G * sd_pa + GAMMA_Q * LIVE_PA, span, vault)
    if fill_n_m3:
        model.forces += plan_loads(model, GAMMA_G * fill_n_m3, span, vault,
                                   shape=lambda x: fill_depth(x, vault))
    res = run(model, workdir / f"t{thickness * 1e3:.0f}_buckle_{tag}", name="buckle",
              buckling_modes=BUCKLING_MODES)
    return res.buckling_factors[0]


# --- statics and section ---------------------------------------------------

def arch_forces(p_plan: np.ndarray, h: float, vault: Vault | None = None
                ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Moment and axial force along a two-pinned parabolic arch under vertical plan load.

    Args:
        p_plan: Plan load [N/m per m width] at ``STATICS_POINTS`` points from 0 to L.
        h: Horizontal thrust [N/m].
        vault: Geometry; the Day 25 vault if None.

    Returns:
        x [m], M [N m/m] (positive sagging), N [N/m] (positive compression).
    """
    span = (vault or DAY25_VAULT).span_m
    x = np.linspace(0.0, span, STATICS_POINTS)
    moment_about_b = np.trapezoid(p_plan * (span - x), x)
    r_a = moment_about_b / span
    cum = np.concatenate(([0.0], np.cumsum((p_plan[1:] + p_plan[:-1]) / 2.0 * np.diff(x))))
    v0 = r_a - cum
    m0 = np.concatenate(([0.0], np.cumsum((v0[1:] + v0[:-1]) / 2.0 * np.diff(x))))
    theta = np.arctan(slope(x, vault))
    z = parabola(x, span, rise_m(vault))
    return x, m0 - h * z, h * np.cos(theta) + v0 * np.sin(theta)


def xi_b() -> float:
    """Relative balanced depth, GB 50010-2010 formula 6.2.7-1 with eps_cu from 6.2.1-5."""
    eps_cu = min(EPS_CU_MAX, EPS_CU_MAX - (FCU_K_PA - EPS_CU_REF_PA) * EPS_CU_SLOPE)
    return BETA_1 / (1.0 + FY_PA / (E_STEEL_PA * eps_cu))


def additional_eccentricity(t: float) -> float:
    """e_a = max(20 mm, t / 30), GB 50010-2010 6.2.5 [m]."""
    return max(EA_MIN_M, t / EA_DEPTH_DIVISOR)


def moment_capacity(n: float, t: float, as_m2_m: float) -> float:
    """N e capacity of a 1 m strip with one mesh layer at mid-depth [N m/m].

    GB 50010-2010 6.2.17 with A_s' = 0 and the bar at mid-depth, so
    h_0 = a = t / 2 and e = e_i. Large eccentricity (x <= xi_b h_0): sigma_s = f_y,
    alpha_1 f_c x = N + f_y A_s (6.2.17-1), N e <= alpha_1 f_c x (h_0 - x / 2)
    (6.2.17-2). Otherwise the mesh is ignored (sigma_s A_s = 0) [J].
    """
    c = n + as_m2_m * FY_PA
    x = c / (ALPHA_1 * FC_PA)
    if x > xi_b() * t / 2.0:
        c = n
        x = c / (ALPHA_1 * FC_PA)
    return max(c * (t - x) / 2.0, 0.0)


def two_layer_cover_m() -> float:
    """Distance a = a' from a face to the inner bar of a two-direction mesh [m].

    Cover plus one outer bar plus half the inner bar (the inner direction
    governs) [J].
    """
    return COVER_M + 1.5 * MESH_BAR_M


def moment_capacity_two_layer(n: float, t: float, as_face_m2_m: float) -> float:
    """N e_i capacity of a 1 m strip with one mesh near each face, A_s = A_s' [N m/m].

    GB 50010-2010 6.2.17, symmetric steel (f_y = f_y'), so alpha_1 f_c x = N.
    - Large eccentricity, 2 a' <= x <= xi_b h_0 (6.2.17-2):
      N e <= alpha_1 f_c x (h_0 - x / 2) + f_y' A_s' (h_0 - a'), with e = e_i + t / 2 - a.
    - x < 2 a' (6.2.17 last paragraph, as 6.2.14): N e' <= f_y A_s (h_0 - a'),
      with e' = e_i - t / 2 + a'.
    - Small eccentricity (x > xi_b h_0): the steel is ignored, as in the one-layer
      check (conservative) [J].
    Returns the largest N e_i the section carries.
    """
    a = two_layer_cover_m()
    h0 = t - a
    x = n / (ALPHA_1 * FC_PA)
    if x > xi_b() * h0:
        return max(n * (t - x) / 2.0, 0.0)
    steel = FY_PA * as_face_m2_m * (h0 - a)
    if x >= 2.0 * a:
        return max(ALPHA_1 * FC_PA * x * (h0 - x / 2.0) + steel - n * (t / 2.0 - a), 0.0)
    return max(steel + n * (t / 2.0 - a), 0.0)


def utilisation(p_plan: np.ndarray, h: float, t: float, as_m2_m: float, buckle: float,
                vault: Vault | None = None, layers: int = 1) -> float:
    """Largest N e_i / capacity along the arch.

    e_i = e_0 + e_a (6.2.17-4, 6.2.5). e_0 = M_2 / N, where M_2 is the first-order
    moment times 1 / (1 - 1 / lambda), with lambda the FE buckling factor. GB 50010
    6.2.3 does not let second-order moments be ignored here (l_c / i is far above
    34 - 12 M_1 / M_2). The amplifier stands in for 6.2.4, which is written for
    straight members [J]. ``layers`` = 2 uses the two-layer capacity, with
    ``as_m2_m`` the steel of each face.
    """
    _, m, n = arch_forces(p_plan, h, vault)
    amp = 1.0 / (1.0 - 1.0 / buckle) if buckle > 1.0 else math.inf
    ea = additional_eccentricity(t)
    cap = moment_capacity if layers == 1 else moment_capacity_two_layer
    return float(max((abs(mi) * amp + ni * ea) / max(cap(ni, t, as_m2_m), 1e-9)
                     for mi, ni in zip(m, n)))


def cover_ok(t: float, layers: int = 1) -> bool:
    """Cover on both faces fits: one mesh at mid-depth, or one near each face."""
    if layers == 1:
        return t >= 2.0 * COVER_M + MESH_BAR_M
    return t >= 2.0 * (COVER_M + 2.0 * MESH_BAR_M)


# --- one panel -------------------------------------------------------------

def size_row(t: float, levelling: str, fl: Flexibility, buckle: float,
             prestressed: bool = False, vault: Vault | None = None,
             true_fill: bool = False, layers: int = 1) -> PanelRow:
    """All checks for one thickness and levelling option, by superposition.

    Args:
        t: Shell thickness [m].
        levelling: Key of ``LEVELLING``.
        fl: Spreads of the unit cases at this thickness.
        buckle: First buckling factor at this thickness and levelling.
        prestressed: True if the tie is tensioned (turnbuckle) until the
            springings do not spread under the dead load, so only the live
            load stretches it [J]; False for an unstressed bar.
        vault: Geometry; the Day 25 vault if None.
        true_fill: Fill at its true depth f - z (needs ``fl.plan_fill``);
            False keeps the Day 25 uniform fill f / 3 deep.
        layers: 1 mesh at mid-depth (Day 25) or 2, one near each face, each
            at the minimum ratio [J].

    The Day 25 Done-when (rigid-tie thrust within 10 % of w L^2 / (8 f)) is a
    pass condition only for uniform load; with ``true_fill`` the load is not
    uniform and h_ratio is reported against the uniform load of the same total.
    """
    span = (vault or DAY25_VAULT).span_m
    f = rise_m(vault)
    shaped = true_fill and is_fill(levelling)
    gamma_fill = fill_unit_weight(levelling) if shaped else 0.0
    sd = FINISHES_PA + (0.0 if shaped else levelling_pa(levelling, vault))
    b = TIE_SPACING_M
    x = np.linspace(0.0, span, STATICS_POINTS)
    self_plan = CONCRETE_N_M3 * t * np.sqrt(1.0 + slope(x, vault) ** 2)  # per m^2 of plan
    fill_plan = gamma_fill * fill_depth(x, vault)
    k = arc_factor(vault)
    w_uls = GAMMA_G * (CONCRETE_N_M3 * t * k + FINISHES_PA + levelling_pa(levelling, vault)) + GAMMA_Q * LIVE_PA
    h_closed = parabolic_thrust(w_uls, span, f)

    d_dead = GAMMA_G * (fl.self_weight + sd * fl.plan_full + (gamma_fill * fl.plan_fill if shaped else 0.0))
    d_uniform = d_dead + GAMMA_Q * LIVE_PA * fl.plan_full
    d_pattern = d_dead + GAMMA_Q * LIVE_PA * fl.plan_half
    t_rigid = d_uniform / fl.unit_force
    d_fixed = d_dead if prestressed else 0.0  # spread the prestress takes out
    strength_bar = tie_bar(t_rigid)

    p_dead = GAMMA_G * (self_plan + sd + fill_plan)
    p_uniform = p_dead + GAMMA_Q * LIVE_PA
    p_pattern = p_dead + GAMMA_Q * LIVE_PA * (x < span / 2.0)
    rho = min_steel_ratio()
    as_m = rho * t

    # Tie stretch lowers the thrust and adds sagging moment, so the bar is
    # stepped up from the strength size until the shell passes (stiffness).
    bar = None
    for d in (BAR_DIAMETERS_MM[BAR_DIAMETERS_MM.index(strength_bar):] if strength_bar else ()):
        c_tie = span / (E_STEEL_PA * bar_area_m2(d))
        h_el_uniform = (d_fixed / fl.unit_force + (d_uniform - d_fixed) / (fl.unit_force + c_tie)) / b
        h_el_pattern = (d_fixed / fl.unit_force + (d_pattern - d_fixed) / (fl.unit_force + c_tie)) / b
        u_uni = utilisation(p_uniform, h_el_uniform, t, as_m, buckle, vault, layers)
        u_pat = utilisation(p_pattern, h_el_pattern, t, as_m, buckle, vault, layers)
        bar = d
        if max(u_uni, u_pat) <= 1.0:
            break
    a_tie = bar_area_m2(bar) if bar else float("nan")
    if not bar:
        h_el_uniform = u_uni = u_pat = float("nan")
    _, _, n_rigid = arch_forces(p_uniform, t_rigid / b, vault)
    sigma = float(n_rigid.max()) / t
    h_rigid = t_rigid / b
    done_when_ok = shaped or abs(h_rigid / h_closed - 1.0) <= DONE_WHEN_TOLERANCE
    passes = bool(bar and cover_ok(t, layers) and max(u_uni, u_pat) <= 1.0 and sigma <= FC_PA
                  and buckle > 1.0 and done_when_ok)
    return PanelRow(
        thickness_m=t, levelling=levelling, prestressed=prestressed, w_uls_pa=w_uls, h_closed_n_m=h_closed,
        h_rigid_n_m=h_rigid, h_ratio=h_rigid / h_closed, tie_bar_mm=bar or 0,
        h_elastic_n_m=h_el_uniform, buckling_factor=buckle, membrane_stress_pa=sigma,
        util_uniform=u_uni, util_pattern=u_pat, concrete_m3_m2=t * k,
        mesh_kg_m2=2.0 * layers * rho * t * k * STEEL_DENSITY_KG_M3,
        tie_kg_m2=a_tie * STEEL_DENSITY_KG_M3 / b if bar else float("nan"), passes=passes)


def size_panel(workdir: Path, thicknesses: tuple[float, ...] = TRIAL_THICKNESSES_M,
               levellings: tuple[str, ...] = tuple(LEVELLING)) -> list[PanelRow]:
    """Run every trial thickness and levelling option (the Day 25 panel).

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
