"""Every ShellBench figure, drawn in the house style from the files in results/.

File: src/shellbench/figures.py

What this module does
---------------------
Each function below draws one figure from plain tables (lists of dicts or
pandas frames). The anchor and benchmark modules call these functions at the
end of their runs; the two surrogate figures are drawn by
``scripts/surrogate_figures.py``, because ``src/shellbench/ml/`` is frozen
(9 Nov 2026, commit 5c11ce8) and keeps its own plotting code. And ``python -m shellbench.figures`` redraws every figure from the CSVs
already in ``results/`` without re-running any analysis. So a figure can only
show numbers that are in a results file, and restyling never touches a result.

Figures (stem in ``figures/``, source file in ``results/``):

* ``anchor_waterfall``        - anchor_waterfall.csv
* ``anchor_seismic_compare``  - anchor_rsa.csv
* ``anchor_quantities``       - anchor_quantities.csv
* ``anchor_carbon``           - anchor_carbon.csv
* ``benchmarks_convergence``  - benchmarks_convergence.csv
* ``surrogate_coverage``      - surrogate_coverage.csv
* ``surrogate_parity``        - surrogate_predictions.csv

Each is saved as PNG (600 dpi preview), PDF and SVG (vector masters) by
``style.save``. ``--paper`` writes footer-free copies to ``figures/paper/``
for journal submission.

Every constant here is a presentation choice [J] unless a source is given;
the plotted numbers all come from the tables passed in.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from shellbench import style as st

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

H4_BAND = (0.88, 0.92)
"""Coverage band in the H4 verdict rule (docs/preregistration.md, section 2.4)."""

ELEMENTS = ("slabs", "frame beams", "longitudinal beams", "secondary beams", "columns", "footings")
"""Element order of the take-off (same as carbon.ELEMENTS)."""

MODEL_NAMES = {"hgb": "Gradient boosting", "mlp": "Multilayer perceptron", "gp": "Gaussian process"}
SPLIT_NAMES = {"random": "Random split", "unseen_storeys": "Unseen storey counts"}


def _finish(fig, path: Path, source: str, note: str = "", paper: bool = False) -> list[Path]:
    """Add the footer (repository figures only), run the automated review and save.

    Args:
        fig: Drawn figure.
        path: Target path (any suffix).
        source: Results file the numbers come from, for the footer.
        note: Optional footer qualifier.
        paper: Paper copy: no footer, written to ``figures/paper/``.

    Returns:
        Written file paths.

    Raises:
        ValueError: If the automated design review finds a problem.
    """
    path = Path(path)
    if paper:
        path = path.parent / "paper" / path.name
    else:
        st.footer(fig, source, note)
    problems = st.review(fig, paper=paper)
    if problems:
        raise ValueError(f"{path.stem} fails the design review: " + "; ".join(problems))
    return st.save(fig, path)


def _fmt_delta(x: float) -> str:
    """Signed label for a waterfall step: one decimal, two when below 0.1 in size.

    Args:
        x: Step value in kgCO2e/m2.

    Returns:
        Label text with a true minus sign.
    """
    if x == 0:
        return "0.0"
    digits = 2 if abs(x) < 0.1 else 1
    return f"{x:+.{digits}f}".replace("-", "−")


# ---------------------------------------------------------------------------
# Anchor building
# ---------------------------------------------------------------------------

def waterfall(steps: list[dict], path: Path = FIGURES / "anchor_waterfall.png",
              paper: bool = False) -> list[Path]:
    """Horizontal waterfall from the slab building to the shell building.

    Totals start at zero in neutral grey; each step floats from the running
    level, blue where carbon falls and red where it rises (diverging pair).
    The whole-building saving 1 - shell/slab is written on the chart; it is
    the same formula as ``S_b`` in results/anchor_slab_vs_shell.csv.

    Args:
        steps: Rows with ``step``, ``kgco2e_per_m2`` and ``kind``
            (``"total"`` or ``"delta"``), in order.
        path: Output path.
        paper: Footer-free paper copy.

    Returns:
        Written file paths.
    """
    from matplotlib.patches import Patch

    n = len(steps)
    fig, ax = st.figure("onehalf", height_mm=86)
    level, ends, xmax = 0.0, [], 0.0
    for i, s in enumerate(steps):
        x = float(s["kgco2e_per_m2"])
        if s["kind"] == "total":
            left, width, colour = 0.0, x, st.TOTAL
            level = x
            label = f"{x:.1f}"
        else:
            left, width = level, x
            colour = st.DECREASE if x < 0 else st.INCREASE
            level += x
            label = _fmt_delta(x)
        ax.barh(i, width, left=left, height=0.62, color=colour, edgecolor="white", linewidth=0.5)
        right = max(left, left + width)
        ax.text(right + 1.2, i, label, va="center", ha="left", fontsize=7,
                color=st.INK, fontweight="bold" if s["kind"] == "total" else "normal")
        ends.append(level)
        xmax = max(xmax, right)
    for i in range(n - 1):
        ax.plot([ends[i], ends[i]], [i + 0.31, i + 0.69], color=st.INK_MUTED, linewidth=0.5,
                linestyle=(0, (1.5, 1.2)))
    ax.set_yticks(range(n), [s["step"][0].upper() + s["step"][1:] for s in steps])
    ax.invert_yaxis()
    ax.set_xlim(0, xmax * 1.3)
    ax.set_xlabel("Embodied carbon A1–A3 [kgCO$_2$e per m$^2$ of floor]")
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    st.hgrid(ax, "x")
    first, last = float(steps[0]["kgco2e_per_m2"]), float(steps[-1]["kgco2e_per_m2"])
    saving = 1.0 - last / first
    ax.text(last + 1.2 + 0.075 * xmax, n - 1, f"whole-building saving {100 * saving:.1f} %",
            va="center", ha="left", fontsize=7, color=st.INK_2)
    ax.legend(handles=[Patch(color=st.TOTAL, label="Building total"),
                       Patch(color=st.DECREASE, label="Step lowers carbon"),
                       Patch(color=st.INCREASE, label="Step adds carbon")],
              loc="center left", bbox_to_anchor=(0.01, 0.42))
    return _finish(fig, path, "results/anchor_waterfall.csv",
                   "anchor building, 4 storeys, 0.10 g; screening-level, footings out of scope", paper)


def seismic_compare(table: list[dict], path: Path = FIGURES / "anchor_seismic_compare.png",
                    paper: bool = False) -> list[Path]:
    """Storey shear and inter-storey drift by storey: base-shear method, response spectrum, thesis.

    Args:
        table: One row per storey (1 = ground) with keys ``storey``,
            ``v_bsm``, ``v_rsa``, ``v_thesis`` [kN] and ``du_bsm``, ``du_rsa``,
            ``du_thesis`` [mm].
        path: Output path.
        paper: Footer-free paper copy.

    Returns:
        Written file paths.
    """
    rows = sorted(table, key=lambda r: r["storey"])
    storeys = [int(r["storey"]) for r in rows]
    series = (("bsm", "Base-shear method"), ("rsa", "Response spectrum (3 modes, SRSS)"),
              ("thesis", "Thesis Table 8-12"))
    fig, axes = st.figure("double", height_mm=72, nrows=1, ncols=2, sharey=True)
    for ax, key, xlabel in ((axes[0], "v", "Storey shear [kN]"),
                            (axes[1], "du", "Inter-storey drift $\\Delta u$ [mm]")):
        for k, (tag, label) in enumerate(series):
            ax.plot([float(r[f"{key}_{tag}"]) for r in rows], storeys, color=st.SERIES[k],
                    marker=st.MARKERS[k], linestyle=st.LINESTYLES[k], label=label,
                    markerfacecolor="white" if k == 2 else st.SERIES[k])
        ax.set_xlabel(xlabel)
        ax.set_xlim(left=0)
        st.hgrid(ax, "x")
    axes[0].set_ylabel("Storey")
    axes[0].set_yticks(storeys)
    axes[0].set_ylim(min(storeys) - 0.4, max(storeys) + 0.4)
    st.panel_labels(axes)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside upper center", ncol=3)
    return _finish(fig, path, "results/anchor_rsa.csv",
                   "thesis shears without the level-5 row (B4); thesis Δu as printed", paper)


def _stack(ax, groups: list[str], values: dict[str, list[float]], label_fmt: str) -> None:
    """Draw stacked vertical bars by element with a thin white gap between segments.

    Args:
        ax: Axes.
        groups: Bar labels.
        values: Element -> one value per group, stacked in ``ELEMENTS`` order.
        label_fmt: Format of the total written above each bar.
    """
    bottom = [0.0] * len(groups)
    for k, e in enumerate(ELEMENTS):
        v = values.get(e, [0.0] * len(groups))
        ax.bar(groups, v, bottom=bottom, color=st.SERIES[k], width=0.56, label=e[0].upper() + e[1:],
               edgecolor="white", linewidth=0.6)
        bottom = [b + x for b, x in zip(bottom, v)]
    top = max(bottom)
    for i, b in enumerate(bottom):
        ax.text(i, b + top * 0.015, format(b, label_fmt), ha="center", va="bottom", fontsize=7,
                color=st.INK, fontweight="bold")
    ax.set_ylim(0, top * 1.1)
    ax.tick_params(axis="x", length=0)
    st.hgrid(ax, "y")


def quantities(rows: list[dict], path: Path = FIGURES / "anchor_quantities.png",
               paper: bool = False) -> list[Path]:
    """Concrete and steel per m^2 of floor by element, grid plan, both steel sources.

    Args:
        rows: Rows of results/anchor_quantities.csv (keys as in that file;
            ``per_floor_area [unit/m2]`` may be str or float).
        path: Output path.
        paper: Footer-free paper copy.

    Returns:
        Written file paths.
    """
    sources = ("thesis", "code")
    names = {"thesis": "Thesis steel", "code": "Code-minimum steel"}
    fig, axes = st.figure("onehalf", height_mm=78, nrows=1, ncols=2)
    for ax, mats, ylabel, fmt in ((axes[0], ("C40",), "Concrete [m$^3$ per m$^2$ of floor]", ".3f"),
                                  (axes[1], ("HRB400", "HPB300"), "Steel [kg per m$^2$ of floor]", ".1f")):
        values = {e: [sum(float(q["per_floor_area [unit/m2]"]) for q in rows
                          if q["plan [text]"] == "grid" and q["steel_source [text]"] == s
                          and q["element [text]"] == e and q["material [text]"] in mats)
                      for s in sources] for e in ELEMENTS}
        _stack(ax, [names[s] for s in sources], values, fmt)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Anchor building, grid plan (B11)")
    st.panel_labels(axes)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles[::-1], labels[::-1], loc="outside right center", title="Element")
    return _finish(fig, path, "results/anchor_quantities.csv", paper=paper)


def carbon(rows: list[dict], path: Path = FIGURES / "anchor_carbon.png",
           paper: bool = False) -> list[Path]:
    """A1-A3 per m^2 of floor by element, grid plan, per factor set and steel source.

    Args:
        rows: Rows of results/anchor_carbon.csv.
        path: Output path.
        paper: Footer-free paper copy.

    Returns:
        Written file paths.
    """
    grid = [r for r in rows if r["plan [text]"] == "grid"]
    order = {"thesis": 0, "code": 1}
    bars = sorted({(r["factor_set [text]"], r["steel_source [text]"]) for r in grid},
                  key=lambda b: (b[0], order.get(b[1], 2), b[1]))
    names = {"thesis": "thesis steel", "code": "code-minimum steel"}
    labels = [f"{fs}\n{names.get(src, src)}" for fs, src in bars]
    values = {e: [sum(float(r["A1-A3 per floor area [kgCO2e/m2]"]) for r in grid
                      if (r["factor_set [text]"], r["steel_source [text]"]) == b
                      and r["element [text]"] == e) for b in bars] for e in ELEMENTS}
    fig, ax = st.figure("single", height_mm=74)
    _stack(ax, labels, values, ".1f")
    ax.set_ylabel("A1–A3 [kgCO$_2$e per m$^2$ of floor]")
    ax.set_xlabel("Factor set and steel source (grid plan)")
    handles, labs = ax.get_legend_handles_labels()
    fig.legend(handles[::-1], labs[::-1], loc="outside right center", title="Element")
    return _finish(fig, path, "results/anchor_carbon.csv", paper=paper)


# ---------------------------------------------------------------------------
# Shell benchmarks
# ---------------------------------------------------------------------------

def convergence(rows: list[dict], path: Path = FIGURES / "benchmarks_convergence.png",
                tolerance: float = 0.02, paper: bool = False) -> list[Path]:
    """Normalised displacement against mesh density for the shell benchmarks, with the band.

    Args:
        rows: Rows with ``problem``, ``n`` (elements per side) and
            ``normalised`` (computed / reference).
        path: Output path.
        tolerance: Half-width of the acceptance band (shellfe.TOLERANCE, playbook Day 24).
        paper: Footer-free paper copy.

    Returns:
        Written file paths.
    """
    names = {"scordelis_lo": "Scordelis–Lo roof", "hemisphere": "Pinched hemisphere"}
    fig, ax = st.figure("single", height_mm=64)
    ax.axhspan(1 - tolerance, 1 + tolerance, color=st.NEUTRAL_FILL, linewidth=0,
               label=f"Within {100 * tolerance:.0f} % of reference")
    ax.axhline(1.0, color=st.INK_2, linewidth=0.6)
    meshes = sorted({int(r["n"]) for r in rows})
    for k, (problem, label) in enumerate(names.items()):
        part = sorted((r for r in rows if r["problem"] == problem), key=lambda r: int(r["n"]))
        ax.plot([int(r["n"]) for r in part], [float(r["normalised"]) for r in part], color=st.SERIES[k],
                marker=st.MARKERS[k], linestyle=st.LINESTYLES[k], label=label,
                markerfacecolor="white" if k else st.SERIES[k])
    ax.set_xscale("log", base=2)
    ax.set_xticks(meshes, [str(m) for m in meshes])
    ax.minorticks_off()
    ax.set_xlim(meshes[0] / 1.25, meshes[-1] * 1.25)
    ax.set_xlabel("Elements per side of the modelled patch")
    ax.set_ylabel("Computed / reference displacement [–]")
    st.hgrid(ax, "y")
    ax.legend(loc="lower right")
    return _finish(fig, path, "results/benchmarks_convergence.csv", paper=paper)


# ---------------------------------------------------------------------------
# Surrogate
# ---------------------------------------------------------------------------

def coverage(cov, path: Path = FIGURES / "surrogate_coverage.png", paper: bool = False,
             note: str = "pre-release data, pipeline test") -> list[Path]:
    """Empirical coverage of the 90 % split-conformal intervals, one row per test fold.

    A dot plot rather than bars: coverage is a proportion near 1, so a bar
    from zero hides the gap to the target that the reader needs to see.
    The random split's single fold equals its pooled value, so it is drawn once.

    Args:
        cov: Frame or rows of results/surrogate_coverage.csv.
        path: Output path.
        paper: Footer-free paper copy.
        note: Footer qualifier.

    Returns:
        Written file paths.
    """
    rows = cov.to_dict("records") if hasattr(cov, "to_dict") else list(cov)
    nominal = float(rows[0]["nominal"])
    plot = []
    rnd = [r for r in rows if r["split"] == "random" and r["fold"] == "pooled"]
    for r in rnd:
        plot.append((f"Random split  (n = {int(r['n_test'])})", float(r["coverage"]), True))
    folds = sorted((r for r in rows if r["split"] == "unseen_storeys" and r["fold"] != "pooled"),
                   key=lambda r: int(str(r["fold"]).split("_")[-1]))
    for r in folds:
        plot.append((f"{str(r['fold']).split('_')[-1]} storeys held out  (n = {int(r['n_test'])})",
                     float(r["coverage"]), False))
    for r in rows:
        if r["split"] == "unseen_storeys" and r["fold"] == "pooled":
            plot.append((f"Unseen storeys, pooled  (n = {int(r['n_test'])})", float(r["coverage"]), True))
    fig, ax = st.figure("onehalf", height_mm=72)
    lo, hi = H4_BAND
    ax.axvspan(100 * lo, 100 * hi, color=st.NEUTRAL_FILL, linewidth=0, label="H4 target band, 88–92 %")
    ax.axvline(100 * nominal, color=st.INK_2, linewidth=0.6, linestyle=(0, (4, 2)),
               label=f"Nominal {100 * nominal:.0f} %")
    y = list(range(len(plot)))
    for yi, (label, c, pooled) in zip(y, plot):
        ax.plot([100 * c, 100 * nominal], [yi, yi], color=st.GRID, linewidth=1.0, zorder=1)
        ax.plot(100 * c, yi, marker="D" if pooled else "o", markersize=5.0 if pooled else 4.2,
                color=st.SERIES[0], markerfacecolor=st.SERIES[0] if pooled else "white", zorder=3,
                linestyle="none")
        ax.text(100 * c - 1.2, yi, f"{100 * c:.1f}", ha="right", va="center", fontsize=7, color=st.INK,
                fontweight="bold" if pooled else "normal")
    ax.set_yticks(y, [p[0] for p in plot])
    ax.invert_yaxis()
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(min(40.0, 100 * min(p[1] for p in plot) - 8), 100)
    ax.set_xlabel("Empirical coverage of the 90 % interval [%]")
    if len(rnd):
        ax.axhline(0.5, color=st.GRID, linewidth=0.6)
    st.hgrid(ax, "x")
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=2, borderaxespad=0.2)
    return _finish(fig, path, "results/surrogate_coverage.csv", note, paper)


def parity(pred, path: Path = FIGURES / "surrogate_parity.png", paper: bool = False,
           note: str = "pre-release data, pipeline test") -> list[Path]:
    """Predicted against true whole-building carbon: one row per split, one column per model.

    Each panel prints RMSE, R^2 and n computed from the same pooled test rows
    as results/surrogate_accuracy.csv, so the text agrees with that file.

    Args:
        pred: Frame with ``model``, ``split``, ``y_true``, ``y_pred`` for one target.
        path: Output path.
        paper: Footer-free paper copy.
        note: Footer qualifier.

    Returns:
        Written file paths.
    """
    import numpy as np

    models = [m for m in MODEL_NAMES if m in set(pred["model"])]
    splits = [s for s in SPLIT_NAMES if s in set(pred["split"])]
    lo = float(min(pred["y_true"].min(), pred["y_pred"].min()))
    hi = float(max(pred["y_true"].max(), pred["y_pred"].max()))
    pad = 0.04 * (hi - lo)
    lim = (lo - pad, hi + pad)
    fig, axes = st.figure("double", height_mm=128, nrows=len(splits), ncols=len(models),
                          sharex=True, sharey=True, squeeze=False)
    for i, split in enumerate(splits):
        for j, model in enumerate(models):
            ax = axes[i][j]
            s = pred[(pred["split"] == split) & (pred["model"] == model)]
            yt, yp = s["y_true"].to_numpy(float), s["y_pred"].to_numpy(float)
            ax.plot(lim, lim, color=st.INK_2, linewidth=0.6, zorder=1)
            ax.scatter(yt, yp, s=2.0, alpha=0.35, color=st.SERIES[j], linewidths=0, zorder=2,
                       rasterized=True)
            rmse = float(np.sqrt(np.mean((yt - yp) ** 2)))
            r2 = float(1 - np.sum((yt - yp) ** 2) / np.sum((yt - yt.mean()) ** 2))
            ax.text(0.04, 0.96, f"RMSE {rmse:.1f}\n$R^2$ {r2:.3f}\nn = {len(yt):,}", transform=ax.transAxes,
                    ha="left", va="top", fontsize=7, color=st.INK, linespacing=1.3)
            ax.set_xlim(lim)
            ax.set_ylim(lim)
            ax.set_aspect("equal", adjustable="box")
            if i == 0:
                ax.text(0.5, 1.04, MODEL_NAMES[model], transform=ax.transAxes, ha="center",
                        va="bottom", fontsize=7.5, fontweight="bold", color=st.INK)
            if i == len(splits) - 1:
                ax.set_xlabel("Full analysis [kgCO$_2$e/m$^2$]")
            if j == 0:
                ax.set_ylabel(f"{SPLIT_NAMES[split]}\nSurrogate [kgCO$_2$e/m$^2$]")
    st.panel_labels([ax for row in axes for ax in row])
    return _finish(fig, path, "results/surrogate_predictions.csv", note, paper)


# ---------------------------------------------------------------------------
# Rebuild everything from results/
# ---------------------------------------------------------------------------

def _read(name: str) -> list[dict]:
    """Read a CSV in results/ as a list of dicts.

    Args:
        name: File name.

    Returns:
        Rows.
    """
    with open(RESULTS / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rsa_table(rows: list[dict]) -> list[dict]:
    """Turn rows of results/anchor_rsa.csv into the ``seismic_compare`` table.

    Args:
        rows: Rows of anchor_rsa.csv.

    Returns:
        One dict per storey.
    """
    return [{"storey": int(r["level [text]"]),
             "v_bsm": float(r["V_base_shear_method [kN]"]), "v_rsa": float(r["V_rsa [kN]"]),
             "v_thesis": float(r["V_thesis_4storey [kN]"]),
             "du_bsm": float(r["du_base_shear_method [mm]"]), "du_rsa": float(r["du_rsa [mm]"]),
             "du_thesis": float(r["du_thesis_printed [mm]"])} for r in rows]


def release_note() -> str:
    """Footer qualifier for surrogate figures, read from the data they were trained on.

    Returns:
        ``"pre-release data, pipeline test"`` while the family files carry a
        pre-release marker in their ``release`` column (as before the DOI
        run), otherwise an empty string.
    """
    import pandas as pd

    for name in ("family_rc_r14_building_v2.parquet", "family_shell.parquet"):
        path = RESULTS / name
        if path.exists():
            rel = pd.read_parquet(path, columns=["release"])["release"].astype(str)
            if rel.str.contains("pre-release").any():
                return "pre-release data, pipeline test"
    return ""


def build_all(paper: bool = False) -> list[Path]:
    """Redraw every figure from the CSVs in results/ (no analysis is re-run).

    Args:
        paper: Write footer-free copies to figures/paper/ instead.

    Returns:
        All written paths.
    """
    import pandas as pd

    out: list[Path] = []
    out += waterfall(_read("anchor_waterfall.csv"), paper=paper)
    out += seismic_compare(rsa_table(_read("anchor_rsa.csv")), paper=paper)
    out += quantities(_read("anchor_quantities.csv"), paper=paper)
    out += carbon(_read("anchor_carbon.csv"), paper=paper)
    conv = [{"problem": r["problem [text]"], "n": int(r["elements_per_side [-]"]),
             "normalised": float(r["normalised [-]"])} for r in _read("benchmarks_convergence.csv")]
    out += convergence(conv, paper=paper)
    note = release_note()
    out += coverage(pd.read_csv(RESULTS / "surrogate_coverage.csv"), paper=paper, note=note)
    pred_csv = RESULTS / "surrogate_predictions.csv"
    if pred_csv.exists():
        out += parity(pd.read_csv(pred_csv), paper=paper, note=note)
    return out


def main() -> None:
    """Command line: ``python -m shellbench.figures [--paper]``."""
    parser = argparse.ArgumentParser(description="Redraw every ShellBench figure from results/.")
    parser.add_argument("--paper", action="store_true", help="footer-free copies in figures/paper/")
    args = parser.parse_args()
    for p in build_all(paper=args.paper):
        print(p.relative_to(ROOT))


if __name__ == "__main__":
    main()
