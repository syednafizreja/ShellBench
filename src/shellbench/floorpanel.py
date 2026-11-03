"""Size one shell floor panel: thickness check, tie, buckling factor, quantities.

File: src/shellbench/floorpanel.py

What this module does
---------------------
Playbook Day 25 (floor-r3). One barrel-vault panel of layout A
(docs/floor_concept.md section 3) spans L between two frame beams and is B
wide. Its shape is the parabola z = 4 f x (L - x) / L^2, which is the
force-density form of a long strip (formfind.py, tested on Day 23).

1. ``closed_form`` gives the thrust per metre H = w L^2 / (8 f), the tie
   force T = H s for ties at spacing s, and the tie area A_t = T / f_y
   (floor_concept.md section 4.5).
2. ``fe_panel`` builds the same panel in CalculiX (shellfe.py, Day 24) with
   pinned springing lines and no rotational supports (the Day 24 finding),
   and reads the thrust from the membrane stress at the crown, plus the
   linear buckling factor of the same load.
3. ``quantities`` gives concrete, mesh steel and tie steel per m^2 of plan.

The Day 25 test: the FE thrust is within 10 % of the closed form
(schedule.md, floor-r3 row).

Values marked [J] are choices; sources are given for the rest. Units: N, m,
Pa, kg.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from shellbench import shellfe

E_C40_PA = 3.25e10  # GB 50010 Table 4.1.5, C40 (as anchor_frame.E_KN_M2)
NU_CONCRETE = 0.2  # notes/gb50010_design_values.md (GB 50010 cl. 4.1.8)
FY_HRB400_PA = 360e6  # GB 50010 Table 4.2.3-1, checked 30 Oct 2026
RHO_MIN_SHELL = 0.00214  # floor_concept.md 4.2: 45 f_t / f_y for C40, HRB400 [J reading]
CONCRETE_KG_M3 = 2500.0  # 25 kN/m^3, thesis s4.1, taken as 2500 kg/m^3 [J]
STEEL_KG_M3 = 7850.0  # steel density [J, standard value]
G = 9.81  # m/s^2
GAMMA_D, GAMMA_L = 1.3, 1.5  # GB 55001-2021 cl. 3.1.13 (design_rules R9)
TOLERANCE = 0.10  # schedule.md, Day 25: tie force within 10 % of the closed form


@dataclass
class Panel:
    """One vault panel.

    Attributes:
        span: L between the frame beams [m].
        width: B, the panel width along the beams [m].
        rise: f [m].
        thickness: t [m].
        tie_spacing: s [m].
        superimposed_dead: Levelling + finishes above the shell, per plan m^2 [Pa].
        live: Live load per plan m^2 [Pa].
    """

    span: float
    width: float
    rise: float
    thickness: float
    tie_spacing: float
    superimposed_dead: float
    live: float

    def arc_factor(self) -> float:
        """Arc length of the parabola over its chord [-]."""
        n = 200
        xs = [self.span * k / n for k in range(n + 1)]
        zs = [4 * self.rise * x * (self.span - x) / self.span ** 2 for x in xs]
        arc = sum(math.hypot(xs[k + 1] - xs[k], zs[k + 1] - zs[k]) for k in range(n))
        return arc / self.span

    def self_weight(self) -> float:
        """Shell weight per plan m^2 [Pa]."""
        return CONCRETE_KG_M3 * G * self.thickness * self.arc_factor()

    def design_load(self) -> float:
        """w = 1.3 (shell + superimposed dead) + 1.5 live, per plan m^2 [Pa]."""
        return GAMMA_D * (self.self_weight() + self.superimposed_dead) + GAMMA_L * self.live


@dataclass
class ClosedForm:
    """Statics of a parabolic arch under uniform plan load."""

    thrust_per_m: float  # H [N/m]
    tie_force: float  # T = H s [N]
    tie_area_mm2: float  # A_t [mm^2]


def closed_form(p: Panel) -> ClosedForm:
    """H = w L^2 / (8 f), T = H s, A_t = T / f_y."""
    h = p.design_load() * p.span ** 2 / (8.0 * p.rise)
    t = h * p.tie_spacing
    return ClosedForm(h, t, t / FY_HRB400_PA * 1e6)


@dataclass
class FEResult:
    """CalculiX results for one panel."""

    thrust_per_m: float  # from the crown membrane stress [N/m]
    crown_deflection: float  # [m], downwards positive
    buckling_factor: float  # first linear buckling factor [-]
    max_abs_stress: float  # largest |sxx| at any integration point [Pa]


def panel_model(p: Panel, nu: int = 16, nv: int = 8) -> tuple[shellfe.ShellModel, dict]:
    """S8R mesh of the vault, pinned along both springing lines.

    The load is a GRAV load with the density set so that rho g t times the
    arc factor equals the design load per plan m^2; so it acts per unit
    surface and its plan total equals w L B [J]. One node at x = L/2 on the
    edge y = 0 is held in y against rigid-body motion.
    """
    def surface(u: float, v: float) -> tuple[float, float, float]:
        x = u * p.span
        return x, v * p.width, 4 * p.rise * x * (p.span - x) / p.span ** 2

    nodes, elements, grid = shellfe.mapped_mesh(surface, nu, nv)
    supports = [(grid[(i, j)], 1, 3) for (i, j) in grid if i in (0, 2 * nu)]
    supports.append((grid[(nu, 0)], 2, 2))
    density = p.design_load() / (G * p.thickness * p.arc_factor())
    model = shellfe.ShellModel(nodes, elements, p.thickness, E_C40_PA, NU_CONCRETE,
                               density=density, supports=supports, gravity=(G, 0.0, 0.0, -1.0))
    return model, grid


def fe_panel(p: Panel, workdir: Path, nu: int = 16, nv: int = 8) -> FEResult:
    """Run the static and buckling analyses and read thrust, deflection and factor.

    Thrust: the mean x-stress over every integration point of the two
    element columns either side of the crown, times t. Through the thickness
    the bending part averages out, leaving the membrane force N_x, which at
    the crown is horizontal and equals H. Elements near y = 0 and y = B are
    left out (two element rows each side) because the free edges carry less [J].
    """
    model, grid = panel_model(p, nu, nv)
    static = shellfe.run(model, workdir, "panel")
    crown = [jj * nu + ii + 1 for jj in range(2, nv - 2) for ii in (nu // 2 - 1, nu // 2)]
    sxx = [s[0] for (e, _), s in static.stresses.items() if e in crown]
    thrust = -sum(sxx) / len(sxx) * p.thickness
    mid = grid[(nu, nv)]
    defl = -static.displacements[mid][2]
    buck = shellfe.run(model, workdir, "panel_buckle", buckling_modes=1)
    peak = max(abs(s[0]) for s in static.stresses.values())
    return FEResult(thrust, defl, buck.buckling_factors[0], peak)


def quantities(p: Panel, tie: ClosedForm) -> dict[str, float]:
    """Material per m^2 of plan: concrete [m^3], mesh steel [kg], tie steel [kg].

    Mesh at the minimum ratio over the full thickness (floor_concept.md 4.2).
    Ties: one bar of area A_t per spacing s, over the span.
    """
    concrete = p.thickness * p.arc_factor()
    mesh = RHO_MIN_SHELL * concrete * STEEL_KG_M3
    ties = tie.tie_area_mm2 / 1e6 * STEEL_KG_M3 / p.tie_spacing
    return {"concrete_m3_per_m2": concrete, "mesh_kg_per_m2": mesh, "tie_kg_per_m2": ties}


#: The Day 25 panel [J]: layout A at the 6.6 m span, 7.2 m wide; f = L/15 (the
#: author's required range is 1/15 to 1/20); t = 60 mm (floor_concept.md 4.1,
#: inside 50-80 mm); s = 1.2 m (4.1); raised floor 29 kg/m^2 (Oval et al. 2023,
#: Table 6) plus finishes 1.05 kPa (floor dead 4.05 less the 3.00 slab,
#: baseline L1); office live 2.5 kPa (B3).
DAY25_PANEL = Panel(span=6.6, width=7.2, rise=6.6 / 15, thickness=0.06, tie_spacing=1.2,
                    superimposed_dead=29.0 * G + 1050.0, live=2500.0)
