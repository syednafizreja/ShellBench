"""2D elastic OpenSeesPy model of the thesis transverse frame (anchor, Layer 1).

File: src/shellbench/anchor_frame.py

What this module does
---------------------
It rebuilds the transverse frame on axis (2) of the author's thesis building
(4 storeys, spans 7.2 / 6.6 / 7.2 m) as a linear-elastic 2D frame in
OpenSeesPy, applies the dead-load case the way the thesis distributes it, and
compares beam-end moments and column axial forces with the typed thesis values
in ``validation/thesis_values/``.

Inputs come only from ``docs/baseline_spec.md`` (geometry, sections, material)
and from the thesis load derivation it points to (Th §4.1, §5.1, §5.2, §6.2.1,
Fig. 4-4 and 4-5). Every constant below names its source.

Load models
-----------
The thesis describes the dead load in three slightly different ways, so the
model can apply any of them (see ``LOAD_MODELS``):

``thesis_fem`` (primary)
    The equivalent uniform loads that produced the fixed-end moments in the
    thesis moment-distribution table (Th §6.2.1, table "6.3"). Roof:
    AB 13.55 + 4.934 = 18.48 kN/m, BC 7.92 + 3.274 = 11.19 kN/m. Floors 1-3:
    AB 23.43 kN/m, BC 10.96 kN/m (printed). The roof sums are a
    reconstruction [J]: they reproduce the printed fixed-end moments
    79.85 and 40.63 kN*m and the mid-span M0 values 119.78 and 60.95 kN*m.
``thesis_text``
    The equivalent loads printed in the text under Fig. 4-5. Same as
    ``thesis_fem`` for floors 1-3, but roof AB 17.15 and BC 10.23 kN/m. The
    thesis used these for the roof beam shears (Tables 4-6, 4-7) and hence for
    the column axial forces.
``actual_shape``
    The actual load shapes of Fig. 4-4: trapezoidal slab load on AB/CD
    (peak 15.21 roof, 14.58 floors, ramps of 1.8 m) and triangular slab load
    on BC (peak 13.94 roof, 13.36 floors), plus the uniform beam and wall
    parts. This is not what the thesis analysed; it is used to show how much
    of each difference comes from the equivalent-load method itself [J].

In all models the concentrated joint loads are the printed totals of Th §5.2
(135.10, 214.11, 167.77, 254.26 kN), the eccentricity moments act at the
exterior joints A and D only, as drawn in Fig. 4-4 and 4-5, and column
self-weight is 9.96 kN/m (Th §4.1). Self-weight is never generated from the
sections, so nothing is counted twice (baseline_spec B13 note).

Units: kN, m, kN*m, kN/m, kN/m^2 (SI-derived, consistent).
Sign convention of the outputs: beam-end moments follow the thesis (clockwise
positive on the member end, so hogging gives -M at the left end and +M at
the right end); column axial forces are positive in compression.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

import openseespy.opensees as ops

# ---------------------------------------------------------------------------
# Geometry (docs/baseline_spec.md A1)
# ---------------------------------------------------------------------------

#: Transverse spans AB, BC, CD [m]. Spec G3 (Th §1.1, §2.6).
SPANS_M: tuple[float, float, float] = (7.2, 6.6, 7.2)

#: Storey heights, ground storey first [m]. Spec G6 (3.6 m typical) and
#: G7 (4.55 m ground column, decided B4).
STOREY_HEIGHTS_M: tuple[float, ...] = (4.55, 3.6, 3.6, 3.6)

#: Column line labels, left to right (Th Fig. 4-4).
AXES: tuple[str, ...] = ("A", "B", "C", "D")

#: Span labels, left to right.
SPAN_LABELS: tuple[str, ...] = ("AB", "BC", "CD")

# ---------------------------------------------------------------------------
# Sections and material (docs/baseline_spec.md A2, A3)
# ---------------------------------------------------------------------------

#: Elastic modulus of C40 concrete [kN/m^2]. Spec X4: 3.25e4 N/mm^2.
E_KN_M2: float = 3.25e4 * 1.0e3

#: Column section b x h [m]. Spec M5: 600 x 600, all storeys.
COLUMN_BH_M: tuple[float, float] = (0.6, 0.6)

#: Frame beam sections b x h [m] by span. Spec M1 (AB, CD 300 x 600; decided
#: B13 for stiffness) and M2 (BC 300 x 500).
BEAM_BH_M: dict[str, tuple[float, float]] = {
    "AB": (0.3, 0.6),
    "BC": (0.3, 0.5),
    "CD": (0.3, 0.6),
}

#: Beam moment-of-inertia factor for the middle frame on axis (2), for
#: slab T-action. Spec M7 (Th §2.6: I = 2.0 I0 middle frame, 1.5 I0 edge).
BEAM_INERTIA_FACTOR: float = 2.0

#: Multiplier on column area for the axially rigid check (a numerical device,
#: not a physical value): large enough that axial shortening vanishes.
RIGID_AXIAL_AREA_FACTOR: float = 1.0e4

#: Number of sub-elements per metre of beam. Used so that the trapezoidal and
#: triangular loads of ``actual_shape`` can be applied piecewise; ramp ends
#: (1.8 m) and the BC apex (3.3 m) fall on sub-element boundaries at 0.1 m.
BEAM_SUBELEMENTS_PER_M: int = 10

# ---------------------------------------------------------------------------
# Dead loads as the thesis distributes them
# ---------------------------------------------------------------------------

#: Column self-weight including plaster [kN/m]. Th §4.1 (spec L5).
COLUMN_SELF_WEIGHT_KN_M: float = 9.96

#: Concentrated joint loads [kN], printed totals of Th §5.2 and Fig. 4-4.
#: Keys: ("exterior" | "interior", "roof" | "floor").
JOINT_LOADS_KN: dict[tuple[str, str], float] = {
    ("exterior", "roof"): 135.10,   # node A4 / D4, Th §5.2 item 1
    ("interior", "roof"): 214.11,   # node B4 / C4, Th §5.2 item 2
    ("exterior", "floor"): 167.77,  # nodes A1-3 / D1-3, Th §5.2 item 3
    ("interior", "floor"): 254.26,  # nodes B1-3 / C1-3, Th §5.2 item 4
}

#: Eccentricity moments at exterior joints [kN*m], Th §6.2.1 and Fig. 4-4/4-5
#: (0.150 m offset of the flush longitudinal beam, Th Fig. 7). The load sits on
#: the outer face, so the moment is anticlockwise at A and clockwise at D.
EXTERIOR_JOINT_MOMENTS_KN_M: dict[str, float] = {"roof": 20.26, "floor": 25.16}

#: Eccentricity moments at interior joints [kN*m]. Printed in the first row of
#: the thesis distribution table (Th §6.2.1) but NOT drawn on Fig. 4-4/4-5.
#: Used only by the ``interior_moments`` check. Their sense is not drawn
#: anywhere; it is taken anticlockwise at B and clockwise at C, because the
#: thesis's own final moments at joint B3 sum to -39.19 kN*m (clockwise-positive
#: member ends), which balances only an anticlockwise 38.09 at B [J].
INTERIOR_JOINT_MOMENTS_KN_M: dict[str, float] = {"roof": 31.79, "floor": 38.09}


@dataclass(frozen=True)
class BeamLoad:
    """Dead load on one frame beam, as uniform part plus a shaped slab part.

    Attributes:
        uniform_kn_m: Uniformly distributed part over the whole span [kN/m].
        shape: ``"none"``, ``"trapezoid"`` or ``"triangle"`` for the slab part.
        peak_kn_m: Peak intensity of the shaped part [kN/m].
        ramp_m: Ramp length of a trapezoid [m] (ignored for other shapes).
    """

    uniform_kn_m: float
    shape: str = "none"
    peak_kn_m: float = 0.0
    ramp_m: float = 0.0

    def intensity(self, x_m: float, span_m: float) -> float:
        """Return the downward load intensity [kN/m] at distance x from the left end.

        Args:
            x_m: Position along the beam from its left end [m].
            span_m: Beam length [m].

        Returns:
            Total intensity (uniform part plus shaped part) at x.
        """
        q = self.uniform_kn_m
        if self.shape == "trapezoid":
            ramp_factor = min(x_m, span_m - x_m, self.ramp_m) / self.ramp_m
            q += self.peak_kn_m * ramp_factor
        elif self.shape == "triangle":
            q += self.peak_kn_m * min(x_m, span_m - x_m) / (span_m / 2.0)
        return q


@dataclass(frozen=True)
class LoadModel:
    """A complete description of the beam line loads for the dead-load case.

    Attributes:
        name: Short identifier used in result files.
        description: One-line description with thesis sources.
        beams: Mapping (level type, span type) -> BeamLoad, where level type is
            ``"roof"`` or ``"floor"`` and span type ``"side"`` (AB, CD) or
            ``"mid"`` (BC).
    """

    name: str
    description: str
    beams: dict[tuple[str, str], BeamLoad] = field(default_factory=dict)


#: The three load models described in the module docstring.
LOAD_MODELS: dict[str, LoadModel] = {
    "thesis_fem": LoadModel(
        name="thesis_fem",
        description=(
            "Equivalent uniform loads behind the thesis fixed-end moments (Th s6.2.1 "
            "table 6.3): roof AB 13.55+4.934, BC 7.92+3.274 [J reconstruction, Th s5.1, "
            "s4.1]; floors AB 23.43, BC 10.96 (printed)"
        ),
        beams={
            ("roof", "side"): BeamLoad(uniform_kn_m=13.55 + 4.934),
            ("roof", "mid"): BeamLoad(uniform_kn_m=7.92 + 3.274),
            ("floor", "side"): BeamLoad(uniform_kn_m=23.43),
            ("floor", "mid"): BeamLoad(uniform_kn_m=10.96),
        },
    ),
    "thesis_text": LoadModel(
        name="thesis_text",
        description=(
            "Equivalent uniform loads printed under Fig. 4-5 (Th s6.2.1): roof AB 17.15, "
            "BC 10.23; floors AB 23.43, BC 10.96"
        ),
        beams={
            ("roof", "side"): BeamLoad(uniform_kn_m=17.15),
            ("roof", "mid"): BeamLoad(uniform_kn_m=10.23),
            ("floor", "side"): BeamLoad(uniform_kn_m=23.43),
            ("floor", "mid"): BeamLoad(uniform_kn_m=10.96),
        },
    ),
    "actual_shape": LoadModel(
        name="actual_shape",
        description=(
            "Actual shapes of Fig. 4-4: trapezoid peak 15.21/14.58 (ramp 1.8 m) on AB/CD, "
            "triangle peak 13.94/13.36 on BC, plus beam 4.934/3.274 (Th s4.1) and, on "
            "floors 1-3, wall 5.51 on AB/CD (Th s4.2) [J: wall placement inferred]"
        ),
        beams={
            ("roof", "side"): BeamLoad(4.934, "trapezoid", 15.21, 1.8),
            ("roof", "mid"): BeamLoad(3.274, "triangle", 13.94),
            ("floor", "side"): BeamLoad(4.934 + 5.51, "trapezoid", 14.58, 1.8),
            ("floor", "mid"): BeamLoad(3.274, "triangle", 13.36),
        },
    ),
}


@dataclass
class FrameModel:
    """Tags of the OpenSees objects built for the frame.

    Attributes:
        node: (axis label, level index) -> node tag; level 0 is the base.
        column: (axis label, storey 1..4) -> element tag.
        beam: (span label, level 1..4) -> list of sub-element tags, left to right.
        beam_nodes: (span label, level 1..4) -> node tags along the beam.
    """

    node: dict[tuple[str, int], int] = field(default_factory=dict)
    column: dict[tuple[str, int], int] = field(default_factory=dict)
    beam: dict[tuple[str, int], list[int]] = field(default_factory=dict)
    beam_nodes: dict[tuple[str, int], list[float]] = field(default_factory=dict)


def axis_x_coordinates() -> list[float]:
    """Return the x coordinate [m] of each column line A-D.

    Returns:
        Cumulative sums of ``SPANS_M`` starting at 0.
    """
    xs = [0.0]
    for span in SPANS_M:
        xs.append(xs[-1] + span)
    return xs


def level_y_coordinates() -> list[float]:
    """Return the y coordinate [m] of the base and each floor level.

    Returns:
        Cumulative sums of ``STOREY_HEIGHTS_M`` starting at 0 (top of footing).
    """
    ys = [0.0]
    for h in STOREY_HEIGHTS_M:
        ys.append(ys[-1] + h)
    return ys


def build_frame(axially_rigid_columns: bool = False) -> FrameModel:
    """Build the 2D elastic frame in a fresh OpenSees domain.

    Columns are one element per storey, fixed at the base. Each beam is split
    into sub-elements (``BEAM_SUBELEMENTS_PER_M``) so shaped loads can be
    applied piecewise. Members meet at centre-line nodes (no rigid offsets),
    as in the thesis hand analysis.

    Args:
        axially_rigid_columns: If True, column area is multiplied by
            ``RIGID_AXIAL_AREA_FACTOR`` to remove axial shortening (a check of
            how much the hand method's neglect of it matters).

    Returns:
        A FrameModel holding the tags of all nodes and elements.
    """
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    ops.geomTransf("Linear", 1)

    fm = FrameModel()
    xs, ys = axis_x_coordinates(), level_y_coordinates()
    tag = 1
    for lvl, y in enumerate(ys):
        for ax, x in zip(AXES, xs):
            ops.node(tag, x, y)
            fm.node[(ax, lvl)] = tag
            if lvl == 0:
                ops.fix(tag, 1, 1, 1)
            tag += 1

    b, h = COLUMN_BH_M
    a_col = b * h * (RIGID_AXIAL_AREA_FACTOR if axially_rigid_columns else 1.0)
    i_col = b * h**3 / 12.0
    ele = 1
    for storey in range(1, len(ys)):
        for ax in AXES:
            ops.element("elasticBeamColumn", ele, fm.node[(ax, storey - 1)],
                        fm.node[(ax, storey)], a_col, E_KN_M2, i_col, 1)
            fm.column[(ax, storey)] = ele
            ele += 1

    for lvl in range(1, len(ys)):
        for i, span in enumerate(SPAN_LABELS):
            bb, hb = BEAM_BH_M[span]
            a_b, i_b = bb * hb, BEAM_INERTIA_FACTOR * bb * hb**3 / 12.0
            n_sub = round(SPANS_M[i] * BEAM_SUBELEMENTS_PER_M)
            left, right = fm.node[(AXES[i], lvl)], fm.node[(AXES[i + 1], lvl)]
            chain = [left]
            for k in range(1, n_sub):
                ops.node(tag, xs[i] + SPANS_M[i] * k / n_sub, ys[lvl])
                chain.append(tag)
                tag += 1
            chain.append(right)
            fm.beam[(span, lvl)] = []
            for k in range(n_sub):
                ops.element("elasticBeamColumn", ele, chain[k], chain[k + 1],
                            a_b, E_KN_M2, i_b, 1)
                fm.beam[(span, lvl)].append(ele)
                ele += 1
            fm.beam_nodes[(span, lvl)] = chain
    return fm


def apply_dead_load(fm: FrameModel, load_model: LoadModel,
                    interior_moments: bool = False) -> float:
    """Apply the dead-load case to a built frame.

    Args:
        fm: The frame returned by ``build_frame``.
        load_model: Which beam line-load description to use.
        interior_moments: If True, also apply the interior eccentricity
            moments of the thesis distribution table at B and C (a check; the
            thesis load figures do not show them).

    Returns:
        The total applied vertical load [kN] (beams, joints, columns), for
        equilibrium checks.
    """
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)
    n_levels = len(STOREY_HEIGHTS_M)
    total = 0.0

    for lvl in range(1, n_levels + 1):
        kind = "roof" if lvl == n_levels else "floor"
        for ax in AXES:
            side = "exterior" if ax in ("A", "D") else "interior"
            p = JOINT_LOADS_KN[(side, kind)]
            if side == "exterior":
                m = EXTERIOR_JOINT_MOMENTS_KN_M[kind] * (1.0 if ax == "A" else -1.0)
            elif interior_moments:
                m = INTERIOR_JOINT_MOMENTS_KN_M[kind] * (1.0 if ax == "B" else -1.0)
            else:
                m = 0.0
            ops.load(fm.node[(ax, lvl)], 0.0, -p, m)
            total += p

        for i, span in enumerate(SPAN_LABELS):
            beam_load = load_model.beams[(kind, "mid" if span == "BC" else "side")]
            subs = fm.beam[(span, lvl)]
            seg = SPANS_M[i] / len(subs)
            for k, ele in enumerate(subs):
                q = beam_load.intensity((k + 0.5) * seg, SPANS_M[i])
                ops.eleLoad("-ele", ele, "-type", "-beamUniform", -q, 0.0)
                total += q * seg

    for (ax, storey), ele in fm.column.items():
        ops.eleLoad("-ele", ele, "-type", "-beamUniform", 0.0, -COLUMN_SELF_WEIGHT_KN_M)
        total += COLUMN_SELF_WEIGHT_KN_M * STOREY_HEIGHTS_M[storey - 1]
    return total


def solve_static() -> None:
    """Run one linear static step of the current load pattern.

    Raises:
        RuntimeError: If OpenSees reports a failed analysis.
    """
    ops.system("BandGeneral")
    ops.numberer("RCM")
    ops.constraints("Plain")
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")
    if ops.analyze(1) != 0:
        raise RuntimeError("OpenSees static analysis failed")
    ops.reactions()


def beam_end_moments(fm: FrameModel) -> dict[tuple[str, str, str], float]:
    """Return beam-end moments in the thesis sign convention [kN*m].

    OpenSees ``localForce`` gives end moments acting on the element,
    anticlockwise positive. The thesis prints clockwise-positive member-end
    moments, so both ends are negated.

    Args:
        fm: A solved frame.

    Returns:
        Mapping (floor label, span, end) -> moment, with end ``"left"`` or
        ``"right"``.
    """
    out = {}
    for (span, lvl), subs in fm.beam.items():
        m_left = ops.eleResponse(subs[0], "localForce")[2]
        m_right = ops.eleResponse(subs[-1], "localForce")[5]
        out[(str(lvl), span, "left")] = -m_left
        out[(str(lvl), span, "right")] = -m_right
    return out


def column_axial_forces(fm: FrameModel) -> dict[tuple[str, str, str], float]:
    """Return column axial forces, compression positive [kN].

    Args:
        fm: A solved frame.

    Returns:
        Mapping (axis label, floor label, ``"top"`` | ``"bottom"``) -> force.
    """
    out = {}
    for (ax, storey), ele in fm.column.items():
        f = ops.eleResponse(ele, "localForce")
        out[(ax, str(storey), "bottom")] = f[0]
        out[(ax, str(storey), "top")] = -f[3]
    return out


def base_reaction_sum() -> float:
    """Return the sum of vertical base reactions [kN] after ``solve_static``.

    Returns:
        Sum over all fixed nodes of the vertical reaction (upward positive).
    """
    return sum(ops.nodeReaction(n, 2) for n in ops.getNodeTags()
               if ops.nodeReaction(n, 2) != 0.0)


@dataclass
class DeadLoadResult:
    """Output of one dead-load run.

    Attributes:
        variant: Name of the run.
        moments: Beam-end moments, see ``beam_end_moments``.
        axial: Column axial forces, see ``column_axial_forces``.
        applied_kn: Total applied vertical load [kN].
        reaction_kn: Sum of vertical base reactions [kN].
    """

    variant: str
    moments: dict[tuple[str, str, str], float]
    axial: dict[tuple[str, str, str], float]
    applied_kn: float
    reaction_kn: float


def run_dead_load(load_model: str = "thesis_fem", axially_rigid_columns: bool = False,
                  interior_moments: bool = False, variant: str | None = None) -> DeadLoadResult:
    """Build, load and solve the frame for one dead-load variant.

    Args:
        load_model: Key of ``LOAD_MODELS``.
        axially_rigid_columns: See ``build_frame``.
        interior_moments: See ``apply_dead_load``.
        variant: Name for the run; defaults to the load-model key.

    Returns:
        A DeadLoadResult with moments, axial forces and the equilibrium totals.
    """
    fm = build_frame(axially_rigid_columns)
    applied = apply_dead_load(fm, LOAD_MODELS[load_model], interior_moments)
    solve_static()
    result = DeadLoadResult(
        variant=variant or load_model,
        moments=beam_end_moments(fm),
        axial=column_axial_forces(fm),
        applied_kn=applied,
        reaction_kn=base_reaction_sum(),
    )
    ops.wipe()
    return result


#: The runs reported. The first is the primary comparison; the others each
#: change one thing so its effect on the differences can be read off.
VARIANTS: dict[str, dict] = {
    "primary": {"load_model": "thesis_fem"},
    "roof_text_loads": {"load_model": "thesis_text"},
    "rigid_column_axial": {"load_model": "thesis_fem", "axially_rigid_columns": True},
    "interior_moments": {"load_model": "thesis_fem", "interior_moments": True},
    "actual_load_shape": {"load_model": "actual_shape"},
}


def read_thesis_targets(repo_root: Path) -> list[dict]:
    """Read the dead-load validation targets typed on Day 3.

    Args:
        repo_root: Repository root containing ``validation/thesis_values``.

    Returns:
        One dict per target with keys quantity, floor, member, end, thesis,
        source, flag. Quantity is ``"M_end"`` [kN*m] or ``"N"`` [kN].
    """
    folder = repo_root / "validation" / "thesis_values"
    rows = []
    with open(folder / "gravity_beam_end_moments.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["load_case [text]"] != "dead":
                continue
            rows.append({
                "quantity": "M_end", "unit": "kN*m", "floor": r["floor [text]"],
                "member": r["span [text]"], "end": r["beam_end [text]"].split(" ")[0],
                "thesis": float(r["M_end [kN*m]"]), "source": r["source [text]"],
                "flag": r["flag [text]"],
            })
    with open(folder / "gravity_column_axial_forces.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["load_case [text]"] != "dead":
                continue
            for end, col in (("top", "N_top [kN]"), ("bottom", "N_bottom [kN]")):
                rows.append({
                    "quantity": "N", "unit": "kN", "floor": r["floor [text]"],
                    "member": r["axis [text]"], "end": end, "thesis": float(r[col]),
                    "source": r["source [text]"], "flag": r["flag [text]"],
                })
    return rows


def model_value(result: DeadLoadResult, target: dict) -> float:
    """Pick the model value that matches one thesis target.

    Column targets for "A/D" and "B/C" are compared with axes A and B; the
    model is symmetric, which the tests check.

    Args:
        result: A dead-load run.
        target: One row from ``read_thesis_targets``.

    Returns:
        The model value in the thesis sign convention.
    """
    if target["quantity"] == "M_end":
        return result.moments[(target["floor"], target["member"], target["end"])]
    axis = target["member"].split("/")[0]
    return result.axial[(axis, target["floor"], target["end"])]


def percent_difference(model: float, thesis: float) -> float:
    """Return (model - thesis) / |thesis| x 100.

    Args:
        model: Model value.
        thesis: Thesis value (non-zero).

    Returns:
        Signed percentage difference relative to the thesis value.
    """
    return (model - thesis) / abs(thesis) * 100.0


def comparison_rows(results: dict[str, DeadLoadResult], targets: list[dict]) -> list[dict]:
    """Build the comparison table rows for the primary run and all variants.

    Args:
        results: Runs keyed by variant name; must include ``"primary"``.
        targets: Output of ``read_thesis_targets``.

    Returns:
        One dict per target with the thesis value, the primary model value,
        the difference and % difference, and each variant's % difference.
    """
    rows = []
    for t in targets:
        m = model_value(results["primary"], t)
        row = {
            "quantity [text]": t["quantity"],
            "floor [text]": t["floor"],
            "member [text]": t["member"],
            "end [text]": t["end"],
            "thesis_value [mixed]": round(t["thesis"], 2),
            "model_value [mixed]": round(m, 2),
            "difference [mixed]": round(m - t["thesis"], 2),
            "difference_pct [%]": round(percent_difference(m, t["thesis"]), 1),
        }
        row["unit [text]"] = t["unit"]
        for name, res in results.items():
            if name == "primary":
                continue
            row[f"pct_{name} [%]"] = round(percent_difference(model_value(res, t), t["thesis"]), 1)
        row["thesis_flag [text]"] = t["flag"]
        row["thesis_source [text]"] = t["source"]
        rows.append(row)
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    """Write a list of dicts to CSV with the keys of the first row as header.

    Args:
        rows: Rows to write (all with the same keys).
        path: Output file; parent folders are created.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main(repo_root: Path | None = None) -> list[dict]:
    """Run every variant, compare with the thesis and save the table.

    Writes ``results/anchor_gravity_dead.csv`` (one row per thesis target)
    and ``results/anchor_gravity_dead_runs.csv`` (equilibrium totals per run).

    Args:
        repo_root: Repository root; defaults to two levels above this file's
            package folder.

    Returns:
        The comparison rows that were written.
    """
    root = repo_root or Path(__file__).resolve().parents[2]
    results = {name: run_dead_load(variant=name, **kw) for name, kw in VARIANTS.items()}
    rows = comparison_rows(results, read_thesis_targets(root))
    write_csv(rows, root / "results" / "anchor_gravity_dead.csv")
    runs = [{
        "variant [text]": name,
        "load_model [text]": kw["load_model"],
        "axially_rigid_columns [text]": str(kw.get("axially_rigid_columns", False)),
        "interior_moments [text]": str(kw.get("interior_moments", False)),
        "applied_vertical_load [kN]": round(results[name].applied_kn, 2),
        "base_reaction_sum [kN]": round(results[name].reaction_kn, 2),
        "description [text]": LOAD_MODELS[kw["load_model"]].description,
    } for name, kw in VARIANTS.items()]
    write_csv(runs, root / "results" / "anchor_gravity_dead_runs.csv")
    return rows


if __name__ == "__main__":
    for r in main():
        print(f"{r['quantity [text]']:5s} fl{r['floor [text]']} {r['member [text]']:3s} "
              f"{r['end [text]']:6s} thesis {r['thesis_value [mixed]']:9.2f} "
              f"model {r['model_value [mixed]']:9.2f} {r['difference_pct [%]']:6.1f} %")
