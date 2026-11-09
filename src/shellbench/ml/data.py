"""Surrogate data and honest splits (Day 43; H4, preregistration 2.4).

File: src/shellbench/ml/data.py

What this module does
---------------------
It loads the two family files, keeps the rows that were designed (``status ==
ok``), turns each row into a fixed feature vector, and builds the two splits of
preregistration 2.4:

* **random**: 80 % of rows for training, 20 % for testing, drawn with
  ``provenance.SEED``. A random split puts rows of the same building (the same
  storey count and PGA, a different floor variant) on both sides, so it
  flatters a model: the test row is almost a copy of a training row.
* **unseen_storeys**: leave one storey count out (3 to 8), six folds. No
  building of the held-out storey count is in training, so the test is
  extrapolation or interpolation in height, which is what a designer needs
  from a surrogate. One fold is one storey count x six PGAs x the floor
  variants (decision card 1, 5 Nov 2026).

Features are frozen here (``FEATURES``); so are the four targets. The rows
used for any result in Paper 2 are the published dataset (after the DOI);
earlier runs are pipeline tests on pre-release rows.

Units: kgCO2e/m^2 for carbon, mm, s, and the drift ratio [-].
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pandas as pd

from shellbench import provenance

ROOT = Path(__file__).resolve().parents[3]
RC = ROOT / "results" / "family_rc_r14_building_v2.parquet"
SHELL = ROOT / "results" / "family_shell.parquet"

#: The four targets (playbook Day 44).
TARGETS: tuple[str, ...] = ("carbon_building_kgco2e_per_m2", "carbon_floor_kgco2e_per_m2",
                            "max_drift_ratio", "period_s")
#: Frozen feature list. Slab rows carry zeros for the shell descriptors.
FEATURES: tuple[str, ...] = ("storeys", "pga_g", "shell_floor", "rise_ratio", "lev_foamed", "lev_recycled",
                             "lev_raised", "mesh_layers", "shell_thickness_mm", "topping_mm")
TEST_FRACTION: float = 0.2


def _thickness_mm(value: object, slab_mm: float) -> float:
    """Shell thickness at the 6.6 m span, the larger bay (``"70/80"`` gives 80); the slab thickness for a slab row."""
    if isinstance(value, str) and value:
        return float(value.split("/")[-1])
    return float(slab_mm)


def load_frame(rc_path: Path = RC, shell_path: Path = SHELL) -> pd.DataFrame:
    """Designed rows of both families, one row each, with the features and targets.

    Args:
        rc_path: Conventional family file.
        shell_path: Shell family file.

    Returns:
        A frame with ``building_id``, ``floor_system``, the ``FEATURES`` and the ``TARGETS``.
    """
    rc = pd.read_parquet(rc_path)
    sh = pd.read_parquet(shell_path)
    rc = rc[rc["status"] == "ok"].copy()
    sh = sh[sh["status"] == "ok"].copy()
    rc["shell_floor"], rc["rise_ratio"], rc["mesh_layers"], rc["topping_mm"] = 0, 0.0, 0, 0
    rc["levelling"] = ""
    rc["shell_thickness_mm"] = rc["slab_mm"].astype(float)
    sh["shell_floor"] = 1
    sh["shell_thickness_mm"] = [_thickness_mm(v, s) for v, s in zip(sh["shell_thickness_mm"], sh["slab_mm"])]
    both = pd.concat([rc, sh], ignore_index=True)
    for key, name in (("foamed_fill", "lev_foamed"), ("recycled_fill", "lev_recycled"), ("raised_floor", "lev_raised")):
        both[name] = (both["levelling"] == key).astype(int)
    cols = ["building_id", "floor_system", "floor_variant_id", *FEATURES, *TARGETS]
    both["floor_variant_id"] = both["floor_variant_id"].fillna("slab")
    return both[cols].reset_index(drop=True)


def random_split(df: pd.DataFrame, seed: int = provenance.SEED) -> tuple[np.ndarray, np.ndarray]:
    """Row positions of train and test for the random split (80 / 20)."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(df))
    n_test = int(round(TEST_FRACTION * len(df)))
    return np.sort(order[n_test:]), np.sort(order[:n_test])


def storey_folds(df: pd.DataFrame) -> Iterator[tuple[int, np.ndarray, np.ndarray]]:
    """Leave-one-storey-count-out folds: (held-out storeys, train positions, test positions)."""
    for s in sorted(df["storeys"].unique()):
        test = np.flatnonzero(df["storeys"].to_numpy() == s)
        train = np.flatnonzero(df["storeys"].to_numpy() != s)
        yield int(s), train, test


def check_no_leakage(df: pd.DataFrame, train: np.ndarray, test: np.ndarray, by: str = "storeys") -> None:
    """Raise ``AssertionError`` if any value of ``by`` is in both train and test (leakage test)."""
    shared = set(df[by].iloc[train]) & set(df[by].iloc[test])
    assert not shared, f"{by} values in both train and test: {sorted(shared)}"
