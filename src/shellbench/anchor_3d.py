"""Simple 3D elastic model of the whole anchor building with rigid floors (periods only).

File: src/shellbench/anchor_3d.py

What this module does
---------------------
Playbook Day 10 asks for the first three periods of the whole building next
to the 2D frame's, so the paper can say how much the 2D simplification
changes T1. The model follows reading rule 6 of docs/anchor_notes.md ("How the
response-spectrum check is read"):

- plan on the drawing grid (spec G4, decision B11): global X along axes 1-7
  (bays 6.0, 6.6, 6.6, 6.6, 6.6, 6.0 m = 38.4 m), global Y along axes A-D
  (7.2, 6.6, 7.2 m = 21.0 m, spec G3); storey heights as the 2D frame;
- 600 x 600 columns at all 28 grid points, fixed at the base (spec M5);
- transverse beams (along Y) as the 2D frame (AB, CD 300 x 600; BC
  300 x 500, spec M1, M2); longitudinal beams (along X) 300 x 600 (spec M3);
  beam I factor 2.0 on interior lines and 1.5 on edge lines (spec M7, applied
  to both directions [J]);
- one rigid diaphragm per level; the mass of each level is the 2D frame's
  G_i / g scaled by plan area, placed at the plan centre with the rotational
  inertia of a uniform rectangle [J].

The E-shaped wings and stair cores are not modelled (decision B11 open point).

Units: kN, m, s.
"""

from __future__ import annotations

import math

import openseespy.opensees as ops

from shellbench import anchor_frame as af
from shellbench import anchor_wind as aw
from shellbench import seismic as s

#: Longitudinal bays along axes 1-7 [m]. Spec G4 (drawings 01-05), decision B11.
LONGITUDINAL_BAYS_M: tuple[float, ...] = (6.0, 6.6, 6.6, 6.6, 6.6, 6.0)

#: Longitudinal beam section b x h [m]. Spec M3 (Th §2.3; decided B13).
LONGITUDINAL_BEAM_BH_M: tuple[float, float] = (0.3, 0.6)

#: Beam I factor on edge frames [-]. Spec M7 (Th §2.6: 1.5 I0 edge).
EDGE_BEAM_INERTIA_FACTOR: float = 1.5

#: Shear modulus as a fraction of E for concrete [-]. GB 50010-2010 cl. 4.1.5
#: (G_c = 0.4 E_c), p. 19 of the author's English translation, read 27 Oct
#: 2026 (notes/gb50010_design_values.md). It only affects torsion of members.
SHEAR_MODULUS_FACTOR: float = 0.4

#: Number of modes reported (Playbook Day 10: "first three periods").
N_MODES_3D: int = 3


def torsion_constant(b_m: float, h_m: float) -> float:
    """Return the St Venant torsion constant of a solid rectangle [m^4].

    Approximation J = beta b^3 h with beta = 1/3 - 0.21 (b/h) (1 - (b/h)^4 / 12),
    b <= h (standard series result for rectangular sections, as tabulated in
    Roark's Formulas for Stress and Strain [?]). Torsion has a minor effect on
    the frame's periods [J].

    Args:
        b_m: Shorter side [m].
        h_m: Longer side [m].

    Returns:
        J [m^4].
    """
    b, h = sorted((b_m, h_m))
    r = b / h
    return (1.0 / 3.0 - 0.21 * r * (1.0 - r**4 / 12.0)) * b**3 * h


def plan_coordinates() -> tuple[list[float], list[float]]:
    """Return the grid line coordinates [m]: X along axes 1-7, Y along A-D.

    Returns:
        (xs, ys) cumulative sums starting at 0.
    """
    xs = [0.0]
    for b in LONGITUDINAL_BAYS_M:
        xs.append(xs[-1] + b)
    return xs, af.axis_x_coordinates()


def level_masses_t(weights_2d_kn: list[float]) -> list[float]:
    """Scale the 2D frame's level weights to the whole plan and convert to mass [t].

    The 2D frame carries a 7.2 m strip (decision B10) of the 21.0 m width;
    the whole plan is 38.4 m long, so the factor is 38.4 / 7.2 [J].

    Args:
        weights_2d_kn: G_i of the 2D frame, level 1 first [kN].

    Returns:
        Level masses [t].
    """
    xs, _ = plan_coordinates()
    factor = xs[-1] / aw.LOADED_WIDTH_M
    return [g * factor / s.G_ACCEL_M_S2 for g in weights_2d_kn]


def build_3d(weights_2d_kn: list[float]) -> dict[int, int]:
    """Build the 3D frame with rigid diaphragms and level masses in a fresh domain.

    Args:
        weights_2d_kn: G_i of the 2D frame, level 1 first [kN].

    Returns:
        Mapping level -> diaphragm master node tag.
    """
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    xs, ys = plan_coordinates()
    zs = af.level_y_coordinates()
    e = af.E_KN_M2
    g_mod = SHEAR_MODULUS_FACTOR * e
    # Columns: local x vertical, local z along global X. Beams along X: local z
    # along global Y, so local y is vertical and Iz is the vertical-bending I.
    # Beams along Y: local z along global X, same meaning of Iz.
    ops.geomTransf("Linear", 1, 1.0, 0.0, 0.0)
    ops.geomTransf("Linear", 2, 0.0, 1.0, 0.0)
    ops.geomTransf("Linear", 3, 1.0, 0.0, 0.0)

    node = {}
    tag = 1
    for k, z in enumerate(zs):
        for i, x in enumerate(xs):
            for j, y in enumerate(ys):
                ops.node(tag, x, y, z)
                node[(i, j, k)] = tag
                if k == 0:
                    ops.fix(tag, 1, 1, 1, 1, 1, 1)
                tag += 1

    ele = 1
    bc, hc = af.COLUMN_BH_M
    for k in range(1, len(zs)):
        for i in range(len(xs)):
            for j in range(len(ys)):
                ops.element("elasticBeamColumn", ele, node[(i, j, k - 1)], node[(i, j, k)],
                            bc * hc, e, g_mod, torsion_constant(bc, hc),
                            bc * hc**3 / 12.0, hc * bc**3 / 12.0, 1)
                ele += 1

    def beam(n1: int, n2: int, bh: tuple[float, float], factor: float, transf: int) -> None:
        """Add one beam element; Iz is the vertical-bending inertia times the T-beam factor."""
        nonlocal ele
        b, h = bh
        ops.element("elasticBeamColumn", ele, n1, n2, b * h, e, g_mod, torsion_constant(b, h),
                    h * b**3 / 12.0, factor * b * h**3 / 12.0, transf)
        ele += 1

    for k in range(1, len(zs)):
        for j in range(len(ys)):
            f = EDGE_BEAM_INERTIA_FACTOR if j in (0, len(ys) - 1) else af.BEAM_INERTIA_FACTOR
            for i in range(len(xs) - 1):
                beam(node[(i, j, k)], node[(i + 1, j, k)], LONGITUDINAL_BEAM_BH_M, f, 2)
        for i in range(len(xs)):
            f = EDGE_BEAM_INERTIA_FACTOR if i in (0, len(xs) - 1) else af.BEAM_INERTIA_FACTOR
            for j, span in enumerate(af.SPAN_LABELS):
                beam(node[(i, j, k)], node[(i, j + 1, k)], af.BEAM_BH_M[span], f, 3)

    masters = {}
    lx, ly = xs[-1], ys[-1]
    for k, m in enumerate(level_masses_t(weights_2d_kn), start=1):
        ops.node(tag, lx / 2.0, ly / 2.0, zs[k])
        ops.fix(tag, 0, 0, 1, 1, 1, 0)
        ops.mass(tag, m, m, 0.0, 0.0, 0.0, m * (lx**2 + ly**2) / 12.0)
        slaves = [node[(i, j, k)] for i in range(len(xs)) for j in range(len(ys))]
        ops.rigidDiaphragm(3, tag, *slaves)
        masters[k] = tag
        tag += 1
    return masters


def periods_3d(weights_2d_kn: list[float], n_modes: int = N_MODES_3D) -> list[dict]:
    """Return the first periods of the 3D model and the direction of each mode.

    The direction is the largest of the roof master's X, Y and r theta_z
    components, with r the radius of gyration of the plan.

    Args:
        weights_2d_kn: G_i of the 2D frame, level 1 first [kN].
        n_modes: Number of modes.

    Returns:
        One dict per mode: period [s], direction label, and the three roof
        components normalised to the largest.
    """
    masters = build_3d(weights_2d_kn)
    ops.constraints("Transformation")
    eig = ops.eigen("-genBandArpack", n_modes)
    xs, ys = plan_coordinates()
    r = math.sqrt((xs[-1] ** 2 + ys[-1] ** 2) / 12.0)
    roof = masters[max(masters)]
    out = []
    for j, lam in enumerate(eig, start=1):
        comp = {
            "X (longitudinal)": ops.nodeEigenvector(roof, j, 1),
            "Y (transverse)": ops.nodeEigenvector(roof, j, 2),
            "torsion": r * ops.nodeEigenvector(roof, j, 6),
        }
        big = max(comp, key=lambda k: abs(comp[k]))
        out.append({"T": 2.0 * math.pi / math.sqrt(lam), "direction": big,
                    # Divided by the signed dominant component, so the sign
                    # ARPACK happens to return does not reach the results file;
                    # "+ 0.0" turns -0.0 into 0.0 for the same reason.
                    **{k: comp[k] / comp[big] + 0.0 for k in comp}})
    ops.wipe()
    return out


def period_rows(periods_2d_s: list[float]) -> list[dict]:
    """Build ``results/anchor_3d_periods.csv``: 3D periods next to the 2D frame's.

    Args:
        periods_2d_s: First periods of the 2D frame [s] (all transverse).

    Returns:
        One dict per mode number.
    """
    g = [w.g_kn for w in s.storey_weights()]
    p3 = periods_3d(g, max(N_MODES_3D, len(periods_2d_s)))
    rows = []
    for j, m in enumerate(p3):
        t2 = periods_2d_s[j] if j < len(periods_2d_s) else None
        rows.append({
            "mode [text]": j + 1,
            "T_3d [s]": round(m["T"], 4),
            "direction_3d [text]": m["direction"],
            "roof_X [-]": round(m["X (longitudinal)"], 3) + 0.0,
            "roof_Y [-]": round(m["Y (transverse)"], 3) + 0.0,
            "roof_r_theta [-]": round(m["torsion"], 3) + 0.0,
            "T_2d_frame [s]": "" if t2 is None else round(t2, 4),
            "direction_2d [text]": "" if t2 is None else "Y (transverse), 2D mode of the same number",
        })
    return rows
