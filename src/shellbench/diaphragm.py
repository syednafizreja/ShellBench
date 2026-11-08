"""Rigid-diaphragm test of the shell floor and the topping rule (Day 27, H3).

File: src/shellbench/diaphragm.py

What this module does
---------------------
It answers one question for each building and each floor variant: is the
vaulted floor a rigid diaphragm for the transverse seismic forces, and if not,
what is the smallest topping (0, 40, 50 or 60 mm) that makes it one?

The criterion
-------------
The preregistration (docs/preregistration.md 2.3) fixes the default rule: the
largest in-plane deformation of the floor must be no more than twice the mean
storey drift of the vertical elements of the same storey, under the same
tributary load. I take this from the flexible-diaphragm condition of
ASCE/SEI 7-16 cl. 12.3.1.3 (checked by Claude, 8 Nov 2026, against the
ASCE 7-10 text and NIST GCR 17-917-47, Sec. 5.1, which states the ASCE 7-16
rule; the 7-16 text itself is paywalled; author to confirm). GB 50011-2010
Table 6.1.6 and JGJ 3-2010 cl. 5.1.5 give no deflection test. JGJ 3 cl. 3.6.2
concerns precast floors with a topping and is not used.

The model
---------
Load direction: transverse, the frame plane, as everywhere in the family.
The floor of one storey spans, as a deep beam, between the transverse frame
lines (the vault span L, 6.0 or 6.6 m) and is d = sum of frame spans deep (21.0 m).
The perimeter longitudinal beams are the chords [J]. For a uniform lateral load
p [kN/m^2] on the plan:

    delta_d = p L^2 / (8 K)        (shear deflection at mid-bay)

where K = G t_eff is the in-plane shear stiffness per m of floor [kN/m].
The bending part of the deep beam is not counted: with stiff chords it is small
for L/d = 0.3 [J].

K of the bare vault comes from CalculiX (``shellfe``): one bay of the vault,
21.0 m deep along the generators, supports on both springing lines, chord
lines held in x, and a body force in y (the load direction). The result is
written as a factor k = K / (G t) < 1 that depends on the geometry. For a flat
plate of the same size the model returns k = 1.0000, which is the check of
the method (tests/test_diaphragm.py). A topping adds G_c t_top, fully
bonded to the shell [J]. The ties carry no in-plane shear in this load
direction, so they do not enter [J].

The check also gives a shear stress tau = p L / (2 t) against f_t, as
information only; I have no code clause for the shear strength of a shell
diaphragm [?].

Limits (Paper 1 Methods): uncracked elastic shear modulus; full shear
connection between shell, topping and beams; transverse direction only; the
ASCE criterion, not a Chinese one. The margin is reported, so a reader can
see how much stiffness the floor could lose before the verdict changes.

Units: N, m, Pa for CalculiX; kN and m for the building check.
"""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import numpy as np

from shellbench import panel
from shellbench.formfind import parabola
from shellbench.shellfe import ShellModel, mapped_mesh, run

ROOT = Path(__file__).resolve().parents[2]
FACTORS_CSV = ROOT / "results" / "diaphragm_library.csv"

#: ASCE/SEI 7-16 cl. 12.3.1.3: flexible if delta_d > 2 x mean storey drift.
RIGIDITY_LIMIT: float = 2.0
#: Plan depth of the floor along the generators [m]: the sum of the anchor frame spans (spec G3).
DEPTH_M: float = 21.0
#: Topping options [mm], preregistration 2.3.
TOPPINGS_MM: tuple[int, ...] = (0, 40, 50, 60)
#: Mesh [J]: 12 elements across the span, 16 along the generators.
ELEMENTS_ALONG_SPAN: int = 12
ELEMENTS_ALONG_GENERATORS: int = 16
#: Body-force test: density [kg/m^3] and acceleration [m/s^2] in y; only the product with t matters.
TEST_DENSITY_KG_M3: float = 1000.0
TEST_ACCELERATION_M_S2: float = 1.0
STATICS_POINTS: int = 801


def shear_modulus_pa() -> float:
    """G = E / (2 (1 + nu)) of the shell concrete [Pa]."""
    return panel.E_CONCRETE_PA / (2.0 * (1.0 + panel.NU_CONCRETE))


def shear_factor(span_m: float, rise_ratio: float, thickness_m: float, workdir: Path | None = None,
                 depth_m: float = DEPTH_M) -> float:
    """k = K / (G t) of one vault bay in in-plane shear, from CalculiX [-].

    The bay is meshed over its span and ``depth_m`` along the generators. All
    nodes of both springing lines are held (ux, uy, uz). The two chord lines
    (y = 0 and y = depth) are held in x only. A body force acts in y. K comes
    from the mid-bay deflection: K = p L^2 / (8 delta), where p is the weight
    per m^2 of plan (density x acceleration x t x arc factor).

    Args:
        span_m: Vault span L [m].
        rise_ratio: f / L [-]; 0 gives a flat plate (the method check).
        thickness_m: Shell thickness [m].
        workdir: Folder for the CalculiX files; a temporary one if None.
        depth_m: Plan depth along the generators [m].

    Returns:
        K / (G t) [-].
    """
    rise = rise_ratio * span_m
    nu, nv = ELEMENTS_ALONG_SPAN, ELEMENTS_ALONG_GENERATORS

    def surface(u: float, v: float) -> tuple[float, float, float]:
        """Point of the vault: u along the span, v along the generators."""
        return u * span_m, v * depth_m, float(parabola(np.array(u * span_m), span_m, rise))

    nodes, elements, grid = mapped_mesh(surface, nu, nv)
    supports = [(n, 1, 3) for (i, j), n in grid.items() if i in (0, 2 * nu)]
    supports += [(n, 1, 1) for (i, j), n in grid.items() if j in (0, 2 * nv) and i not in (0, 2 * nu)]
    model = ShellModel(nodes, elements, thickness_m, panel.E_CONCRETE_PA, panel.NU_CONCRETE,
                       density=TEST_DENSITY_KG_M3, supports=supports,
                       gravity=(TEST_ACCELERATION_M_S2, 0.0, 1.0, 0.0))
    if workdir is None:
        with tempfile.TemporaryDirectory() as tmp:
            res = run(model, Path(tmp), name="diaphragm")
    else:
        res = run(model, workdir, name="diaphragm")
    delta = max(res.displacements[n][1] for (i, j), n in grid.items() if i == nu)
    x = np.linspace(0.0, span_m, STATICS_POINTS)
    arc = float(np.trapezoid(np.sqrt(1.0 + np.gradient(parabola(x, span_m, rise), x) ** 2), x) / span_m)
    p_pa = TEST_DENSITY_KG_M3 * TEST_ACCELERATION_M_S2 * thickness_m * arc
    k_n_m = p_pa * span_m**2 / (8.0 * delta)
    return k_n_m / (shear_modulus_pa() * thickness_m)


def library_factors(path: Path = FACTORS_CSV) -> dict[str, float]:
    """k of every floor-library case, by variant ID; read from ``path``."""
    with open(path, newline="") as f:
        return {r["variant_id"]: float(r["shear_factor"]) for r in csv.DictReader(f)}


def build_library_factors(path: Path = FACTORS_CSV) -> list[dict]:
    """Run ``shear_factor`` for every case of results/floor_library.csv and write ``path``."""
    import pandas as pd
    lib = pd.read_csv(ROOT / "results" / "floor_library.csv")
    rows = []
    for r in lib.itertuples():
        k = shear_factor(r.span_m, r.rise_ratio, r.thickness_m)
        rows.append({"variant_id": r.variant_id, "span_m": r.span_m, "rise_ratio": r.rise_ratio,
                     "thickness_m": r.thickness_m, "shear_factor": round(k, 4)})
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return rows


def bay_stiffness_kn_m(k_shear: float, thickness_m: float, topping_mm: float) -> float:
    """In-plane shear stiffness K of one bay with its topping [kN/m per m of floor].

    K = k G t_shell + G t_top (topping fully bonded [J]).
    """
    g_kpa = shear_modulus_pa() / 1.0e3
    return g_kpa * (k_shear * thickness_m + topping_mm / 1000.0)


def check_storey(force_kn: float, area_m2: float, drift_m: float, span_m: float, k_kn_m: float,
                 thickness_m: float, topping_mm: float) -> dict[str, float]:
    """Diaphragm test of one storey and one bay.

    Args:
        force_kn: Storey seismic force of the frame strip [kN].
        area_m2: Plan area carrying it [m^2].
        drift_m: Elastic storey drift of the frame under that force [m].
        span_m: Bay span L (vault span) [m].
        k_kn_m: Shear stiffness K from ``bay_stiffness_kn_m`` [kN/m].
        thickness_m: Shell thickness [m].
        topping_mm: Topping [mm].

    Returns:
        ``delta_m`` (mid-bay deflection), ``ratio`` = delta / (2 drift) (rigid if <= 1),
        ``stiffness_ratio`` = drift / delta (diaphragm against frame storey stiffness),
        ``tau_over_ft`` (information only).
    """
    p = force_kn / area_m2
    delta = p * span_m**2 / (8.0 * k_kn_m)
    t_all = thickness_m + topping_mm / 1000.0
    tau_kpa = p * span_m / (2.0 * t_all)
    return {"delta_m": delta, "ratio": delta / (RIGIDITY_LIMIT * drift_m),
            "stiffness_ratio": drift_m / delta, "tau_over_ft": tau_kpa * 1.0e3 / panel.FT_PA}
