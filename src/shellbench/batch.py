"""Batch runner for the conventional building family (Playbook Day 18).

File: src/shellbench/batch.py

What this module does
---------------------
It builds the family definition (one ``BuildingInput`` per building), runs
``generator.generate`` on each building and writes one row per building in the
frozen format of ``docs/data_card.md``. A building that fails or cannot be run
is written with its status and reason; no row is dropped (preregistration 2.0).

Family definition
-----------------
Storey counts 3-8 and PGA 0.05, 0.10, 0.15, 0.20, 0.30 and 0.40 g
(preregistration 2.0, research_question.md). Every other input is the anchor's
(tests/test_generator_anchor.py gives the source of each value). Taller
buildings add 3.6 m storeys above the 4.55 m ground storey [J]. Tg 0.35 s and
C40 for every building [J]; both are columns, so later values can be added.

Order: the validated 0.10 g block first, then the other PGAs in rising order;
storeys rise inside each block [J]. ``--n 10`` takes the first ten buildings,
so the sample shows the six 0.10 g rows and the first four 0.05 g rows.

PGA and alpha_max
-----------------
alpha_max comes from ``seismic.alpha_max_frequent`` (Table 5.1.4-1, all six
PGAs since 4 Nov 2026). A missing entry still gives status ``blocked``.
Seismic grade from Table 6.1.2 sets the column axial ratio limit (Table 6.3.6).
A building taller than the frame limit of Table 6.1.1 (24 m at 9 degrees) is
kept with status ``outside_code`` and is not run. Height is the sum of storey
heights [J].

Carbon
------
The column ``takeoff_scope`` names the elements in each row (``--scope``):

* ``frame_strip_v1`` (pilot): the quantities from ``generator.quantities``.
  One frame strip, with slab, frame beams, columns and their longitudinal bars.
* ``building_v2``: v1 plus the anchor-plan elements that do not depend on
  member size (``carbon.family_fixed_per_m2``, grid plan, code steel). Slab
  bars and secondary beams go to the floor; longitudinal beams go to lateral.
  Frame-beam and column stirrups and footings are still left out (data card
  row 4).
* ``building_v3``: v2 plus frame-beam and column stirrups at the generator's
  member sizes (``carbon.frame_stirrups_kg``, anchor detailing [J]), both to
  lateral. Footings are still left out: the generator returns no base loads.

Factors come from ``data/carbon_factors.csv`` (set GBT51366).

Usage::

    python -m shellbench.batch --n 10 --out results/family_rc_sample

Units: m, s, g (PGA), mm for sections, m^3 and kg per m^2 of floor, kgCO2e
per m^2 of floor.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

import pandas as pd

import shellbench
from shellbench import anchor_frame as af
from shellbench import carbon as cb
from shellbench import generator as g
from shellbench import seismic as s

ROOT = Path(__file__).resolve().parents[2]
FACTOR_FILE = ROOT / "data" / "carbon_factors.csv"
FACTOR_SET = "GBT51366"  # the only set in data/carbon_factors.csv
RELEASE = "pre-release, not for results"  # schedule.md, ShellForm hand-over item 2
TAKEOFF_SCOPE = "frame_strip_v1"  # slab, frame beams, columns, longitudinal bars
#: Take-off scopes. ``building_v2`` adds the size-independent elements of the
#: anchor plan (``carbon.family_fixed_per_m2``): slab bars and secondary beams
#: to the floor, longitudinal beams to the lateral system (preregistration.md,
#: Measured). Frame-beam and column stirrups and footings are not in it yet.
SCOPES: tuple[str, ...] = (TAKEOFF_SCOPE, "building_v2", "building_v3")

STOREYS: tuple[int, ...] = (3, 4, 5, 6, 7, 8)  # preregistration 2.0
PGAS_G: tuple[float, ...] = (0.10, 0.05, 0.15, 0.20, 0.30, 0.40)  # 0.10 g first [J]
#: Intensity for each PGA, GB 50011-2010 Table 3.2.2 (2016 edition, p. 6; checked:
#: S. N. R. Hasib, 4 Nov 2026). 0.15 g and 0.30 g are designed
#: as 7 and 8 degrees (3.2.2).
INTENSITY: dict[float, int] = {0.05: 6, 0.10: 7, 0.15: 7, 0.20: 8, 0.30: 8, 0.40: 9}
#: Largest height of a frame structure [m], GB 50011-2010 Table 6.1.1 (p. 48).
FRAME_MAX_HEIGHT_M: dict[float, float] = {0.05: 60.0, 0.10: 50.0, 0.15: 50.0, 0.20: 40.0,
                                          0.30: 35.0, 0.40: 24.0}
#: Frame seismic grade, GB 50011-2010 Table 6.1.2 (p. 49), class C buildings:
#: intensity -> (grade at height <= 24 m, grade above 24 m).
FRAME_GRADE: dict[int, tuple[int, int]] = {6: (4, 3), 7: (3, 2), 8: (2, 1), 9: (1, 1)}
GRADE_SPLIT_HEIGHT_M: float = 24.0  # Table 6.1.2
#: Column axial ratio limit of a frame by seismic grade, GB 50011-2010 Table 6.3.6 (p. 62).
FRAME_AXIAL_LIMIT: dict[int, float] = {1: 0.65, 2: 0.75, 3: 0.85, 4: 0.90}
TG_S: float = 0.35  # anchor, test_generator_anchor.py [J] for the family
CONCRETE_GRADE: str = "C40"  # spec X1; checks.py values are C40
GROUND_STOREY_M: float = 4.55  # spec G7 (B4)
UPPER_STOREY_M: float = 3.60  # spec G6

#: Anchor inputs; each value and its source is listed in tests/test_generator_anchor.py.
ANCHOR = g.BuildingInput(
    spans_m=af.SPANS_M, storey_heights_m=af.STOREY_HEIGHTS_M, tributary_width_m=7.2,
    slab_panel_m=3.6, floor_dead_kn_m2=4.05, roof_dead_kn_m2=4.224,
    live_kn_m2=(2.5, 3.0, 2.5), roof_live_kn_m2=0.5,
    floor_secondary_kn_m=(2.54, 2.54, 2.54), roof_secondary_kn_m=(2.78, 2.54, 2.78),
    floor_beam_wall_kn_m=(5.51, 0.0, 5.51), exterior_wall_kn_m=8.37,
    interior_wall_kn_m=6.36, longitudinal_beam_kn_m=3.61, parapet_kn_m=2.54,
    alpha_max=0.08, tg_s=0.35, psi_t=0.7, concrete_e_mpa=3.25e4, beam_i_factor=af.BEAM_INERTIA_FACTOR)

#: Frozen column order of family_rc (docs/data_card.md). Add columns at the end only.
COLUMNS: tuple[str, ...] = (
    "building_id", "release", "shellbench_version", "takeoff_scope",
    "storeys", "pga_g", "intensity", "tg_s", "alpha_max", "concrete_grade",
    "spans_m", "storey_heights_m", "tributary_width_m", "floor_area_m2", "floor_system",
    "status", "failure_reason", "n_passes", "period_s", "max_drift_ratio", "axial_ratio",
    "column_mm", "beam_b_mm", "beam_h_mm", "slab_mm",
    "concrete_m3_per_m2", "bar_steel_kg_per_m2",
    "floor_concrete_m3_per_m2", "lateral_concrete_m3_per_m2",
    "floor_steel_kg_per_m2", "lateral_steel_kg_per_m2",
    "carbon_floor_kgco2e_per_m2", "carbon_lateral_kgco2e_per_m2", "carbon_building_kgco2e_per_m2",
    "seismic_grade", "axial_ratio_limit",  # added 4 Nov 2026, at the end
)
#: family_shell order (docs/data_card.md): COLUMNS[:34] + shell columns 35-47 + COLUMNS[34:].
FROZEN_RC_COUNT: int = 34


def seismic_grade(intensity: int, height_m: float) -> int:
    """Frame seismic grade (1-4) from GB 50011-2010 Table 6.1.2, class C building."""
    low, high = FRAME_GRADE[intensity]
    return low if height_m <= GRADE_SPLIT_HEIGHT_M else high


def building_id(storeys: int, pga_g: float, tg_s: float, grade: str) -> str:
    """Stable building ID, shared by family_rc and family_shell.

    It is made from the inputs, not from a row index, so adding a family
    dimension later does not change an existing ID. Example: ``s04-p010-tg35-C40``.
    """
    return f"s{storeys:02d}-p{round(pga_g * 100):03d}-tg{round(tg_s * 100):02d}-{grade}"


def storey_heights(storeys: int) -> tuple[float, ...]:
    """Ground storey 4.55 m, then 3.6 m storeys [m]."""
    return (GROUND_STOREY_M,) + (UPPER_STOREY_M,) * (storeys - 1)


def family() -> list[dict]:
    """The family definition, in run order: one dict of inputs per building."""
    return [{"storeys": n, "pga_g": pga, "intensity": INTENSITY[pga], "tg_s": TG_S,
             "concrete_grade": CONCRETE_GRADE,
             "building_id": building_id(n, pga, TG_S, CONCRETE_GRADE)}
            for pga in PGAS_G for n in STOREYS]


def factors() -> tuple[float, float]:
    """Carbon factors: concrete [kgCO2e/m^3] and bar steel [kgCO2e/kg]."""
    f = cb.read_factors(FACTOR_FILE)
    conc, conc_unit = f[(FACTOR_SET, CONCRETE_GRADE)]
    steel, steel_unit = f[(FACTOR_SET, cb.BAR_STEEL)]
    return conc * cb.CONVERSIONS[conc_unit][1], steel * cb.CONVERSIONS[steel_unit][1]


def run_building(spec: dict, conc_factor: float, steel_factor: float, drift_rule: str = "best_ratio",
                 beam_i_factor: float | None = None, scope: str = TAKEOFF_SCOPE) -> dict:
    """Run one building and return its row (all ``COLUMNS``).

    Args:
        spec: One entry of ``family()``.
        conc_factor: Concrete factor [kgCO2e/m^3].
        steel_factor: Bar steel factor [kgCO2e/kg].
        drift_rule: R11 drift-fix rule, one of ``generator.DRIFT_RULES``.
        beam_i_factor: Beam I factor on I0 [-]; None keeps the anchor value
            (``anchor_frame.BEAM_INERTIA_FACTOR``, spec M7). Sensitivity runs only.
        scope: Take-off scope, one of ``SCOPES``. Stirrups in ``building_v2``
            use the bar steel factor: the HPB300 row equals the HRB400 row (D28 (e)).
    """
    if scope not in SCOPES:
        raise ValueError(f"unknown take-off scope {scope!r}")
    height = sum(storey_heights(spec["storeys"]))
    grade = seismic_grade(spec["intensity"], height)
    b = replace(ANCHOR, storey_heights_m=storey_heights(spec["storeys"]), tg_s=spec["tg_s"],
                axial_ratio_limit=FRAME_AXIAL_LIMIT[grade])
    if beam_i_factor is not None:
        b = replace(b, beam_i_factor=beam_i_factor)
    n =spec["storeys"]
    row = dict.fromkeys(COLUMNS)
    row.update(spec)
    row.update(release=RELEASE, shellbench_version=shellbench.__version__, takeoff_scope=scope,
               spans_m="/".join(f"{x:g}" for x in b.spans_m),
               storey_heights_m="/".join(f"{x:g}" for x in b.storey_heights_m),
               tributary_width_m=b.tributary_width_m,
               floor_area_m2=n * sum(b.spans_m) * b.tributary_width_m, floor_system="beam_slab",
               failure_reason="", seismic_grade=grade, axial_ratio_limit=b.axial_ratio_limit)
    if height > FRAME_MAX_HEIGHT_M[spec["pga_g"]]:
        row.update(status="outside_code", failure_reason=(
            f"frame height {height:g} m > {FRAME_MAX_HEIGHT_M[spec['pga_g']]:g} m (GB 50011 Table 6.1.1)"))
        return row
    try:
        b = replace(b, alpha_max=s.alpha_max_frequent(spec["intensity"], spec["pga_g"]))
    except KeyError as exc:
        row.update(status="blocked", failure_reason=str(exc).strip("'\""))
        return row
    row["alpha_max"] = b.alpha_max
    try:
        res = g.generate(b, drift_rule=drift_rule)
    except RuntimeError as exc:
        row.update(status="failed", failure_reason=str(exc))
        return row
    q = res.quantities
    floor_c, lat_c = q["slab_concrete_m3_per_m2"], q["beam_concrete_m3_per_m2"] + q["column_concrete_m3_per_m2"]
    floor_s, lat_s = 0.0, q["beam_bar_kg_per_m2"] + q["column_bar_kg_per_m2"]  # slab bars not in v1
    conc_all, steel_all = q["concrete_m3_per_m2"], q["bar_steel_kg_per_m2"]
    if scope in ("building_v2", "building_v3"):
        for key, v in cb.family_fixed_per_m2().items():
            to_floor = cb.FAMILY_FIXED_ELEMENTS[key] == "floor"
            if key[1] == cb.CONCRETE_GRADE:
                floor_c, lat_c = (floor_c + v, lat_c) if to_floor else (floor_c, lat_c + v)
                conc_all += v
            else:
                floor_s, lat_s = (floor_s + v, lat_s) if to_floor else (floor_s, lat_s + v)
                steel_all += v
    if scope == "building_v3":
        area = n * sum(b.spans_m) * b.tributary_width_m
        sb, sc = cb.frame_stirrups_kg(b.spans_m, b.storey_heights_m, res.final.column_mm,
                                      tuple(res.final.beams_mm))
        lat_s += (sb + sc) / area
        steel_all += (sb + sc) / area
    row.update(
        status="ok", n_passes=sum(h.startswith("pass ") for h in res.history), period_s=res.period_s,
        max_drift_ratio=max(res.drift_ratios), axial_ratio=res.axial_ratio,
        column_mm=res.final.column_mm, beam_b_mm="/".join(str(bw) for bw, _ in res.final.beams_mm),
        beam_h_mm="/".join(str(h) for _, h in res.final.beams_mm), slab_mm=res.final.slab_mm,
        concrete_m3_per_m2=conc_all, bar_steel_kg_per_m2=steel_all,
        floor_concrete_m3_per_m2=floor_c, lateral_concrete_m3_per_m2=lat_c,
        floor_steel_kg_per_m2=floor_s, lateral_steel_kg_per_m2=lat_s,
        carbon_floor_kgco2e_per_m2=floor_c * conc_factor + floor_s * steel_factor,
        carbon_lateral_kgco2e_per_m2=lat_c * conc_factor + lat_s * steel_factor)
    row["carbon_building_kgco2e_per_m2"] = row["carbon_floor_kgco2e_per_m2"] + row["carbon_lateral_kgco2e_per_m2"]
    return row


def run_family(n: int | None = None, drift_rule: str = "best_ratio",
               beam_i_factor: float | None = None, scope: str = TAKEOFF_SCOPE) -> pd.DataFrame:
    """Run the first ``n`` buildings of the family (all if None), frozen column order.

    ``beam_i_factor`` overrides the beam I factor for a sensitivity run (None = anchor value).
    """
    conc, steel = factors()
    specs = family()[:n] if n else family()
    return pd.DataFrame([run_building(sp, conc, steel, drift_rule, beam_i_factor, scope) for sp in specs], columns=list(COLUMNS))


def write(df: pd.DataFrame, stem: Path) -> None:
    """Write ``stem``.parquet and ``stem``.csv (numbers to 4 significant figures in the CSV)."""
    stem.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(stem.with_suffix(".parquet"), index=False)
    df.to_csv(stem.with_suffix(".csv"), index=False, float_format="%.4g")


def main(argv: list[str] | None = None) -> None:
    """Command line: ``--n`` buildings, written to ``--out`` (no suffix)."""
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--n", type=int, default=None, help="first n buildings of the family")
    p.add_argument("--out", type=Path, default=ROOT / "results" / "family_rc_sample")
    p.add_argument("--drift-rule", choices=g.DRIFT_RULES, default="best_ratio",
                   help="R11 drift-fix rule (decision card 2, 5 Nov 2026)")
    p.add_argument("--beam-i-factor", type=float, default=None,
                   help="beam I factor on I0 for a sensitivity run (default: spec M7 value)")
    p.add_argument("--scope", choices=SCOPES, default=TAKEOFF_SCOPE,
                   help="take-off scope (data_card row 4)")
    a = p.parse_args(argv)
    df = run_family(a.n, a.drift_rule, a.beam_i_factor, a.scope)
    write(df, a.out)
    print(df["status"].value_counts().to_string())


if __name__ == "__main__":
    main()
