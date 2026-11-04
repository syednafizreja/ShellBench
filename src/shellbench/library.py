"""Shell floor library: the sized panel for every span, rise, levelling and live load.

File: src/shellbench/library.py

What this module does
---------------------
Playbook Day 26. The Day 25 panel (``panel.py``) is sized for one span, rise
and live load. This module repeats that sizing over the library grid
(``GRID``) and keeps, for each case, the thinnest trial thickness at which
every check passes with a prestressed tie (the author's decision of 3 Nov
2026). Each case is one row of ``results/floor_library.csv``.

The checks are panel.py's, unchanged: thrust against w L^2 / (8 f), the
GB 50010 6.2.17 section check under uniform and half-span live load with
e_a and the 1 / (1 - 1/lambda) amplifier, membrane stress below f_c, cover,
and a buckling factor above 1. ``panel.py`` reads its span, rise and live
load from module constants, so this module sets those constants for each
case, in its own process [J]. No check or value in panel.py is changed.

``spot_checks`` recomputes five quantities by hand for five cases (the Day 26
Done-when: 60 or more cases, 5 spot checks).

Run:  python -m shellbench.library        (about 15 minutes on 4 cores)

Units: N, m, Pa; quantities per m^2 of floor.
"""

from __future__ import annotations

import csv
import math
import tempfile
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

from shellbench import panel

ROOT = Path(__file__).resolve().parents[2]
LIBRARY_CSV = ROOT / "results" / "floor_library.csv"

#: Library grid [J]. Spans cover the family's frame spacing (data_card.md,
#: 6.0-8.4 m), because in layout A the vault spans between frames. Rise
#: ratios cover the author's required band 1/15-1/20 (floor_concept decision 4).
#: Live loads: the anchor office value and the corridor value (B3).
GRID: dict[str, tuple] = {
    "span_m": (6.0, 6.6, 7.2, 7.8, 8.4),
    "rise_ratio": (1.0 / 15.0, 1.0 / 17.5, 1.0 / 20.0),
    "live_pa": (2.5e3, 3.0e3),
    "levelling": tuple(panel.LEVELLING),
}
WORKERS = 4

COLUMNS = ("case_id", "span_m", "rise_ratio", "live_pa", "levelling", "status") + tuple(
    panel.PanelRow.__dataclass_fields__)


def size_case_group(span: float, rise_ratio: float) -> list[dict]:
    """All live loads and levellings for one span and rise; thinnest passing thickness each.

    Thicknesses are tried thinnest first. The CalculiX flexibility runs at a
    thickness do not depend on live load or levelling, so they are shared.
    """
    panel.SPAN_M, panel.RISE_RATIO = span, rise_ratio
    open_cases = {(q, lev) for q in GRID["live_pa"] for lev in GRID["levelling"]}
    found: dict[tuple[float, str], panel.PanelRow] = {}
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for t in panel.TRIAL_THICKNESSES_M:
            if not open_cases:
                break
            fl = panel.flexibility(t, work)
            for q, lev in sorted(open_cases):
                panel.LIVE_PA = q
                sd = panel.FINISHES_PA + panel.levelling_pa(lev)
                buckle = panel.buckling_factor(t, sd, work, f"{lev}_{q:.0f}")
                row = panel.size_row(t, lev, fl, buckle, prestressed=True)
                if row.passes:
                    found[(q, lev)] = row
                    open_cases.discard((q, lev))
    out = []
    for q in GRID["live_pa"]:
        for lev in GRID["levelling"]:
            base = {"span_m": span, "rise_ratio": round(rise_ratio, 5), "live_pa": q, "levelling": lev}
            row = found.get((q, lev))
            if row is None:
                blank = {k: "" for k in panel.PanelRow.__dataclass_fields__ if k != "levelling"}
                out.append({**base, "status": "no_pass", **blank})
            else:
                out.append({**base, "status": "ok", **asdict(row)})
    return out


def build_library(workers: int = WORKERS) -> list[dict]:
    """Every case of GRID, in grid order, with a case id."""
    groups = [(s, r) for s in GRID["span_m"] for r in GRID["rise_ratio"]]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        parts = list(ex.map(size_case_group, *zip(*groups)))
    rows = [r for part in parts for r in part]
    for k, r in enumerate(rows, start=1):
        r["case_id"] = f"SF{k:03d}"
    return rows


def write_library(rows: list[dict], path: Path = LIBRARY_CSV) -> None:
    """Write the library, numbers to 4 significant figures."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in r.items()})


def read_library(path: Path = LIBRARY_CSV) -> list[dict]:
    """Read the library CSV back."""
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def spot_checks(row: dict) -> dict[str, float]:
    """Five hand checks of one library row; each value is (hand / library) - 1.

    1. w_uls = 1.3 (25 kN/m^3 t k + finishes + levelling) + 1.5 q.
    2. H = w L^2 / (8 f).
    3. CalculiX rigid-tie thrust against H (the Day 25 Done-when, 10 %).
    4. Concrete per m^2 = t k, with k the arc length over the span.
    5. Tie steel = (pi d^2 / 4) 7850 / s.
    """
    span, ratio, q, t = (float(row[k]) for k in ("span_m", "rise_ratio", "live_pa", "thickness_m"))
    f = ratio * span
    n = 2000
    k = sum(math.hypot(span / n, 4 * f * (span - 2 * (i + 0.5) * span / n) / span ** 2 * span / n)
            for i in range(n)) / span
    kind, value = panel.LEVELLING[row["levelling"]]
    lev = value * panel.G_ACCEL * (f / 3.0 if kind == "fill" else 1.0)
    w = panel.GAMMA_G * (panel.CONCRETE_N_M3 * t * k + panel.FINISHES_PA + lev) + panel.GAMMA_Q * q
    h = w * span ** 2 / (8.0 * f)
    d = float(row["tie_bar_mm"]) / 1000.0
    tie = math.pi * d * d / 4.0 * panel.STEEL_DENSITY_KG_M3 / panel.TIE_SPACING_M
    return {
        "w_uls": w / float(row["w_uls_pa"]) - 1.0,
        "h_closed": h / float(row["h_closed_n_m"]) - 1.0,
        "h_fe_vs_closed": float(row["h_rigid_n_m"]) / h - 1.0,
        "concrete": t * k / float(row["concrete_m3_m2"]) - 1.0,
        "tie_steel": tie / float(row["tie_kg_m2"]) - 1.0,
    }


def main() -> None:
    """Build the library, write it and print the pass count."""
    rows = build_library()
    write_library(rows)
    ok = sum(r["status"] == "ok" for r in rows)
    print(f"{len(rows)} cases, {ok} sized, {len(rows) - ok} with no passing thickness")


if __name__ == "__main__":
    main()
