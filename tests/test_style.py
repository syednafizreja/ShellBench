"""Tests for the house style and the figure builders (presentation only).

File: tests/test_style.py

What is checked
---------------
* The style file loads and sets the Elsevier lettering size (7 pt) and
  embeds TrueType fonts in PDF.
* Figures open at the exact Elsevier column widths (90, 140, 190 mm).
* ``save`` writes PNG, PDF and SVG, and the vector files are byte-identical
  when saved twice (no date or software stamp).
* ``review`` catches each fault it is meant to catch and passes a clean figure.
* Every figure in ``figures`` builds from the committed results/ files and
  passes the review; the numbers written on the waterfall and parity
  figures equal the results files.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import pytest

from shellbench import figures as fg
from shellbench import style as st

ROOT = Path(__file__).resolve().parents[1]


def test_style_file_sets_lettering_and_fonts():
    """7 pt text, TrueType (type 42) fonts in PDF, Arial first in the font list."""
    st.apply()
    rc = matplotlib.rcParams
    assert rc["font.size"] == pytest.approx(st.MIN_TEXT_PT)
    assert rc["pdf.fonttype"] == 42
    assert rc["font.sans-serif"][0] == "Arial"
    assert rc["savefig.dpi"] == st.PREVIEW_DPI


@pytest.mark.parametrize("name,mm", [("single", 90.0), ("onehalf", 140.0), ("double", 190.0)])
def test_figure_widths_are_elsevier_columns(name, mm):
    """Width in inches times 25.4 gives the column width in mm."""
    fig, _ = st.figure(name, height_mm=60)
    assert fig.get_figwidth() * st.MM_PER_INCH == pytest.approx(mm)
    assert fig.get_figheight() * st.MM_PER_INCH == pytest.approx(60.0)
    import matplotlib.pyplot as plt
    plt.close(fig)


def _clean_figure():
    """A small figure that should pass the review."""
    fig, ax = st.figure("single", height_mm=60)
    ax.plot([0, 1, 2], [0, 1, 4], marker="o")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [kN]")
    return fig, ax


def test_review_passes_clean_figure():
    """No problems on a labelled figure at a column width."""
    fig, _ = _clean_figure()
    assert st.review(fig) == []
    assert st.review(fig, paper=True) == []


def test_review_catches_small_text_and_bad_width():
    """6 pt text and a 100 mm width are both reported."""
    fig, ax = _clean_figure()
    ax.text(0.5, 0.5, "tiny", fontsize=6)
    fig.set_figwidth(100 / st.MM_PER_INCH)
    problems = st.review(fig)
    assert any("tiny" in p for p in problems)
    assert any("100.0 mm" in p for p in problems)


def test_review_catches_missing_label_title_footer_and_overflow():
    """Missing y label, a title and footer in a paper figure, and text off the page."""
    fig, ax = st.figure("single", height_mm=60)
    ax.plot([0, 1], [0, 1])
    ax.set_xlabel("x [m]")
    ax.set_title("A title")
    ax.text(5.0, 0.5, "far away", transform=ax.transAxes)
    st.footer(fig, "results/x.csv")
    problems = st.review(fig, paper=True)
    assert any("no y-axis label" in p for p in problems)
    assert any("title" in p for p in problems)
    assert any("footer" in p for p in problems)
    assert any("far away" in p for p in problems)


def test_category_axis_needs_no_label():
    """Word tick labels name the axis themselves."""
    fig, ax = st.figure("single", height_mm=60)
    ax.barh([0, 1], [3, 4])
    ax.set_yticks([0, 1], ["Slabs", "Columns"])
    ax.set_xlabel("Carbon [kgCO2e]")
    assert st.review(fig) == []


def test_save_writes_three_formats_deterministically(tmp_path):
    """PNG, PDF, SVG written; PDF and SVG identical byte for byte on a second save."""
    first = st.save(_clean_figure()[0], tmp_path / "a" / "fig.png")
    assert [p.suffix for p in first] == [".png", ".pdf", ".svg"]
    assert all(p.stat().st_size > 0 for p in first)
    second = st.save(_clean_figure()[0], tmp_path / "b" / "fig.png")
    for a, b in zip(first[1:], second[1:]):
        assert a.read_bytes() == b.read_bytes(), a.suffix
    assert b"CreationDate" not in first[1].read_bytes()


def test_series_colours_are_the_validated_order():
    """Slots 1-3 (all-pairs safe) and the diverging poles are fixed."""
    assert st.SERIES[:3] == ("#2a78d6", "#eb6834", "#1baf7a")
    assert st.DECREASE == st.SERIES[0]
    assert st.INCREASE == st.SERIES[7]
    assert len(set(st.SERIES)) == 8


def _read(name: str) -> list[dict]:
    """Rows of a committed results file."""
    with open(ROOT / "results" / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _texts(path: Path) -> str:
    """All text in an SVG (svg.fonttype none keeps text as text)."""
    return path.with_suffix(".svg").read_text(encoding="utf-8")


def test_waterfall_saving_matches_results(tmp_path):
    """The saving written on the chart equals S_b in anchor_slab_vs_shell.csv to 0.1 %."""
    paths = fg.waterfall(_read("anchor_waterfall.csv"), tmp_path / "w.png")
    s_b = next(float(r["shell"]) for r in _read("anchor_slab_vs_shell.csv")
               if r["quantity"] == "whole-building saving S_b")
    assert f"whole-building saving {100 * s_b:.1f} %" in _texts(paths[0])


@pytest.mark.parametrize("builder,source", [
    (lambda p, paper: fg.seismic_compare(fg.rsa_table(_read("anchor_rsa.csv")), p, paper=paper), "rsa"),
    (lambda p, paper: fg.quantities(_read("anchor_quantities.csv"), p, paper=paper), "quantities"),
    (lambda p, paper: fg.carbon(_read("anchor_carbon.csv"), p, paper=paper), "carbon"),
    (lambda p, paper: fg.coverage(pd.read_csv(ROOT / "results" / "surrogate_coverage.csv"), p,
                                  paper=paper), "coverage"),
])
@pytest.mark.parametrize("paper", [False, True])
def test_every_figure_builds_and_passes_review(tmp_path, builder, source, paper):
    """Each builder writes three files and raises nothing (the review runs inside)."""
    paths = builder(tmp_path / f"{source}.png", paper)
    assert len(paths) == 3 and all(p.exists() for p in paths)
    assert (paths[0].parent.name == "paper") is paper
    assert ("Syed Nafiz Reja Hasib" in _texts(paths[0])) is not paper


def test_convergence_builds(tmp_path):
    """The benchmark figure builds from its results file."""
    rows = [{"problem": r["problem [text]"], "n": int(r["elements_per_side [-]"]),
             "normalised": float(r["normalised [-]"])} for r in _read("benchmarks_convergence.csv")]
    assert len(fg.convergence(rows, tmp_path / "c.png")) == 3


def test_coverage_draws_random_split_once(tmp_path):
    """The random split's 'all' fold equals its pooled row, so only one row is drawn."""
    cov = pd.read_csv(ROOT / "results" / "surrogate_coverage.csv")
    svg = _texts(fg.coverage(cov, tmp_path / "cov.png")[0])
    assert svg.count("Random split") == 1
    assert svg.count("storeys held out") == 6


def test_parity_prints_rmse_of_its_rows(tmp_path):
    """RMSE in each panel is the RMSE of the rows drawn in it."""
    rng = np.random.default_rng(0)
    rows = []
    for model in ("hgb", "mlp", "gp"):
        for split in ("random", "unseen_storeys"):
            y = rng.uniform(80, 160, 50)
            rows.append(pd.DataFrame({"model": model, "split": split, "y_true": y,
                                      "y_pred": y + rng.normal(0, 5, 50)}))
    pred = pd.concat(rows, ignore_index=True)
    svg = _texts(fg.parity(pred, tmp_path / "p.png")[0])
    s = pred[(pred["model"] == "gp") & (pred["split"] == "random")]
    rmse = float(np.sqrt(np.mean((s["y_true"] - s["y_pred"]) ** 2)))
    assert f"RMSE {rmse:.1f}" in svg
