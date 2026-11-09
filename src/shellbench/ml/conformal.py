"""Split-conformal prediction intervals at 90 % (Day 45; H4).

File: src/shellbench/ml/conformal.py

What this module does
---------------------
For the best model, it builds an interval around each prediction that should
contain the true value 90 % of the time, and measures how often it does on the
test rows of each split.

Split conformal, in steps (the 10-point example on paper is in
docs/surrogate_notes.md):

1. Hold out a calibration set from the training rows (20 %, drawn with
   ``provenance.SEED``). Fit the model on the other 80 %.
2. On the calibration rows, compute the absolute residuals |y - prediction|.
3. Take the q-th quantile of these n residuals with q = ceil((n + 1) x 0.9) / n.
   Call it ``half_width``.
4. The interval of a test row is prediction -/+ half_width.

If calibration and test rows are exchangeable, the coverage is at least 90 %
(Vovk; Lei et al. 2018). On the random split they are, apart from the near-copy
rows (same building, other floor variant), which push coverage up. On the
unseen-storeys split they are not: the test storey count is outside the
training range of storey counts, so the residuals there are larger than the
calibration residuals and coverage can fall below 90 %. That is reported as it
is, and it is the point of the split.

The "best model" is the one with the lowest RMSE of whole-building carbon on the
random split (preregistration 2.4); its tuned parameters come from ``train``.

Output: ``results/surrogate_coverage.csv`` and ``figures/surrogate_coverage.png``.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from shellbench import provenance
from shellbench.ml import data as d
from shellbench.ml import train as t

ROOT = Path(__file__).resolve().parents[3]
COVERAGE_CSV = ROOT / "results" / "surrogate_coverage.csv"
COVERAGE_PNG = ROOT / "figures" / "surrogate_coverage.png"

NOMINAL: float = 0.90
CALIBRATION_FRACTION: float = 0.20


def conformal_quantile(residuals: np.ndarray, level: float = NOMINAL) -> float:
    """Split-conformal half-width: the ceil((n + 1) x level)-th smallest absolute residual.

    If ceil((n + 1) x level) > n, the interval is unbounded (``inf``).
    """
    n = len(residuals)
    k = math.ceil((n + 1) * level)
    if k > n:
        return float("inf")
    return float(np.sort(np.abs(residuals))[k - 1])


def best_model(accuracy: pd.DataFrame, target: str = d.TARGETS[0]) -> str:
    """Model with the lowest random-split RMSE on ``target`` (preregistration 2.4)."""
    sub = accuracy[(accuracy["split"] == "random") & (accuracy["target"] == target)]
    return str(sub.loc[sub["rmse"].idxmin(), "model"])


def interval_coverage(df: pd.DataFrame, model: str, params: dict, target: str = d.TARGETS[0]) -> pd.DataFrame:
    """Coverage and mean width of 90 % intervals on every fold of both splits.

    Args:
        df: Frame from ``data.load_frame``.
        model: Model name from ``train.MODELS``.
        params: ``params`` dict returned by ``train.run_all``.
        target: Target column.

    Returns:
        One row per split and fold: coverage, mean width, calibration size, test size.
    """
    x = df[list(d.FEATURES)].to_numpy(float)
    y = df[target].to_numpy(float)
    rows = []
    rng = np.random.default_rng(provenance.SEED)
    for split, folds in t.splits(df).items():
        for label, tr, te in folds:
            order = rng.permutation(tr)
            n_cal = int(round(CALIBRATION_FRACTION * len(order)))
            cal, fit = order[:n_cal], order[n_cal:]
            est = t.make_estimator(model, **{k.split("__")[-1]: v for k, v in params[(model, split, label, target)].items()})
            if model == "gp" and len(fit) > t.GP_SUBSAMPLE:
                fit = np.random.default_rng(provenance.SEED).choice(fit, t.GP_SUBSAMPLE, replace=False)
            est.fit(x[fit], y[fit])
            half = conformal_quantile(y[cal] - est.predict(x[cal]))
            p = est.predict(x[te])
            inside = np.abs(y[te] - p) <= half
            rows.append({"model": model, "split": split, "fold": label, "target": target, "nominal": NOMINAL,
                         "coverage": float(inside.mean()), "mean_width": 2.0 * half,
                         "n_calibration": int(len(cal)), "n_test": int(len(te))})
    out = pd.DataFrame(rows)
    pooled = {}
    for split, g in out.groupby("split"):
        w = g["n_test"].to_numpy()
        pooled[split] = {"model": model, "split": split, "fold": "pooled", "target": target, "nominal": NOMINAL,
                         "coverage": float(np.average(g["coverage"], weights=w)),
                         "mean_width": float(np.average(g["mean_width"], weights=w)),
                         "n_calibration": int(g["n_calibration"].sum()), "n_test": int(w.sum())}
    return pd.concat([out, pd.DataFrame(pooled.values())], ignore_index=True)


def plot_coverage(cov: pd.DataFrame, path: Path = COVERAGE_PNG) -> None:
    """Coverage of each fold against the 90 % target line."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 3.8), dpi=200)
    sub = cov.copy()
    sub["label"] = sub["split"].str.replace("_", " ") + "\n" + sub["fold"].str.replace("storeys_", "")
    colours = ["#3b6fb6" if f == "pooled" else "#9bb7dc" for f in sub["fold"]]
    ax.bar(range(len(sub)), 100 * sub["coverage"], color=colours)
    ax.axhline(100 * NOMINAL, color="black", lw=0.8, ls="--")
    ax.set_xticks(range(len(sub)), sub["label"], fontsize=6)
    ax.set_ylabel("empirical coverage [%]")
    ax.set_title("Split-conformal 90 % intervals (pre-release data, pipeline test)", fontsize=9)
    fig.text(0.01, 0.01, "© 2026 Syed Nafiz Reja Hasib. Pre-release.", fontsize=6)
    fig.tight_layout()
    path.parent.mkdir(exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def main() -> None:
    """Full pipeline: accuracy table, parity plot, coverage table and plot (pre-release data unless the family files are the DOI version)."""
    df = d.load_frame()
    acc, pred, params = t.run_all(df)
    acc.to_csv(t.ACCURACY_CSV, index=False, float_format="%.5g")
    t.plot_parity(pred)
    best = best_model(acc)
    cov = interval_coverage(df, best, params)
    cov.to_csv(COVERAGE_CSV, index=False, float_format="%.5g")
    plot_coverage(cov)
    print(acc.round(4).to_string())
    print("best model:", best)
    print(cov.round(4).to_string())


if __name__ == "__main__":
    main()
