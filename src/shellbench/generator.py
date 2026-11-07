"""Size a regular RC frame from building inputs, following docs/design_rules.md.

File: src/shellbench/generator.py

Playbook Day 16. The generator takes the inputs of one building (storeys,
spans, storey heights, seismic input, loads) and returns member sizes, steel,
drift and check results and frame quantities. It works on one transverse
2D frame with a tributary width, as the anchor does; the whole-building
plan is Day 18's batch runner.

Each step names the rule it implements (R1-R16 of docs/design_rules.md).
Values marked [J] there are choices, not code; values marked [?] are
cited but not yet opened. Nothing in this module is a thesis result: the
thesis inputs live in the test, with their sources.

Units: kN, m, kN/m^2 for loads; mm and mm^2 for sections and steel.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import openseespy.opensees as ops

from shellbench import capacity as cap
from shellbench import checks as c
from shellbench import seismic as s

SIZE_STEP_MM = 50  # R15, playbook
CONCRETE_UNIT_WEIGHT_KN_M3 = 25.0  # GB 50009 Appendix A [?]; thesis s4.1 uses 25
G_E_LIVE_FACTOR = 0.5  # GB 50011 Table 5.1.3 (floor live; roof live excluded)
GAMMA_G_SEISMIC = 1.3  # GB 55002-2021 cl. 4.3.2, Table 4.3.2-1 (R9)
GAMMA_EH = 1.4  # GB 55002-2021 cl. 4.3.2, Table 4.3.2-2 (R9)
GAMMA_D = 1.3  # GB 55001-2021 cl. 3.1.13 item 1 (R9)
GAMMA_L = 1.5  # GB 55001-2021 cl. 3.1.13 item 4 (R9)
#: Elastic storey drift limit of an RC frame, GB 50011-2010 Table 5.5.1 (English
#: edition, p. 40; checked: S. N. R. Hasib, 5 Nov 2026 from the IISEE copy) (R11).
DRIFT_LIMIT = 1.0 / 550.0
#: Beam section limits, GB 50011-2010 cl. 6.3.1 (English edition, p. 55; checked:
#: S. N. R. Hasib, 5 Nov 2026): b >= 200 mm, h/b <= 4, clear span/h >= 4.
BEAM_MIN_B_MM = 200
BEAM_MAX_H_OVER_B = 4.0
BEAM_MIN_CLEAR_SPAN_OVER_H = 4.0
PRELIM_GRAVITY_KN_M2 = 14.0  # Th s2.4, load per floor for preliminary sizing (R5)
PRELIM_BETA_EDGE = 1.3  # Th s2.4 (R5)
PRELIM_BETA_INTERIOR = 1.25  # Th s2.4 (R5)
SLAB_MIN_MM = 120  # R3 decision 1, 31 Oct 2026 [J]
SLAB_SPAN_RATIO_TWO_WAY = 40.0  # Th s2.1; GB 50010 cl. 9.1.2 [?] (R3)
BEAM_SPAN_RATIO = 12.0  # R4 [J], within Th s2.3's L/14 to L/8
BEAM_MIN_WIDTH_MM = 250  # R4 [J]
COLUMN_GROWTH_LIMIT = 1.5  # R11 stopping rule of the "columns_first" rule [J]
#: R11 drift-fix rules (decision card 2, 5 Nov 2026 [J]). "best_ratio" is the
#: default; "columns_first" is the rule of 4 Nov, kept for the sensitivity run.
DRIFT_RULES = ("best_ratio", "columns_first")
BAR_DIAMETERS_MM = (12, 14, 16, 18, 20, 22, 25, 28, 32)  # R15 [J]; GB 1499.2 [?]
BARS_PER_LAYER = (2, 6)  # R15 [J], 300 mm beam
MAX_ITERATIONS = 40


@dataclass
class BuildingInput:
    """One building, as the generator sees it (Day 16 playbook inputs).

    Attributes:
        spans_m: Transverse bay spans, left to right [m].
        storey_heights_m: Ground storey first [m].
        tributary_width_m: Frame spacing carried by this frame [m].
        slab_panel_m: Short side of a slab panel, for R3 [m].
        floor_dead_kn_m2: Floor finishes + slab, per plan area [kN/m^2].
        roof_dead_kn_m2: Roof build-up + slab [kN/m^2].
        live_kn_m2: Floor live load for each span [kN/m^2].
        roof_live_kn_m2: Roof live load [kN/m^2].
        floor_secondary_kn_m: Secondary beam self-weight per span, floors [kN/m].
        roof_secondary_kn_m: Secondary beam self-weight per span, roof [kN/m].
        floor_beam_wall_kn_m: Wall standing on the frame beam, per span [kN/m].
        exterior_wall_kn_m: Wall on the longitudinal beams of the edge lines [kN/m].
        interior_wall_kn_m: Wall on the longitudinal beams of the inner lines [kN/m].
        longitudinal_beam_kn_m: Longitudinal beam self-weight, every line [kN/m].
        parapet_kn_m: Roof parapet on the edge lines [kN/m].
        alpha_max: Frequent-earthquake alpha_max (GB 50011 Table 5.1.4-1).
        tg_s: Site characteristic period [s].
        psi_t: Period reduction factor for infill (R8).
        concrete_e_mpa: Young's modulus of the concrete [MPa].
        beam_i_factor: Slab contribution to beam stiffness (spec M7).
        axial_ratio_limit: Column axial ratio limit for the seismic grade (R6).
        seismic_grade: Seismic grade of the frame, 1-4 (R14); 3 is the anchor.
    """

    spans_m: tuple[float, ...]
    storey_heights_m: tuple[float, ...]
    tributary_width_m: float
    slab_panel_m: float
    floor_dead_kn_m2: float
    roof_dead_kn_m2: float
    live_kn_m2: tuple[float, ...]
    roof_live_kn_m2: float
    floor_secondary_kn_m: tuple[float, ...]
    roof_secondary_kn_m: tuple[float, ...]
    floor_beam_wall_kn_m: tuple[float, ...]
    exterior_wall_kn_m: float
    interior_wall_kn_m: float
    longitudinal_beam_kn_m: float
    parapet_kn_m: float
    alpha_max: float
    tg_s: float
    psi_t: float
    concrete_e_mpa: float
    beam_i_factor: float
    axial_ratio_limit: float = c.AXIAL_RATIO_LIMIT
    seismic_grade: int = 3


@dataclass
class Sizes:
    """Member sizes [mm]: one square column size, one beam (b, h) per span."""

    column_mm: int
    beams_mm: list[tuple[int, int]]
    slab_mm: int


@dataclass
class GeneratorResult:
    """What the generator returns.

    Attributes:
        preliminary: Sizes from R3-R5, before any check.
        final: Sizes after the R11-R13 loop.
        history: One line per sizing pass, plus one per resize naming the rule.
        period_s: T1 of the final frame, after psi_t [s].
        drift_ratios: Largest elastic storey drift ratio per storey [-].
        axial_ratio: Largest column axial ratio [-].
        beam_steel: (span index, location) -> (As required, bars) [mm^2].
        column_steel: (As required, bars) for every column [mm^2].
        quantities: Concrete [m^3] and bar steel [kg] per m^2 of floor.
        capacity: R14 outcome (column bars, stirrups, demands); empty when
            the generator ran with ``capacity_design=False``.
    """

    preliminary: Sizes
    final: Sizes
    history: list[str]
    period_s: float
    drift_ratios: list[float]
    axial_ratio: float
    beam_steel: dict[tuple[int, str], tuple[float, str]] = field(default_factory=dict)
    column_steel: tuple[float, str] = (0.0, "")
    quantities: dict[str, float] = field(default_factory=dict)
    capacity: dict = field(default_factory=dict)


def round_up(value_mm: float, step: int = SIZE_STEP_MM) -> int:
    """Round a size up to the next multiple of ``step`` mm (R15)."""
    return int(math.ceil(value_mm / step - 1e-9) * step)


# ---------------------------------------------------------------------------
# Preliminary sizes (R3-R5)
# ---------------------------------------------------------------------------


def slab_thickness_mm(panel_m: float) -> int:
    """R3: max(l/40, 120 mm) for a two-way panel, rounded up to 10 mm."""
    return max(SLAB_MIN_MM, round_up(panel_m * 1000.0 / SLAB_SPAN_RATIO_TWO_WAY, 10))


def beam_size_mm(span_m: float) -> tuple[int, int]:
    """R4: h = L/12 and b = h/2 (at least 250 mm), both rounded up to 50 mm."""
    h = round_up(span_m * 1000.0 / BEAM_SPAN_RATIO)
    return max(BEAM_MIN_WIDTH_MM, round_up(h / 2.0)), h


def preliminary_column_mm(b: BuildingInput) -> int:
    """R5: A >= beta g A_trib n / (mu_lim f_c), square, rounded up to 50 mm.

    Every column takes the size of the largest (Th s2.4). The tributary
    area of a column is half of each adjacent span times the frame spacing.
    """
    n = len(b.storey_heights_m)
    spans = (0.0, *b.spans_m, 0.0)
    a_req = 0.0
    for k in range(len(b.spans_m) + 1):
        edge = k in (0, len(b.spans_m))
        beta = PRELIM_BETA_EDGE if edge else PRELIM_BETA_INTERIOR
        area = (spans[k] + spans[k + 1]) / 2.0 * b.tributary_width_m
        n_kn = beta * area * PRELIM_GRAVITY_KN_M2 * n
        a_req = max(a_req, n_kn * 1e3 / (b.axial_ratio_limit * c.FC_N_MM2))
    return round_up(math.sqrt(a_req))


def preliminary_sizes(b: BuildingInput) -> Sizes:
    """R3-R5 together."""
    return Sizes(preliminary_column_mm(b), [beam_size_mm(L) for L in b.spans_m],
                 slab_thickness_mm(b.slab_panel_m))


# ---------------------------------------------------------------------------
# The 2D frame (R10)
# ---------------------------------------------------------------------------


@dataclass
class Frame:
    """Node and element numbers of the OpenSeesPy model."""

    xs: list[float]
    ys: list[float]
    node: dict[tuple[int, int], int]
    beams: dict[tuple[int, int], int]  # (level, span) -> element
    columns: dict[tuple[int, int], int]  # (storey, line) -> element


def build(b: BuildingInput, z: Sizes) -> Frame:
    """Build the elastic frame: fixed base, rigid joints, centre-line model."""
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    e = b.concrete_e_mpa * 1e3  # kN/m^2
    xs = [0.0]
    for L in b.spans_m:
        xs.append(xs[-1] + L)
    ys = [0.0]
    for h in b.storey_heights_m:
        ys.append(ys[-1] + h)
    node = {}
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            tag = 100 * j + i + 1
            node[(j, i)] = tag
            ops.node(tag, x, y)
            if j == 0:
                ops.fix(tag, 1, 1, 1)
    ops.geomTransf("Linear", 1)
    a_col = (z.column_mm / 1000.0) ** 2
    i_col = (z.column_mm / 1000.0) ** 4 / 12.0
    columns, beams = {}, {}
    for j in range(1, len(ys)):
        for i in range(len(xs)):
            tag = 10000 + 100 * j + i
            ops.element("elasticBeamColumn", tag, node[(j - 1, i)], node[(j, i)], a_col, e, i_col, 1)
            columns[(j, i)] = tag
        for k, (bw, h) in enumerate(z.beams_mm):
            tag = 20000 + 100 * j + k
            a, i_b = bw * h / 1e6, b.beam_i_factor * (bw / 1000.0) * (h / 1000.0) ** 3 / 12.0
            ops.element("elasticBeamColumn", tag, node[(j, k)], node[(j, k + 1)], a, e, i_b, 1)
            beams[(j, k)] = tag
    return Frame(xs, ys, node, beams, columns)


def beam_line_loads(b: BuildingInput, z: Sizes, level: int, case: str) -> list[float]:
    """Uniform beam loads [kN/m] for one level and one case ("D", "L" or "GE").

    The slab load is the area load times the tributary width (the
    equivalent-uniform route of the anchor [J]); beam self-weight is the web
    below the slab. The secondary beam of the bay is spread the same way [J],
    and the wall standing on the frame beam is added on floors (R8).
    """
    roof = level == len(b.storey_heights_m)
    out = []
    for k, (bw, h) in enumerate(z.beams_mm):
        dead = (b.roof_dead_kn_m2 if roof else b.floor_dead_kn_m2) * b.tributary_width_m
        dead += CONCRETE_UNIT_WEIGHT_KN_M3 * bw / 1000.0 * (h - z.slab_mm) / 1000.0
        dead += b.roof_secondary_kn_m[k] if roof else b.floor_secondary_kn_m[k] + b.floor_beam_wall_kn_m[k]
        live = (b.roof_live_kn_m2 if roof else b.live_kn_m2[k]) * b.tributary_width_m
        if case == "D":
            out.append(dead)
        elif case == "L":
            out.append(live)
        else:  # G_E: roof live excluded
            out.append(dead + (0.0 if roof else G_E_LIVE_FACTOR * live))
    return out


def column_weight_kn(z: Sizes, height_m: float) -> float:
    """Self-weight of one column over one storey [kN]."""
    return CONCRETE_UNIT_WEIGHT_KN_M3 * (z.column_mm / 1000.0) ** 2 * height_m


def joint_dead_kn(b: BuildingInput, z: Sizes, level: int) -> list[float]:
    """Dead load carried to each column line by the longitudinal members (R8) [kN].

    Clear length is the frame spacing less one column, and the parapet runs the
    full spacing (both as Th s5.2). The slab shares printed in Th s5.2 are left
    out, because ``beam_line_loads`` already puts the whole slab on the frame.
    """
    clear_m = b.tributary_width_m - z.column_mm / 1000.0
    roof = level == len(b.storey_heights_m)
    out = []
    for i in range(len(b.spans_m) + 1):
        edge = i in (0, len(b.spans_m))
        load = b.longitudinal_beam_kn_m * clear_m
        if roof:
            load += b.parapet_kn_m * b.tributary_width_m if edge else 0.0
        else:
            load += (b.exterior_wall_kn_m if edge else b.interior_wall_kn_m) * clear_m
        out.append(load)
    return out


def apply_gravity(fm: Frame, b: BuildingInput, z: Sizes, case: str) -> None:
    """Beam line loads, plus column weight and longitudinal loads at the joints (D, G_E)."""
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    for j in range(1, len(fm.ys)):
        for k, w in enumerate(beam_line_loads(b, z, j, case)):
            ops.eleLoad("-ele", fm.beams[(j, k)], "-type", "-beamUniform", -w)
        if case in ("D", "GE"):
            wc = column_weight_kn(z, b.storey_heights_m[j - 1])
            for i, joint in enumerate(joint_dead_kn(b, z, j)):
                ops.load(fm.node[(j, i)], 0.0, -(wc + joint), 0.0)


def solve() -> None:
    """Linear static solution of the current pattern."""
    ops.system("BandGeneral")
    ops.numberer("RCM")
    ops.constraints("Plain")
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")
    if ops.analyze(1) != 0:
        raise RuntimeError("static analysis failed")


def storey_weights_kn(b: BuildingInput, z: Sizes) -> list[float]:
    """G_i per level: beam G_E loads, joint dead loads, half the columns above and below."""
    out = []
    n = len(b.storey_heights_m)
    for j in range(1, n + 1):
        g = sum(w * L for w, L in zip(beam_line_loads(b, z, j, "GE"), b.spans_m))
        g += sum(joint_dead_kn(b, z, j))
        cols = len(b.spans_m) + 1
        g += cols * column_weight_kn(z, b.storey_heights_m[j - 1]) / 2.0
        if j < n:
            g += cols * column_weight_kn(z, b.storey_heights_m[j]) / 2.0
        out.append(g)
    return out


def period_s(b: BuildingInput, z: Sizes, weights_kn: list[float]) -> float:
    """First-mode period with G_i / g lumped horizontally at each level's nodes."""
    fm = build(b, z)
    for j, g in enumerate(weights_kn, start=1):
        m = g / 9.81 / len(fm.xs)
        for i in range(len(fm.xs)):
            ops.mass(fm.node[(j, i)], m, 0.0, 0.0)
    lam = ops.eigen("-fullGenLapack", 1)[0]
    return 2.0 * math.pi / math.sqrt(lam)


@dataclass
class CaseForces:
    """Beam end moments (sagging positive), column forces and floor sway.

    column_m holds the column end moments (bottom, top) on the member,
    anticlockwise positive (global sense, as eleForce); column_v the shear
    at the bottom end [kN]. column_n is the axial force at the bottom end,
    compression positive.
    """

    beam_m: dict[tuple[int, int], tuple[float, float]]
    beam_v: dict[tuple[int, int], tuple[float, float]]
    column_n: dict[tuple[int, int], float]
    level_u: list[float]
    column_m: dict[tuple[int, int], tuple[float, float]] = field(default_factory=dict)
    column_v: dict[tuple[int, int], float] = field(default_factory=dict)


def read_forces(fm: Frame) -> CaseForces:
    """Read member forces from the solved model.

    For a 2D elasticBeamColumn, eleForce gives the end forces on the member
    in global axes. Sagging-positive bending is -M at the i-end and +M at
    the j-end.
    """
    bm, bv = {}, {}
    for key, tag in fm.beams.items():
        f = ops.eleForce(tag)
        bm[key] = (-f[2], f[5])
        bv[key] = (f[1], -f[4])
    cn, cm, cv = {}, {}, {}
    for key, tag in fm.columns.items():
        f = ops.eleForce(tag)
        cn[key] = f[1]
        cm[key] = (f[2], f[5])
        cv[key] = f[0]
    lu = [sum(ops.nodeDisp(fm.node[(j, i)], 1) for i in range(len(fm.xs))) / len(fm.xs)
          for j in range(len(fm.ys))]
    return CaseForces(bm, bv, cn, lu, cm, cv)


def run_case(b: BuildingInput, z: Sizes, case: str, lateral_kn: list[float] | None = None
             ) -> CaseForces:
    """Run one load case: "D", "L", "GE" or "E" (lateral forces from the left)."""
    fm = build(b, z)
    if case == "E":
        ops.timeSeries("Linear", 1)
        ops.pattern("Plain", 1, 1)
        for j, f in enumerate(lateral_kn, start=1):
            ops.load(fm.node[(j, 0)], f, 0.0, 0.0)
    else:
        apply_gravity(fm, b, z, case)
    solve()
    return read_forces(fm)


# ---------------------------------------------------------------------------
# Checks and the resize loop (R11-R13)
# ---------------------------------------------------------------------------


def seismic_forces(b: BuildingInput, z: Sizes) -> tuple[float, list[float]]:
    """T1 (with psi_t) and the base-shear-method storey forces (R8)."""
    g = storey_weights_kn(b, z)
    t1 = b.psi_t * period_s(b, z, g)
    alpha = s.alpha_spectrum(t1, b.alpha_max, b.tg_s)
    f_ek = alpha * 0.85 * sum(g)
    heights = [sum(b.storey_heights_m[:j]) for j in range(1, len(g) + 1)]
    return t1, s.storey_forces(g, heights, f_ek, s.top_additional_factor(t1, b.tg_s))


def drift_ratios(b: BuildingInput, quake: CaseForces) -> list[float]:
    """Elastic storey drift ratio per storey under E (R11)."""
    u = quake.level_u
    return [abs(u[j] - u[j - 1]) / b.storey_heights_m[j - 1] for j in range(1, len(u))]


def face_moment(m: float, v: float, half_column_m: float) -> float:
    """Moment at the column face from the centre-line end moment and shear [J].

    Linear reduction over half a column width: |M| - |V| a, never below 0,
    keeping the sign of the centre-line moment.
    """
    reduced = max(0.0, abs(m) - abs(v) * half_column_m)
    return math.copysign(reduced, m)


def beam_design_moments(b: BuildingInput, z: Sizes, cases: dict[str, CaseForces]
                        ) -> dict[tuple[int, int, str], float]:
    """Design moments [kN m] per beam (level, span) and location (R13).

    Ends: the worse of hogging and sagging over 1.3D + 1.5L and
    1.3 G_E +- 1.4 E, times gamma_RE for the seismic ones. Mid-span: the
    simply supported moment less the mean end moment under 1.3D + 1.5L.
    """
    a = z.column_mm / 2000.0
    out = {}
    for key in cases["D"].beam_m:
        j, k = key
        span = b.spans_m[k]
        for end in (0, 1):
            def fm(case: str) -> float:
                return face_moment(cases[case].beam_m[key][end], cases[case].beam_v[key][end], a)
            grav = GAMMA_D * fm("D") + GAMMA_L * fm("L")
            seis = [c.GAMMA_RE_BEAM_FLEXURE * (GAMMA_G_SEISMIC * fm("GE") + sign * GAMMA_EH * fm("E"))
                    for sign in (1.0, -1.0)]
            hog = -min(0.0, grav, *seis)
            sag = max(0.0, grav, *seis)
            out[(j, k, ("left" if end == 0 else "right") + " top")] = hog
            out[(j, k, ("left" if end == 0 else "right") + " bottom")] = sag
        w = (GAMMA_D * beam_line_loads(b, z, j, "D")[k] + GAMMA_L * beam_line_loads(b, z, j, "L")[k])
        ends = [GAMMA_D * cases["D"].beam_m[key][e] + GAMMA_L * cases["L"].beam_m[key][e] for e in (0, 1)]
        out[(j, k, "mid bottom")] = max(0.0, w * span ** 2 / 8.0 + (ends[0] + ends[1]) / 2.0)
    return out


def choose_bars(as_req_mm2: float) -> str:
    """R15: one diameter, 2-6 bars, area >= As; least area, then fewest bars [J].

    Read literally, "fewest bars" picks 2C28 for 1000 mm^2 (23 % spare); the
    least-area reading picks 5C16 (0.5 % spare), which keeps the steel carbon
    close to need. Ties go to fewer bars.
    """
    best = None
    for d in BAR_DIAMETERS_MM:
        a1 = math.pi * d * d / 4.0
        n = max(BARS_PER_LAYER[0], math.ceil(as_req_mm2 / a1 - 1e-9))
        if n <= BARS_PER_LAYER[1]:
            cand = (round(n * a1), n, d)
            if best is None or cand < best:
                best = cand
    if best is None:
        return "more than one layer needed"
    return f"{best[1]}C{best[2]}"


def column_bars(column_mm: int) -> tuple[float, str]:
    """R12: total steel at the grade III minimum, as 4 corner + 4 side bars [J]."""
    as_req = c.RHO_MIN_COLUMN_TOTAL * column_mm * column_mm
    for d in BAR_DIAMETERS_MM:
        if 8 * math.pi * d * d / 4.0 >= as_req:
            return as_req, f"8C{d}"
    return as_req, "more than 8C32"


def bars_area_mm2(label: str, as_req_mm2: float) -> float:
    """Area of a bar label such as "5C16"; ``as_req_mm2`` if no single layer fits (R15)."""
    n, sep, d = label.partition("C")
    if not (sep and n.isdigit() and d.isdigit()):
        return as_req_mm2
    return int(n) * math.pi * int(d) ** 2 / 4.0


def max_drift(b: BuildingInput, z: Sizes) -> float:
    """Largest elastic storey drift ratio under E for sizes ``z`` [-] (R11)."""
    _, forces = seismic_forces(b, z)
    return max(drift_ratios(b, run_case(b, z, "E", forces)))


def frame_concrete_m3(b: BuildingInput, z: Sizes) -> float:
    """Concrete of the frame strip's beams and columns [m^3] (slab excluded)."""
    n = len(b.storey_heights_m)
    beams = n * sum(bw / 1000.0 * (h - z.slab_mm) / 1000.0 * L for (bw, h), L in zip(z.beams_mm, b.spans_m))
    cols = (len(b.spans_m) + 1) * sum(b.storey_heights_m) * (z.column_mm / 1000.0) ** 2
    return beams + cols


def beams_meet_631(b: BuildingInput, z: Sizes) -> bool:
    """True if every beam meets GB 50011-2010 cl. 6.3.1 (width, h/b, clear span/h)."""
    return all(bw >= BEAM_MIN_B_MM and h / bw <= BEAM_MAX_H_OVER_B
               and (L * 1000.0 - z.column_mm) / h >= BEAM_MIN_CLEAR_SPAN_OVER_H
               for (bw, h), L in zip(z.beams_mm, b.spans_m))


def grow_beam(bw: int, h: int, span_m: float, column_mm: int) -> tuple[int, int, str]:
    """Grow one beam by one step while keeping GB 50011-2010 cl. 6.3.1 (P1, 7 Nov 2026).

    The beam gets 50 mm deeper. If the deeper section would break h/b <= 4 or
    clear span/h >= 4, it gets 50 mm wider instead [J].

    Args:
        bw: Beam width [mm].
        h: Beam depth [mm].
        span_m: Span [m].
        column_mm: Column side [mm], for the clear span.

    Returns:
        (new width, new depth, "deeper" or "wider").
    """
    h2 = h + SIZE_STEP_MM
    if h2 / bw <= BEAM_MAX_H_OVER_B and (span_m * 1000.0 - column_mm) / h2 >= BEAM_MIN_CLEAR_SPAN_OVER_H:
        return bw, h2, "deeper"
    return bw + SIZE_STEP_MM, h, "wider"


def drift_step(b: BuildingInput, z: Sizes, drift: float) -> tuple[Sizes, str]:
    """One R11 step of the "best_ratio" rule (decision card 2, 5 Nov 2026 [J]).

    Two candidates are tried: all columns +50 mm, or all beams +50 mm deeper.
    The one with the larger drift reduction per m^3 of added frame concrete is
    kept. The beam candidate is only allowed if it meets cl. 6.3.1. If neither
    reduces the drift, the columns grow.
    """
    col = Sizes(z.column_mm + SIZE_STEP_MM, list(z.beams_mm), z.slab_mm)
    bm = Sizes(z.column_mm, [(bw, h + SIZE_STEP_MM) for bw, h in z.beams_mm], z.slab_mm)
    v0 = frame_concrete_m3(b, z)
    ratios = {name: (drift - max_drift(b, cand)) / (frame_concrete_m3(b, cand) - v0)
              for name, cand in (("columns", col), ("beams", bm))}
    if not beams_meet_631(b, bm):
        ratios["beams"] = float("-inf")
    if ratios["beams"] > ratios["columns"] and ratios["beams"] > 0.0:
        return bm, f"R11 drift {drift:.5f} > 1/550: beams +50 mm (best ratio)"
    return col, f"R11 drift {drift:.5f} > 1/550: columns to {col.column_mm} (best ratio)"


def generate(b: BuildingInput, verbose: bool = False, drift_rule: str = "best_ratio",
             capacity_design: bool = True) -> GeneratorResult:
    """Size the frame: preliminary sizes, then check and resize until all pass.

    Order of the loop (R11-R13): drift first, then the axial ratio (columns),
    then xi at the beam ends (that beam's depth). The drift fix follows
    ``drift_rule``: "best_ratio" (default) grows whichever of columns or beams
    gives more drift reduction per m^3 of concrete; "columns_first" grows the
    columns until 1.5 times their preliminary size, then the beams. Then R14
    (``capacity_design``, default on): strong column, shear and detailing by
    seismic grade (capacity.py); a failed check grows the member and the loop
    runs again. With ``capacity_design=False`` the R11-R13 generator of
    Day 17 is kept (8 bars at the grade III minimum, no stirrups). With
    ``verbose``, the log of each pass is printed.
    """
    if drift_rule not in DRIFT_RULES:
        raise ValueError(f"drift_rule must be one of {DRIFT_RULES}")
    pre = preliminary_sizes(b)
    z = Sizes(pre.column_mm, list(pre.beams_mm), pre.slab_mm)
    history = []
    for n_pass in range(1, MAX_ITERATIONS + 1):
        t1, forces = seismic_forces(b, z)
        cases = {name: run_case(b, z, name) for name in ("D", "L", "GE")}
        cases["E"] = run_case(b, z, "E", forces)
        drifts = drift_ratios(b, cases["E"])
        history.append(f"pass {n_pass}: columns {z.column_mm}, beams {z.beams_mm}, "
                       f"T1 {t1:.3f} s, drift 1/{1.0 / max(drifts):.0f}")
        if max(drifts) > DRIFT_LIMIT and drift_rule == "best_ratio":
            z, line = drift_step(b, z, max(drifts))
            history.append(line)
            continue
        if max(drifts) > DRIFT_LIMIT:
            if z.column_mm + SIZE_STEP_MM <= COLUMN_GROWTH_LIMIT * pre.column_mm:
                z.column_mm += SIZE_STEP_MM
                history.append(f"R11 drift {max(drifts):.5f} > 1/550: columns to {z.column_mm}")
            else:
                z.beams_mm = [(bw, h + SIZE_STEP_MM) for bw, h in z.beams_mm]
                history.append(f"R11 drift {max(drifts):.5f} > 1/550: beams +50 mm")
            continue
        n_max = max(GAMMA_G_SEISMIC * cases["GE"].column_n[k] + GAMMA_EH * abs(cases["E"].column_n[k])
                    for k in cases["GE"].column_n if k[0] == 1)
        mu = n_max * 1e3 / (c.FC_N_MM2 * z.column_mm ** 2)
        if mu > b.axial_ratio_limit:
            z.column_mm += SIZE_STEP_MM
            history.append(f"R12 axial ratio {mu:.3f} > {b.axial_ratio_limit}: columns to {z.column_mm}")
            continue
        moments = beam_design_moments(b, z, cases)
        steel, grow = {}, set()
        # R14 (Day 20): hogging ends count the bottom steel as compression steel,
        # A_s' = r A_s (GB 50010 cl. 11.3.1, 11.3.6 item 2); r = 0 keeps R13.
        r_comp = c.BEAM_END_COMP_RATIO[b.seismic_grade] if capacity_design else 0.0
        # capacity_design False is the Day 19 rule set: R13 at grade 3 for all.
        r13_grade = b.seismic_grade if capacity_design else 3
        for (j, k, loc), m in moments.items():
            bw, h = z.beams_mm[k]
            d = c.design_section(m, bw, h, "mid-span" if loc.startswith("mid") else "support",
                                 at_end=not loc.startswith("mid"), grade=r13_grade,
                                 comp_ratio=r_comp if loc.endswith("top") else 0.0)
            if d.status != "ok":
                grow.add(k)
            steel[(j, k, loc)] = d.as_req_mm2
        if r_comp > 0.0:
            for (j, k, loc) in list(steel):
                if loc.endswith("top"):
                    bot = (j, k, loc.replace("top", "bottom"))
                    steel[bot] = max(steel[bot], r_comp * steel[(j, k, loc)])
        if grow:
            for k in sorted(grow):
                bw, h, _ = grow_beam(*z.beams_mm[k], b.spans_m[k], z.column_mm)
                z.beams_mm[k] = (bw, h)
                history.append(f"R13 xi limit at span {k}: beam to {bw} x {h}")
            continue
        beam_steel = {}
        for k in range(len(b.spans_m)):
            for loc in ("left top", "right top", "left bottom", "right bottom", "mid bottom"):
                as_req = max(steel[(j, k, loc)] for j in range(1, len(b.storey_heights_m) + 1))
                beam_steel[(k, loc)] = (as_req, choose_bars(as_req))
        r14 = {}
        col_steel = column_bars(z.column_mm)
        if capacity_design:
            r14 = capacity_step(b, z, cases, steel, beam_steel)
            if r14["grow_column"] or r14["grow_beams"]:
                if r14["grow_column"]:
                    z.column_mm += SIZE_STEP_MM
                    history.append(f"R14 {r14['grow_column']}: columns to {z.column_mm}")
                for k in sorted(r14["grow_beams"]):
                    bw, h, _ = grow_beam(*z.beams_mm[k], b.spans_m[k], z.column_mm)
                    z.beams_mm[k] = (bw, h)
                    history.append(f"R14 {r14['grow_beams'][k]} at span {k}: beam to {bw} x {h}")
                continue
            col_steel = (r14["column_bars"].area_mm2, r14["column_bars"].label)
        res = GeneratorResult(pre, z, history, t1, drifts, mu, beam_steel, col_steel, capacity=r14)
        res.quantities = quantities(b, z, res)
        if verbose:
            print("\n".join(history))
        return res
    raise RuntimeError("generator did not converge in MAX_ITERATIONS resizes")


def quantities(b: BuildingInput, z: Sizes, res: GeneratorResult) -> dict[str, float]:
    """Concrete [m^3/m^2] and longitudinal bar steel [kg/m^2] of the frame strip [J].

    Slab over the strip, beam webs below the slab, columns full height. Bars
    run the full beam or column length at the chosen bar areas (R15). Stirrup
    mass from R14 is reported in its own two keys and not added to
    bar_steel_kg_per_m2; footings are left out.
    """
    n = len(b.storey_heights_m)
    width = sum(b.spans_m)
    area = n * width * b.tributary_width_m
    slab = n * width * b.tributary_width_m * z.slab_mm / 1000.0
    beams = n * sum(bw / 1000.0 * (h - z.slab_mm) / 1000.0 * L for (bw, h), L in zip(z.beams_mm, b.spans_m))
    cols = (len(b.spans_m) + 1) * sum(b.storey_heights_m) * (z.column_mm / 1000.0) ** 2

    def chosen(entry: tuple[float, str]) -> float:
        return bars_area_mm2(entry[1], entry[0]) / 1e6

    beam_steel_m3 = n * sum((chosen(res.beam_steel[(k, "left top")]) + chosen(res.beam_steel[(k, "mid bottom")])) * L
                            for k, L in enumerate(b.spans_m))
    column_steel_m3 = (len(b.spans_m) + 1) * sum(b.storey_heights_m) * chosen(res.column_steel)
    steel_m3 = beam_steel_m3 + column_steel_m3
    # The split keys (Day 18) let the batch runner separate floor and lateral
    # system; the two totals above are unchanged.
    return {"concrete_m3_per_m2": (slab + beams + cols) / area,
            "bar_steel_kg_per_m2": steel_m3 * 7850.0 / area,
            "slab_concrete_m3_per_m2": slab / area,
            "beam_concrete_m3_per_m2": beams / area,
            "column_concrete_m3_per_m2": cols / area,
            "beam_bar_kg_per_m2": beam_steel_m3 * 7850.0 / area,
            "column_bar_kg_per_m2": column_steel_m3 * 7850.0 / area,
            # R14 stirrups (Day 20); 0 when capacity design was off.
            "beam_stirrup_kg_per_m2": res.capacity.get("beam_stirrup_kg", 0.0) / area,
            "column_stirrup_kg_per_m2": res.capacity.get("column_stirrup_kg", 0.0) / area}


# ---------------------------------------------------------------------------
# R14: capacity design, shear and detailing (Day 20)
# ---------------------------------------------------------------------------


def bar_diameter_mm(label: str) -> int:
    """Diameter of a bar label such as "5C16" [mm]; the largest bar if none fits."""
    _, sep, d = label.partition("C")
    return int(d) if sep and d.isdigit() else BAR_DIAMETERS_MM[-1]


def capacity_step(b: BuildingInput, z: Sizes, cases: dict[str, CaseForces],
                  steel: dict[tuple[int, int, str], float],
                  beam_steel: dict[tuple[int, str], tuple[float, str]]) -> dict:
    """R14 on a frame that has passed R11-R13 (design_rules.md R14).

    1. Seismic combinations 1.3 G_E +- 1.4 E of the column end moments; at each
       joint below the roof whose column axial ratio is >= 0.15, both column
       ends are scaled up until their sum is eta_c times the beam face moments
       in the same sense (GB 50011 cl. 6.2.2); the base end of the bottom
       storey times the base factor (cl. 6.2.3).
    2. Column bars from eccentric compression (GB 50010 cl. 6.2.17) under the
       magnified seismic forces (times gamma_RE) and 1.3D + 1.5L; one bar set
       for every column [J]. Second order checked by cl. 6.2.3.
    3. Beam shear eta_vb (M_l + M_r)/l_n + V_Gb, or the combined shear for
       grade 4; section limit and stirrups (cl. 11.3.2-11.3.9).
    4. Column shear eta_vc (M_t + M_b)/H_n; section limit, stirrups and
       volumetric ratio (cl. 11.4.3-11.4.18).

    The axial force of each column is taken at its bottom end for both ends
    [J]. H_n is the storey height less the deepest beam of the floor above [J].

    Returns:
        A dict: "grow_column" (reason or ""), "grow_beams" (span -> reason),
        and, when nothing grows, "column_bars", "beam_stirrups",
        "column_stirrups", "beam_stirrup_kg", "column_stirrup_kg",
        "max_column_rho", "second_order_ok".
    """
    grade = b.seismic_grade
    cap.check_grade(grade)
    n_st, n_ln = len(b.storey_heights_m), len(b.spans_m) + 1
    h_col = z.column_mm
    area = float(h_col * h_col)
    a = h_col / 2000.0
    signs = (1.0, -1.0)
    ge, e, d, lv = cases["GE"], cases["E"], cases["D"], cases["L"]
    out = {"grow_column": "", "grow_beams": {}}
    if h_col < cap.COLUMN_MIN_MM[grade] and n_st > 2:
        out["grow_column"] = f"column below {cap.COLUMN_MIN_MM[grade]} mm (cl. 11.4.11)"
        return out

    def n_comb(key, s):
        return GAMMA_G_SEISMIC * ge.column_n[key] + s * GAMMA_EH * e.column_n[key]

    def mu_of(key):
        return max(n_comb(key, s) for s in signs) * 1e3 / (c.FC_N_MM2 * area)

    # 1. column end moments of the seismic combinations, then magnification
    cm = {s: {key: [GAMMA_G_SEISMIC * ge.column_m[key][end] + s * GAMMA_EH * e.column_m[key][end]
                    for end in (0, 1)] for key in ge.column_m} for s in signs}

    def beam_face(key, end, s):
        def f(case):
            return face_moment(cases[case].beam_m[key][end], cases[case].beam_v[key][end], a)
        return GAMMA_G_SEISMIC * f("GE") + s * GAMMA_EH * f("E")

    def mbua(k, loc):
        bw, h = z.beams_mm[k]
        as_req, label = beam_steel[(k, loc)]
        return cap.beam_mbua_knm(bars_area_mm2(label, as_req), h, c.A_S_MM, c.GAMMA_RE_BEAM_FLEXURE)

    def sum_bua(i):
        """Grade 1: larger of the two sway directions of sum M_bua at line i [J]."""
        left, right = i - 1, i
        dirs = []
        for top_side in ("left", "right"):
            m = 0.0
            if left >= 0:
                m += mbua(left, "right top" if top_side == "left" else "right bottom")
            if right < n_ln - 1:
                m += mbua(right, "left bottom" if top_side == "left" else "left top")
            dirs.append(m)
        return max(dirs)

    for s in signs:
        for j in range(1, n_st):
            for i in range(n_ln):
                if mu_of((j, i)) < cap.STRONG_COLUMN_MIN_MU:
                    continue
                m_r_left = beam_face((j, i - 1), 1, s) if i > 0 else 0.0
                m_l_right = beam_face((j, i), 0, s) if i < n_ln - 1 else 0.0
                if grade == 1 and m_r_left < 0.0 and m_l_right < 0.0:
                    # GB 50011 cl. 6.2.2: both ends hogging, the smaller is taken as zero
                    if abs(m_r_left) < abs(m_l_right):
                        m_r_left = 0.0
                    else:
                        m_l_right = 0.0
                sum_b = abs(m_l_right - m_r_left)
                sum_c = abs(cm[s][(j, i)][1] + cm[s][(j + 1, i)][0])
                need = (cap.GRADE1_MBUA_FACTOR * sum_bua(i) if grade == 1
                        else cap.ETA_C[grade] * sum_b)
                if sum_c > 0.0:
                    k = max(1.0, need / sum_c)
                    cm[s][(j, i)][1] *= k
                    cm[s][(j + 1, i)][0] *= k
        for i in range(n_ln):
            cm[s][(1, i)][0] *= cap.ETA_BASE[grade]

    # 2. column bars and second order
    side, so_ok = 0.0, True
    for key in ge.column_m:
        h_m = b.storey_heights_m[key[0] - 1]
        for s in signs:
            n = n_comb(key, s)
            g_re = cap.gamma_re_column(n * 1e3 / (c.FC_N_MM2 * area))
            for m in cm[s][key]:
                side = max(side, cap.column_side_steel_mm2(g_re * n, g_re * m, h_col, h_col))
            so_ok &= cap.second_order_negligible(cm[s][key][0], cm[s][key][1], mu_of(key), h_m, h_col)
        n_g = GAMMA_D * d.column_n[key] + GAMMA_L * lv.column_n[key]
        for end in (0, 1):
            m_g = GAMMA_D * d.column_m[key][end] + GAMMA_L * lv.column_m[key][end]
            side = max(side, cap.column_side_steel_mm2(n_g, m_g, h_col, h_col))
    if not so_ok:
        out["grow_column"] = "second order not negligible (GB 50010 cl. 6.2.3)"
        return out
    bars = cap.column_bars(h_col, side, grade, BAR_DIAMETERS_MM)
    if bars is None:
        out["grow_column"] = "no column bar layout fits (GB 50010 cl. 9.3.1, 11.4.13)"
        return out
    if bars.rho > cap.COLUMN_RHO_CAP:
        out["grow_column"] = f"column steel above {cap.COLUMN_RHO_CAP:.0%} [J]"
        return out

    # 3. beam shear and stirrups
    beam_st, beam_kg = {}, 0.0
    for (j, k) in ge.beam_m:
        bw, h = z.beams_mm[k]
        ln = b.spans_m[k] - h_col / 1000.0
        w_ge = beam_line_loads(b, z, j, "GE")[k]
        v_gb = GAMMA_G_SEISMIC * w_ge * ln / 2.0
        v_seis = 0.0
        for s in signs:
            m_l, m_r = beam_face((j, k), 0, s), beam_face((j, k), 1, s)
            v_comb = max(abs(GAMMA_G_SEISMIC * ge.beam_v[(j, k)][end] + s * GAMMA_EH * e.beam_v[(j, k)][end])
                         for end in (0, 1))
            v_seis = max(v_seis, cap.beam_shear_kn(grade, m_l - m_r, ln, v_gb, v_comb))
        v_grav = max(abs(GAMMA_D * d.beam_v[(j, k)][end] + GAMMA_L * lv.beam_v[(j, k)][end]) for end in (0, 1))
        if v_seis > cap.section_limit_kn(bw, h, ln * 1000.0 / h > cap.BEAM_SLENDER_SPAN_DEPTH):
            out["grow_beams"][k] = "beam shear above the section limit (cl. 11.3.3)"
            continue
        asv = max(cap.beam_asv_per_s(v_seis, bw, h), cap.beam_asv_per_s(v_grav, bw, h, seismic=False))
        labels = [beam_steel[(k, loc)][1] for loc in ("left top", "right top", "mid bottom")]
        bar_d = min(bar_diameter_mm(lab) for lab in labels)
        end_ratio = max(steel[(j, k, "left top")], steel[(j, k, "right top")]) / (bw * (h - c.A_S_MM))
        pick = cap.beam_stirrups(grade, bw, h, asv, bar_d, end_ratio)
        if pick is None:
            out["grow_beams"][k] = "no stirrup set meets the beam shear [J]"
            continue
        beam_st[(j, k)] = pick
        beam_kg += cap.beam_stirrup_kg(bw, h, bar_d, ln, *pick)
    if out["grow_beams"]:
        return out

    # 4. column shear and hoops
    col_st, col_kg = {}, 0.0
    for key in ge.column_m:
        j = key[0]
        hn = b.storey_heights_m[j - 1] - max(hb for _, hb in z.beams_mm) / 1000.0
        v = max(cap.column_shear_kn(grade, cm[s][key][1], cm[s][key][0], hn) for s in signs)
        lam = cap.column_lambda(hn, h_col)
        if v > cap.section_limit_kn(h_col, h_col, lam > cap.COLUMN_SLENDER_LAMBDA):
            out["grow_column"] = "column shear above the section limit (cl. 11.4.6)"
            return out
        n_low = min(n_comb(key, s) for s in signs)
        asv = cap.column_asv_per_s(v, n_low, h_col, hn)
        mu = mu_of(key)
        bottom = cap.column_stirrups(grade, h_col, asv, mu, bars, hn, root=(j == 1))
        top = cap.column_stirrups(grade, h_col, asv, mu, bars, hn, root=False)
        if bottom is None or top is None:
            out["grow_column"] = "no hoop set meets the column shear and confinement [J]"
            return out
        mid = max(bottom[1], top[1], key=lambda st: st.asv_per_s)
        col_st[key] = (bottom[0], top[0], mid)
        col_kg += cap.column_stirrup_kg(h_col, bars.diameter_mm, hn, top[0], bottom[0], mid)

    out.update(column_bars=bars, beam_stirrups=beam_st, column_stirrups=col_st,
               beam_stirrup_kg=beam_kg, column_stirrup_kg=col_kg,
               max_column_rho=bars.rho, second_order_ok=so_ok)
    return out
