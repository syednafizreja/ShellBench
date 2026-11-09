"""Three surrogate models, tuned on training data only (Day 44; H4).

File: src/shellbench/ml/train.py

What this module does
---------------------
For each target and each split it fits three models and reports their error on
rows the model never saw:

* ``hgb``: gradient boosting, scikit-learn ``HistGradientBoostingRegressor``;
* ``mlp``: a small multilayer perceptron, ``MLPRegressor`` on standardised
  inputs and a standardised target;
* ``gp``: a Gaussian process baseline on a random 1,000-row subsample of the
  training rows (a Gaussian process costs O(n^3), so the subsample is the
  baseline's own limit, not a tuning choice).

Each model is tuned by 5-fold cross-validation on the training rows only. The
grids below are frozen with this file (preregistration 2.4: code and
hyperparameters frozen before the dataset DOI); the test rows never enter the
search. Metrics: MAE, RMSE, R^2 and MAPE on the test rows. MAPE is not defined
when a true value is zero; no target here is zero.

Splits: ``random`` and ``unseen_storeys`` (leave one storey count out, six
folds, test predictions pooled). The playbook asks for a third split; the
preregistration lists two, and a third would need a change-log entry [J].

Output: ``results/surrogate_accuracy.csv`` and ``figures/surrogate_parity.png``.
Rows run on pre-release data are pipeline tests, not results.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from shellbench import provenance
from shellbench.ml import data as d

ROOT = Path(__file__).resolve().parents[3]
ACCURACY_CSV = ROOT / "results" / "surrogate_accuracy.csv"
PARITY_PNG = ROOT / "figures" / "surrogate_parity.png"

MODELS: tuple[str, ...] = ("hgb", "mlp", "gp")
CV_FOLDS: int = 5
GP_SUBSAMPLE: int = 1000
#: Frozen search grids (keys are the estimator parameter names).
GRIDS: dict[str, dict[str, list]] = {
    "hgb": {"learning_rate": [0.05, 0.1], "max_depth": [3, 6]},
    "mlp": {"hidden_layer_sizes": [(32, 32), (64, 64)], "alpha": [1.0e-4, 1.0e-2]},
    "gp": {"alpha": [1.0e-6, 1.0e-2]},
}
HGB_ITERATIONS: int = 300
MLP_MAX_ITER: int = 500
MLP_PATIENCE: int = 20


def make_estimator(name: str, **params):
    """A fresh, unfitted model of kind ``name`` with the given parameters.

    Args:
        name: ``hgb``, ``mlp`` or ``gp``.
        params: Estimator parameters, as in ``GRIDS``.

    Returns:
        A scikit-learn estimator that standardises inputs (and the target for mlp and gp).
    """
    seed = provenance.SEED
    if name == "hgb":
        return HistGradientBoostingRegressor(max_iter=HGB_ITERATIONS, random_state=seed, **params)
    if name == "mlp":
        net = MLPRegressor(max_iter=MLP_MAX_ITER, early_stopping=True, n_iter_no_change=MLP_PATIENCE,
                           random_state=seed, **params)
        return Pipeline([("x", StandardScaler()), ("m", TransformedTargetRegressor(net, transformer=StandardScaler()))])
    if name == "gp":
        kernel = ConstantKernel(1.0) * Matern(length_scale=3.0, nu=2.5) + WhiteKernel(1.0e-3)
        gp = GaussianProcessRegressor(kernel=kernel, normalize_y=True, random_state=seed, **params)
        return Pipeline([("x", StandardScaler()), ("m", gp)])
    raise ValueError(f"unknown model {name!r}")


def _grid_for(name: str) -> dict[str, list]:
    """Search grid with the pipeline prefix that the model needs."""
    prefix = {"hgb": "", "mlp": "m__regressor__", "gp": "m__"}[name]
    return {prefix + k: v for k, v in GRIDS[name].items()}


def fit_tuned(name: str, x: np.ndarray, y: np.ndarray) -> tuple[object, dict]:
    """Tune by 5-fold cross-validation on (x, y) only, then refit on all of it.

    For ``gp`` the rows are first reduced to a random subsample of ``GP_SUBSAMPLE``.

    Returns:
        The refitted best estimator and its chosen parameters.
    """
    if name == "gp" and len(x) > GP_SUBSAMPLE:
        keep = np.random.default_rng(provenance.SEED).choice(len(x), GP_SUBSAMPLE, replace=False)
        x, y = x[keep], y[keep]
    search = GridSearchCV(make_estimator(name), _grid_for(name), cv=KFold(CV_FOLDS, shuffle=True, random_state=provenance.SEED),
                          scoring="neg_root_mean_squared_error", n_jobs=-1, refit=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        search.fit(x, y)
    return search.best_estimator_, search.best_params_


def metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """MAE, RMSE, R^2 and MAPE [%]."""
    return {"mae": float(mean_absolute_error(y_true, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "r2": float(r2_score(y_true, y_pred)),
            "mape_pct": float(100.0 * np.mean(np.abs((y_true - y_pred) / y_true)))}


def splits(df: pd.DataFrame) -> dict[str, list[tuple[str, np.ndarray, np.ndarray]]]:
    """Both splits as lists of (fold label, train positions, test positions)."""
    tr, te = d.random_split(df)
    d.check_no_leakage(df, np.array([], dtype=int), np.array([], dtype=int))
    out = {"random": [("all", tr, te)], "unseen_storeys": []}
    for s, a, b in d.storey_folds(df):
        d.check_no_leakage(df, a, b)
        out["unseen_storeys"].append((f"storeys_{s}", a, b))
    return out


def run_all(df: pd.DataFrame, models: tuple[str, ...] = MODELS, targets: tuple[str, ...] = d.TARGETS):
    """Fit every model on every target and split.

    Returns:
        ``accuracy`` (one row per model, split, target; unseen_storeys pooled over its six folds; ``n_train`` is the mean training size per fold),
        ``predictions`` (test rows with the prediction of each model; used for the conformal step and the plots)
        and ``params`` (chosen parameters per (model, split, fold, target)).
    """
    x_all = df[list(d.FEATURES)].to_numpy(float)
    acc, preds, params = [], [], {}
    for split, folds in splits(df).items():
        for target in targets:
            y_all = df[target].to_numpy(float)
            for name in models:
                pooled_t, pooled_p = [], []
                for label, tr, te in folds:
                    est, best = fit_tuned(name, x_all[tr], y_all[tr])
                    p = est.predict(x_all[te])
                    params[(name, split, label, target)] = best
                    pooled_t.append(y_all[te])
                    pooled_p.append(p)
                    preds.append(pd.DataFrame({"model": name, "split": split, "fold": label, "target": target,
                                               "row": te, "y_true": y_all[te], "y_pred": p}))
                yt, yp = np.concatenate(pooled_t), np.concatenate(pooled_p)
                acc.append({"model": name, "split": split, "target": target, "n_train": int(round(np.mean([len(f[1]) for f in folds]))),
                            "n_test": int(len(yt)), **metrics(yt, yp)})
    return pd.DataFrame(acc), pd.concat(preds, ignore_index=True), params


def plot_parity(pred: pd.DataFrame, path: Path = PARITY_PNG) -> None:
    """Predicted against true whole-building carbon, one panel per split, one colour per model."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    target = d.TARGETS[0]
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2), dpi=200)
    for ax, split in zip(axes, ("random", "unseen_storeys")):
        for name, colour in zip(MODELS, ("#3b6fb6", "#c0392b", "#2e8b57")):
            s = pred[(pred["split"] == split) & (pred["target"] == target) & (pred["model"] == name)]
            ax.scatter(s["y_true"], s["y_pred"], s=3, alpha=0.4, color=colour, label=name)
        lim = [pred[pred["target"] == target]["y_true"].min(), pred[pred["target"] == target]["y_true"].max()]
        ax.plot(lim, lim, color="black", lw=0.8)
        ax.set_title(split.replace("_", " "), fontsize=9)
        ax.set_xlabel("true [kgCO2e/m2]")
    axes[0].set_ylabel("predicted [kgCO2e/m2]")
    axes[0].legend(markerscale=4, fontsize=8)
    fig.suptitle("Whole-building carbon, test rows (pre-release data, pipeline test)", fontsize=9)
    fig.text(0.01, 0.01, "© 2026 Syed Nafiz Reja Hasib. Pre-release.", fontsize=6)
    fig.tight_layout()
    path.parent.mkdir(exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
