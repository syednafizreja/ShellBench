"""ShellBench house style for every figure (presentation only, no analysis).

File: src/shellbench/style.py

What this module does
---------------------
One place sets how every ShellBench figure looks, so the anchor report, the
README, both papers and the dataset record read as one body of work:

* ``apply()`` loads ``shellbench.mplstyle`` (Arial or its metric twin, 7 pt
  lettering, thin recessive axes, the validated colour order).
* ``figure()`` opens a figure at a final printed width of 90, 140 or 190 mm,
  so nothing is scaled after drawing and 7 pt stays 7 pt in print.
* ``save()`` writes vector PDF and SVG plus a 600 dpi PNG preview, with the
  date and software stamps removed, so the same inputs give the same files.
* ``footer()`` adds the ownership and source line to repository figures;
  paper figures leave it off (the journal sets its own credit line).
* ``review()`` is the automated half of the design review in
  docs/visual_standard.md: it lists every text below 7 pt, a width that is
  not an Elsevier column width, an axis without a label, and a title inside a
  paper figure.

Sources
-------
* Column widths 90, 140, 190 mm; 7 pt lettering, 6 pt minimum for
  sub/superscripts; 1000 dpi for line art if a raster is needed: Elsevier,
  "Artwork sizing", https://www.elsevier.com/about/policies-and-standards/author/artwork-and-media-instructions/artwork-sizing
  (read 9 Nov 2026).
* Fonts Arial/Helvetica, Courier, Symbol, Times; EPS or PDF for vector art:
  Elsevier, "Artwork overview", same site, /artwork-overview (read 9 Nov 2026).
* Colours: categorical slots 1-8 of the dataviz reference palette, in its
  fixed order; slots 1-6 pass its validator on adjacent pairs and slots 1-3
  on all pairs (light surface). Diverging pair blue/red with a grey neutral.
  Run log in docs/visual_standard.md.
* Everything else (line weights, 600 dpi preview, footer wording) is a house
  choice [J], listed in docs/visual_standard.md.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

STYLE_FILE = Path(__file__).with_name("shellbench.mplstyle")

MM_PER_INCH: float = 25.4
"""Millimetres per inch (exact, by definition of the inch)."""

COLUMN_WIDTH_MM: dict[str, float] = {"single": 90.0, "onehalf": 140.0, "double": 190.0}
"""Elsevier printed widths (Artwork sizing page, table 'Target size')."""

MIN_TEXT_PT: float = 7.0
"""Elsevier rule of thumb for normal lettering at printed size (Artwork sizing)."""

MIN_SCRIPT_PT: float = 6.0
"""Elsevier minimum for sub- and superscript characters (Artwork sizing)."""

PREVIEW_DPI: int = 600
"""PNG preview resolution [J]; vector PDF/SVG are the files sent to journals."""

LINE_ART_DPI: int = 1000
"""Elsevier resolution for line art when a raster file is required (Artwork sizing)."""

# ---- Colour roles (dataviz reference palette, light mode) -------------------
SERIES: tuple[str, ...] = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100",
                           "#e87ba4", "#008300", "#6250d6", "#e34948")
"""Categorical slots 1-8 in fixed order. Never cycled, never re-ordered by rank."""

INK = "#0b0b0b"          # primary text
INK_2 = "#52514e"        # secondary text, axes
INK_MUTED = "#898781"    # footers, de-emphasised labels
GRID = "#e1e0d9"         # hairline grid
NEUTRAL = "#c3c2b7"      # reference bands' edges, baselines
NEUTRAL_FILL = "#f0efec"  # diverging midpoint, shaded bands
DECREASE = "#2a78d6"     # diverging pole: less carbon (blue)
INCREASE = "#e34948"     # diverging pole: more carbon (red)
TOTAL = "#52514e"        # totals in a waterfall: neutral, not a series colour

MARKERS: tuple[str, ...] = ("o", "s", "^", "D", "v", "P", "X", "*")
"""Second channel for series identity, so colour is never the only cue."""

LINESTYLES: tuple[str, ...] = ("-", (0, (4.0, 1.6)), (0, (1.0, 1.4)), (0, (5.0, 1.5, 1.0, 1.5)))
"""Solid, dashed, dotted, dash-dot, in the same order as SERIES."""

OWNER_LINE = "© 2026 Syed Nafiz Reja Hasib"
"""Ownership mark for repository figures (author's standing rule, 23 Oct 2026)."""


def apply() -> None:
    """Load the ShellBench matplotlib style and select the non-interactive backend.

    Safe to call more than once. Uses the Agg backend so figures build on CI
    and on machines without a display.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.style.use(str(STYLE_FILE))


def width_in(width: str | float) -> float:
    """Return a figure width in inches.

    Args:
        width: ``"single"``, ``"onehalf"`` or ``"double"`` (Elsevier column
            widths), or a number of millimetres.

    Returns:
        Width in inches.
    """
    mm = COLUMN_WIDTH_MM[width] if isinstance(width, str) else float(width)
    return mm / MM_PER_INCH


def figure(width: str | float = "single", height_mm: float | None = None, nrows: int = 1,
           ncols: int = 1, **subplot_kw):
    """Open a figure at its final printed size in the house style.

    Args:
        width: Column width name or millimetres (see ``width_in``).
        height_mm: Height in millimetres. Default: 0.62 of the width per row
            of panels, capped at 230 mm (the Elsevier page body is about 240 mm
            tall [J]).
        nrows, ncols: Panel grid.
        **subplot_kw: Passed to ``plt.subplots`` (``sharex``, ``sharey``...).

    Returns:
        ``(fig, axes)`` as from ``plt.subplots``.
    """
    apply()
    import matplotlib.pyplot as plt

    w = width_in(width)
    if height_mm is None:
        h = min(w * 0.62 * nrows, 230.0 / MM_PER_INCH)
    else:
        h = height_mm / MM_PER_INCH
    return plt.subplots(nrows, ncols, figsize=(w, h), **subplot_kw)


def panel_labels(axes: Iterable, start: str = "a") -> None:
    """Write bold (a), (b), ... at the top left of each panel, outside the plot area.

    Args:
        axes: Axes in reading order.
        start: First letter.
    """
    for i, ax in enumerate(axes):
        ax.text(-0.02, 1.02, f"({chr(ord(start) + i)})", transform=ax.transAxes,
                ha="right", va="bottom", fontsize=8.0, fontweight="bold", color=INK)


def hgrid(ax, axis: str = "y") -> None:
    """Draw the recessive hairline grid on one axis only, behind the data.

    Args:
        ax: Axes.
        axis: ``"x"`` or ``"y"``.
    """
    ax.grid(True, axis=axis, color=GRID, linewidth=0.4)
    ax.set_axisbelow(True)


def footer(fig, source: str, note: str = "") -> None:
    """Add the ownership and source line at the bottom left of a repository figure.

    Not used for paper submission files: the journal prints its own credit,
    and a copyright line inside the artwork conflicts with its licence [J].

    Args:
        fig: Figure.
        source: Where the plotted numbers come from, for example
            ``"results/anchor_waterfall.csv"``.
        note: Optional short qualifier ("pre-release data", "screening-level").
    """
    narrow = fig.get_figwidth() * MM_PER_INCH < COLUMN_WIDTH_MM["onehalf"] - 1.0
    sep = "\n" if narrow else "  ·  "
    text = sep.join([f"{OWNER_LINE}  ·  ShellBench", f"data: {source}"])
    if note:
        text += "\n" + note
    lines = text.count("\n") + 1
    fig.text(0.004, 0.004, text, ha="left", va="bottom", fontsize=MIN_TEXT_PT, color=INK_MUTED,
             linespacing=1.25, gid="shellbench-footer")
    band = (lines * MIN_TEXT_PT * 1.3 + 4.0) / 72.0 / fig.get_figheight()
    engine = fig.get_layout_engine()
    if engine is not None and hasattr(engine, "set"):
        engine.set(rect=(0.0, band, 1.0, 1.0 - band))


def _strip_metadata(fmt: str) -> dict:
    """Return savefig metadata that removes date and software stamps for a format.

    Args:
        fmt: ``"pdf"``, ``"svg"`` or ``"png"``.

    Returns:
        Metadata dictionary for ``Figure.savefig``.
    """
    if fmt == "pdf":
        return {"Creator": None, "Producer": None, "CreationDate": None}
    if fmt == "svg":
        return {"Creator": None, "Date": None}
    return {"Software": None}


def save(fig, path: Path | str, formats: Sequence[str] = ("png", "pdf", "svg"),
         dpi: int = PREVIEW_DPI) -> list[Path]:
    """Save a figure in every requested format next to each other and close it.

    ``path`` may carry any suffix; the stem is used. PNG is the preview shown
    in the README; PDF and SVG are the vector masters.

    Args:
        fig: Figure.
        path: Target path, for example ``figures/anchor_waterfall.png``.
        formats: File formats to write.
        dpi: Raster resolution for PNG.

    Returns:
        The written paths, in the order of ``formats``.
    """
    import matplotlib.pyplot as plt

    stem = Path(path).with_suffix("")
    stem.parent.mkdir(parents=True, exist_ok=True)
    written = []
    for fmt in formats:
        out = stem.with_suffix("." + fmt)
        fig.savefig(out, format=fmt, dpi=dpi, metadata=_strip_metadata(fmt))
        written.append(out)
    plt.close(fig)
    return written


def _categorical(ticklabels) -> bool:
    """True if tick labels are words (a category axis names itself), or there are none.

    Args:
        ticklabels: Tick label texts of one axis.

    Returns:
        Whether the axis needs no separate label.
    """
    texts = [t.get_text() for t in ticklabels if t.get_text()]
    return not texts or any(any(c.isalpha() for c in t) for t in texts)


def review(fig, paper: bool = False) -> list[str]:
    """Automated design review of a drawn figure (docs/visual_standard.md, part A).

    Checks what a script can check; the visual items in part B still need a
    person (or Claude) looking at the rendered file.

    Args:
        fig: A drawn figure (call before ``save``, which closes it).
        paper: True for a paper figure, which may not carry a title inside
            the artwork or a footer.

    Returns:
        A list of problems, empty if the figure passes.
    """
    problems: list[str] = []
    width_mm = fig.get_figwidth() * MM_PER_INCH
    if not any(abs(width_mm - w) < 0.5 for w in COLUMN_WIDTH_MM.values()):
        problems.append(f"width {width_mm:.1f} mm is not 90, 140 or 190 mm")
    fig.canvas.draw()
    for text in fig.findobj(lambda a: hasattr(a, "get_fontsize") and hasattr(a, "get_text")):
        if not text.get_visible() or not text.get_text().strip():
            continue
        if text.get_fontsize() < MIN_TEXT_PT - 1e-9:
            problems.append(f"text {text.get_text()[:30]!r} is {text.get_fontsize():.1f} pt (< 7 pt)")
    renderer = fig.canvas.get_renderer()
    fig_box = fig.bbox
    tick_texts = {id(t) for ax in fig.axes for axis in (ax.xaxis, ax.yaxis)
                  for tick in axis.get_major_ticks() + axis.get_minor_ticks()
                  for t in (tick.label1, tick.label2)}
    for text in fig.findobj(lambda a: hasattr(a, "get_window_extent") and hasattr(a, "get_text")):
        if id(text) in tick_texts or not text.get_visible() or not text.get_text().strip():
            continue
        box = text.get_window_extent(renderer)
        if (box.x0 < fig_box.x0 - 1 or box.x1 > fig_box.x1 + 1
                or box.y0 < fig_box.y0 - 1 or box.y1 > fig_box.y1 + 1):
            problems.append(f"text {text.get_text()[:30]!r} runs outside the figure")
    for ax in fig.axes:
        if not ax.get_visible() or not ax.axison:
            continue
        has_x = (bool(ax.get_xlabel()) or not ax.xaxis.get_visible()
                 or _categorical(ax.get_xticklabels()))
        has_y = (bool(ax.get_ylabel()) or not ax.yaxis.get_visible()
                 or _categorical(ax.get_yticklabels()))
        shared_x = ax.get_shared_x_axes().get_siblings(ax)
        shared_y = ax.get_shared_y_axes().get_siblings(ax)
        if not has_x and not any(a.get_xlabel() for a in shared_x):
            problems.append("an axes has no x-axis label")
        if not has_y and not any(a.get_ylabel() for a in shared_y):
            problems.append("an axes has no y-axis label")
        titles = [ax.get_title(loc) for loc in ("left", "center", "right") if ax.get_title(loc)]
        if paper and titles:
            problems.append(f"paper figure carries a title {titles[0]!r}; put it in the caption")
    if paper and fig.findobj(lambda a: getattr(a, "get_gid", lambda: None)() == "shellbench-footer"):
        problems.append("paper figure carries the repository footer")
    return problems
