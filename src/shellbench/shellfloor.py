"""Shell floor in the generator (Day 29): the family_shell rows.

Each building of the conventional family is designed again with a vaulted
shell floor in place of the 120 mm slab and secondary beams (floor_concept,
layout A). The frame is sized by the same generator (R3-R14) under the shell
floor's dead load, so the knock-on in beams, columns and their steel is in
the row.

A floor variant pairs the two layout-A spans of the floor library
(results/floor_library.csv): 6.0 m (end bays) and 6.6 m (inner bays), with
the same rise, levelling and mesh. Its per-m^2 values are the bay-length
weighted mean of the two cases: 2 x 6.0 and 4 x 6.6 m of the 38.4 m grid
(spec G3) [J]. A variant is used only if both cases pass.

Floor of one row, per m^2 of floor:

* dead load = shell self-weight (concrete_m3_m2 x 25 kN/m^3) + finishes
  (panel.FINISHES_PA) + levelling (mean fill depth f/3, or the raised-floor
  mass) + topping (25 kN/m^3 x topping thickness);
* concrete = shell + topping; steel = mesh + ties (no topping mesh [J]);
* fill or raised floor mass, with its own factor (data/carbon_factors.csv).

The lateral system is the conventional row's, as building_v2 counts it, plus
the beam depth that the slab took in the conventional take-off (with no slab,
the beams are counted full depth) [J].

Not modelled here (limitations, Paper 1 Methods):

* the rigid-diaphragm test (H3, Day 27, ``diaphragm.py``) fills
  ``diaphragm_rigid`` for every row; the topping rule is ``topping_rule``;
* the beam stiffness factor stays the anchor's (spec M7), as if the floor
  still gave a slab flange [J];
* the roof keeps the conventional slab [J];
* the vault thrust is carried by the ties only (floor_concept 3).
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

import pandas as pd

from shellbench import batch as bt
from shellbench import carbon as cb
from shellbench import diaphragm as dp
from shellbench import generator as gen
from shellbench import panel
from shellbench import provenance

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "results" / "floor_library.csv"
#: Bay lengths of the 38.4 m grid on each layout-A span (spec G3) [m].
BAY_WEIGHTS_M: dict[float, float] = {6.0: 2 * 6.0, 6.6: 4 * 6.6}
TOPPINGS_MM: tuple[int, ...] = (0, 40, 50, 60)  # preregistration 2.3
CONCRETE_KN_M3: float = panel.CONCRETE_N_M3 / 1e3  # spec X7
#: Carbon factor row of each levelling option (data/carbon_factors.csv).
LEVELLING_FACTOR: dict[str, tuple[str, str]] = {
    "foamed_fill": ("GBT51366", "FOAMED_FILL"),
    "recycled_fill": ("GBT51366", "RECYCLED_FILL"),
    "raised_floor": ("OVAL2023", "RAISED_FLOOR"),
}
SHELL_COLUMNS: tuple[str, ...] = (
    "floor_variant_id", "vault_span_m", "rise_ratio", "levelling", "mesh_layers",
    "shell_thickness_mm", "tie_bar_mm", "tie_spacing_m", "tie_prestressed", "topping_mm",
    "diaphragm_rigid", "fill_kg_per_m2", "tie_steel_kg_per_m2",
)
COLUMNS: tuple[str, ...] = bt.COLUMNS[:bt.FROZEN_RC_COUNT] + SHELL_COLUMNS + bt.COLUMNS[bt.FROZEN_RC_COUNT:]
TIE_SPACING_M: float = 1.2  # floor_concept 4.1, approved 3 Nov


def fill_kg_m2(levelling: str, span_m: float, rise_ratio: float) -> float:
    """Levelling mass per m^2 of plan [kg/m^2]: fill density x f/3, or the raised-floor mass."""
    kind, value = panel.LEVELLING[levelling]
    return value * span_m * rise_ratio / 3.0 if kind == "fill" else value


def variants(path: Path = LIBRARY) -> list[dict]:
    """Floor variants: the 6.0 and 6.6 m library cases paired and weighted by bay length."""
    lib = pd.read_csv(path)
    out = []
    total = sum(BAY_WEIGHTS_M.values())
    for (r, lev, m), grp in lib.groupby(["rise_ratio", "levelling", "mesh_layers"], sort=True):
        cases = {row.span_m: row for row in grp.itertuples()}
        if set(cases) != set(BAY_WEIGHTS_M) or not all(bool(c.passes) for c in cases.values()):
            continue

        def mean(f):
            """Return the bay-weighted mean of f over the spans."""
            return sum(BAY_WEIGHTS_M[L] * f(cases[L], L) for L in BAY_WEIGHTS_M) / total
        out.append({
            "floor_variant_id": "+".join(cases[L].variant_id for L in sorted(cases)),
            "vault_span_m": "/".join(f"{L:g}" for L in sorted(cases)),
            "rise_ratio": r, "levelling": lev, "mesh_layers": int(m),
            "shell_thickness_mm": "/".join(f"{cases[L].thickness_m * 1000:g}" for L in sorted(cases)),
            "tie_bar_mm": "/".join(f"{cases[L].tie_bar_mm:g}" for L in sorted(cases)),
            "tie_prestressed": all(bool(c.prestressed) for c in cases.values()),
            "concrete_m3_m2": mean(lambda c, L: c.concrete_m3_m2),
            "mesh_kg_m2": mean(lambda c, L: c.mesh_kg_m2),
            "tie_kg_m2": mean(lambda c, L: c.tie_kg_m2),
            "fill_kg_m2": mean(lambda c, L: fill_kg_m2(lev, L, r)),
        })
    return out


def floor_dead_kn_m2(v: dict, topping_mm: int) -> float:
    """Floor dead load of a variant with its topping [kN/m^2]."""
    return (CONCRETE_KN_M3 * (v["concrete_m3_m2"] + topping_mm / 1000.0) + panel.FINISHES_PA / 1e3
            + v["fill_kg_m2"] * panel.G_ACCEL / 1e3)


def shell_input(v: dict, topping_mm: int) -> bt.g.BuildingInput:
    """The anchor input with the shell floor: its dead load and no secondary beams."""
    return replace(bt.ANCHOR, floor_dead_kn_m2=floor_dead_kn_m2(v, topping_mm),
                   floor_secondary_kn_m=tuple(0.0 for _ in bt.ANCHOR.spans_m))


def factors() -> dict[str, float]:
    """Carbon factors used here, per m^3 or per kg."""
    f = cb.read_factors(bt.FACTOR_FILE)

    def get(key):
        """Return a carbon factor converted to the unit used here."""
        value, unit = f[key]
        return value * cb.CONVERSIONS[unit][1]
    out = {"concrete": get((bt.FACTOR_SET, bt.CONCRETE_GRADE)), "bar": get((bt.FACTOR_SET, cb.BAR_STEEL)),
           "tie": get(("GBT51366", "TIE_BAR"))}
    out.update({lev: get(key) for lev, key in LEVELLING_FACTOR.items()})
    return out


def diaphragm_test(b: gen.BuildingInput, res: gen.GeneratorResult, v: dict, topping_mm: int) -> dict:
    """Rigid-diaphragm test of one designed building (diaphragm.py): every storey, every bay span.

    Each storey takes its own seismic force from the base-shear method and its
    own elastic drift from the generator. The two bay spans of the variant are
    tested with their own thickness and shear factor; the worst governs.

    Returns:
        ``rigid`` (every storey and bay has delta <= 2 x drift), ``ratio`` (largest
        delta / (2 drift)), ``stiffness_ratio`` (smallest drift / delta) and
        ``tau_over_ft`` (largest, information only).
    """
    _, forces = gen.seismic_forces(b, res.final)
    area = sum(b.spans_m) * b.tributary_width_m
    k_lib = dp.library_factors()
    ids = v["floor_variant_id"].split("+")
    spans = [float(x) for x in v["vault_span_m"].split("/")]
    thick = [float(x) / 1000.0 for x in v["shell_thickness_mm"].split("/")]
    worst = {"ratio": 0.0, "stiffness_ratio": float("inf"), "tau_over_ft": 0.0}
    for vid, span, t in zip(ids, spans, thick):
        k = dp.bay_stiffness_kn_m(k_lib[vid], t, topping_mm)
        for i, force in enumerate(forces):
            drift_m = res.drift_ratios[i] * b.storey_heights_m[i]
            c = dp.check_storey(force, area, drift_m, span, k, t, topping_mm)
            worst["ratio"] = max(worst["ratio"], c["ratio"])
            worst["stiffness_ratio"] = min(worst["stiffness_ratio"], c["stiffness_ratio"])
            worst["tau_over_ft"] = max(worst["tau_over_ft"], c["tau_over_ft"])
    worst["rigid"] = worst["ratio"] <= 1.0
    return worst


def topping_rule(side: pd.DataFrame) -> pd.DataFrame:
    """Smallest topping that makes each building and floor variant a rigid diaphragm.

    Args:
        side: The diaphragm side table (building_id, floor_variant_id, topping_mm, rigid, ...).

    Returns:
        One row per building and variant: ``min_topping_mm`` (NaN if even 60 mm fails).
    """
    ok = side[side["rigid"]]
    out = ok.groupby(["building_id", "floor_variant_id"])["topping_mm"].min().rename("min_topping_mm")
    keys = side[["building_id", "floor_variant_id"]].drop_duplicates().set_index(["building_id", "floor_variant_id"])
    return keys.join(out).reset_index()


def run_shell(spec: dict, v: dict, topping_mm: int, fac: dict[str, float], side: list | None = None) -> dict:
    """One family_shell row: the building of ``spec`` with floor variant ``v`` and a topping.

    ``side``, if a list, receives the diaphragm test of an ``ok`` row (ratios and stiffness ratio).
    """
    kept: dict = {}
    rc = bt.run_building(spec, fac["concrete"], fac["bar"], scope="building_v2", base=shell_input(v, topping_mm),
                         keep=kept)
    row = dict.fromkeys(COLUMNS)
    row.update({k: rc[k] for k in bt.COLUMNS})
    row.update({k: v[k] for k in SHELL_COLUMNS if k in v})
    row.update(floor_system="shell_vault", topping_mm=topping_mm, tie_spacing_m=TIE_SPACING_M,
               diaphragm_rigid=None, fill_kg_per_m2=v["fill_kg_m2"], tie_steel_kg_per_m2=v["tie_kg_m2"])
    if rc["status"] != "ok":
        return row
    fixed = cb.family_fixed_per_m2()
    # remove the conventional floor (slab, slab bars, secondary beams) ...
    slab_c = rc["slab_mm"] / 1000.0
    sec_c = sum(q for (e, m), q in fixed.items() if cb.FAMILY_FIXED_ELEMENTS[(e, m)] == "floor"
                and m == cb.CONCRETE_GRADE)
    # ... and count the beams full depth: the part the slab took [J]
    n = spec["storeys"]
    b = shell_input(v, topping_mm)
    beams_b = [float(x) for x in rc["beam_b_mm"].split("/")]
    extra = n * sum(bw / 1000.0 * slab_c * L for bw, L in zip(beams_b, b.spans_m)) / rc["floor_area_m2"]
    floor_c = v["concrete_m3_m2"] + topping_mm / 1000.0
    floor_s = v["mesh_kg_m2"] + v["tie_kg_m2"]
    lat_c = rc["lateral_concrete_m3_per_m2"] + extra
    lat_s = rc["lateral_steel_kg_per_m2"]
    c_floor = (floor_c * fac["concrete"] + v["mesh_kg_m2"] * fac["bar"] + v["tie_kg_m2"] * fac["tie"]
               + v["fill_kg_m2"] * fac[v["levelling"]])
    c_lat = lat_c * fac["concrete"] + lat_s * fac["bar"]
    row.update(slab_mm=0, floor_concrete_m3_per_m2=floor_c, floor_steel_kg_per_m2=floor_s,
               lateral_concrete_m3_per_m2=lat_c, concrete_m3_per_m2=floor_c + lat_c,
               bar_steel_kg_per_m2=floor_s + lat_s,
               carbon_floor_kgco2e_per_m2=c_floor, carbon_lateral_kgco2e_per_m2=c_lat,
               carbon_building_kgco2e_per_m2=c_floor + c_lat)
    assert sec_c >= 0.0  # secondary beams are dropped with the slab
    d = diaphragm_test(kept["b"], kept["res"], v, topping_mm)
    row["diaphragm_rigid"] = d["rigid"]
    if side is not None:
        side.append({"building_id": row["building_id"], "floor_variant_id": v["floor_variant_id"],
                     "topping_mm": topping_mm, **d})
    return row


#: Diaphragm side table of the last ``run`` call (rows of ``ok`` buildings).
SIDE: list[dict] = []


def run(storeys: int | None = None, pga_g: float | None = None, n_variants: int | None = None,
        toppings: tuple[int, ...] = TOPPINGS_MM) -> pd.DataFrame:
    """family_shell rows for the chosen buildings, variants and toppings."""
    fac = factors()
    specs = [sp for sp in bt.family() if (storeys is None or sp["storeys"] == storeys)
             and (pga_g is None or sp["pga_g"] == pga_g)]
    vs = variants()[:n_variants] if n_variants else variants()
    SIDE.clear()
    rows = [run_shell(sp, v, t, fac, SIDE) for sp in specs for v in vs for t in toppings]
    return pd.DataFrame(rows, columns=list(COLUMNS))


def main(argv: list[str] | None = None) -> None:
    """Command line: filter by --storeys and --pga, then write --out (CSV, Parquet, provenance)."""
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--storeys", type=int, default=None)
    p.add_argument("--pga", type=float, default=None)
    p.add_argument("--variants", type=int, default=None, help="first n floor variants")
    p.add_argument("--toppings", type=int, nargs="+", default=list(TOPPINGS_MM))
    p.add_argument("--out", type=Path, default=ROOT / "results" / "family_shell_sample")
    a = p.parse_args(argv)
    df = run(a.storeys, a.pga, a.variants, tuple(a.toppings))
    bt.write(df, a.out, storeys=a.storeys, pga=a.pga, variants=a.variants, toppings=a.toppings)
    side = pd.DataFrame(SIDE)
    side.to_csv(a.out.with_name(a.out.name + "_diaphragm.csv"), index=False)
    print(df["status"].value_counts().to_string())


if __name__ == "__main__":
    main()
