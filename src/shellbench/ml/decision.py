"""Decision-level test and leakage test of the surrogate (Day 46; H4, preregistration 2.4).

File: src/shellbench/ml/decision.py

What this module does
---------------------
Two checks that H4 needs before any verdict.

1. **Leakage test.** For every fold of both splits it checks that nothing of
   the test rows reached training or calibration: shared storey counts, shared
   buildings, identical feature vectors, calibration rows outside the training
   rows, and target columns used as features. The random split is expected to
   fail the storey and building checks (it mixes rows of one building); the
   report shows that, so a reader can see the test can fail. The unseen-storeys
   split must pass every check.
2. **Decision test.** For every building that has a conventional slab and at
   least one shell row that passes the diaphragm test, the full analysis picks
   the floor system with the lower whole-building carbon (the slab, or the
   lowest-carbon rigid shell variant: preregistration 2.0). The surrogate picks
   the same way from its own predictions. A building is predicted only by the
   model fitted without its storey count (leave-one-storey-count-out, the
   unseen-storeys split). Agreement is the share of buildings where both pick
   the same system. Two baselines go beside it: always choose the shell, and
   the number of near ties.

The model is the one the frozen rule selects (lowest random-split RMSE of
whole-building carbon, ``conformal.best_model``), tuned with ``train.fit_tuned``
unchanged. This module adds no model choice and changes no frozen setting.

Also reported, because the system choice alone can hide a poor model: whether the
surrogate picks the same shell variant as the full analysis, and the regret, the
extra carbon of the variant it picks over the true best one.

Outputs: ``results/surrogate_leakage.csv``, ``results/surrogate_decision.csv``
(one row per building), ``results/surrogate_decision_summary.csv`` and
``figures/surrogate_decision.png``.

Units: kgCO2e per m^2 of floor area; savings in per cent of the slab building.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from shellbench import provenance
from shellbench.ml import conformal as cf
from shellbench.ml import data as d
from shellbench.ml import train as t

ROOT = Path(__file__).resolve().parents[3]
SIDE = ROOT / "results" / "family_shell_diaphragm.csv"
LEAKAGE_CSV = ROOT / "results" / "surrogate_leakage.csv"
DECISION_CSV = ROOT / "results" / "surrogate_decision.csv"
SUMMARY_CSV = ROOT / "results" / "surrogate_decision_summary.csv"
DECISION_PNG = ROOT / "figures" / "surrogate_decision.png"

TARGET: str = d.TARGETS[0]
#: Agreement needed for the H4 decision criterion (preregistration 2.4 [J]).
AGREEMENT_THRESHOLD: float = 0.80
#: A building is a near tie if the two systems differ by less than this share of the slab building [J].
NEAR_TIE: float = 0.01


def leakage_report(df: pd.DataFrame) -> pd.DataFrame:
    """Leakage checks for every fold of both splits.

    Args:
        df: Frame from ``data.load_frame``.

    Returns:
        One row per split, fold and check: ``passed`` and a ``detail`` string.
        The random split is expected to fail the storey and building checks.
    """
    x = df[list(d.FEATURES)].round(9)
    keys = x.astype(str).agg("|".join, axis=1)
    rng = np.random.default_rng(provenance.SEED)  # same draws as conformal.interval_coverage
    rows = []

    def add(split: str, fold: str, check: str, passed: bool, detail: str) -> None:
        rows.append({"split": split, "fold": fold, "check": check, "passed": bool(passed), "detail": detail})

    for split, folds in t.splits(df).items():
        for label, tr, te in folds:
            shared_s = sorted(set(df["storeys"].iloc[tr]) & set(df["storeys"].iloc[te]))
            shared_b = set(df["building_id"].iloc[tr]) & set(df["building_id"].iloc[te])
            dup = set(keys.iloc[tr]) & set(keys.iloc[te])
            order = rng.permutation(tr)
            cal = order[:int(round(cf.CALIBRATION_FRACTION * len(order)))]
            add(split, label, "no storey count in both train and test", not shared_s, f"shared: {shared_s}")
            add(split, label, "no building in both train and test", not shared_b, f"{len(shared_b)} shared")
            add(split, label, "no identical feature vector in both", not dup, f"{len(dup)} shared")
            add(split, label, "train and test rows are disjoint", not set(tr) & set(te), f"{len(set(tr) & set(te))} shared")
            add(split, label, "calibration rows are training rows", set(cal) <= set(tr), f"{len(cal)} calibration rows")
            add(split, label, "calibration and test rows are disjoint", not set(cal) & set(te), f"{len(set(cal) & set(te))} shared")
    add("all", "all", "no target column used as a feature", not set(d.FEATURES) & set(d.TARGETS), f"features: {len(d.FEATURES)}")
    add("all", "all", "no identifier column used as a feature", not {"building_id", "floor_variant_id"} & set(d.FEATURES), "building_id, floor_variant_id")
    return pd.DataFrame(rows)


def leakage_passes(report: pd.DataFrame) -> bool:
    """True if every check passes on the unseen-storeys split and the global checks (the random split is expected to fail)."""
    gate = report[report["split"].isin(["unseen_storeys", "all"])]
    return bool(gate["passed"].all())


def rigid_shell_rows(df: pd.DataFrame, side: pd.DataFrame) -> np.ndarray:
    """Boolean mask over ``df`` rows: shell rows that pass the diaphragm test (preregistration 2.0)."""
    key = ["building_id", "floor_variant_id", "topping_mm"]
    ok = side.loc[side["rigid"], key].assign(_ok=True)
    m = df.merge(ok, on=key, how="left")["_ok"].fillna(False).to_numpy(bool)
    return m & (df["floor_system"].to_numpy() == "shell_vault")


def predict_unseen(df: pd.DataFrame, model: str) -> np.ndarray:
    """Whole-building carbon of every row, predicted by the model fitted without that row's storey count."""
    x = df[list(d.FEATURES)].to_numpy(float)
    y = df[TARGET].to_numpy(float)
    pred = np.full(len(df), np.nan)
    for _, tr, te in d.storey_folds(df):
        est, _ = t.fit_tuned(model, x[tr], y[tr])
        pred[te] = est.predict(x[te])
    return pred


def decide(df: pd.DataFrame, pred: np.ndarray, rigid: np.ndarray) -> pd.DataFrame:
    """One row per building: the full analysis choice and the surrogate choice.

    Args:
        df: Frame from ``data.load_frame``.
        pred: Out-of-fold predicted whole-building carbon per row.
        rigid: Mask from ``rigid_shell_rows``.

    Returns:
        Per building with a slab and a rigid shell row: true and predicted carbon of the slab and of the
        best shell variant, both choices, ``agree``, the saving by the full analysis, the shell variant each
        picks, and the regret of the surrogate's variant [kgCO2e/m^2].
    """
    work = df.assign(pred=pred, rigid=rigid)
    rows = []
    for b, g in work.groupby("building_id"):
        slab, shell = g[g["floor_system"] == "beam_slab"], g[g["rigid"]]
        if slab.empty or shell.empty:
            continue
        true_slab = float(slab[TARGET].iloc[0])
        i_true = shell[TARGET].idxmin()
        i_pred = shell["pred"].idxmin()
        true_shell, pred_shell = float(shell.loc[i_true, TARGET]), float(shell.loc[i_pred, "pred"])
        pred_slab = float(slab["pred"].iloc[0])
        full_pick = "slab" if true_slab < true_shell else "shell"
        sur_pick = "slab" if pred_slab < pred_shell else "shell"
        rows.append({"building_id": b, "storeys": int(g["storeys"].iloc[0]), "pga_g": float(g["pga_g"].iloc[0]),
                     "true_slab": true_slab, "true_best_shell": true_shell,
                     "pred_slab": pred_slab, "pred_best_shell": pred_shell,
                     "saving_full_pct": 100.0 * (1.0 - true_shell / true_slab),
                     "saving_surrogate_pct": 100.0 * (1.0 - pred_shell / pred_slab),
                     "full_pick": full_pick, "surrogate_pick": sur_pick, "agree": full_pick == sur_pick,
                     "true_best_variant": shell.loc[i_true, "floor_variant_id"],
                     "surrogate_variant": shell.loc[i_pred, "floor_variant_id"],
                     "same_variant": shell.loc[i_true, "floor_variant_id"] == shell.loc[i_pred, "floor_variant_id"],
                     "regret_kgco2e_m2": float(shell.loc[i_pred, TARGET]) - true_shell})
    return pd.DataFrame(rows)


def summarise(dec: pd.DataFrame) -> pd.DataFrame:
    """Headline numbers of the decision test as ``measure, value`` rows."""
    n = len(dec)
    near = (dec["saving_full_pct"].abs() < 100.0 * NEAR_TIE)
    miss = dec[~dec["agree"]]
    out = [
        ("buildings compared", n),
        ("agreement, surrogate vs full analysis", float(dec["agree"].mean())),
        ("agreement needed (preregistration 2.4)", AGREEMENT_THRESHOLD),
        ("baseline agreement, always choose shell", float((dec["full_pick"] == "shell").mean())),
        ("buildings where the full analysis picks the slab", int((dec["full_pick"] == "slab").sum())),
        ("disagreements", int(len(miss))),
        ("disagreements that are near ties (< 1 % saving)", int(near[~dec["agree"]].sum())),
        ("buildings that are near ties", int(near.sum())),
        ("same shell variant as the full analysis", float(dec["same_variant"].mean())),
        ("mean regret of the surrogate's variant [kgCO2e/m2]", float(dec["regret_kgco2e_m2"].mean())),
        ("largest regret [kgCO2e/m2]", float(dec["regret_kgco2e_m2"].max())),
        ("mean regret as share of the best shell carbon [%]", float(100.0 * (dec["regret_kgco2e_m2"] / dec["true_best_shell"]).mean())),
        ("RMSE of the saving, surrogate vs full [percentage points]", float(np.sqrt(np.mean((dec["saving_surrogate_pct"] - dec["saving_full_pct"]) ** 2)))),
    ]
    return pd.DataFrame(out, columns=["measure", "value"])


def plot_decision(dec: pd.DataFrame, path: Path = DECISION_PNG) -> None:
    """Two panels: surrogate against full-analysis saving per building, and agreement by storey count."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    blue, orange, grey = "#2b5c9e", "#d9822b", "#6b6b6b"
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.4), dpi=200, gridspec_kw={"width_ratios": [1.15, 1]})
    lim = (min(dec["saving_full_pct"].min(), dec["saving_surrogate_pct"].min()) - 2,
           max(dec["saving_full_pct"].max(), dec["saving_surrogate_pct"].max()) + 2)
    a.axhspan(lim[0], 0, color="#eeeeee", zorder=0)
    a.axvspan(lim[0], 0, color="#eeeeee", zorder=0)
    a.plot(lim, lim, color=grey, lw=0.9, ls="--", label="surrogate = full analysis")
    a.axhline(0, color="black", lw=0.7)
    a.axvline(0, color="black", lw=0.7)
    ok = dec["agree"]
    a.scatter(dec.loc[ok, "saving_full_pct"], dec.loc[ok, "saving_surrogate_pct"], s=34, color=blue, edgecolor="white", lw=0.5, zorder=3, label=f"same choice ({int(ok.sum())})")
    a.scatter(dec.loc[~ok, "saving_full_pct"], dec.loc[~ok, "saving_surrogate_pct"], s=52, marker="D", color=orange, edgecolor="black", lw=0.6, zorder=4, label=f"different choice ({int((~ok).sum())})")
    a.set_xlim(lim)
    a.set_ylim(lim)
    a.set_xlabel("whole-building saving, full analysis [% of slab building]")
    a.set_ylabel("whole-building saving, surrogate [%]")
    a.set_title("(a) Each building, predicted without its storey count", fontsize=9, loc="left")
    a.text(0.98, 0.012, "grey band: slab is lower", transform=a.transAxes, fontsize=7, color=grey, ha="right")
    a.legend(fontsize=7, loc="upper left", frameon=False)
    by = dec.groupby("storeys")["agree"].agg(["mean", "size"])
    xs = np.arange(len(by))
    b.bar(xs, 100 * by["mean"], color=blue, width=0.62)
    for x, (m, n) in zip(xs, by.itertuples(index=False)):
        b.text(x, 100 * m + 2.5, f"{int(round(100 * m))} %\n(n={n})", ha="center", fontsize=7)
    base = 100 * float((dec["full_pick"] == "shell").mean())
    b.axhline(base, color=orange, lw=1.2, ls="-", label=f"always choose shell: {base:.0f} %")
    b.axhline(100 * AGREEMENT_THRESHOLD, color="black", lw=0.9, ls="--", label="H4 threshold: 80 %")
    b.set_xticks(xs, by.index.astype(str))
    b.set_xlabel("storey count (held out in training)")
    b.set_ylabel("agreement with full analysis [%]")
    b.set_ylim(0, 150)
    b.set_yticks([0, 25, 50, 75, 100])
    b.set_title("(b) Agreement by storey count", fontsize=9, loc="left")
    b.legend(fontsize=7, loc="upper center", frameon=False, ncol=1)
    for ax in (a, b):
        ax.tick_params(labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Floor-system choice by the surrogate (pre-release data, pipeline test)", fontsize=10, x=0.01, y=0.985, ha="left")
    fig.text(0.01, 0.01, "© 2026 Syed Nafiz Reja Hasib. Pre-release.", fontsize=6, color=grey)
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    path.parent.mkdir(exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def main() -> None:
    """Run the leakage test, then the decision test; write the CSV files and the figure."""
    df = d.load_frame()
    rep = leakage_report(df)
    rep.to_csv(LEAKAGE_CSV, index=False)
    unseen = rep[rep["split"] == "unseen_storeys"]
    rand = rep[rep["split"] == "random"]
    print(f"leakage, unseen storeys: {int(unseen['passed'].sum())} of {len(unseen)} checks pass;"
          f" random split: {int(rand['passed'].sum())} of {len(rand)} (expected to fail the storey and building checks)")
    if not leakage_passes(rep):
        raise SystemExit("Leakage test failed on the unseen-storeys split: no H4 verdict may be given.")
    acc = pd.read_csv(t.ACCURACY_CSV)
    model = cf.best_model(acc)
    side = pd.read_csv(SIDE)
    pred = predict_unseen(df, model)
    dec = decide(df, pred, rigid_shell_rows(df, side))
    dec.to_csv(DECISION_CSV, index=False, float_format="%.5g")
    summ = summarise(dec)
    summ.to_csv(SUMMARY_CSV, index=False, float_format="%.5g")
    plot_decision(dec)
    print("model:", model)
    print(summ.to_string(index=False))


if __name__ == "__main__":
    main()
