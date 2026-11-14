"""Verdicts on H1, H2 and H3, and the sensitivity cases (Day 32; preregistration 2.1-2.3, C1, C2).

File: src/shellbench/verdicts.py

What this module does
---------------------
It reads the two family files, recomputes the carbon of every row from its
quantities and the factor file (so the bounds of change C1 can be applied),
and applies the verdict rules of docs/preregistration.md **exactly as written**.

Rules, in short (the file preregistration.md is the authority):

* The primary baseline is the conventional design of the building (family_rc).
* The shell design of a building is its lowest-carbon row among the rows that
  pass the diaphragm test (2.0). The topping is part of the row.
* H1: S_f and S_b per building; supported if S_b < S_f and S_b > 0 in every
  building; partly supported if S_b > 0 in at least 90 % of buildings.
* H2: Spearman correlation of S_b with PGA at each fixed storey count, and with
  storey count at each fixed PGA; permutation test (10 000 permutations,
  two-sided, alpha 0.05, seed ``provenance.SEED``); supported if positive and
  significant in more than half of the slices for both, and the lateral-system
  saving also grows with PGA.
* H3: the share of buildings whose untopped floor fails the diaphragm rule and
  the median R of the topping; supported if both (more than half; R >= 5 %).

Only buildings with an ``ok`` conventional design and at least one ``ok`` rigid
shell row are compared. The others are counted and listed, never dropped quietly.

Choices not fixed by the plan, each marked [J] where it is used:
slices with fewer than 4 buildings cannot be significant and count as not
significant; "the lateral-system saving also grows with PGA" uses the same rule
as S_b (positive and significant in more than half of the storey-count slices).

Outputs: ``results/verdicts_buildings.csv`` (one row per building and case),
``results/verdicts_summary.csv`` (one row per case and hypothesis) and
``results/verdicts_slices.csv`` (every Spearman test).

Units: kgCO2e per m^2 of floor area; savings are fractions (the CSV also gives per cent).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from shellbench import provenance
from shellbench.family_checks import factor, level_factor

ROOT = Path(__file__).resolve().parents[2]
RC = ROOT / "results" / "family_rc_r14_building_v2.parquet"
SHELL = ROOT / "results" / "family_shell.parquet"
SIDE = ROOT / "results" / "family_shell_diaphragm.csv"
OUT_BUILDINGS = ROOT / "results" / "verdicts_buildings.csv"
OUT_SUMMARY = ROOT / "results" / "verdicts_summary.csv"
OUT_SLICES = ROOT / "results" / "verdicts_slices.csv"

#: Permutations of the H2 test and the significance level (preregistration 2.2).
N_PERMUTATIONS: int = 10_000
ALPHA: float = 0.05
#: Smallest slice that can reach p < 0.05 two-sided with a permutation test [J].
MIN_SLICE: int = 4
#: H1: share of buildings with S_b > 0 for "partly supported" (2.1).
H1_PARTLY_SHARE: float = 0.90
#: H3: median R needed (2.3).
H3_MIN_MEDIAN_R: float = 0.05
#: Seismic grade at which the grade-I rows are dropped in the sensitivity case (C2).
GRADE_I: int = 1


@dataclass(frozen=True)
class Case:
    """One analysis case: the factors that differ from the base set, and whether grade-I rows are dropped.

    ``c40`` is the concrete factor [kgCO2e/m^3]; ``steel`` is the factor of every steel row [kgCO2e/kg];
    ``None`` keeps the base value from ``data/carbon_factors.csv``.
    """

    name: str
    c40: float | None = None
    steel: float | None = None
    drop_grade_i: bool = False


def cases() -> list[Case]:
    """The primary case and the five sensitivity cases (C1: four factor bounds; C2: grade-I rows dropped).

    Bounds are rows already in ``data/carbon_factors.csv`` or in GB/T 51366-2019 Table D.0.1 (C1):
    C30 295 and C50 385 kgCO2e/m^3 for concrete; 1990 and 3030 kgCO2e/t for all steel.
    """
    return [Case("base"),
            Case("concrete_C30", c40=factor("GBT51366", "C30")),
            Case("concrete_C50", c40=385.0),
            Case("steel_converter", steel=factor("GBT51366", "TIE_STEEL_BOF")),
            Case("steel_eaf", steel=factor("GBT51366", "TIE_STEEL_EAF")),
            Case("drop_grade_I", drop_grade_i=True)]


def row_carbon(df: pd.DataFrame, case: Case) -> pd.DataFrame:
    """Floor, lateral and building carbon of every row of ``df`` under ``case`` [kgCO2e/m^2].

    Shell rows: concrete x C40; mesh steel (floor steel - tie steel) x bar factor; tie steel x tie factor;
    levelling mass x its factor. Conventional rows: concrete x C40 + steel x bar factor. Lateral: concrete x C40
    + steel x bar factor. The same formulas as ``family_checks`` (checked there against the files).
    """
    c40 = case.c40 if case.c40 is not None else factor("GBT51366", "C40")
    bar = case.steel if case.steel is not None else factor("GBT51366", "HRB400")
    tie = case.steel if case.steel is not None else factor("GBT51366", "TIE_BAR")
    shell = df["floor_system"] == "shell_vault"
    zero = pd.Series(0.0, index=df.index)
    tie_kg = df["tie_steel_kg_per_m2"].fillna(0.0).where(shell, 0.0) if "tie_steel_kg_per_m2" in df else zero
    fill = np.zeros(len(df))
    if "levelling" in df:
        for key in ("foamed_fill", "recycled_fill", "raised_floor"):
            m = (df["levelling"] == key).to_numpy()
            if m.any():
                fill[m] = df.loc[m, "fill_kg_per_m2"].to_numpy() * level_factor(key)
    floor = (df["floor_concrete_m3_per_m2"] * c40 + (df["floor_steel_kg_per_m2"] - tie_kg) * bar
             + tie_kg * tie + np.where(shell, fill, 0.0))
    lateral = df["lateral_concrete_m3_per_m2"] * c40 + df["lateral_steel_kg_per_m2"] * bar
    return pd.DataFrame({"floor": floor, "lateral": lateral, "building": floor + lateral}, index=df.index)


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Conventional rows and rigid shell rows (``ok`` only), with the case-independent columns."""
    rc = pd.read_parquet(RC)
    sh = pd.read_parquet(SHELL)
    side = pd.read_csv(SIDE)
    ok_side = side.loc[side["rigid"], ["building_id", "floor_variant_id", "topping_mm"]].assign(_rigid=True)
    sh = sh[sh["status"] == "ok"].merge(ok_side, on=["building_id", "floor_variant_id", "topping_mm"], how="left")
    sh["rigid_row"] = sh["_rigid"].fillna(False).astype(bool)
    return rc[rc["status"] == "ok"].copy(), sh


def building_table(rc: pd.DataFrame, sh: pd.DataFrame, case: Case) -> pd.DataFrame:
    """One row per compared building: S_f, S_b, lateral saving and the chosen shell row, under ``case``.

    The shell row is the lowest-carbon (building) row among the rigid rows, re-chosen under the case factors.
    """
    rc = rc.copy()
    rc_c = row_carbon(rc, case)
    rc["c_floor"], rc["c_lat"], rc["c_bld"] = rc_c["floor"], rc_c["lateral"], rc_c["building"]
    if case.drop_grade_i:
        rc = rc[rc["seismic_grade"] != GRADE_I]
    shr = sh[sh["rigid_row"]].copy()
    sc = row_carbon(shr, case)
    shr["s_floor"], shr["s_lat"], shr["s_bld"] = sc["floor"], sc["lateral"], sc["building"]
    best = shr.loc[shr.groupby("building_id")["s_bld"].idxmin()].set_index("building_id")
    t = rc.set_index("building_id").join(best[["s_floor", "s_lat", "s_bld", "floor_variant_id", "topping_mm"]], how="inner")
    t["s_f"] = 1.0 - t["s_floor"] / t["c_floor"]
    t["s_b"] = 1.0 - t["s_bld"] / t["c_bld"]
    t["abs_saving"] = t["c_bld"] - t["s_bld"]
    t["lateral_saving"] = t["c_lat"] - t["s_lat"]
    t["case"] = case.name
    keep = ["case", "storeys", "pga_g", "seismic_grade", "c_floor", "s_floor", "c_lat", "s_lat", "c_bld", "s_bld",
            "s_f", "s_b", "abs_saving", "lateral_saving", "floor_variant_id", "topping_mm"]
    return t[keep].reset_index().sort_values(["storeys", "pga_g"]).reset_index(drop=True)


def h1(t: pd.DataFrame) -> dict:
    """H1 numbers and verdict (preregistration 2.1)."""
    n = len(t)
    pos = int((t["s_b"] > 0).sum())
    below = int((t["s_b"] < t["s_f"]).sum())
    every = bool(((t["s_b"] < t["s_f"]) & (t["s_b"] > 0)).all())
    verdict = "supported" if every else "partly supported" if pos / n >= H1_PARTLY_SHARE else "not supported"
    return {"hypothesis": "H1", "verdict": verdict, "n_buildings": n, "n_s_b_positive": pos, "share_s_b_positive": pos / n,
            "n_s_b_below_s_f": below, "s_b_min": t["s_b"].min(), "s_b_median": t["s_b"].median(), "s_b_max": t["s_b"].max(),
            "s_f_min": t["s_f"].min(), "s_f_median": t["s_f"].median(), "s_f_max": t["s_f"].max()}


def permutation_p(x: np.ndarray, y: np.ndarray, rng: np.random.Generator, n_perm: int = N_PERMUTATIONS) -> tuple[float, float]:
    """Spearman rho and its two-sided permutation p-value (``n_perm`` shuffles of y; the observed order counts once)."""
    rho = spearmanr(x, y).statistic
    if not np.isfinite(rho):
        return float("nan"), 1.0
    ge = 1
    for _ in range(n_perm):
        r = spearmanr(x, rng.permutation(y)).statistic
        if abs(r) >= abs(rho) - 1e-12:
            ge += 1
    return float(rho), ge / (n_perm + 1)


def slices(t: pd.DataFrame, value: str, seed: int = provenance.SEED) -> pd.DataFrame:
    """Spearman tests of ``value`` against PGA (one slice per storey count) and against storeys (one per PGA)."""
    rng = np.random.default_rng(seed)
    rows = []
    for axis, fixed, other in (("pga", "storeys", "pga_g"), ("storeys", "pga_g", "storeys")):
        for level in sorted(t[fixed].unique()):
            g = t[t[fixed] == level]
            if len(g) < MIN_SLICE or g[other].nunique() < 2 or g[value].nunique() < 2:
                rho, p = float("nan"), 1.0
            else:
                rho, p = permutation_p(g[other].to_numpy(float), g[value].to_numpy(float), rng)
            rows.append({"value": value, "against": axis, "fixed": fixed, "level": float(level), "n": int(len(g)),
                         "rho": rho, "p": p, "positive_significant": bool(np.isfinite(rho) and rho > 0 and p < ALPHA)})
    return pd.DataFrame(rows)


def h2(t: pd.DataFrame, sl_b: pd.DataFrame, sl_lat: pd.DataFrame) -> dict:
    """H2 verdict from the slice tests (preregistration 2.2).

    "More than half of the fixed slices" is counted over all slices of that axis, those too small to test included [J].
    """
    def many(sl: pd.DataFrame, axis: str) -> tuple[int, int, bool]:
        """Slices on one axis with a significant positive trend: (count, slices, more than half)."""
        s = sl[sl["against"] == axis]
        k = int(s["positive_significant"].sum())
        return k, len(s), k > len(s) / 2

    k_pga, n_pga, ok_pga = many(sl_b, "pga")
    k_sto, n_sto, ok_sto = many(sl_b, "storeys")
    k_lat, n_lat, ok_lat = many(sl_lat, "pga")
    if ok_pga and ok_sto and ok_lat:
        verdict = "supported"
    elif ok_pga != ok_sto or (ok_pga and ok_sto):
        verdict = "partly supported"   # one axis only; or both axes but the lateral saving does not grow [J]
    else:
        verdict = "not supported"
    return {"hypothesis": "H2", "verdict": verdict, "n_buildings": len(t),
            "pga_slices_positive_significant": f"{k_pga} of {n_pga}", "storey_slices_positive_significant": f"{k_sto} of {n_sto}",
            "lateral_vs_pga_slices_positive_significant": f"{k_lat} of {n_lat}",
            "rho_median_pga": float(np.nanmedian(sl_b.loc[sl_b['against'] == 'pga', 'rho'])),
            "rho_median_storeys": float(np.nanmedian(sl_b.loc[sl_b['against'] == 'storeys', 'rho']))}


def h3(rc: pd.DataFrame, sh: pd.DataFrame, side: pd.DataFrame, case: Case, t: pd.DataFrame) -> dict:
    """H3 numbers and verdict (preregistration 2.3).

    For each compared building the floor is its chosen variant. It fails if the untopped (0 mm) row of that variant
    is not rigid. R = (S_b without topping - S_b with the minimum rigid topping) / S_b without topping.
    """
    all_rows = pd.read_parquet(SHELL)
    all_rows = all_rows[all_rows["status"] == "ok"].merge(
        side[["building_id", "floor_variant_id", "topping_mm", "rigid"]], on=["building_id", "floor_variant_id", "topping_mm"], how="left")
    sc = row_carbon(all_rows, case)
    all_rows["s_bld"] = sc["building"]
    rcc = row_carbon(rc, case)
    base = pd.Series(rcc["building"].to_numpy(), index=rc["building_id"].to_numpy())
    fails, rs, n_variants_fail, n_variants = [], [], 0, 0
    for b in t["building_id"]:
        g = all_rows[all_rows["building_id"] == b]
        untopped = g[g["topping_mm"] == 0]
        n_variants += len(untopped)
        n_variants_fail += int((~untopped["rigid"].fillna(False).astype(bool)).sum())
        v = t.loc[t["building_id"] == b, "floor_variant_id"].iloc[0]
        gv = g[g["floor_variant_id"] == v].sort_values("topping_mm")
        rigid = gv[gv["rigid"].fillna(False).astype(bool)]
        no_top = gv[gv["topping_mm"] == 0].iloc[0]
        fails.append(not bool(no_top["rigid"]))
        s_none = 1.0 - no_top["s_bld"] / base[b]
        if rigid.empty:
            rs.append(float("nan"))
        else:
            s_min = 1.0 - rigid.iloc[0]["s_bld"] / base[b]
            rs.append((s_none - s_min) / s_none if s_none > 0 else float("nan"))
    n = len(fails)
    share = sum(fails) / n
    med_r = float(np.nanmedian(rs)) if np.isfinite(rs).any() else float("nan")
    c1, c2 = share > 0.5, bool(np.isfinite(med_r) and med_r >= H3_MIN_MEDIAN_R)
    verdict = "supported" if c1 and c2 else "partly supported" if c1 or c2 else "not supported"
    return {"hypothesis": "H3", "verdict": verdict, "n_buildings": n, "share_untopped_fails": share,
            "n_untopped_fails": int(sum(fails)), "median_R": med_r, "max_R": float(np.nanmax(rs)) if np.isfinite(rs).any() else float("nan"),
            "variants_untopped_failing": f"{n_variants_fail} of {n_variants}"}


def run(seed: int = provenance.SEED) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """All cases: building tables, summary rows and slice tests."""
    rc, sh = load()
    side = pd.read_csv(SIDE)
    all_rc = pd.read_parquet(RC)
    buildings, summary, slice_rows = [], [], []
    for case in cases():
        t = building_table(rc, sh, case)
        buildings.append(t)
        sl_b = slices(t, "s_b", seed).assign(case=case.name)
        sl_lat = slices(t, "lateral_saving", seed).assign(case=case.name)
        slice_rows += [sl_b, sl_lat]
        rcc = rc[rc["seismic_grade"] != GRADE_I] if case.drop_grade_i else rc
        for res in (h1(t), h2(t, sl_b, sl_lat), h3(rcc, sh, side, case, t)):
            summary.append({"case": case.name, **res})
    n_all = all_rc["building_id"].nunique()
    summary.append({"case": "base", "hypothesis": "coverage", "verdict": "info", "n_buildings": int(len(buildings[0])),
                    "note": f"{len(buildings[0])} of {n_all} buildings compared; the rest have no ok conventional or no ok rigid shell design: "
                            + ", ".join(sorted(set(all_rc["building_id"]) - set(buildings[0]["building_id"])))})
    return pd.concat(buildings, ignore_index=True), pd.DataFrame(summary), pd.concat(slice_rows, ignore_index=True)


def main() -> None:
    """Run all cases, write the three CSV files and print the verdicts."""
    b, s, sl = run()
    b.to_csv(OUT_BUILDINGS, index=False, float_format="%.6g")
    s.to_csv(OUT_SUMMARY, index=False, float_format="%.6g")
    sl.to_csv(OUT_SLICES, index=False, float_format="%.6g")
    show = s[s["hypothesis"].isin(["H1", "H2", "H3"])].pivot(index="case", columns="hypothesis", values="verdict")
    print(show.to_string())
    print(s[s["case"] == "base"].dropna(axis=1, how="all").T.to_string())


if __name__ == "__main__":
    main()
