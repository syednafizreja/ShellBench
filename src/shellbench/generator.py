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

from shellbench import checks as c
from shellbench import seismic as s

SIZE_STEP_MM = 50  # R15, playbook
CONCRETE_UNIT_WEIGHT_KN_M3 = 25.0  # GB 50009 Appendix A [?]; thesis s4.1 uses 25
G_E_LIVE_FACTOR = 0.5  # GB 50011 Table 5.1.3 (floor live; roof live excluded)
GAMMA_G_SEISMIC = 1.3  # GB 55002-2021 cl. 4.3.2, Table 4.3.2-1 (R9)
GAMMA_EH = 1.4  # GB 55002-2021 cl. 4.3.2, Table 4.3.2-2 (R9)
GAMMA_D = 1.3  # GB 55001-2021 cl. 3.1.13 item 1 (R9)
GAMMA_L = 1.5  # GB 55001-2021 cl. 3.1.13 item 4 (R9)
DRIFT_LIMIT = 1.0 / 550.0  # spec S11; GB 50011 Table 5.5.1 [?] (R11)
PRELIM_GRAVITY_KN_M2 = 14.0  # Th s2.4, load per floor for preliminary sizing (R5)
PRELIM_BETA_EDGE = 1.3  # Th s2.4 (R5)
PRELIM_BETA_INTERIOR = 1.25  # Th s2.4 (R5)
SLAB_MIN_MM = 120  # R3 decision 1, 31 Oct 2026 [J]
SLAB_SPAN_RATIO_TWO_WAY = 40.0  # Th s2.1; GB 50010 cl. 9.1.2 [?] (R3)
BEAM_SPAN_RATIO = 12.0  # R4 [J], within Th s2.3's L/14 to L/8
BEAM_MIN_WIDTH_MM = 250  # R4 [J]
COLUMN_GROWTH_LIMIT = 1.5  # R11 stopping rule [J]
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
        alpha_max: Frequent-earthquake alpha_max (GB 50011 Table 5.1.4-1).
        tg_s: Site characteristic period [s].
        psi_t: Period reduction factor for infill (R8).
        concrete_e_mpa: Young's modulus of the concrete [MPa].
        beam_i_factor: Slab contribution to beam stiffness (spec M7).
        axial_ratio_limit: Column axial ratio limit for the seismic grade (R6).
    """

    spans_m: tuple[float, ...]
    storey_heights_m: tuple[float, ...]
    tributary_width_m: float
    slab_panel_m: float
    floor_dead_kn_m2: float
    roof_dead_kn_m2: float
    live_kn_m2: tuple[float, ...]
    roof_live_kn_m2: float
    alpha_max: float
    tg_s: float
    psi_t: float
    concrete_e_mpa: float
    beam_i_factor: float
    axial_ratio_limit: float = c.AXIAL_RATIO_LIMIT


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
        history: One line per resize, saying which rule moved which member.
        period_s: T1 of the final frame, after psi_t [s].
        drift_ratios: Largest elastic storey drift ratio per storey [-].
        axial_ratio: Largest column axial ratio [-].
        beam_steel: (span index, location) -> (As required, bars) [mm^2].
        column_steel: (As required, bars) for every column [mm^2].
        quantities: Concrete [m^3] and bar steel [kg] per m^2 of floor.
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
    below the slab.
    """
    roof = level == len(b.storey_heights_m)
    out = []
    for k, (bw, h) in enumerate(z.beams_mm):
        dead = (b.roof_dead_kn_m2 if roof else b.floor_dead_kn_m2) * b.tributary_width_m
        dead += CONCRETE_UNIT_WEIGHT_KN_M3 * bw / 1000.0 * (h - z.slab_mm) / 1000.0
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


def apply_gravity(fm: Frame, b: BuildingInput, z: Sizes, case: str) -> None:
    """Beam line loads, plus column self-weight at the top node of each storey (D, G_E)."""
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    for j in range(1, len(fm.ys)):
        for k, w in enumerate(beam_line_loads(b, z, j, case)):
            ops.eleLoad("-ele", fm.beams[(j, k)], "-type", "-beamUniform", -w)
        if case in ("D", "GE"):
            wc = column_weight_kn(z, b.storey_heights_m[j - 1])
            for i in range(len(fm.xs)):
                ops.load(fm.node[(j, i)], 0.0, -wc, 0.0)


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
    """G_i per level: beam G_E loads plus half the columns above and below."""
    out = []
    n = len(b.storey_heights_m)
    for j in range(1, n + 1):
        g = sum(w * L for w, L in zip(beam_line_loads(b, z, j, "GE"), b.spans_m))
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
    """Beam end bending moments (sagging positive) and column base axial forces."""

    beam_m: dict[tuple[int, int], tuple[float, float]]
    beam_v: dict[tuple[int, int], tuple[float, float]]
    column_n: dict[tuple[int, int], float]
    level_u: list[float]


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
    cn = {key: ops.eleForce(tag)[1] for key, tag in fm.columns.items()}
    lu = [sum(ops.nodeDisp(fm.node[(j, i)], 1) for i in range(len(fm.xs))) / len(fm.xs)
          for j in range(len(fm.ys))]
    return CaseForces(bm, bv, cn, lu)


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


def generate(b: BuildingInput) -> GeneratorResult:
    """Size the frame: preliminary sizes, then check and resize until all pass.

    Order of the loop (R11-R13): drift first (columns, then beams once the
    columns reach 1.5 times their preliminary size), then the axial ratio
    (columns), then xi at the beam ends (that beam's depth).
    """
    pre = preliminary_sizes(b)
    z = Sizes(pre.column_mm, list(pre.beams_mm), pre.slab_mm)
    history = []
    for _ in range(MAX_ITERATIONS):
        t1, forces = seismic_forces(b, z)
        cases = {name: run_case(b, z, name) for name in ("D", "L", "GE")}
        cases["E"] = run_case(b, z, "E", forces)
        drifts = drift_ratios(b, cases["E"])
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
        for (j, k, loc), m in moments.items():
            bw, h = z.beams_mm[k]
            d = c.design_section(m, bw, h, "mid-span" if loc.startswith("mid") else "support",
                                 at_end=not loc.startswith("mid"))
            if d.status != "ok":
                grow.add(k)
            steel[(j, k, loc)] = d.as_req_mm2
        if grow:
            for k in sorted(grow):
                bw, h = z.beams_mm[k]
                z.beams_mm[k] = (bw, h + SIZE_STEP_MM)
                history.append(f"R13 xi limit at span {k}: beam to {bw} x {h + SIZE_STEP_MM}")
            continue
        beam_steel = {}
        for k in range(len(b.spans_m)):
            for loc in ("left top", "right top", "left bottom", "right bottom", "mid bottom"):
                as_req = max(steel[(j, k, loc)] for j in range(1, len(b.storey_heights_m) + 1))
                beam_steel[(k, loc)] = (as_req, choose_bars(as_req))
        res = GeneratorResult(pre, z, history, t1, drifts, mu, beam_steel, column_bars(z.column_mm))
        res.quantities = quantities(b, z, res)
        return res
    raise RuntimeError("generator did not converge in MAX_ITERATIONS resizes")


def quantities(b: BuildingInput, z: Sizes, res: GeneratorResult) -> dict[str, float]:
    """Concrete [m^3/m^2] and longitudinal bar steel [kg/m^2] of the frame strip [J].

    Slab over the strip, beam webs below the slab, columns full height. Bars
    run the full beam or column length; stirrups and footings are left to
    the take-off module (carbon.py), which already handles them.
    """
    n = len(b.storey_heights_m)
    width = sum(b.spans_m)
    area = n * width * b.tributary_width_m
    slab = n * width * b.tributary_width_m * z.slab_mm / 1000.0
    beams = n * sum(bw / 1000.0 * (h - z.slab_mm) / 1000.0 * L for (bw, h), L in zip(z.beams_mm, b.spans_m))
    cols = (len(b.spans_m) + 1) * sum(b.storey_heights_m) * (z.column_mm / 1000.0) ** 2
    steel_m3 = n * sum((res.beam_steel[(k, "left top")][0] + res.beam_steel[(k, "mid bottom")][0]) / 1e6 * L
                       for k, L in enumerate(b.spans_m))
    steel_m3 += (len(b.spans_m) + 1) * sum(b.storey_heights_m) * res.column_steel[0] / 1e6
    return {"concrete_m3_per_m2": (slab + beams + cols) / area,
            "bar_steel_kg_per_m2": steel_m3 * 7850.0 / area}
