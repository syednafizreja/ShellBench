"""Whole-building quantity take-off and A1-A3 embodied carbon of the anchor.

File: src/shellbench/carbon.py

What this module does
---------------------
Playbook Day 12. It measures the concrete volume and the steel mass of the
whole anchor building (suspended slabs, frame beams, longitudinal and
secondary beams, columns and column footings) from docs/baseline_spec.md,
and, once the author's factor file exists, turns them into A1-A3 embodied
carbon per m^2 of floor area for every factor set in
``data/carbon_factors.csv``.

The reading rules were committed before the first run (docs/anchor_notes.md,
"How the take-off is read", commit f38e731, 29 Oct 2026); the rule numbers
below refer to that list. Every value marked [J] is Claude's judgement and
every value marked [?] is a code reference the author still has to confirm.

Two switches
------------
* ``plan``: ``"grid"`` is the full 38.4 x 21.0 m rectangle of decision B11
  (28 columns); ``"drawn"`` follows Claude's reading of drawing 03 (no
  column at A4 and a 13.2 x 7.2 m notch on A-B between axes 3 and 5), a
  sensitivity until the author confirms it (rule 2).
* ``steel``: ``"thesis"`` takes the frame beam steel from the s9.2 table and
  4C22 columns; ``"code"`` takes the frame beams from ``shellbench.checks``
  and the GB 50010 column minimum (rule 6).

No carbon factor is written in this module. If the factor file is missing,
the quantities are still written and the carbon step reports "pending".

Units: lengths in m, areas of steel in mm^2, concrete in m^3, steel in kg,
forces in kN, pressures in kPa, carbon in kgCO2e.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from shellbench import anchor_frame as af
from shellbench import checks as c

# Plan grid (spec G3, G4; decision B11). Bays along the building between
# axes 1-7, and spans across it between axes A-D.
BAYS_X_M = (6.0, 6.6, 6.6, 6.6, 6.6, 6.0)
SPANS_Y = ("AB", "BC", "CD")
SPANS_Y_M = (7.2, 6.6, 7.2)
LINES_Y = ("A", "B", "C", "D")

# Panels missing in the "drawn" plan, as (bay index, span index): the A-B
# notch between axes 3 and 5 on drawing 03 (rule 2) [J].
DRAWN_NOTCH = frozenset({(2, 0), (3, 0)})

STOREY_HEIGHTS_M = (4.55, 3.60, 3.60, 3.60)  # spec G6, G7 (B4)
N_SLAB_LEVELS = 4  # levels 1-3 and the roof (rule 3) [J]
SLAB_T_M = 0.12  # spec G10 (B1)
COLUMN_B_M = 0.6  # spec M5
BEAM_B_M = 0.3  # spec M1-M4
FRAME_BEAM_H_M = {"AB": 0.6, "BC": 0.5, "CD": 0.6}  # spec M1, M2 (B13)
LONG_BEAM_H_M = 0.6  # spec M3
SECONDARY_BEAM_H_M = 0.5  # spec M4

# Secondary beams at mid-span of the 7.2 m spans, by (bay index, span index),
# as read on drawing 03 (rule 4) [J].
SECONDARY_BAYS = frozenset({(0, 0), (1, 0), (4, 0), (5, 0), (1, 2), (4, 2)})

CONCRETE_GRADE = "C40"  # spec X1; footings too [J] (rule 4)
BAR_STEEL = "HRB400"  # spec X5 (B7)
STIRRUP_STEEL = "HPB300"  # spec X6
STEEL_DENSITY_KG_M3 = 7850.0  # [J]; GB 50009 Appendix A [?] (rule 9)

# Slab steel (rule 5): C8@200 each way (Th Table 3.1; slab drawings).
SLAB_BAR = "1C8"
SLAB_BAR_SPACING_M = 0.2
SLAB_TOP_BAR_LENGTH_M = 1.2  # each side of a beam line; drawings 0.8-1.6 m [J]

# Beam and column steel (rule 6).
THESIS_COLUMN_BARS = "4C22"  # spec R1, decision B6
CODE_COLUMN_RHO = c.RHO_MIN_COLUMN_TOTAL  # GB 50010 Table 11.4.12-1, p. 163
LONG_BEAM_BARS = "4C16"  # drawing 03 note, top and bottom [J]
SECONDARY_BEAM_BARS = "3C20"  # drawing 03 note, top and bottom [J]
CONTINUOUS_TOP_BARS = "2C14"  # GB 50011 cl. 6.3.4 [?]
TOP_END_FRACTION = 1.0 / 3.0  # top end bars over l_n / 3 from each face [J]
THESIS_FLOOR_FOR_LEVEL = {1: "1", 2: "1", 3: "1", 4: "5"}  # B4; levels 2-3 [J]

# Stirrups (rule 7).
STIRRUP_BAR = "1C10"  # phi10, area only
BEAM_STIRRUP_SPACING_M = 0.2  # drawing 03 note
COLUMN_STIRRUP_SPACING_M = 0.1  # drawing 01, phi10@100(4)
COLUMN_STIRRUP_LEGS = 4  # legs in each direction, drawing 01
STIRRUP_COVER_M = 0.05  # [J]

# Footings (rule 8; proposed D28) [J].
FAK_KPA = 220.0  # decision B8
FILL_UNIT_WEIGHT_KN_M3 = 20.0  # footing plus fill, GB 50007 cl. 5.2.1 [?]
FOUNDATION_TOP_DEPTH_M = 0.5  # spec G9
FOOTING_T_M = 0.6  # [J]
FOOTING_SIZE_STEP_M = 0.1  # [J]
FOOTING_LOAD_FACTOR = 1.35  # GB 50007 cl. 3.0.6 [?]
FOOTING_RHO_MIN = 0.0015  # GB 50007 cl. 8.2.1 [?]
FOOTING_COVER_M = 0.05  # [J]
ANCHOR_TRIBUTARY_WIDTH_M = 7.2  # spec G4 (B10)

ELEMENTS = ("slabs", "frame beams", "longitudinal beams", "secondary beams",
            "columns", "footings")
FACTOR_FIELDS = ("set [text]", "material [text]", "value", "unit [text]",
                 "source [text]", "page [text]")
CONVERSIONS = {"kgCO2e/m3": ("m3", 1.0), "kgCO2e/kg": ("kg", 1.0),
               "kgCO2e/t": ("kg", 1e-3)}


@dataclass
class Plan:
    """Panels, beams and columns of one floor plan.

    Attributes:
        name: ``"grid"`` or ``"drawn"``.
        panels: Slab panels present, as (bay index, span index).
    """

    name: str
    panels: frozenset

    def area_m2(self) -> float:
        """Return the plan area of one level [m^2]."""
        return sum(BAYS_X_M[i] * SPANS_Y_M[j] for i, j in self.panels)

    def _has(self, i: int, j: int) -> bool:
        return (i, j) in self.panels

    def columns(self) -> list[tuple[int, int]]:
        """Return the column nodes (axis index 0-6, line index 0-3) next to a panel."""
        return [(k, m) for k in range(len(BAYS_X_M) + 1) for m in range(len(LINES_Y))
                if self.panels_at_node(k, m)]

    def panels_at_node(self, k: int, m: int) -> list[tuple[int, int]]:
        """Return the panels that touch column node (k, m)."""
        return [(i, j) for i in (k - 1, k) for j in (m - 1, m) if self._has(i, j)]

    def transverse_beams(self) -> list[tuple[int, int, int]]:
        """Return frame beams as (axis index, span index, panels beside it)."""
        out = []
        for k in range(len(BAYS_X_M) + 1):
            for j in range(len(SPANS_Y)):
                sides = sum(self._has(i, j) for i in (k - 1, k))
                if sides:
                    out.append((k, j, sides))
        return out

    def longitudinal_beams(self) -> list[tuple[int, int, int]]:
        """Return longitudinal beams as (line index, bay index, panels beside it)."""
        out = []
        for m in range(len(LINES_Y)):
            for i in range(len(BAYS_X_M)):
                sides = sum(self._has(i, j) for j in (m - 1, m))
                if sides:
                    out.append((m, i, sides))
        return out

    def secondary_beams(self) -> list[tuple[int, int]]:
        """Return secondary beams as (bay index, span index) where the panel exists."""
        return sorted(p for p in SECONDARY_BAYS if p in self.panels)


def make_plan(name: str) -> Plan:
    """Build the ``"grid"`` (B11) or ``"drawn"`` (drawing 03 [J]) plan.

    Args:
        name: ``"grid"`` or ``"drawn"``.

    Returns:
        The plan.
    """
    full = frozenset((i, j) for i in range(len(BAYS_X_M)) for j in range(len(SPANS_Y)))
    if name == "grid":
        return Plan(name, full)
    if name == "drawn":
        return Plan(name, full - DRAWN_NOTCH)
    raise ValueError(f"unknown plan {name!r}")


def steel_kg(area_mm2: float, length_m: float) -> float:
    """Return the mass of a bar group of a given area and length [kg]."""
    return area_mm2 * 1e-6 * length_m * STEEL_DENSITY_KG_M3


def stirrup_kg(legs_length_m: float, spacing_m: float, run_m: float) -> float:
    """Return the stirrup mass along a member [kg].

    Args:
        legs_length_m: Total leg length of one stirrup set [m].
        spacing_m: Stirrup spacing [m].
        run_m: Length of member that carries stirrups [m].
    """
    n = math.floor(run_m / spacing_m) + 1
    return n * steel_kg(c.bar_area_mm2(STIRRUP_BAR), legs_length_m)


def beam_stirrup_legs_m(h_m: float) -> float:
    """Return the leg length of one closed 2-leg beam stirrup [m] (rule 7)."""
    return 2 * ((BEAM_B_M - 2 * STIRRUP_COVER_M) + (h_m - 2 * STIRRUP_COVER_M))


def column_stirrup_legs_m() -> float:
    """Return the leg length of one 4 x 4-leg column stirrup set [m] (rule 7)."""
    return 2 * COLUMN_STIRRUP_LEGS * (COLUMN_B_M - 2 * STIRRUP_COVER_M)


@dataclass
class FrameBeamSteel:
    """Longitudinal steel of one frame beam [mm^2].

    Attributes:
        top_left: Top steel at the left face.
        top_right: Top steel at the right face.
        bottom: Bottom steel, run over the full clear span.
    """

    top_left: float
    top_right: float
    bottom: float

    def mass_kg(self, clear_m: float) -> float:
        """Return the bar mass of the beam with the rule-6 bar lengths [kg]."""
        top_end = (self.top_left + self.top_right) * TOP_END_FRACTION * clear_m
        cont = c.bar_area_mm2(CONTINUOUS_TOP_BARS) * (1 - 2 * TOP_END_FRACTION) * clear_m
        return steel_kg(1.0, top_end + cont + self.bottom * clear_m)


def thesis_frame_beam_steel(repo_root: Path) -> dict[tuple[str, int], FrameBeamSteel]:
    """Frame beam steel from the s9.2 printed A_s,prov (rule 6, "thesis").

    Args:
        repo_root: Repository root.

    Returns:
        Steel keyed (span, level 1-4).
    """
    rows = c.read_thesis_beam_steel(repo_root)
    prov = {(r["floor_printed [text]"], r["span [text]"], r["section [text]"]):
            float(r["As_prov [mm2]"]) for r in rows}
    out = {}
    for lvl, fl in THESIS_FLOOR_FOR_LEVEL.items():
        for span in SPANS_Y:
            out[(span, lvl)] = FrameBeamSteel(prov[(fl, span, "left end")],
                                              prov[(fl, span, "right end")],
                                              prov[(fl, span, "middle")])
    return out


def code_frame_beam_steel(beam_rows: list[dict]) -> dict[tuple[str, int], FrameBeamSteel]:
    """Frame beam steel from the Day 11 design (rule 6, "code").

    Args:
        beam_rows: Rows of ``checks.beam_design_rows``.

    Returns:
        Steel keyed (span, level 1-4); bottom is the largest bottom steel of
        the beam.
    """
    req = {(r["span [text]"], r["level [text]"], r["location [text]"], r["steel [text]"]):
           r["As_req [mm2]"] for r in beam_rows}
    out = {}
    for lvl in range(1, 5):
        for span in SPANS_Y:
            bottom = max(v for (s, lv, _, st), v in req.items()
                         if s == span and lv == lvl and st == "bottom")
            out[(span, lvl)] = FrameBeamSteel(req[(span, lvl, "left end", "top")],
                                              req[(span, lvl, "right end", "top")], bottom)
    return out


@dataclass
class Footing:
    """One pad footing (rule 8).

    Attributes:
        node: Column node (axis index, line index).
        n_k_kn: Characteristic axial force D + L at the footing [kN].
        b_m: Side of the square pad [m].
        as_mm2: Bottom steel each way over the width [mm^2].
    """

    node: tuple[int, int]
    n_k_kn: float
    b_m: float
    as_mm2: float

    def concrete_m3(self) -> float:
        """Return the pad concrete [m^3]."""
        return self.b_m ** 2 * FOOTING_T_M

    def steel_kg(self) -> float:
        """Return the pad bottom steel, both ways [kg]."""
        return 2 * steel_kg(self.as_mm2, self.b_m)


def tributary_area_m2(plan: Plan, k: int, m: int) -> float:
    """Return the plan area carried by column node (k, m): a quarter of each panel."""
    return sum(BAYS_X_M[i] * SPANS_Y_M[j] / 4 for i, j in plan.panels_at_node(k, m))


def anchor_tributary_area_m2(m: int) -> float:
    """Return the plan area carried by the axis-2 frame column on line m [m^2]."""
    across = sum(SPANS_Y_M[j] / 2 for j in (m - 1, m) if 0 <= j < len(SPANS_Y))
    return ANCHOR_TRIBUTARY_WIDTH_M * across


def size_footing(node: tuple[int, int], n_k_kn: float) -> Footing:
    """Size one square pad for fak and design its bottom steel (rule 8) [J].

    Args:
        node: Column node.
        n_k_kn: Characteristic axial force D + L [kN].

    Returns:
        The footing.
    """
    d = FOUNDATION_TOP_DEPTH_M + FOOTING_T_M
    b = math.sqrt(n_k_kn / (FAK_KPA - FILL_UNIT_WEIGHT_KN_M3 * d))
    b = math.ceil(round(b / FOOTING_SIZE_STEP_M, 9)) * FOOTING_SIZE_STEP_M
    p_j = FOOTING_LOAD_FACTOR * n_k_kn / b ** 2
    m_knm = (b - COLUMN_B_M) ** 2 * (2 * b + COLUMN_B_M) * p_j / 24
    h0_mm = (FOOTING_T_M - FOOTING_COVER_M) * 1e3
    as_calc = m_knm * 1e6 / (0.9 * c.FY_N_MM2 * h0_mm)
    as_min = FOOTING_RHO_MIN * b * 1e3 * FOOTING_T_M * 1e3
    return Footing(node, n_k_kn, round(b, 1), max(as_calc, as_min))


def footings(plan: Plan, cases: dict[str, c.CaseResult]) -> list[Footing]:
    """Size the pad under every column of a plan (rule 8).

    N_k is D + L at the base of the axis-2 column of the same line (C and D
    mirror B and A), scaled by tributary plan area [J].

    Args:
        plan: Floor plan.
        cases: Load cases from ``checks.run_cases``.

    Returns:
        One footing per column.
    """
    out = []
    for k, m in plan.columns():
        line = LINES_Y[min(m, 3 - m)]
        n2d = cases["D"].axial[(line, "1", "bottom")] + cases["L"].axial[(line, "1", "bottom")]
        scale = tributary_area_m2(plan, k, m) / anchor_tributary_area_m2(m)
        out.append(size_footing((k, m), n2d * scale))
    return out


def _row(plan: Plan, source: str, element: str, material: str, unit: str,
         qty: float) -> dict:
    floor = N_SLAB_LEVELS * plan.area_m2()
    return {"plan [text]": plan.name, "steel_source [text]": source,
            "element [text]": element, "material [text]": material,
            "unit [text]": unit, "quantity": round(qty, 3),
            "floor_area [m2]": round(floor, 2),
            "per_floor_area [unit/m2]": round(qty / floor, 5)}


def take_off(plan: Plan, source: str, frame_steel: dict[tuple[str, int], FrameBeamSteel],
             pads: list[Footing]) -> list[dict]:
    """Measure one plan with one steel source (rules 3-9).

    Args:
        plan: Floor plan.
        source: ``"thesis"`` or ``"code"``.
        frame_steel: Frame beam steel keyed (span, level).
        pads: Footings of the plan.

    Returns:
        Rows of ``results/anchor_quantities.csv`` for this plan and source.
    """
    q = {(e, mat): 0.0 for e in ELEMENTS for mat in ("concrete", "bars", "stirrups")}
    cols = plan.columns()
    slab_bar = c.bar_area_mm2(SLAB_BAR) / SLAB_BAR_SPACING_M  # mm2 per m width
    col_area_in_slab = sum(len(plan.panels_at_node(k, m)) / 4 * COLUMN_B_M ** 2
                           for k, m in cols)
    beam_lines = []  # (centre-line length, panels beside it) for slab top bars

    for _ in range(N_SLAB_LEVELS):
        q[("slabs", "concrete")] += (plan.area_m2() - col_area_in_slab) * SLAB_T_M
        q[("slabs", "bars")] += 2 * steel_kg(slab_bar, 1.0) * plan.area_m2()
    for lvl in range(1, N_SLAB_LEVELS + 1):
        for k, j, sides in plan.transverse_beams():
            span = SPANS_Y[j]
            h = FRAME_BEAM_H_M[span]
            clear = SPANS_Y_M[j] - COLUMN_B_M
            q[("frame beams", "concrete")] += BEAM_B_M * (h - SLAB_T_M) * clear
            q[("frame beams", "bars")] += frame_steel[(span, lvl)].mass_kg(clear)
            q[("frame beams", "stirrups")] += stirrup_kg(beam_stirrup_legs_m(h),
                                                         BEAM_STIRRUP_SPACING_M, clear)
            beam_lines.append((SPANS_Y_M[j], sides))
        for m, i, sides in plan.longitudinal_beams():
            clear = BAYS_X_M[i] - COLUMN_B_M
            q[("longitudinal beams", "concrete")] += BEAM_B_M * (LONG_BEAM_H_M - SLAB_T_M) * clear
            q[("longitudinal beams", "bars")] += 2 * steel_kg(c.bar_area_mm2(LONG_BEAM_BARS), clear)
            q[("longitudinal beams", "stirrups")] += stirrup_kg(
                beam_stirrup_legs_m(LONG_BEAM_H_M), BEAM_STIRRUP_SPACING_M, clear)
            beam_lines.append((BAYS_X_M[i], sides))
        for i, _j in plan.secondary_beams():
            clear = BAYS_X_M[i] - BEAM_B_M
            q[("secondary beams", "concrete")] += (BEAM_B_M * (SECONDARY_BEAM_H_M - SLAB_T_M)
                                                   * clear)
            q[("secondary beams", "bars")] += 2 * steel_kg(c.bar_area_mm2(SECONDARY_BEAM_BARS),
                                                           clear)
            q[("secondary beams", "stirrups")] += stirrup_kg(
                beam_stirrup_legs_m(SECONDARY_BEAM_H_M), BEAM_STIRRUP_SPACING_M, clear)
            beam_lines.append((BAYS_X_M[i], 2))
    for length, sides in beam_lines:
        q[("slabs", "bars")] += steel_kg(slab_bar * length, sides * SLAB_TOP_BAR_LENGTH_M)

    col_bars = (c.bar_area_mm2(THESIS_COLUMN_BARS) if source == "thesis"
                else CODE_COLUMN_RHO * (COLUMN_B_M * 1e3) ** 2)
    for h in STOREY_HEIGHTS_M:
        q[("columns", "concrete")] += len(cols) * COLUMN_B_M ** 2 * h
        q[("columns", "bars")] += len(cols) * steel_kg(col_bars, h)
        q[("columns", "stirrups")] += len(cols) * stirrup_kg(column_stirrup_legs_m(),
                                                             COLUMN_STIRRUP_SPACING_M, h)
    q[("footings", "concrete")] = sum(p.concrete_m3() for p in pads)
    q[("footings", "bars")] = sum(p.steel_kg() for p in pads)

    rows = []
    for e in ELEMENTS:
        rows.append(_row(plan, source, e, CONCRETE_GRADE, "m3", q[(e, "concrete")]))
        rows.append(_row(plan, source, e, BAR_STEEL, "kg", q[(e, "bars")]))
        if q[(e, "stirrups")]:
            rows.append(_row(plan, source, e, STIRRUP_STEEL, "kg", q[(e, "stirrups")]))
    return rows


def footing_rows(plan: Plan, pads: list[Footing]) -> list[dict]:
    """Build ``results/anchor_footings.csv`` rows for one plan."""
    return [{"plan [text]": plan.name, "axis [text]": str(k + 1), "line [text]": LINES_Y[m],
             "N_k [kN]": round(p.n_k_kn, 2), "B [m]": p.b_m, "t [m]": FOOTING_T_M,
             "As_each_way [mm2]": round(p.as_mm2, 1),
             "concrete [m3]": round(p.concrete_m3(), 3), "steel [kg]": round(p.steel_kg(), 2)}
            for p in pads for k, m in (p.node,)]


def read_factors(path: Path) -> dict[tuple[str, str], tuple[float, str]]:
    """Read the author's carbon factor file (rule 10).

    Args:
        path: ``data/carbon_factors.csv``.

    Returns:
        (value, unit) keyed (set, material).

    Raises:
        ValueError: If a row lacks a field, a source or a page, or has a unit
            this module cannot convert.
    """
    out = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if any(not (r.get(f) or "").strip() for f in FACTOR_FIELDS):
                raise ValueError(f"factor row incomplete: {r}")
            if r["unit [text]"].strip() not in CONVERSIONS:
                raise ValueError(f"unit {r['unit [text]']!r} not one of {sorted(CONVERSIONS)}")
            out[(r["set [text]"].strip(), r["material [text]"].strip())] = (
                float(r["value"]), r["unit [text]"].strip())
    return out


def carbon_rows(quantities: list[dict], factors: dict[tuple[str, str], tuple[float, str]]
                ) -> list[dict]:
    """Turn quantities into A1-A3 carbon for every factor set (rule 10).

    Args:
        quantities: Rows of ``take_off``.
        factors: Output of ``read_factors``.

    Returns:
        One row per factor set, plan, steel source and element.

    Raises:
        KeyError: If a set has no factor for a material in the take-off.
    """
    sets = sorted({s for s, _ in factors})
    totals: dict[tuple, float] = {}
    floor = {}
    for fset in sets:
        for q in quantities:
            key = (fset, q["material [text]"])
            if key not in factors:
                raise KeyError(f"factor set {fset!r} has no row for {q['material [text]']!r}")
            value, unit = factors[key]
            qty_unit, mult = CONVERSIONS[unit]
            if qty_unit != q["unit [text]"]:
                raise ValueError(f"{key}: factor per {qty_unit}, quantity in {q['unit [text]']}")
            k = (fset, q["plan [text]"], q["steel_source [text]"], q["element [text]"])
            totals[k] = totals.get(k, 0.0) + q["quantity"] * value * mult
            floor[k[1:3]] = q["floor_area [m2]"]
    return [{"factor_set [text]": k[0], "plan [text]": k[1], "steel_source [text]": k[2],
             "element [text]": k[3], "A1-A3 [kgCO2e]": round(v, 1),
             "A1-A3 per floor area [kgCO2e/m2]": round(v / floor[k[1:3]], 2)}
            for k, v in totals.items()]


def plot_quantities(quantities: list[dict], path: Path) -> None:
    """Save stacked bars of concrete and steel per m^2 by element (grid plan).

    Args:
        quantities: Rows of ``take_off``.
        path: Output PNG.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colours = ("#2a5783", "#5b8db8", "#9cc3e0", "#c9a227", "#7a7a7a", "#b5651d")
    sources = ("thesis", "code")
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.6))
    panels = ((axes[0], ("C40",), "Concrete [m³ per m² floor]"),
              (axes[1], ("HRB400", "HPB300"), "Steel [kg per m² floor]"))
    for ax, mats, label in panels:
        bottom = [0.0, 0.0]
        for e, col in zip(ELEMENTS, colours):
            vals = [sum(q["per_floor_area [unit/m2]"] for q in quantities
                        if q["plan [text]"] == "grid" and q["steel_source [text]"] == s
                        and q["element [text]"] == e and q["material [text]"] in mats)
                    for s in sources]
            ax.bar(sources, vals, bottom=bottom, color=col, label=e, width=0.55)
            bottom = [b + v for b, v in zip(bottom, vals)]
        ax.set_ylabel(label)
        ax.set_xlabel("steel source")
        ax.grid(True, axis="y", color="#dddddd", linewidth=0.6)
        ax.set_axisbelow(True)
    axes[1].legend(fontsize=7, frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.suptitle("Anchor building, grid plan (B11): quantities by element", fontsize=9)
    fig.text(0.01, 0.01, "© 2026 Syed Nafiz Reja Hasib.", fontsize=6.5, color="#666666")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, metadata={"Software": None})
    plt.close(fig)


def plot_carbon(rows: list[dict], path: Path) -> None:
    """Save stacked bars of A1-A3 per m^2 by element, per factor set (grid plan).

    Args:
        rows: Rows of ``carbon_rows``.
        path: Output PNG.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colours = ("#2a5783", "#5b8db8", "#9cc3e0", "#c9a227", "#7a7a7a", "#b5651d")
    grid = [r for r in rows if r["plan [text]"] == "grid"]
    bars = sorted({(r["factor_set [text]"], r["steel_source [text]"]) for r in grid})
    labels = [f"{s}\n{src}" for s, src in bars]
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    bottom = [0.0] * len(bars)
    for e, col in zip(ELEMENTS, colours):
        vals = [sum(r["A1-A3 per floor area [kgCO2e/m2]"] for r in grid
                    if (r["factor_set [text]"], r["steel_source [text]"]) == b
                    and r["element [text]"] == e) for b in bars]
        ax.bar(labels, vals, bottom=bottom, color=col, label=e, width=0.55)
        bottom = [x + v for x, v in zip(bottom, vals)]
    ax.set_ylabel("A1-A3 [kgCO₂e per m² floor]")
    ax.grid(True, axis="y", color="#dddddd", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(fontsize=7, frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.text(0.01, 0.01, "© 2026 Syed Nafiz Reja Hasib.", fontsize=6.5, color="#666666")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, metadata={"Software": None})
    plt.close(fig)


def main(repo_root: Path | None = None) -> dict:
    """Run the take-off for both plans and both steel sources, and the carbon if possible.

    Writes ``results/anchor_quantities.csv``, ``results/anchor_footings.csv``
    and ``figures/anchor_quantities.png``. If ``data/carbon_factors.csv``
    exists, also ``results/anchor_carbon.csv`` and ``figures/anchor_carbon.png``.

    Args:
        repo_root: Repository root; defaults to two levels above this file's
            package folder.

    Returns:
        ``"quantities"`` and ``"footings"`` rows, ``"carbon"`` rows or None,
        and ``"carbon_status"`` ("done" or "pending: ...").
    """
    root = repo_root or Path(__file__).resolve().parents[2]
    wind, quake = c.anchor_forces(root)
    cases = c.run_cases(wind, quake)
    steel = {"thesis": thesis_frame_beam_steel(root),
             "code": code_frame_beam_steel(c.beam_design_rows(cases))}
    quantities, foot = [], []
    for name in ("grid", "drawn"):
        plan = make_plan(name)
        pads = footings(plan, cases)
        foot += footing_rows(plan, pads)
        for source in ("thesis", "code"):
            quantities += take_off(plan, source, steel[source], pads)
    af.write_csv(quantities, root / "results" / "anchor_quantities.csv")
    af.write_csv(foot, root / "results" / "anchor_footings.csv")
    plot_quantities(quantities, root / "figures" / "anchor_quantities.png")

    factor_file = root / "data" / "carbon_factors.csv"
    out = {"quantities": quantities, "footings": foot, "carbon": None,
           "carbon_status": f"pending: {factor_file.relative_to(root)} not found"}
    if factor_file.exists():
        carbon = carbon_rows(quantities, read_factors(factor_file))
        af.write_csv(carbon, root / "results" / "anchor_carbon.csv")
        plot_carbon(carbon, root / "figures" / "anchor_carbon.png")
        out.update(carbon=carbon, carbon_status="done")
    return out


if __name__ == "__main__":
    t = main()
    for r in t["quantities"]:
        print(f"{r['plan [text]']:5s} {r['steel_source [text]']:6s} {r['element [text]']:18s} "
              f"{r['material [text]']:6s} {r['quantity']:10.2f} {r['unit [text]']:2s} "
              f"{r['per_floor_area [unit/m2]']:.4f}/m2")
    print(t["carbon_status"])
