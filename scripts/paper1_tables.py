"""scripts/paper1_tables.py

Build the Paper 1 tables from the frozen files in results/ and data/.

Run:  python scripts/paper1_tables.py
Writes paper/paper1/tables/table{1..5}_*.csv and a matching .tex (booktabs)
for each. Nothing is re-analysed: every cell is read from a committed file or
is a count, median or range of one. tests/test_paper1_tables.py checks that
the committed tables equal a fresh build.

Tables (paper/paper1/00_core.md section 9):
    1  Anchor validation against the thesis (results/anchor_*.csv)
    2  Floor library summary by span (results/floor_library.csv)
    3  Carbon factors with source page (data/carbon_factors.csv)
    4  Shell benchmark convergence (results/benchmarks_convergence.csv)
    5  H1-H4 verdicts (results/verdicts_summary.csv, results/surrogate_*.csv)
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
OUT = ROOT / "paper" / "paper1" / "tables"
TOL_PCT = 10.0
"""Gravity agreement band [%] used in docs/anchor_report.md (|difference| <= 10 %)."""


def _col(df: pd.DataFrame, name: str) -> str:
    """Return the column of ``df`` whose header starts with ``name`` (headers carry units)."""
    for c in df.columns:
        if c.split(" [")[0] == name:
            return c
    raise KeyError(name)


def table1_anchor() -> pd.DataFrame:
    """Anchor validation: gravity, wind and seismic agreement with the thesis."""
    rows = []
    for case in ("dead", "live"):
        d = pd.read_csv(RES / f"anchor_gravity_{case}.csv")
        pct = pd.to_numeric(d[_col(d, "difference_pct")], errors="coerce").abs().dropna()
        rows.append({"check": f"Gravity, {case} load: beam-end moments", "targets": len(pct),
                     "above_10pct": int((pct > TOL_PCT).sum()),
                     "result": f"median |difference| {pct.median():.2f} %",
                     "source": f"results/anchor_gravity_{case}.csv"})
    w = pd.read_csv(RES / "anchor_wind.csv")
    du = pd.to_numeric(w[_col(w, "du_pct_vs_thesis")], errors="coerce")
    rows.append({"check": "Wind: storey drift", "targets": len(du), "above_10pct": int((du.abs() > TOL_PCT).sum()),
                 "result": f"difference {du.max():.1f} to {du.min():.1f} %", "source": "results/anchor_wind.csv"})
    s = pd.read_csv(RES / "anchor_seismic.csv")
    v_m = float(s[_col(s, "V_model")].iloc[0])
    v_t = float(s[_col(s, "V_thesis_4storey")].iloc[0])
    p = pd.read_csv(RES / "anchor_3d_periods.csv")
    t2d = float(p[_col(p, "T_2d_frame")].iloc[0])
    t3d = float(p[_col(p, "T_3d")].iloc[0])
    rows.append({"check": "Earthquake: base shear (bare 2D frame)", "targets": 1,
                 "above_10pct": int(abs(v_m / v_t - 1) * 100 > TOL_PCT),
                 "result": f"{v_m:.2f} kN vs {v_t:.2f} kN ({100 * (v_m / v_t - 1):+.1f} %); T1 {t2d:.3f} s (2D), {t3d:.3f} s (3D)",
                 "source": "results/anchor_seismic.csv; results/anchor_3d_periods.csv"})
    return pd.DataFrame(rows)


def table2_library() -> pd.DataFrame:
    """Floor library: cases, passes, thickness, concrete and buckling factor by span."""
    f = pd.read_csv(RES / "floor_library.csv")
    g = f.groupby("span_m")
    t = pd.DataFrame({
        "span_m": g.size().index,
        "cases": g.size().to_numpy(),
        "passing": g["passes"].sum().astype(int).to_numpy(),
        "thickness_mm": [f"{1000 * a:.0f}-{1000 * b:.0f}" for a, b in zip(g["thickness_m"].min(), g["thickness_m"].max())],
        "concrete_m3_per_m2": [f"{a:.3f}-{b:.3f}" for a, b in zip(g["concrete_m3_m2"].min(), g["concrete_m3_m2"].max())],
        "buckling_factor": [f"{a:.1f}-{b:.1f}" for a, b in zip(g["buckling_factor"].min(), g["buckling_factor"].max())],
    })
    return t


def table3_factors() -> pd.DataFrame:
    """Carbon factors as committed, with the clause or page that gives each."""
    c = pd.read_csv(ROOT / "data" / "carbon_factors.csv", index_col=False)
    keep = [x for x in c.columns if x.split(" [")[0] in ("set", "material", "value", "unit", "page")]
    return c[keep]


def table4_benchmarks() -> pd.DataFrame:
    """Shell benchmarks: normalised displacement at each mesh density."""
    b = pd.read_csv(RES / "benchmarks_convergence.csv")
    b.columns = [x.split(" [")[0] for x in b.columns]
    return b.pivot(index="elements_per_side", columns="problem", values="normalised").reset_index()


def table5_verdicts() -> pd.DataFrame:
    """Preregistered verdicts, base case for H1-H3 plus H4 from the surrogate files."""
    v = pd.read_csv(RES / "verdicts_summary.csv")
    base = v[(v["case"] == "base") & v["hypothesis"].isin(["H1", "H2", "H3"])]
    rows = []
    for _, r in base.iterrows():
        if r["hypothesis"] == "H1":
            ev = (f"S_b > 0 in {int(r['n_s_b_positive'])} of {int(r['n_buildings'])}; S_b < S_f in {int(r['n_s_b_below_s_f'])}; "
                  f"S_b median {100 * r['s_b_median']:.2f} % (min {100 * r['s_b_min']:.2f}, max {100 * r['s_b_max']:.2f})")
        elif r["hypothesis"] == "H2":
            ev = (f"positive and significant slices: S_b vs PGA {r['pga_slices_positive_significant']}, "
                  f"vs storeys {r['storey_slices_positive_significant']}")
        else:
            ev = (f"untopped floors failing the topping rule: {int(r['n_untopped_fails'])} of {int(r['n_buildings'])} "
                  f"buildings ({r['variants_untopped_failing']} variants); median R {r['median_R']:g}, max R {r['max_R']:g}")
        rows.append({"hypothesis": r["hypothesis"], "verdict": r["verdict"], "n_buildings": int(r["n_buildings"]),
                     "evidence": ev, "source": "results/verdicts_summary.csv (case base)"})
    sens = v.groupby("hypothesis")["verdict"].nunique()
    for row in rows:
        row["same_in_all_sensitivity_cases"] = bool(sens.get(row["hypothesis"], 1) == 1)
    # H4: rule in docs/preregistration.md 2.4; verdict as recorded in its section 3 table.
    acc = pd.read_csv(RES / "surrogate_accuracy.csv")
    hgb = acc[(acc["model"] == "hgb") & (acc["target"] == "carbon_building_kgco2e_per_m2")].set_index("split")
    ratio = hgb.loc["unseen_storeys", "rmse"] / hgb.loc["random", "rmse"]
    cov = pd.read_csv(RES / "surrogate_coverage.csv")
    pooled = cov[(cov["model"] == "hgb") & (cov["split"] == "unseen_storeys") & (cov["fold"] == "pooled")]["coverage"].iloc[0]
    dec = pd.read_csv(RES / "surrogate_decision_summary.csv").set_index("measure")["value"]
    n_b = int(dec["buildings compared"])
    agree = float(dec["agreement, surrogate vs full analysis"])
    holds = [ratio >= 1.5, 0.88 <= pooled <= 0.92, agree >= 0.8]
    rows.append({"hypothesis": "H4",
                 "verdict": "supported" if all(holds) else ("partly supported" if any(holds) else "not supported"),
                 "n_buildings": n_b,
                 "evidence": (f"RMSE ratio unseen/random {ratio:.2f} (needs >= 1.5); conformal coverage unseen storeys "
                              f"{100 * pooled:.1f} % (needs 88-92 %); decision agreement {round(agree * n_b)}/{n_b} "
                              f"({100 * agree:.1f} %, needs 80 %)"),
                 "source": "results/surrogate_accuracy.csv; surrogate_coverage.csv; surrogate_decision_summary.csv",
                 "same_in_all_sensitivity_cases": True})
    return pd.DataFrame(rows)


def _tex_escape(x) -> str:
    """Escape one table cell for LaTeX."""
    out = str(x)
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("_", r"\_"),
                 ("#", r"\#"), ("$", r"\$"), ("|", r"\textbar{}")):
        out = out.replace(a, b)
    return out


def _latex(df: pd.DataFrame) -> str:
    """Return ``df`` as a booktabs tabular, written by hand so no jinja2 is needed."""
    head = " & ".join(_tex_escape(c) for c in df.columns) + r" \\"
    body = [" & ".join(_tex_escape(v) for v in row) + r" \\" for row in df.itertuples(index=False)]
    return "\n".join([r"\begin{tabular}{" + "l" * df.shape[1] + "}", r"\toprule", head, r"\midrule",
                      *body, r"\bottomrule", r"\end{tabular}", ""])


TABLES = {
    "table1_anchor_validation": table1_anchor,
    "table2_floor_library": table2_library,
    "table3_carbon_factors": table3_factors,
    "table4_benchmarks": table4_benchmarks,
    "table5_verdicts": table5_verdicts,
}


def build(out: Path = OUT) -> list[Path]:
    """Write every table as CSV and booktabs LaTeX; return the written paths."""
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, fn in TABLES.items():
        df = fn()
        csv = out / f"{name}.csv"
        df.to_csv(csv, index=False, lineterminator="\n")
        tex = out / f"{name}.tex"
        tex.write_text(_latex(df), encoding="utf-8", newline="\n")
        paths += [csv, tex]
    return paths


if __name__ == "__main__":
    for p in build():
        print(p.relative_to(ROOT).as_posix())
