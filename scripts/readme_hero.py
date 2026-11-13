# scripts/readme_hero.py
"""Draw the README hero: floor saving S_f against whole-building saving S_b.

Two 6 x 6 matrices (storeys 3-8 against PGA 0.05-0.40 g) for the base case of
``results/verdicts_buildings.csv``, one PNG per GitHub theme (light and dark),
at 1280 x 640 px so the light one also serves as the social preview. The plotted
numbers are written to ``docs/img/hero.json``. Nothing here changes a result.

Run: python scripts/readme_hero.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402

from shellbench import style  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "results" / "verdicts_buildings.csv"
OUT = ROOT / "docs" / "img"
STOREYS = [3, 4, 5, 6, 7, 8]
PGAS = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40]
CLIP = 0.30  # colour scale limit [-]; the number in each cell is the exact value

THEMES = {
    "light": {"bg": "#ffffff", "ink": style.INK, "muted": "#52514e", "faint": style.INK_MUTED,
              "mid": style.NEUTRAL_FILL, "neg": style.INCREASE, "pos": style.DECREASE, "empty": "#f7f6f2",
              "edge": "#ffffff"},
    "dark": {"bg": "#0d1117", "ink": "#f0efec", "muted": "#c3c2b7", "faint": "#8f8d86",
             "mid": "#2a2a28", "neg": "#e66767", "pos": "#3987e5", "empty": "#161b22", "edge": "#0d1117"},
}


def grid(t: pd.DataFrame, col: str) -> np.ndarray:
    """Matrix of ``col`` with storeys as rows (top = 8) and PGA as columns; NaN where no building."""
    m = np.full((len(STOREYS), len(PGAS)), np.nan)
    for _, r in t.iterrows():
        i = STOREYS[::-1].index(int(r["storeys"]))
        j = PGAS.index(round(float(r["pga_g"]), 2))
        m[i, j] = r[col]
    return m


def text_ink(v: float, th: dict) -> str:
    """White on strong fills, theme ink otherwise."""
    return "#ffffff" if abs(v) > 0.6 * CLIP else th["ink"]


def draw(t: pd.DataFrame, theme: str) -> Path:
    th = THEMES[theme]
    plt.rcParams.update({"font.family": ["Arial", "Liberation Sans", "DejaVu Sans"], "font.size": 11})
    cmap = LinearSegmentedColormap.from_list("saving", [th["neg"], th["mid"], th["pos"]])
    norm = TwoSlopeNorm(vmin=-CLIP, vcenter=0.0, vmax=CLIP)
    fig = plt.figure(figsize=(12.8, 6.4), dpi=100, facecolor=th["bg"])
    fig.text(0.045, 0.90, "Thin-shell floors cut floor carbon by a median 14.3 %, the whole building by 5.7 %",
             fontsize=18, fontweight="bold", color=th["ink"])
    fig.text(0.045, 0.845, "Carbon saving of the best thin-shell floor against a flat slab, A1-A3, "
             "33 code-compliant GB-code RC frames", fontsize=12, color=th["muted"])
    panels = [("s_f", "Floor only, S_f", 0.045), ("s_b", "Whole building, S_b", 0.525)]
    for col, title, x0 in panels:
        ax = fig.add_axes([x0 + 0.04, 0.15, 0.39, 0.58], facecolor=th["bg"])
        m = grid(t, col)
        for i in range(len(STOREYS)):
            for j in range(len(PGAS)):
                v = m[i, j]
                fc = th["empty"] if np.isnan(v) else cmap(norm(np.clip(v, -CLIP, CLIP)))
                ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=fc, edgecolor=th["edge"], linewidth=2.5))
                if np.isnan(v):
                    ax.text(j + 0.5, i + 0.5, "n/a", ha="center", va="center", fontsize=10, color=th["faint"])
                else:
                    ax.text(j + 0.5, i + 0.5, f"{100 * v:.1f}", ha="center", va="center",
                            fontsize=11, color=text_ink(v, th))
        ax.set_xlim(0, len(PGAS))
        ax.set_ylim(len(STOREYS), 0)
        ax.set_xticks(np.arange(len(PGAS)) + 0.5, [f"{p:.2f}" for p in PGAS])
        ax.set_yticks(np.arange(len(STOREYS)) + 0.5, [str(s) for s in STOREYS[::-1]])
        ax.tick_params(length=0, colors=th["muted"], labelsize=10.5)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_xlabel("Peak ground acceleration [g]", color=th["muted"], fontsize=10.5)
        ax.set_ylabel("Storeys", color=th["muted"], fontsize=10.5)
        ax.set_title(title + " [%]", loc="left", color=th["ink"], fontsize=13, fontweight="bold", pad=8)
    fig.text(0.045, 0.035, "Blue: less carbon than the slab; red: more. Colour clipped at ±30 %; "
             "the number is exact. n/a: no compliant conventional design. "
             "Data: results/verdicts_buildings.csv (base case).", fontsize=9.5, color=th["faint"])
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"hero_{theme}.png"
    fig.savefig(path, dpi=100, facecolor=th["bg"], metadata={"Software": None})
    plt.close(fig)
    return path


def main() -> None:
    t = pd.read_csv(DATA)
    t = t[t["case"] == "base"]
    for theme in THEMES:
        print(draw(t, theme))
    plotted = {"source": "results/verdicts_buildings.csv", "case": "base",
               "rows_storeys_top_to_bottom": STOREYS[::-1], "cols_pga_g": PGAS,
               "s_f": [[None if np.isnan(v) else round(float(v), 6) for v in r] for r in grid(t, "s_f")],
               "s_b": [[None if np.isnan(v) else round(float(v), 6) for v in r] for r in grid(t, "s_b")]}
    (OUT / "hero.json").write_text(json.dumps(plotted, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
