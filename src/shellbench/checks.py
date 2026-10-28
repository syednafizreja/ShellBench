"""GB 50010 / GB 50011 design checks on the anchor frame, against the thesis steel.

File: src/shellbench/checks.py

What this module does
---------------------
Playbook Day 11. It runs the anchor frame (``shellbench.anchor_frame``) for
every load case the thesis combined, combines them with the thesis load
combinations (``shellbench.combinations``) and checks:

1. the column axial compression ratio against the grade-III limit 0.85
   (GB 50010 Table 11.4.16; decision B16);
2. the beam top and bottom steel needed for the factored moments, with the
   rectangular stress block (GB 50010 cl. 6.2.10);
3. the minimum steel of beams and columns (GB 50010 Tables 11.3.6-1 and
   11.4.12-1).

The results are set next to the thesis steel (s9.2 table, typed in
``validation/thesis_values/beam_steel_areas.csv``; columns 4C22, spec R1) and
every member where the thesis steel is below the requirement is flagged.
The reading rules were committed before the first run (docs/anchor_notes.md,
"How the design checks are read", commit 468df78, 28 Oct 2026); the rule
numbers below refer to that list.

Code values
-----------
From ``notes/gb50010_design_values.md`` and the author's English translation
of GB 50010-2010 (2010 issue; page numbers of the translation, +/- 1 page).
Four of them were cross-checked against the Chinese 2015 edition on 27 Oct
2026; the rest are still to be checked by the author [?].

Units: inside OpenSees kN, m, kN*m. Section design in N and mm (moments
converted from kN*m with 1e6). Steel areas in mm^2.
"""

from __future__ import annotations

import csv
import math
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import openseespy.opensees as ops

from shellbench import anchor_frame as af
from shellbench import anchor_wind as aw
from shellbench import combinations as cb
from shellbench import seismic as s

# ---------------------------------------------------------------------------
# Code values (notes/gb50010_design_values.md)
# ---------------------------------------------------------------------------

#: Design axial compressive strength of C40 [N/mm^2]. GB 50010 Table 4.1.4-1, p. 18.
FC_N_MM2: float = 19.1

#: Design axial tensile strength of C40 [N/mm^2]. GB 50010 Table 4.1.4-2, p. 18.
FT_N_MM2: float = 1.71

#: Design yield strength of HRB400, tension and compression [N/mm^2].
#: GB 50010 Table 4.2.3-1, p. 21.
FY_N_MM2: float = 360.0

#: Elastic modulus of HRB400 [N/mm^2]. GB 50010 Table 4.2.5, p. 22.
ES_N_MM2: float = 2.0e5

#: Stress-block factors for grades up to C50 [-]. GB 50010 cl. 6.2.6, p. 34.
ALPHA1: float = 1.0
BETA1: float = 0.80

#: Ultimate concrete strain, capped value [-]. GB 50010 cl. 6.2.1, formula 6.2.1-5.
EPS_CU: float = 0.0033

#: Largest relative compression depth at a frame-beam end, grade II and III
#: [-]. GB 50010 cl. 11.3.1, formula 11.3.1-2, p. 154 (x <= 0.35 h0).
XI_END_LIMIT_GRADE_III: float = 0.35

#: Seismic adjustment coefficient for flexural members [-]. GB 50010 Table 11.1.6, p. 152.
GAMMA_RE_BEAM_FLEXURE: float = 0.75

#: Axial compression ratio limit, frame structure, grade III [-].
#: GB 50010 Table 11.4.16, p. 164; spec S6, decision B16.
AXIAL_RATIO_LIMIT: float = 0.85

#: Minimum total longitudinal ratio of a frame column (middle or side, frame
#: structure, grade III, 400 MPa bars) [-]: 0.7 % + 0.05 %. GB 50010
#: Table 11.4.12-1 and notes 1-2, p. 163.
RHO_MIN_COLUMN_TOTAL: float = 0.0075

#: Minimum longitudinal ratio on each side of a frame column [-].
#: GB 50010 cl. 11.4.12 (each side >= 0.2 %), p. 163.
RHO_MIN_COLUMN_SIDE: float = 0.0020

#: Distance from the extreme fibre to the bar centroid, beams and columns [mm].
#: Spec X10, decision B14 (h0 = h - 50).
A_S_MM: float = 50.0

#: Column half-width: distance from the column centre-line to its face [m].
#: Half of the 600 mm column (spec M5); reading rule 3.
COLUMN_HALF_WIDTH_M: float = af.COLUMN_BH_M[0] / 2.0


def xi_b() -> float:
    """Return the balanced relative compression depth xi_b [-].

    xi_b = beta1 / (1 + f_y / (E_s eps_cu)), GB 50010 formula 6.2.7-1, p. 34.

    Returns:
        0.518 for C40 / HRB400.
    """
    return BETA1 / (1.0 + FY_N_MM2 / (ES_N_MM2 * EPS_CU))


def rho_min_beam(position: str) -> float:
    """Return the minimum tension-steel ratio of a grade-III frame beam [-].

    GB 50010 Table 11.3.6-1, p. 156: support max(0.25 %, 55 f_t / f_y);
    mid-span max(0.20 %, 45 f_t / f_y). The ratio is on b x h.

    Args:
        position: ``"support"`` or ``"mid-span"``.

    Returns:
        The ratio as a fraction.

    Raises:
        ValueError: For any other position.
    """
    if position == "support":
        return max(0.0025, 55.0 * FT_N_MM2 / FY_N_MM2 / 100.0)
    if position == "mid-span":
        return max(0.0020, 45.0 * FT_N_MM2 / FY_N_MM2 / 100.0)
    raise ValueError(f"unknown beam position {position!r}")


def bar_area_mm2(bars: str) -> float:
    """Return the area of a bar group written as ``nCd`` (e.g. ``"3C16"``) [mm^2].

    ``C`` is the thesis's symbol for HRB400 bars; the area of one bar is
    pi d^2 / 4 (nominal diameter d in mm).

    Args:
        bars: Bar group such as ``"3C16"`` or ``"4C22"``.

    Returns:
        n x pi d^2 / 4.

    Raises:
        ValueError: If the text is not of the form ``nCd``.
    """
    m = re.fullmatch(r"\s*(\d+)\s*C\s*(\d+)\s*", bars)
    if not m:
        raise ValueError(f"cannot read bar group {bars!r}")
    n, d = int(m.group(1)), float(m.group(2))
    return n * math.pi * d * d / 4.0


@dataclass(frozen=True)
class SectionDesign:
    """Tension steel needed by one rectangular section for one moment.

    Attributes:
        m_knm: Design moment, already multiplied by gamma_RE where it applies [kN*m].
        xi: Relative compression depth x / h0 of the singly reinforced section [-].
        as_calc_mm2: Steel from the stress block [mm^2].
        as_min_mm2: Minimum steel [mm^2].
        as_req_mm2: max(as_calc, as_min) [mm^2].
        status: ``"ok"`` or why the singly reinforced section is not enough.
    """

    m_knm: float
    xi: float
    as_calc_mm2: float
    as_min_mm2: float
    as_req_mm2: float
    status: str


def design_section(m_knm: float, b_mm: float, h_mm: float, position: str,
                   at_end: bool) -> SectionDesign:
    """Design the tension steel of a singly reinforced rectangular beam section.

    alpha_s = M / (alpha1 f_c b h0^2), xi = 1 - sqrt(1 - 2 alpha_s),
    A_s = alpha1 f_c b xi h0 / f_y (GB 50010 cl. 6.2.10, p. 36-37), with
    h0 = h - a_s. The section is reported as needing compression steel when
    xi > xi_b, or at a beam end when xi > 0.35 (cl. 11.3.1); it is not
    redesigned (reading rule 4).

    Args:
        m_knm: Design moment, >= 0 [kN*m].
        b_mm: Width [mm].
        h_mm: Depth [mm].
        position: ``"support"`` or ``"mid-span"``, for the minimum steel.
        at_end: True at a beam end (cl. 11.3.1 applies).

    Returns:
        A SectionDesign.
    """
    h0 = h_mm - A_S_MM
    as_min = rho_min_beam(position) * b_mm * h_mm
    if m_knm <= 0.0:
        return SectionDesign(0.0, 0.0, 0.0, as_min, as_min, "ok")
    alpha_s = m_knm * 1.0e6 / (ALPHA1 * FC_N_MM2 * b_mm * h0 * h0)
    if alpha_s >= 0.5:
        return SectionDesign(m_knm, math.inf, math.inf, as_min, math.inf,
                             "section too small (alpha_s >= 0.5)")
    xi = 1.0 - math.sqrt(1.0 - 2.0 * alpha_s)
    as_calc = ALPHA1 * FC_N_MM2 * b_mm * xi * h0 / FY_N_MM2
    status = "ok"
    if xi > xi_b():
        status = "needs compression steel (xi > xi_b)"
    elif at_end and xi > XI_END_LIMIT_GRADE_III:
        status = "needs compression steel (xi > 0.35, cl. 11.3.1)"
    return SectionDesign(m_knm, xi, as_calc, as_min, max(as_calc, as_min), status)


# ---------------------------------------------------------------------------
# Load cases (reading rule 1)
# ---------------------------------------------------------------------------


@dataclass
class CaseResult:
    """Member forces of one load case.

    Attributes:
        name: Load-case name as used in ``shellbench.combinations``.
        moments: (span, level) -> sagging-positive bending moment at each node
            along the beam, left to right [kN*m].
        axial: Column axial forces, compression positive, keyed as
            ``anchor_frame.column_axial_forces`` [kN].
    """

    name: str
    moments: dict[tuple[str, int], list[float]]
    axial: dict[tuple[str, str, str], float]

    def effects(self) -> dict[tuple, float]:
        """Flatten the forces into one mapping for ``combinations.combine``.

        Returns:
            Keys ``("M", span, level, node index)`` and ``("N", axis, storey, end)``.
        """
        out = {("M", sp, lvl, k): v for (sp, lvl), ms in self.moments.items()
               for k, v in enumerate(ms)}
        out.update({("N", ax, st, e): v for (ax, st, e), v in self.axial.items()})
        return out


def beam_moment_diagrams(fm: af.FrameModel) -> dict[tuple[str, int], list[float]]:
    """Read the sagging-positive moment at every node of every beam [kN*m].

    OpenSees ``localForce`` gives end moments acting on each sub-element,
    anticlockwise positive. A sagging moment acts clockwise on the left end
    and anticlockwise on the right end of an element, so the sagging moment
    is -M_i at the first node and +M_j at every later node. At the beam
    ends this equals ``anchor_frame.beam_end_moments`` at the left end and
    its negative at the right end (the thesis convention).

    Args:
        fm: A solved frame.

    Returns:
        (span, level) -> list of moments, one per node of the beam chain.
    """
    out = {}
    for (span, lvl), subs in fm.beam.items():
        ms = [-ops.eleResponse(subs[0], "localForce")[2]]
        ms += [ops.eleResponse(e, "localForce")[5] for e in subs]
        out[(span, lvl)] = ms
    return out


def solve_case(name: str, apply: Callable[[af.FrameModel], None]) -> CaseResult:
    """Build the frame, apply one load case, solve and read the member forces.

    Args:
        name: Load-case name.
        apply: Function that applies the loads to a freshly built frame.

    Returns:
        A CaseResult.
    """
    fm = af.build_frame()
    apply(fm)
    af.solve_static()
    res = CaseResult(name, beam_moment_diagrams(fm), af.column_axial_forces(fm))
    ops.wipe()
    return res


def apply_lateral(fm: af.FrameModel, forces_kn: list[float], direction: str) -> None:
    """Apply horizontal storey forces from the left (at axis A) or right (at axis D).

    From the left the forces push in +x at the axis-A joints, as on Days 8
    and 9 (``anchor_wind.apply_wind``); from the right they push in -x at
    the axis-D joints, the mirror image (reading rule 1).

    Args:
        fm: The frame returned by ``anchor_frame.build_frame``.
        forces_kn: Force at each level, level 1 first [kN], >= 0.
        direction: ``"left"`` or ``"right"``.

    Raises:
        ValueError: For any other direction.
    """
    if direction not in ("left", "right"):
        raise ValueError(f"unknown direction {direction!r}")
    ax, sign = ("A", 1.0) if direction == "left" else ("D", -1.0)
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)
    for lvl, f in enumerate(forces_kn, start=1):
        ops.load(fm.node[(ax, lvl)], sign * f, 0.0, 0.0)


def gravity_representative_model() -> tuple[af.LoadModel, dict, dict]:
    """Return the beam loads, joint loads and joint moments of G_E.

    G_E = dead + 0.5 x floor live, with no roof live (GB 50011 Table 5.1.3;
    coefficients ``seismic.LIVE_COMBINATION_COEFF_FLOOR`` and ``_ROOF``), built
    from the primary dead and live models (``thesis_fem``), so that G_E is
    run as one case (reading rule 1). Both primary models are uniform loads,
    so the sum is again a uniform load.

    Returns:
        (load model, joint loads [kN], exterior joint moments [kN*m]).

    Raises:
        ValueError: If a primary model is not uniform.
    """
    dead, live = af.LOAD_MODELS["thesis_fem"], af.LIVE_LOAD_MODELS["thesis_fem"]
    coeff = {"roof": s.LIVE_COMBINATION_COEFF_ROOF, "floor": s.LIVE_COMBINATION_COEFF_FLOOR}
    beams = {}
    for key, bd in dead.beams.items():
        bl = live.beams[key]
        if bd.shape != "none" or bl.shape != "none":
            raise ValueError("G_E needs uniform primary load models")
        beams[key] = af.BeamLoad(bd.uniform_kn_m + coeff[key[0]] * bl.uniform_kn_m)
    model = af.LoadModel("gravity_representative",
                         "G_E = D + 0.5 floor live, no roof live (GB 50011 Table 5.1.3)", beams)
    joints = {k: v + coeff[k[1]] * af.LIVE_JOINT_LOADS_KN[k] for k, v in af.JOINT_LOADS_KN.items()}
    moments = {k: v + coeff[k] * af.LIVE_EXTERIOR_JOINT_MOMENTS_KN_M[k]
               for k, v in af.EXTERIOR_JOINT_MOMENTS_KN_M.items()}
    return model, joints, moments


def floor_live_model() -> tuple[af.LoadModel, dict, dict]:
    """Return the primary live load with the roof part removed (a check of G_E).

    Returns:
        (load model, joint loads [kN], exterior joint moments [kN*m]).
    """
    live = af.LIVE_LOAD_MODELS["thesis_fem"]
    beams = {k: (v if k[0] == "floor" else af.BeamLoad(0.0)) for k, v in live.beams.items()}
    joints = {k: (v if k[1] == "floor" else 0.0) for k, v in af.LIVE_JOINT_LOADS_KN.items()}
    moments = {k: (v if k == "floor" else 0.0) for k, v in af.LIVE_EXTERIOR_JOINT_MOMENTS_KN_M.items()}
    return af.LoadModel("floor_live", "primary live load without the roof", beams), joints, moments


def run_cases(wind_kn: list[float], quake_kn: list[float]) -> dict[str, CaseResult]:
    """Solve every load case the combinations need (reading rule 1).

    Args:
        wind_kn: Wind force W_k at each level, level 1 first [kN].
        quake_kn: Earthquake storey force F_i at each level [kN].

    Returns:
        Load-case name -> CaseResult, for D, L, GE, W_left, W_right, E_left
        and E_right.
    """
    ge_model, ge_joints, ge_moments = gravity_representative_model()
    appliers = {
        "D": lambda fm: af.apply_dead_load(fm, af.LOAD_MODELS["thesis_fem"]),
        "L": lambda fm: af.apply_live_load(fm, af.LIVE_LOAD_MODELS["thesis_fem"]),
        "GE": lambda fm: af.apply_gravity_case(fm, ge_model, ge_joints, ge_moments, None,
                                               af.COLUMN_SELF_WEIGHT_KN_M),
        "W_left": lambda fm: apply_lateral(fm, wind_kn, "left"),
        "W_right": lambda fm: apply_lateral(fm, wind_kn, "right"),
        "E_left": lambda fm: apply_lateral(fm, quake_kn, "left"),
        "E_right": lambda fm: apply_lateral(fm, quake_kn, "right"),
    }
    return {name: solve_case(name, f) for name, f in appliers.items()}


def is_seismic(combo: cb.Combination) -> bool:
    """Say whether a combination contains an earthquake case.

    Args:
        combo: A combination.

    Returns:
        True if any case name starts with ``"E_"``.
    """
    return any(c.startswith("E_") for c in combo.factors)


#: Thesis gravity and wind combinations (the first five of Th s8.7).
GRAVITY_WIND_COMBINATIONS: tuple[cb.Combination, ...] = tuple(
    c for c in cb.THESIS_COMBINATIONS if not is_seismic(c))

#: The thesis set (reading rule 2).
PRIMARY_COMBINATIONS: tuple[cb.Combination, ...] = cb.THESIS_COMBINATIONS

#: Sensitivity set: the seismic combinations with the GB 55002-2021 factors
#: 1.3 / 1.4 (flag D21; reading rule 9).
CODE_SEISMIC_SET: tuple[cb.Combination, ...] = GRAVITY_WIND_COMBINATIONS + cb.CODE_SEISMIC_COMBINATIONS


# ---------------------------------------------------------------------------
# Beams (reading rules 3-5)
# ---------------------------------------------------------------------------

#: Design locations of a beam: (location, steel face).
BEAM_LOCATIONS: tuple[tuple[str, str], ...] = (
    ("left end", "top"), ("left end", "bottom"), ("middle", "bottom"),
    ("right end", "top"), ("right end", "bottom"))


@dataclass(frozen=True)
class BeamDemand:
    """Largest design moment at one beam location over a set of combinations.

    Attributes:
        m_knm: Moment, gamma_RE applied for seismic combinations, >= 0 [kN*m].
        combination: Name of the governing combination ("none" if all are 0).
    """

    m_knm: float
    combination: str


def face_index(span: str, n_nodes: int, at_face: bool) -> int:
    """Return the node index of the left design section of a beam.

    Args:
        span: Span label (AB, BC, CD).
        n_nodes: Number of nodes along the beam.
        at_face: True for the column face, False for the centre-line node.

    Returns:
        Node index; the right section is ``n_nodes - 1 - index``.

    Raises:
        ValueError: If no node lies on the column face.
    """
    if not at_face:
        return 0
    length = af.SPANS_M[af.SPAN_LABELS.index(span)]
    step = length / (n_nodes - 1)
    k = round(COLUMN_HALF_WIDTH_M / step)
    if abs(k * step - COLUMN_HALF_WIDTH_M) > 1e-9:
        raise ValueError(f"no node on the column face of span {span}")
    return k


def beam_demands(cases: dict[str, CaseResult], combos: tuple[cb.Combination, ...],
                 at_face: bool = True) -> dict[tuple[str, int, str, str], BeamDemand]:
    """Envelope the design moments of every beam location over the combinations.

    Args:
        cases: Solved load cases.
        combos: Combinations to envelope.
        at_face: Design sections at the column faces (True, reading rule 3)
            or at the centre-lines (False, sensitivity).

    Returns:
        (span, level, location, face) -> BeamDemand.
    """
    effects = {n: c.effects() for n, c in cases.items()}
    combined = {c.name: (cb.combine(effects, c), GAMMA_RE_BEAM_FLEXURE if is_seismic(c) else 1.0)
                for c in combos}
    out = {}
    for (span, lvl), ms in cases["D"].moments.items():
        n = len(ms)
        kl = face_index(span, n, at_face)
        kr = n - 1 - kl
        best = {loc: BeamDemand(0.0, "none") for loc in BEAM_LOCATIONS}
        for name, (eff, g) in combined.items():
            m = [eff[("M", span, lvl, k)] for k in range(n)]
            values = {
                ("left end", "top"): max(0.0, -m[kl]) * g,
                ("left end", "bottom"): max(0.0, m[kl]) * g,
                ("middle", "bottom"): max(0.0, max(m[kl:kr + 1])) * g,
                ("right end", "top"): max(0.0, -m[kr]) * g,
                ("right end", "bottom"): max(0.0, m[kr]) * g,
            }
            for loc, v in values.items():
                if v > best[loc].m_knm:
                    best[loc] = BeamDemand(v, name)
        for (loc, face), d in best.items():
            out[(span, lvl, loc, face)] = d
    return out


def design_beam_location(span: str, location: str, m_knm: float) -> SectionDesign:
    """Design one beam location for a moment (section from the spec).

    Args:
        span: Span label.
        location: ``"left end"``, ``"middle"`` or ``"right end"``.
        m_knm: Design moment [kN*m].

    Returns:
        A SectionDesign.
    """
    b, h = (1000.0 * x for x in af.BEAM_BH_M[span])
    at_end = location != "middle"
    return design_section(m_knm, b, h, "support" if at_end else "mid-span", at_end)


def beam_design_rows(cases: dict[str, CaseResult]) -> list[dict]:
    """Build ``results/anchor_design_beams.csv``: every beam location of the frame.

    Args:
        cases: Solved load cases.

    Returns:
        One dict per (level, span, location, face).
    """
    primary = beam_demands(cases, PRIMARY_COMBINATIONS)
    centre = beam_demands(cases, PRIMARY_COMBINATIONS, at_face=False)
    code = beam_demands(cases, CODE_SEISMIC_SET)
    rows = []
    for key in sorted(primary, key=lambda k: (k[1], af.SPAN_LABELS.index(k[0]),
                                               BEAM_LOCATIONS.index((k[2], k[3])))):
        span, lvl, loc, face = key
        d = design_beam_location(span, loc, primary[key].m_knm)
        dc = design_beam_location(span, loc, centre[key].m_knm)
        dk = design_beam_location(span, loc, code[key].m_knm)
        rows.append({
            "level [text]": lvl,
            "span [text]": span,
            "location [text]": loc,
            "steel [text]": face,
            "M_design [kN*m]": round(d.m_knm, 2),
            "governing_combination [text]": primary[key].combination,
            "xi [-]": round(d.xi, 4),
            "status [text]": d.status,
            "As_calc [mm2]": round(d.as_calc_mm2, 1),
            "As_min [mm2]": round(d.as_min_mm2, 1),
            "As_req [mm2]": round(d.as_req_mm2, 1),
            "M_centreline [kN*m]": round(dc.m_knm, 2),
            "As_req_centreline [mm2]": round(dc.as_req_mm2, 1),
            "M_code_seismic [kN*m]": round(dk.m_knm, 2),
            "As_req_code_seismic [mm2]": round(dk.as_req_mm2, 1),
        })
    return rows


#: Thesis s9.2 floor label -> model level (decision B4: "5" is the roof).
THESIS_FLOOR_TO_LEVEL: dict[str, int] = {"5": 4, "1": 1}

#: Thesis s9.2 location -> (model location, steel face) (reading rule 7).
THESIS_LOCATION: dict[str, tuple[str, str]] = {
    "left end": ("left end", "top"), "middle": ("middle", "bottom"),
    "right end": ("right end", "top")}


def read_thesis_beam_steel(repo_root: Path) -> list[dict]:
    """Read the typed s9.2 beam table.

    Args:
        repo_root: Repository root.

    Returns:
        The rows of ``validation/thesis_values/beam_steel_areas.csv``.
    """
    path = repo_root / "validation" / "thesis_values" / "beam_steel_areas.csv"
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def beam_check_rows(cases: dict[str, CaseResult], thesis: list[dict]) -> list[dict]:
    """Build ``results/anchor_design_check.csv``: thesis beam steel against the code.

    Check (a) sets the model's requirement against the printed A_s,prov and
    the printed bars; check (b) puts the thesis's own printed "gammaRE x M"
    through the same formula (reading rule 8). Sensitivity flags use
    centre-line moments and the GB 55002 seismic factors (rule 9).

    Args:
        cases: Solved load cases.
        thesis: Rows from ``read_thesis_beam_steel``.

    Returns:
        One dict per thesis row.
    """
    primary = beam_demands(cases, PRIMARY_COMBINATIONS)
    centre = beam_demands(cases, PRIMARY_COMBINATIONS, at_face=False)
    code = beam_demands(cases, CODE_SEISMIC_SET)
    rows = []
    for t in thesis:
        lvl = THESIS_FLOOR_TO_LEVEL[t["floor_printed [text]"]]
        span = t["span [text]"]
        loc, face = THESIS_LOCATION[t["section [text]"]]
        key = (span, lvl, loc, face)
        d = design_beam_location(span, loc, primary[key].m_knm)
        dc = design_beam_location(span, loc, centre[key].m_knm)
        dk = design_beam_location(span, loc, code[key].m_knm)
        prov = float(t["As_prov [mm2]"])
        bars = bar_area_mm2(t["bars [text]"])
        provided = min(prov, bars)

        def short(req: float) -> str:
            """Name what falls short of a requirement (empty if nothing)."""
            parts = []
            if prov < req:
                parts.append("printed As_prov")
            if bars < req:
                parts.append("bars")
            return " and ".join(parts)

        own = design_beam_location(span, loc, float(t["gammaRE_M [kN*m]"]))
        own_075 = design_beam_location(span, loc, GAMMA_RE_BEAM_FLEXURE * float(t["M [kN*m]"]))
        rows.append({
            "floor_printed [text]": t["floor_printed [text]"],
            "level [text]": lvl,
            "span [text]": span,
            "location [text]": loc,
            "steel [text]": face,
            "thesis_M [kN*m]": float(t["M [kN*m]"]),
            "thesis_gammaRE_M [kN*m]": float(t["gammaRE_M [kN*m]"]),
            "thesis_As_req [mm2]": float(t["As_req [mm2]"]),
            "thesis_As_prov [mm2]": prov,
            "thesis_bars [text]": t["bars [text]"],
            "bars_area [mm2]": round(bars, 1),
            "thesis_As_min [mm2]": float(t["As_min [mm2]"]),
            "model_M_design [kN*m]": round(d.m_knm, 2),
            "model_governing [text]": primary[key].combination,
            "model_status [text]": d.status,
            "model_As_req [mm2]": round(d.as_req_mm2, 1),
            "code_As_min [mm2]": round(d.as_min_mm2, 1),
            "provided_over_required [-]": round(provided / d.as_req_mm2, 3),
            "flag_a [text]": "yes" if short(d.as_req_mm2) else "no",
            "flag_a_short [text]": short(d.as_req_mm2) or "none",
            "check_b_As_calc [mm2]": round(own.as_calc_mm2, 1),
            "check_b_As_req [mm2]": round(own.as_req_mm2, 1),
            "check_b_calc_over_thesis_As_req [-]": round(own.as_calc_mm2 / float(t["As_req [mm2]"]), 3),
            "flag_b [text]": "yes" if short(own.as_req_mm2) else "no",
            "info_As_req_0.75M [mm2]": round(own_075.as_req_mm2, 1),
            "info_short_0.75M [text]": short(own_075.as_req_mm2) or "none",
            "sens_flag_centreline [text]": "yes" if short(dc.as_req_mm2) else "no",
            "sens_flag_code_seismic [text]": "yes" if short(dk.as_req_mm2) else "no",
            "thesis_flags [text]": t["flag [text]"],
        })
    return rows


# ---------------------------------------------------------------------------
# Columns (reading rules 5-7)
# ---------------------------------------------------------------------------

#: Column bars as designed (spec R1, decision B6: 4C22 in every column).
THESIS_COLUMN_BARS: str = "4C22"

#: Column bar sets to check for the ratio only (rule 7): source -> bars.
COLUMN_BAR_SETS: dict[str, str] = {
    "Th s9.3, spec R1 (all columns, decision B6)": "4C22",
    "Dwg 01, KZ-2, floors 2 and 4": "4C20",
    "Dwg 01, KZ-3, floors 2 and 4": "4C25",
}


def column_steel_ratios(bars: str) -> tuple[float, float]:
    """Return the total and one-side steel ratios of a 600 x 600 column with corner bars.

    With four bars, one in each corner, each side holds two bars.

    Args:
        bars: Bar group such as ``"4C22"``.

    Returns:
        (total ratio, one-side ratio) as fractions of b x h.
    """
    b, h = (1000.0 * x for x in af.COLUMN_BH_M)
    a = bar_area_mm2(bars)
    n = int(re.match(r"\s*(\d+)", bars).group(1))
    if n != 4:
        raise ValueError("only four corner bars are handled")
    return a / (b * h), 2.0 * a / n / (b * h)


def column_steel_flag(rho: float, rho_side: float) -> str:
    """Say which column minimum-steel rule a column fails (Table 11.4.12-1).

    Args:
        rho: Total steel ratio [-].
        rho_side: Steel ratio of one side [-].

    Returns:
        ``"no"``, or ``"yes: "`` followed by the rules that fail.
    """
    short = []
    if rho < RHO_MIN_COLUMN_TOTAL:
        short.append("total steel below minimum")
    if rho_side < RHO_MIN_COLUMN_SIDE:
        short.append("one side below minimum")
    return "yes: " + " and ".join(short) if short else "no"


def column_rows(cases: dict[str, CaseResult]) -> list[dict]:
    """Build ``results/anchor_design_columns.csv``: axial ratio and minimum steel.

    Args:
        cases: Solved load cases.

    Returns:
        One dict per column (axis, storey), ground storey first.
    """
    effects = {n: c.effects() for n, c in cases.items()}
    prim = {c.name: cb.combine(effects, c) for c in PRIMARY_COMBINATIONS}
    code = {c.name: cb.combine(effects, c) for c in cb.CODE_SEISMIC_COMBINATIONS}
    b, h = (1000.0 * x for x in af.COLUMN_BH_M)
    area = b * h
    rho, rho_side = column_steel_ratios(THESIS_COLUMN_BARS)
    rows = []
    for storey in range(1, len(af.STOREY_HEIGHTS_M) + 1):
        for ax in af.AXES:
            key = ("N", ax, str(storey), "bottom")
            seis = {n: e[key] for n, e in prim.items()
                    if is_seismic(next(c for c in PRIMARY_COMBINATIONS if c.name == n))}
            grav = {n: e[key] for n, e in prim.items() if n not in seis}
            n_s = max(seis, key=seis.get)
            n_g = max(grav, key=grav.get)
            mu = seis[n_s] * 1.0e3 / (FC_N_MM2 * area)
            mu_code = max(code.values(), key=lambda e: e[key])[key] * 1.0e3 / (FC_N_MM2 * area)
            rows.append({
                "storey [text]": storey,
                "axis [text]": ax,
                "N_seismic [kN]": round(seis[n_s], 2),
                "seismic_combination [text]": n_s,
                "axial_ratio [-]": round(mu, 4),
                "axial_ratio_limit [-]": AXIAL_RATIO_LIMIT,
                "axial_ratio_ok [text]": "yes" if mu <= AXIAL_RATIO_LIMIT else "no",
                "axial_ratio_code_seismic [-]": round(mu_code, 4),
                "N_gravity_max [kN]": round(grav[n_g], 2),
                "gravity_combination [text]": n_g,
                "bars [text]": THESIS_COLUMN_BARS,
                "rho_total [%]": round(100.0 * rho, 3),
                "rho_total_min [%]": round(100.0 * RHO_MIN_COLUMN_TOTAL, 3),
                "rho_side [%]": round(100.0 * rho_side, 3),
                "rho_side_min [%]": round(100.0 * RHO_MIN_COLUMN_SIDE, 3),
                "As_min_total [mm2]": round(RHO_MIN_COLUMN_TOTAL * area, 1),
                "flag [text]": column_steel_flag(rho, rho_side),
            })
    return rows


def column_bar_set_rows() -> list[dict]:
    """Build ``results/anchor_design_column_bars.csv``: each drawn bar set against the minimum.

    Returns:
        One dict per bar set in ``COLUMN_BAR_SETS``.
    """
    rows = []
    for src, bars in COLUMN_BAR_SETS.items():
        rho, side = column_steel_ratios(bars)
        rows.append({
            "source [text]": src,
            "bars [text]": bars,
            "As [mm2]": round(bar_area_mm2(bars), 1),
            "rho_total [%]": round(100.0 * rho, 3),
            "rho_side [%]": round(100.0 * side, 3),
            "meets_total_min_0.75 [text]": "yes" if rho >= RHO_MIN_COLUMN_TOTAL else "no",
            "meets_side_min_0.20 [text]": "yes" if side >= RHO_MIN_COLUMN_SIDE else "no",
        })
    return rows


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------


def anchor_forces(repo_root: Path) -> tuple[list[float], list[float]]:
    """Return the wind and earthquake storey forces of the anchor (reading rule 1).

    Args:
        repo_root: Repository root.

    Returns:
        (W_k as printed in Table 8-2, F_i of the base-shear method with
        psi_T = ``seismic.ANCHOR_PSI_T``), level 1 first [kN].
    """
    wind = [t.w_kn for t in aw.read_thesis_wind(repo_root)]
    quake = s.run_base_shear(psi_t=s.ANCHOR_PSI_T).forces_kn
    return wind, quake


def main(repo_root: Path | None = None) -> dict[str, list[dict]]:
    """Run the design checks and save the tables.

    Writes to ``results/``: ``anchor_design_beams.csv`` (every beam
    location), ``anchor_design_check.csv`` (the s9.2 rows with flags),
    ``anchor_design_columns.csv`` (axial ratio and minimum steel) and
    ``anchor_design_column_bars.csv`` (the drawn column bar sets).

    Args:
        repo_root: Repository root; defaults to two levels above this file's
            package folder.

    Returns:
        The rows written, keyed ``"beams"``, ``"check"``, ``"columns"`` and
        ``"column_bars"``.
    """
    root = repo_root or Path(__file__).resolve().parents[2]
    out = root / "results"
    wind, quake = anchor_forces(root)
    cases = run_cases(wind, quake)
    tables = {
        "beams": beam_design_rows(cases),
        "check": beam_check_rows(cases, read_thesis_beam_steel(root)),
        "columns": column_rows(cases),
        "column_bars": column_bar_set_rows(),
    }
    af.write_csv(tables["beams"], out / "anchor_design_beams.csv")
    af.write_csv(tables["check"], out / "anchor_design_check.csv")
    af.write_csv(tables["columns"], out / "anchor_design_columns.csv")
    af.write_csv(tables["column_bars"], out / "anchor_design_column_bars.csv")
    return tables


if __name__ == "__main__":
    t = main()
    for r in t["check"]:
        print(f"fl{r['floor_printed [text]']} {r['span [text]']} {r['location [text]']:9s} "
              f"{r['steel [text]']:6s} M {r['model_M_design [kN*m]']:7.2f} "
              f"req {r['model_As_req [mm2]']:7.1f} prov {r['thesis_As_prov [mm2]']:6.0f} "
              f"bars {r['bars_area [mm2]']:6.0f} a:{r['flag_a [text]']} b:{r['flag_b [text]']}")
    for r in t["columns"]:
        print(f"col {r['axis [text]']}{r['storey [text]']} N {r['N_seismic [kN]']:8.1f} "
              f"mu {r['axial_ratio [-]']:.3f} ok {r['axial_ratio_ok [text]']} {r['flag [text]']}")
