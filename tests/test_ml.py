"""Surrogate pipeline: splits, leakage test, conformal quantile on the 10-point example."""

import numpy as np
import pytest

from shellbench.ml import conformal as cf
from shellbench.ml import data as d
from shellbench.ml import train as t


def test_conformal_ten_point_example():
    """docs/surrogate_notes.md: ten errors, 90 %, k = ceil(11 x 0.9) = 10, half-width 2.0."""
    errors = np.array([0.2, 0.3, 0.5, 0.6, 0.8, 0.9, 1.1, 1.2, 1.5, 2.0])
    assert cf.conformal_quantile(errors) == 2.0
    assert cf.conformal_quantile(errors[:9]) == 1.5  # k = ceil(10 x 0.9) = 9
    assert cf.conformal_quantile(errors[:5]) == float("inf")  # k = ceil(6 x 0.9) = 6 > 5


def test_conformal_coverage_on_exchangeable_data():
    """Residuals from one distribution: coverage averaged over 400 calibration draws is at least 90 % (within 1 point)."""
    rng = np.random.default_rng(1)
    covered = []
    for _ in range(400):
        half = cf.conformal_quantile(rng.normal(size=49))  # k = ceil(50 x 0.9) = 45 of 49
        covered.append((np.abs(rng.normal(size=2000)) <= half).mean())
    assert np.mean(covered) > 0.89


@pytest.fixture(scope="module")
def frame():
    """Designed rows of both committed family files."""
    return d.load_frame()


def test_frame_columns_and_rows(frame):
    """Features and targets are present; both floor systems; no missing values."""
    assert set(d.FEATURES) <= set(frame.columns) and set(d.TARGETS) <= set(frame.columns)
    assert set(frame["floor_system"]) == {"beam_slab", "shell_vault"}
    assert not frame[list(d.FEATURES) + list(d.TARGETS)].isna().any().any()


def test_random_split_sizes(frame):
    """80 / 20, disjoint, covering every row."""
    tr, te = d.random_split(frame)
    assert len(tr) + len(te) == len(frame) and not set(tr) & set(te)
    assert abs(len(te) / len(frame) - d.TEST_FRACTION) < 0.001


def test_storey_folds_have_no_leakage(frame):
    """Leakage test: no storey count is in both train and test of any fold; six folds."""
    folds = list(d.storey_folds(frame))
    assert [s for s, _, _ in folds] == [3, 4, 5, 6, 7, 8]
    for s, tr, te in folds:
        d.check_no_leakage(frame, tr, te)
        assert set(frame["storeys"].iloc[te]) == {s}


def test_leakage_test_catches_a_leak(frame):
    """The random split does leak storey counts, and the check says so."""
    tr, te = d.random_split(frame)
    with pytest.raises(AssertionError):
        d.check_no_leakage(frame, tr, te)


def test_models_fit_a_linear_target():
    """Each model learns y = 2 x1 + x2 well enough on 300 rows (R^2 above 0.9)."""
    rng = np.random.default_rng(0)
    x = rng.uniform(size=(300, 3))
    y = 2.0 * x[:, 0] + x[:, 1] + 5.0
    for name in t.MODELS:
        est, _ = t.fit_tuned(name, x[:240], y[:240])
        assert t.metrics(y[240:], est.predict(x[240:]))["r2"] > 0.9, name


def test_leakage_report_passes_unseen_and_fails_random(frame):
    """Day 46: every unseen-storeys check passes; the random split fails the storey and building checks (the test can fail)."""
    from shellbench.ml import decision as dc
    rep = dc.leakage_report(frame)
    assert dc.leakage_passes(rep)
    rand = rep[rep["split"] == "random"]
    failed = set(rand.loc[~rand["passed"], "check"])
    assert failed == {"no storey count in both train and test", "no building in both train and test"}


def test_decide_on_a_toy_frame():
    """Two buildings: slab 100 vs shell 90 / 95 (shell wins); slab 100 vs shell 102 (slab wins). A wrong prediction flips one choice."""
    import pandas as pd
    from shellbench.ml import decision as dc
    tgt = dc.TARGET
    df = pd.DataFrame({
        "building_id": ["a", "a", "a", "b", "b"], "storeys": [3, 3, 3, 4, 4], "pga_g": 0.1,
        "floor_system": ["beam_slab", "shell_vault", "shell_vault", "beam_slab", "shell_vault"],
        "floor_variant_id": ["slab", "v1", "v2", "slab", "v1"], tgt: [100.0, 90.0, 95.0, 100.0, 102.0]})
    rigid = (df["floor_system"] == "shell_vault").to_numpy()
    good = dc.decide(df, df[tgt].to_numpy(), rigid).set_index("building_id")
    assert good.loc["a", "full_pick"] == "shell" and good.loc["b", "full_pick"] == "slab" and good["agree"].all()
    assert good.loc["a", "true_best_variant"] == "v1" and good["regret_kgco2e_m2"].eq(0.0).all()
    wrong = dc.decide(df, np.array([100.0, 97.0, 90.0, 100.0, 99.0]), rigid).set_index("building_id")
    assert wrong.loc["a", "agree"] and wrong.loc["a", "surrogate_variant"] == "v2"
    assert wrong.loc["a", "regret_kgco2e_m2"] == pytest.approx(5.0)
    assert not wrong.loc["b", "agree"]
    s = dc.summarise(wrong).set_index("measure")["value"]
    assert s["agreement, surrogate vs full analysis"] == pytest.approx(0.5)
    assert s["baseline agreement, always choose shell"] == pytest.approx(0.5)
