"""Floor library: size every shell-floor variant of layout A (Playbook Day 26).

File: src/shellbench/floorlib.py

What this module does
---------------------
A library case is one floor variant: span x rise x levelling option x mesh
layout, always with a prestressed tie every 1.2 m (approved by the author on
3 Nov 2026). For each case the module finds the smallest trial thickness that
passes every check of ``panel.size_row``. A case where no trial thickness
passes is kept and marked ``sized = False``; it is never dropped.

Variants [J]
------------
- Span 6.0 and 6.6 m: the two bay widths of layout A (spec G4, floor_concept
  decision 2).
- Rise-to-span 1/8, 1/10, 1/12, 1/15, 1/18 and 1/20: the range of floor_concept
  decision 4, low end included.
- Levelling: foamed fill, recycled fill, raised floor (floor_concept 4.3).
  Fills are at their true depth f - z(x), not the Day 25 uniform f / 3.
- Mesh: one layer at mid-depth (Day 25), or one layer near each face at the
  minimum ratio each (handoff of 3 Nov, Day 26 to-do).

Trial thicknesses run from 50 to 150 mm in 10 mm steps [J]. Buckling is linear,
with no imperfection allowance: the JGJ 22-2012 stability analysis (3.2.9) is
still open (handoff of 3 Nov).

Usage::

    python -m shellbench.floorlib

writes ``results/floor_library.csv``. Units: m, N, Pa, kg.
"""

from __future__ import annotations

import csv
import tempfile
from dataclasses import asdict
from pathlib import Path

from shellbench import panel as p

ROOT = Path(__file__).resolve().parents[2]
RESULTS_CSV = ROOT / "results" / "floor_library.csv"

SPANS_M: tuple[float, ...] = (6.0, 6.6)  # layout A bays, spec G4
RISE_DENOMINATORS: tuple[int, ...] = (8, 10, 12, 15, 18, 20)  # f / L = 1 / n, floor_concept decision 4
MESH_LAYERS: tuple[int, ...] = (1, 2)
THICKNESSES_M: tuple[float, ...] = tuple(round(0.050 + 0.010 * i, 3) for i in range(11))  # 50-150 mm [J]
SHORT: dict[str, str] = {"foamed_fill": "ff", "recycled_fill": "rf", "raised_floor": "rs"}


def variant_id(span_m: float, rise_den: int, levelling: str, layers: int) -> str:
    """Case ID, for example ``L66-r15-ff-m1`` (6.6 m, f/L = 1/15, foamed fill, one mesh)."""
    return f"L{round(span_m * 10):02d}-r{rise_den:02d}-{SHORT[levelling]}-m{layers}"


def cases() -> list[dict]:
    """Every library case, in run order."""
    return [{"variant_id": variant_id(L, n, lev, m), "span_m": L, "rise_den": n,
             "levelling": lev, "mesh_layers": m}
            for L in SPANS_M for n in RISE_DENOMINATORS for lev in p.LEVELLING for m in MESH_LAYERS]


def size_geometry(span_m: float, rise_den: int, workdir: Path) -> list[dict]:
    """Size the six cases of one vault geometry.

    Thicknesses are tried from thin to thick. At each one the five unit cases
    and one buckling run per levelling option are run, and every case not yet
    sized is checked. The loop stops when all six are sized.

    Returns:
        One row per case: the case keys, ``sized`` and the ``PanelRow`` fields
        of the sized thickness (or of the thickest trial if none passes).
    """
    vault = p.Vault(span_m, 1.0 / rise_den)
    todo = {(lev, m): None for lev in p.LEVELLING for m in MESH_LAYERS}
    last = {}
    for t in THICKNESSES_M:
        sub = workdir / f"L{span_m:g}_r{rise_den}"
        fl = p.flexibility(t, sub, vault, fill_shape=True)
        for lev in p.LEVELLING:
            if all(todo[(lev, m)] for m in MESH_LAYERS):
                continue
            if p.is_fill(lev):
                buckle = p.buckling_factor(t, p.FINISHES_PA, sub, lev, vault, p.fill_unit_weight(lev))
            else:
                buckle = p.buckling_factor(t, p.FINISHES_PA + p.levelling_pa(lev, vault), sub, lev, vault)
            for m in MESH_LAYERS:
                if todo[(lev, m)]:
                    continue
                row = p.size_row(t, lev, fl, buckle, prestressed=True, vault=vault, true_fill=True, layers=m)
                last[(lev, m)] = row
                if row.passes:
                    todo[(lev, m)] = row
        if all(todo.values()):
            break
    out = []
    for (lev, m), row in todo.items():
        r = row or last[(lev, m)]
        out.append({"variant_id": variant_id(span_m, rise_den, lev, m), "span_m": span_m,
                    "rise_ratio": 1.0 / rise_den, "mesh_layers": m, "sized": row is not None, **asdict(r)})
    return out


def build_library(workdir: Path) -> list[dict]:
    """Size every case of ``cases()``; one row per case."""
    rows = []
    for span in SPANS_M:
        for n in RISE_DENOMINATORS:
            rows += size_geometry(span, n, workdir)
    order = {c["variant_id"]: i for i, c in enumerate(cases())}
    return sorted(rows, key=lambda r: order[r["variant_id"]])


def write_rows(rows: list[dict], path: Path = RESULTS_CSV) -> None:
    """Write the library to CSV, numbers to 4 significant figures."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        for r in rows:
            writer.writerow({k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in r.items()})


def main() -> None:
    """Build the library, write results/floor_library.csv and print a summary."""
    with tempfile.TemporaryDirectory() as tmp:
        rows = build_library(Path(tmp))
    write_rows(rows)
    for r in rows:
        print(f"{r['variant_id']} t={r['thickness_m'] * 1e3:.0f} mm tie {r['tie_bar_mm']} "
              f"u={max(r['util_uniform'], r['util_pattern']):.2f} buckle={r['buckling_factor']:.1f} "
              f"sized={r['sized']}")
    print(f"{sum(r['sized'] for r in rows)} of {len(rows)} cases sized")


if __name__ == "__main__":
    main()
