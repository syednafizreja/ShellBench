"""Day 31 checks on the two building families, before the dataset DOI.

File: src/shellbench/family_checks.py

What this module does
---------------------
Playbook Day 31, "Done when": ``family_shell`` has the same building IDs as
``family_rc``. It also checks the failure counts and recomputes three random
paired buildings by hand. The hand sums here read the carbon factors straight
from ``data/carbon_factors.csv`` and use only the columns of the result files,
so they do not share code with the runner that wrote the files.

Checks
------
1. Same building IDs in both files; the shell file has every floor variant and
   topping for every building (36 x 36 x 4 rows).
2. Failure counts: rows by status, buildings that fail, and the reason.
3. Every ``ok`` row: floor + lateral = building carbon; the conventional floor
   carbon equals concrete x C40 factor + bar steel x HRB400 factor.
4. Three paired buildings, drawn with ``provenance.SEED``: the conventional row
   and the shell row of the preregistered verdict variant (lowest carbon among
   the variants that pass the diaphragm test) are recomputed from their
   quantities, and S_f and S_b are recomputed from the carbon values.

Output: ``results/day31_checks.csv`` (one line per check).

Units: kgCO2e per m^2 of floor, unless a column says otherwise.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

import pandas as pd

from shellbench import provenance

ROOT = Path(__file__).resolve().parents[1].parent
RC = ROOT / "results" / "family_rc_r14_building_v2.parquet"
SHELL = ROOT / "results" / "family_shell.parquet"
FACTORS = ROOT / "data" / "carbon_factors.csv"
OUT = ROOT / "results" / "day31_checks.csv"

#: Tolerance on carbon sums [kgCO2e/m^2]: the parquet files keep full precision.
TOLERANCE: float = 1.0e-6
#: Paired buildings to recompute by hand (playbook Day 31).
N_PAIRS: int = 3


def factor(set_name: str, material: str) -> float:
    """Read one factor from data/carbon_factors.csv as kgCO2e per m^3 or per kg.

    ``kgCO2e/t`` values are divided by 1000.
    """
    with open(FACTORS, newline="") as f:
        for row in csv.DictReader(f):
            if row["set [text]"] == set_name and row["material [text]"] == material:
                value, unit = float(row["value"]), row["unit [text]"]
                return value / 1000.0 if unit == "kgCO2e/t" else value
    raise KeyError((set_name, material))


def level_factor(levelling: str) -> float:
    """Factor of the levelling layer, per kg."""
    return {"foamed_fill": factor("GBT51366", "FOAMED_FILL"),
            "recycled_fill": factor("GBT51366", "RECYCLED_FILL"),
            "raised_floor": factor("OVAL2023", "RAISED_FLOOR")}[levelling]


def verdict_variants(shell: pd.DataFrame, side: pd.DataFrame) -> pd.DataFrame:
    """The lowest-carbon shell row per building among the rows that pass the diaphragm test."""
    ok = shell[shell["status"] == "ok"].merge(
        side[side["rigid"]][["building_id", "floor_variant_id", "topping_mm"]],
        on=["building_id", "floor_variant_id", "topping_mm"])
    return ok.loc[ok.groupby("building_id")["carbon_building_kgco2e_per_m2"].idxmin()].set_index("building_id")


def shell_floor_by_hand(r: pd.Series) -> float:
    """Floor carbon of a shell row from its quantities and the factor file [kgCO2e/m^2].

    Concrete (shell + topping) x C40; mesh = floor steel - tie steel, x bar factor;
    ties x tie factor; levelling mass x its factor.
    """
    mesh = r["floor_steel_kg_per_m2"] - r["tie_steel_kg_per_m2"]
    return (r["floor_concrete_m3_per_m2"] * factor("GBT51366", "C40")
            + mesh * factor("GBT51366", "HRB400")
            + r["tie_steel_kg_per_m2"] * factor("GBT51366", "TIE_BAR")
            + r["fill_kg_per_m2"] * level_factor(r["levelling"]))


def run_checks() -> list[dict]:
    """Run all checks; one dict per check line (``check``, ``result``, ``detail``)."""
    rc, shell = pd.read_parquet(RC), pd.read_parquet(SHELL)
    side = pd.read_csv(ROOT / "results" / "family_shell_diaphragm.csv")
    out: list[dict] = []

    def add(check: str, passed: bool | None, detail: str) -> None:
        out.append({"check": check, "result": {True: "pass", False: "FAIL", None: "info"}[passed], "detail": detail})

    same = set(rc["building_id"]) == set(shell["building_id"])
    add("same building IDs", same, f"{rc['building_id'].nunique()} in family_rc, {shell['building_id'].nunique()} in family_shell")
    per = shell.groupby("building_id").size()
    add("shell rows per building", bool((per == 36 * 4).all()), f"{int(per.min())} to {int(per.max())} (expect 144 = 36 variants x 4 toppings)")
    st_rc, st_sh = rc["status"].value_counts().to_dict(), shell["status"].value_counts().to_dict()
    add("family_rc status", None, str(st_rc))
    add("family_shell status", None, str(st_sh))
    in_rc = st_rc.get("ok", 0) + st_rc.get("failed", 0)
    in_sh = st_sh.get("ok", 0) + st_sh.get("failed", 0)
    add("failed share inside the code, family_rc", None, f"{st_rc.get('failed', 0)} of {in_rc} = {100 * st_rc.get('failed', 0) / in_rc:.1f} %")
    add("failed share inside the code, family_shell", None, f"{st_sh.get('failed', 0)} of {in_sh} = {100 * st_sh.get('failed', 0) / in_sh:.1f} %")
    fails = shell[shell["status"] == "failed"].groupby("building_id")["failure_reason"].agg(lambda s: s.iloc[0][:60])
    add("failing buildings, family_shell", None, "; ".join(f"{k}: {v}" for k, v in fails.items()))
    bad_rc = rc[(rc["status"] == "failed")]["building_id"].tolist()
    add("failing buildings, family_rc", None, ", ".join(bad_rc))
    both_fail = set(bad_rc) <= set(fails.index)
    add("a building that fails conventionally also fails with shell, or not", None,
        f"conventional failures {bad_rc}; shell failures {sorted(fails.index)}; overlap {both_fail}")

    for name, df in (("family_rc", rc), ("family_shell", shell)):
        ok = df[df["status"] == "ok"]
        err = (ok["carbon_floor_kgco2e_per_m2"] + ok["carbon_lateral_kgco2e_per_m2"] - ok["carbon_building_kgco2e_per_m2"]).abs().max()
        add(f"{name}: floor + lateral = building", err < TOLERANCE, f"largest error {err:.2e}")
    ok = rc[rc["status"] == "ok"]
    hand = ok["floor_concrete_m3_per_m2"] * factor("GBT51366", "C40") + ok["floor_steel_kg_per_m2"] * factor("GBT51366", "HRB400")
    err = (hand - ok["carbon_floor_kgco2e_per_m2"]).abs().max()
    add("family_rc: floor carbon from quantities", err < TOLERANCE, f"largest error {err:.2e}")
    oks = shell[shell["status"] == "ok"]
    hand = oks.apply(shell_floor_by_hand, axis=1)
    err = (hand - oks["carbon_floor_kgco2e_per_m2"]).abs().max()
    add("family_shell: floor carbon from quantities", err < TOLERANCE, f"largest error {err:.2e} over {len(oks)} rows")

    best = verdict_variants(shell, side)
    rc_ok = rc[rc["status"] == "ok"].set_index("building_id")
    pool = sorted(set(best.index) & set(rc_ok.index))
    rng = random.Random(provenance.SEED)
    for b in rng.sample(pool, N_PAIRS):
        r, s = rc_ok.loc[b], best.loc[b]
        c_floor_rc = r["floor_concrete_m3_per_m2"] * factor("GBT51366", "C40") + r["floor_steel_kg_per_m2"] * factor("GBT51366", "HRB400")
        c_lat_rc = r["lateral_concrete_m3_per_m2"] * factor("GBT51366", "C40") + r["lateral_steel_kg_per_m2"] * factor("GBT51366", "HRB400")
        c_floor_sh = shell_floor_by_hand(s)
        c_lat_sh = s["lateral_concrete_m3_per_m2"] * factor("GBT51366", "C40") + s["lateral_steel_kg_per_m2"] * factor("GBT51366", "HRB400")
        s_f = 1.0 - c_floor_sh / c_floor_rc
        s_b = 1.0 - (c_floor_sh + c_lat_sh) / (c_floor_rc + c_lat_rc)
        file_s_f = 1.0 - s["carbon_floor_kgco2e_per_m2"] / r["carbon_floor_kgco2e_per_m2"]
        file_s_b = 1.0 - s["carbon_building_kgco2e_per_m2"] / r["carbon_building_kgco2e_per_m2"]
        ok_pair = (abs(c_floor_rc + c_lat_rc - r["carbon_building_kgco2e_per_m2"]) < TOLERANCE
                   and abs(c_floor_sh + c_lat_sh - s["carbon_building_kgco2e_per_m2"]) < TOLERANCE
                   and abs(s_f - file_s_f) < 1e-9 and abs(s_b - file_s_b) < 1e-9)
        add(f"pair {b}", ok_pair, f"slab floor {c_floor_rc:.2f}, building {c_floor_rc + c_lat_rc:.2f}; shell {s['floor_variant_id']} + {int(s['topping_mm'])} mm: "
            f"floor {c_floor_sh:.2f}, building {c_floor_sh + c_lat_sh:.2f}; S_f {100 * s_f:.1f} %, S_b {100 * s_b:.1f} %")
    return out


def main() -> None:
    """Run the checks, print them and write ``results/day31_checks.csv``."""
    rows = run_checks()
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["check", "result", "detail"])
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"{r['result']:5} {r['check']}: {r['detail']}")


if __name__ == "__main__":
    main()
