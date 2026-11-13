"""H1-H3 verdicts (Day 32): carbon recomputation, rule logic, permutation test, pinned headline numbers."""

import numpy as np
import pandas as pd
import pytest
from scipy.stats import spearmanr

from shellbench import verdicts as v

RESULTS = v.ROOT / "results"


@pytest.fixture(scope="module")
def data():
    """Conventional rows, rigid shell rows and the base-case building table."""
    rc, sh = v.load()
    return rc, sh, v.building_table(rc, sh, v.cases()[0])


def test_base_carbon_equals_the_files(data):
    """Recomputed carbon at the base factors matches the family files (the bounds rely on this)."""
    rc, sh, _ = data
    base = v.cases()[0]
    for df in (rc, sh):
        err = (v.row_carbon(df, base)["building"] - df["carbon_building_kgco2e_per_m2"]).abs().max()
        assert err < 1e-9


def test_three_day31_pairs_are_reproduced(data):
    """S_f and S_b of the three hand-checked Day 31 pairs (results/day31_checks.csv) come out the same."""
    t = data[2].set_index("building_id")
    for b, s_f, s_b in (("s03-p040-tg35-C40", -0.7, 7.7), ("s04-p020-tg35-C40", 12.2, 3.6), ("s04-p030-tg35-C40", 14.3, 3.8)):
        assert 100 * t.loc[b, "s_f"] == pytest.approx(s_f, abs=0.05)
        assert 100 * t.loc[b, "s_b"] == pytest.approx(s_b, abs=0.05)


def test_anchor_saving_matches_the_anchor_comparison(data):
    """The anchor building (4 storeys, 0.10 g): S_f 17.8 % and S_b 6.2 % (README, results/anchor_slab_vs_shell.csv)."""
    r = data[2].set_index("building_id").loc["s04-p010-tg35-C40"]
    assert 100 * r["s_f"] == pytest.approx(17.8, abs=0.05) and 100 * r["s_b"] == pytest.approx(6.2, abs=0.05)


def test_h1_rule_on_toy_tables():
    """Every building S_b < S_f and S_b > 0 gives supported; 9 of 10 positive gives partly; 8 of 10 gives not supported."""
    base = pd.DataFrame({"s_f": [0.2] * 10, "s_b": [0.05] * 10})
    assert v.h1(base)["verdict"] == "supported"
    nine = base.copy()
    nine.loc[0, "s_b"] = -0.01
    assert v.h1(nine)["verdict"] == "partly supported"
    eight = nine.copy()
    eight.loc[1, "s_b"] = -0.01
    assert v.h1(eight)["verdict"] == "not supported"


def test_h1_partly_when_s_b_exceeds_s_f_but_stays_positive():
    """S_b above S_f in one building breaks 'every building', but 100 % positive keeps it partly supported."""
    t = pd.DataFrame({"s_f": [0.2, -0.01], "s_b": [0.05, 0.08]})
    assert v.h1(t)["verdict"] == "partly supported"


def test_permutation_test_separates_trend_from_noise():
    """Six perfectly ordered points give p near 2/720; unrelated points give a large p."""
    rng = np.random.default_rng(1)
    x = np.arange(6, dtype=float)
    rho, p = v.permutation_p(x, x * 2.0, rng, n_perm=3000)
    assert rho == pytest.approx(1.0) and p < 0.01
    rho2, p2 = v.permutation_p(x, np.array([3.0, 1.0, 4.0, 1.5, 5.0, 2.0]), rng, n_perm=3000)
    assert abs(rho2) < 0.7 and p2 > 0.05


def test_small_slices_cannot_be_significant():
    """A slice with fewer than 4 buildings is reported as not significant [J]."""
    t = pd.DataFrame({"storeys": [3, 3, 3], "pga_g": [0.1, 0.2, 0.3], "s_b": [0.01, 0.02, 0.03]})
    sl = v.slices(t, "s_b")
    assert not sl["positive_significant"].any()


def test_h2_verdict_logic():
    """Supported needs both axes and the lateral trend; one axis only is partly; none is not supported."""
    t = pd.DataFrame({"x": [1]})

    def sl(pga, sto):
        rows = [{"against": "pga", "positive_significant": f, "rho": 0.5} for f in pga]
        rows += [{"against": "storeys", "positive_significant": f, "rho": 0.5} for f in sto]
        return pd.DataFrame(rows)
    yes, no = [True] * 4 + [False] * 2, [False] * 6
    assert v.h2(t, sl(yes, yes), sl(yes, no))["verdict"] == "supported"
    assert v.h2(t, sl(yes, no), sl(yes, no))["verdict"] == "partly supported"
    assert v.h2(t, sl(no, no), sl(no, no))["verdict"] == "not supported"
    assert v.h2(t, sl([True] * 3 + [False] * 3, no), sl(no, no))["verdict"] == "not supported"  # exactly half is not more than half


def test_slice_rho_in_the_file_matches_a_fresh_calculation(data):
    """results/verdicts_slices.csv: the Spearman rho of every base-case S_b slice equals a fresh scipy value."""
    t = data[2]
    sl = pd.read_csv(RESULTS / "verdicts_slices.csv")
    sl = sl[(sl["case"] == "base") & (sl["value"] == "s_b")]
    for _, r in sl.iterrows():
        g = t[t[r["fixed"]] == r["level"]]
        other = "pga_g" if r["against"] == "pga" else "storeys"
        if np.isfinite(r["rho"]):
            assert spearmanr(g[other], g["s_b"]).statistic == pytest.approx(r["rho"], abs=1e-5)
        assert len(g) == r["n"]


def test_pinned_headline_numbers_and_verdicts(data):
    """Base case, 11-13 Nov 2026 run on the v0.4.0 files: 33 buildings, 32 with S_b > 0, H1 partly, H2 and H3 not supported, in all six cases."""
    t = data[2]
    assert len(t) == 33 and int((t["s_b"] > 0).sum()) == 32
    s = pd.read_csv(RESULTS / "verdicts_summary.csv")
    sub = s[s["hypothesis"].isin(["H1", "H2", "H3"])]
    assert set(sub["case"]) == {c.name for c in v.cases()}
    for h, word in (("H1", "partly supported"), ("H2", "not supported"), ("H3", "not supported")):
        assert (sub[sub["hypothesis"] == h]["verdict"] == word).all()


def test_h3_untopped_floors_are_rigid_in_every_row():
    """No ok shell row fails the diaphragm test at 0 mm topping, so R is 0 and H3 is not supported."""
    side = pd.read_csv(v.SIDE)
    assert side["rigid"].all()
