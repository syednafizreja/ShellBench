"""Anchor building, slab against shell (Day 30): the headline comparison.

File: src/shellbench/anchor_compare.py

What this module does
---------------------
It takes the 4-storey, 0.10 g building of the family (``s04-p010-tg35-C40``,
the family's version of the thesis building) and designs it twice with the
same generator: once with the conventional slab floor, once with the shell
floor. The shell variant and topping are chosen by the preregistered rule
(docs/preregistration.md 2.2): the lowest-carbon variant that passes every check,
including the rigid-diaphragm test (``diaphragm.py``).

It writes ``results/anchor_slab_vs_shell.csv`` (one row per quantity) and
``results/anchor_waterfall.csv`` (the steps from the slab building to the shell
building), and draws ``figures/anchor_waterfall.png``.

Hand check (playbook Day 30)
----------------------------
With the member sizes held fixed, the change of seismic weight that the
generator reports equals the change of floor load per m^2 times the floor
area of the frame strip, less the secondary beams that the shell floor does
not have. ``floor_weight_check`` does the sum by hand and compares.

Limits
------
* Footings are not in the take-off scope (building_v2), so the waterfall has
  no footing bar [J].
* The storey height is not changed for the shell floor (floor_concept 7) [J].
* One factor set exists in data/carbon_factors.csv (GB/T 51366). The playbook
  asks for both factor sets; the carbon-factor sensitivity of preregistration
  change C1 covers the bounds instead.
* The roof keeps the conventional slab (shellfloor.py) [J].

Units: kN, m, kg, kgCO2e.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from shellbench import batch as bt
from shellbench import carbon as cb
from shellbench import generator as gen
from shellbench import shellfloor as sf

ROOT = Path(__file__).resolve().parents[2]
ANCHOR_ID = "s04-p010-tg35-C40"
RESULTS_CSV = ROOT / "results" / "anchor_slab_vs_shell.csv"
WATERFALL_CSV = ROOT / "results" / "anchor_waterfall.csv"
WATERFALL_PNG = ROOT / "figures" / "anchor_waterfall.png"
FAMILY_SHELL = ROOT / "results" / "family_shell"


def anchor_spec() -> dict:
    """The family entry of the anchor building."""
    return next(sp for sp in bt.family() if sp["building_id"] == ANCHOR_ID)


def choose_variant(df: pd.DataFrame, side: pd.DataFrame, building_id: str = ANCHOR_ID) -> tuple[str, int]:
    """Lowest-carbon variant and topping that pass the diaphragm test for one building.

    Args:
        df: family_shell rows.
        side: The diaphragm side table (``family_shell_diaphragm.csv``).
        building_id: Building to choose for.

    Returns:
        (floor_variant_id, topping_mm).
    """
    rows = df[(df["building_id"] == building_id) & (df["status"] == "ok")]
    rigid = side[(side["building_id"] == building_id) & side["rigid"]][["floor_variant_id", "topping_mm"]]
    rows = rows.merge(rigid, on=["floor_variant_id", "topping_mm"])
    best = rows.loc[rows["carbon_building_kgco2e_per_m2"].idxmin()]
    return str(best["floor_variant_id"]), int(best["topping_mm"])


def floor_weight_check(v: dict, topping_mm: int) -> dict[str, float]:
    """Seismic weight change with the sizes held fixed: code against hand sum [kN].

    Hand sum, per level below the roof: (q_shell - q_slab) x (spans x tributary width)
    minus the secondary beams of the slab floor, sum(line load x span). The
    roof is unchanged.

    Args:
        v: Floor variant (``shellfloor.variants()`` entry).
        topping_mm: Topping [mm].

    Returns:
        ``code_kn`` (generator), ``hand_kn`` (sum above) and ``levels`` (storeys below the roof).
    """
    spec = anchor_spec()
    base = bt.ANCHOR
    b_slab = _input(base, spec)
    b_shell = _input(sf.shell_input(v, topping_mm), spec)
    z = gen.Sizes(column_mm=500, beams_mm=[(300, 600), (300, 550), (300, 600)], slab_mm=120)
    code = sum(gen.storey_weights_kn(b_shell, z)) - sum(gen.storey_weights_kn(b_slab, z))
    area = sum(base.spans_m) * base.tributary_width_m
    secondary = sum(w * L for w, L in zip(base.floor_secondary_kn_m, base.spans_m))
    levels = spec["storeys"] - 1
    hand = levels * ((sf.floor_dead_kn_m2(v, topping_mm) - base.floor_dead_kn_m2) * area - secondary)
    return {"code_kn": code, "hand_kn": hand, "levels": float(levels)}


def _input(base: gen.BuildingInput, spec: dict) -> gen.BuildingInput:
    """``base`` with the storey heights and Tg of ``spec`` (as ``batch.run_building`` sets them)."""
    from dataclasses import replace
    return replace(base, storey_heights_m=bt.storey_heights(spec["storeys"]), tg_s=spec["tg_s"])


def run_both(v: dict, topping_mm: int) -> dict[str, dict]:
    """Design the anchor with the slab and with the shell; return rows, inputs and results."""
    spec = anchor_spec()
    fac = sf.factors()
    out = {}
    for name, base in (("slab", None), ("shell", sf.shell_input(v, topping_mm))):
        kept: dict = {}
        row = bt.run_building(spec, fac["concrete"], fac["bar"], scope="building_v2", base=base, keep=kept)
        out[name] = {"row": row, **kept}
    out["shell"]["row"] = sf.run_shell(spec, v, topping_mm, fac)
    out["fac"] = fac
    return out


def _frame_carbon(q: dict[str, float], fac: dict[str, float]) -> dict[str, float]:
    """Carbon of beams and columns per m^2 of floor from the generator quantities."""
    return {
        "beams": q["beam_concrete_m3_per_m2"] * fac["concrete"]
        + (q["beam_bar_kg_per_m2"] + q["beam_stirrup_kg_per_m2"]) * fac["bar"],
        "columns": q["column_concrete_m3_per_m2"] * fac["concrete"]
        + (q["column_bar_kg_per_m2"] + q["column_stirrup_kg_per_m2"]) * fac["bar"],
    }


def waterfall(both: dict, v: dict, topping_mm: int) -> list[dict]:
    """Steps from the slab building to the shell building [kgCO2e per m^2 of floor].

    Steps: the slab floor removed; shell concrete, mesh, ties, fill, topping added;
    beams and columns changed (the beams include the depth the slab took in the
    slab take-off, shellfloor.py [J]). The sum of steps equals the change of
    whole-building carbon; ``assert`` checks it.
    """
    fac = both["fac"]
    slab, shell = both["slab"], both["shell"]
    qs, qh = slab["res"].quantities, shell["res"].quantities
    fs, fh = _frame_carbon(qs, fac), _frame_carbon(qh, fac)
    row_s, row_h = slab["row"], shell["row"]
    area = row_s["floor_area_m2"]
    n = slab["b"].storey_heights_m.__len__()
    beams_b = [float(x) for x in row_h["beam_b_mm"].split("/")]
    extra = n * sum(bw / 1000.0 * (shell["res"].final.slab_mm / 1000.0) * L
                    for bw, L in zip(beams_b, shell["b"].spans_m)) / area
    steps = [
        ("slab building", row_s["carbon_building_kgco2e_per_m2"], "total"),
        ("slab floor removed", -row_s["carbon_floor_kgco2e_per_m2"], "delta"),
        ("shell concrete", v["concrete_m3_m2"] * fac["concrete"], "delta"),
        ("mesh", v["mesh_kg_m2"] * fac["bar"], "delta"),
        ("ties", v["tie_kg_m2"] * fac["tie"], "delta"),
        ("fill or raised floor", v["fill_kg_m2"] * fac[v["levelling"]], "delta"),
        ("topping", topping_mm / 1000.0 * fac["concrete"], "delta"),
        ("beams", fh["beams"] - fs["beams"] + extra * fac["concrete"], "delta"),
        ("columns", fh["columns"] - fs["columns"], "delta"),
    ]
    total = sum(x for _, x, k in steps if k == "delta") + steps[0][1]
    steps.append(("shell building", row_h["carbon_building_kgco2e_per_m2"], "total"))
    assert abs(total - row_h["carbon_building_kgco2e_per_m2"]) < 1e-6, (total, row_h["carbon_building_kgco2e_per_m2"])
    return [{"step": s, "kgco2e_per_m2": x, "kind": k} for s, x, k in steps]


def comparison_rows(both: dict, v: dict, topping_mm: int) -> list[dict]:
    """One row per compared quantity: slab, shell, change."""
    out = []
    slab, shell = both["slab"], both["shell"]
    for key, label, unit in (
            ("carbon_floor_kgco2e_per_m2", "floor carbon", "kgCO2e/m2"),
            ("carbon_lateral_kgco2e_per_m2", "frame (lateral) carbon", "kgCO2e/m2"),
            ("carbon_building_kgco2e_per_m2", "whole-building carbon", "kgCO2e/m2"),
            ("period_s", "T1", "s"), ("max_drift_ratio", "largest drift ratio", "-"),
            ("column_mm", "column size", "mm"), ("beam_h_mm", "beam depths", "mm"),
            ("beam_b_mm", "beam widths", "mm")):
        out.append({"quantity": label, "unit": unit, "slab": slab["row"][key], "shell": shell["row"][key]})
    ws = gen.storey_weights_kn(slab["b"], slab["res"].final)
    wh = gen.storey_weights_kn(shell["b"], shell["res"].final)
    out.append({"quantity": "seismic weight", "unit": "kN", "slab": sum(ws), "shell": sum(wh)})
    out.append({"quantity": "base shear F_Ek", "unit": "kN", "slab": sum(gen.seismic_forces(slab["b"], slab["res"].final)[1]),
                "shell": sum(gen.seismic_forces(shell["b"], shell["res"].final)[1])})
    out.append({"quantity": "floor saving S_f", "unit": "-", "slab": None,
                "shell": 1.0 - shell["row"]["carbon_floor_kgco2e_per_m2"] / slab["row"]["carbon_floor_kgco2e_per_m2"]})
    out.append({"quantity": "whole-building saving S_b", "unit": "-", "slab": None,
                "shell": 1.0 - shell["row"]["carbon_building_kgco2e_per_m2"] / slab["row"]["carbon_building_kgco2e_per_m2"]})
    out.append({"quantity": "floor variant", "unit": "-", "slab": "slab 120 mm", "shell": v["floor_variant_id"]})
    out.append({"quantity": "topping", "unit": "mm", "slab": 0, "shell": topping_mm})
    return out


def plot_waterfall(steps: list[dict], path: Path = WATERFALL_PNG) -> None:
    """Draw the waterfall from the slab building to the shell building."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    level = 0.0
    for i, s in enumerate(steps):
        x = s["kgco2e_per_m2"]
        if s["kind"] == "total":
            ax.bar(i, x, color="#3b6fb6")
            ax.text(i, x + 1, f"{x:.1f}", ha="center", fontsize=8)
            level = x
        else:
            ax.bar(i, x, bottom=level, color="#c0392b" if x > 0 else "#2e8b57")
            ax.text(i, max(level, level + x) + 1, f"{x:+.1f}", ha="center", fontsize=8)
            level += x
    ax.set_xticks(range(len(steps)), [s["step"] for s in steps], rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Embodied carbon A1-A3 [kgCO2e per m2 of floor]")
    ax.set_title("Anchor building (4 storeys, 0.10 g): slab to shell, pre-release", fontsize=10)
    fig.text(0.01, 0.01, "© 2026 Syed Nafiz Reja Hasib. Elastic, screening-level; footings not in scope.", fontsize=7)
    fig.tight_layout()
    path.parent.mkdir(exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def main() -> None:
    """Choose the variant, run both buildings, write the two CSV files and the figure."""
    df = pd.read_csv(FAMILY_SHELL.with_suffix(".csv"))
    side = pd.read_csv(FAMILY_SHELL.with_name(FAMILY_SHELL.name + "_diaphragm.csv"))
    vid, topping = choose_variant(df, side)
    v = next(x for x in sf.variants() if x["floor_variant_id"] == vid)
    both = run_both(v, topping)
    steps = waterfall(both, v, topping)
    rows = comparison_rows(both, v, topping)
    chk = floor_weight_check(v, topping)
    rows.append({"quantity": "hand check: weight change, code", "unit": "kN", "slab": None, "shell": chk["code_kn"]})
    rows.append({"quantity": "hand check: weight change, by hand", "unit": "kN", "slab": None, "shell": chk["hand_kn"]})
    for path, data in ((RESULTS_CSV, rows), (WATERFALL_CSV, steps)):
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    plot_waterfall(steps)
    print(pd.DataFrame(rows).to_string())
    print(pd.DataFrame(steps).to_string())


if __name__ == "__main__":
    main()
