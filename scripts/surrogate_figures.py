"""Run the frozen surrogate pipeline and draw its figures in the house style.

File: scripts/surrogate_figures.py

Usage (repository root, ``research`` environment)::

    python scripts/surrogate_figures.py

Why this script exists
----------------------
The surrogate code in ``src/shellbench/ml/`` was frozen on 9 Nov 2026 at
commit 5c11ce8 (docs/surrogate_notes.md), before the house style was adopted.
To keep the freeze clean this script does not change that code. It calls the
frozen functions in the same order as ``shellbench.ml.conformal.main`` and
writes the same two files with the same formatting:

* ``results/surrogate_accuracy.csv``  (``train.run_all``)
* ``results/surrogate_coverage.csv``  (``conformal.interval_coverage``)

It adds one file, ``results/surrogate_predictions.csv``: the pooled test
predictions of whole-building carbon (``data.TARGETS[0]``) that the parity
figure plots, so ``python -m shellbench.figures`` can redraw it without
re-training. Then it draws ``figures/surrogate_parity`` and
``figures/surrogate_coverage`` with ``shellbench.figures``.

Run time: about 11 minutes on four cores (cloud, 9 Nov 2026). On that run
``surrogate_accuracy.csv`` came out byte-identical to the committed file.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from shellbench import figures
from shellbench.ml import conformal as cf
from shellbench.ml import data as d
from shellbench.ml import train as t

ROOT = Path(__file__).resolve().parents[1]
PREDICTIONS_CSV = ROOT / "results" / "surrogate_predictions.csv"


def predictions_table(pred):
    """Return the rows of the parity figure: whole-building target, stable order.

    Args:
        pred: Predictions frame from ``train.run_all``.

    Returns:
        Frame with model, split, fold, row, y_true, y_pred.
    """
    out = pred[pred["target"] == d.TARGETS[0]][["model", "split", "fold", "row", "y_true", "y_pred"]]
    return out.sort_values(["model", "split", "fold", "row"], kind="stable").reset_index(drop=True)


def main() -> None:
    """Run the frozen pipeline, write the CSVs and draw the two figures."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.parse_args()
    note = figures.release_note()
    df = d.load_frame()
    acc, pred, params = t.run_all(df)
    acc.to_csv(t.ACCURACY_CSV, index=False, float_format="%.5g")
    table = predictions_table(pred)
    table.to_csv(PREDICTIONS_CSV, index=False, float_format="%.5g")
    figures.parity(table, t.PARITY_PNG, note=note)
    best = cf.best_model(acc)
    cov = cf.interval_coverage(df, best, params)
    cov.to_csv(cf.COVERAGE_CSV, index=False, float_format="%.5g")
    figures.coverage(cov, cf.COVERAGE_PNG, note=note)
    print(acc.round(4).to_string())
    print("best model:", best)
    print(cov.round(4).to_string())


if __name__ == "__main__":
    main()
