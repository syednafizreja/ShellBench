"""Batch runner for the conventional building family (Playbook Day 18).

File: src/shellbench/family.py

What this module does
---------------------
``sample_family`` draws building inputs from the frozen family definition
(``FAMILY``) with a fixed seed. ``run_building`` sizes one building with the
generator (Day 16) and returns one row: its inputs, its status, the sized
members, the checks and the frame-strip quantities and carbon. ``run_family``
does this for n buildings and writes ``family_rc.csv`` (and
``family_rc.parquet`` when pyarrow is installed). The column list ``COLUMNS``
is the frozen data format of docs/data_card.md: after 4 Nov 2026 a column is
never renamed or given new units; columns may only be added.

Nothing is dropped. A building that the generator cannot size is a row with
status "failed" and the reason. A building whose seismic input is not yet
confirmed from GB 50011 is a row with status "not_run" and the reason
(preregistration.md 2.1, "Valid buildings").

Run:  python -m shellbench.family --n 10 --out results/family_sample

Units: m, kN, kN/m^2, mm for sections, kg and kgCO2e per m^2 of floor.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from shellbench import __version__
from shellbench import generator as g
from shellbench import seismic as s

ROOT = Path(__file__).resolve().parents[2]
CARBON_CSV = ROOT / "data" / "carbon_factors.csv"
FACTOR_SET = "GBT51366"  # D29: one factor set
SEED = 20261104  # fixed seed, the date of the format freeze [J]
STEEL_KG_M3 = 7850.0  # as generator.quantities [J]

#: GB 50011-2010 Table 3.2.2: design basic acceleration -> intensity [?].
INTENSITY_FOR_PGA: dict[float, int] = {0.05: 6, 0.10: 7, 0.15: 7, 0.20: 8, 0.30: 8, 0.40: 9}

#: The frozen family definition (Day 18) [J]. Storeys and PGA are the
#: charter's. The other ranges keep the anchor's three-bay transverse frame
#: (two side bays and one middle bay) and span its values: side span 7.2,
#: middle 6.6, frame spacing 7.2, ground storey 4.55, upper storeys 3.6 m.
FAMILY: dict[str, object] = {
    "storeys": (3, 4, 5, 6, 7, 8),
    "pga_g": (0.05, 0.10, 0.15, 0.20, 0.30, 0.40),
    "side_span_m": (6.0, 8.4),
    "middle_span_m": (5.4, 7.8),
    "frame_spacing_m": (6.0, 8.4),
    "ground_storey_m": (3.9, 4.8),
    "upper_storey_m": (3.3, 3.9),
    "office_live_kn_m2": (2.0, 3.5),
}
#: Values held at the anchor's for every building (generator test inputs,
#: tests/test_generator_anchor.py, with their sources there).
FIXED: dict[str, float] = {
    "floor_dead_kn_m2": 4.05, "roof_dead_kn_m2": 4.224, "corridor_live_kn_m2": 3.0,
    "roof_live_kn_m2": 0.5, "secondary_kn_m": 2.54, "beam_wall_kn_m": 5.51,
    "exterior_wall_kn_m": 8.37, "interior_wall_kn_m": 6.36, "longitudinal_beam_kn_m": 3.61,
    "parapet_kn_m": 2.54, "tg_s": 0.35, "psi_t": 0.7, "concrete_e_mpa": 3.25e4,
    "beam_i_factor": 2.0,
}
LENGTH_STEP_M = 0.3  # spans and frame spacing on a 300 mm module [J]
HEIGHT_STEP_M = 0.15  # storey heights on a 150 mm module [J]
LIVE_STEP_KN_M2 = 0.5  # live load in 0.5 kN/m^2 steps [J]


@dataclass
class Sample:
    """The sampled inputs of one building."""

    building_id: str
    storeys: int
    pga_g: float
    side_span_m: float
    middle_span_m: float
    frame_spacing_m: float
    ground_storey_m: float
    upper_storey_m: float
    office_live_kn_m2: float


#: Frozen data format (docs/data_card.md). Order is part of the format.
COLUMNS: tuple[str, ...] = (
    "building_id", "status", "reason", "storeys", "pga_g", "intensity",
    "side_span_m", "middle_span_m", "frame_spacing_m", "ground_storey_m", "upper_storey_m",
    "office_live_kn_m2", "floor_system", "slab_mm", "column_mm", "side_beam_b_mm",
    "side_beam_h_mm", "middle_beam_b_mm", "middle_beam_h_mm", "period_s", "max_drift_ratio",
    "axial_ratio", "resizes", "concrete_m3_per_m2", "bar_steel_kg_per_m2",
    "carbon_kgco2e_per_m2", "factor_set", "generator_version", "git_commit",
)


def _grid(lo: float, hi: float, step: float, u: np.ndarray) -> np.ndarray:
    """Map u in [0, 1) onto the values lo, lo + step, ..., hi."""
    values = np.round(np.arange(lo, hi + step / 2, step), 3)
    return values[np.minimum((u * len(values)).astype(int), len(values) - 1)]


def sample_family(n: int, seed: int = SEED) -> list[Sample]:
    """Draw n buildings: storeys and PGA cycle through every cell; the rest by Latin hypercube.

    Building k takes cell k mod 36 of the 6 x 6 storey-PGA grid, so every
    cell gets n/36 buildings (one more for the first n mod 36 cells). Each
    continuous input is stratified over n and shuffled independently.
    """
    rng = np.random.default_rng(seed)
    cells = [(st, pga) for st in FAMILY["storeys"] for pga in FAMILY["pga_g"]]
    names = ("side_span_m", "middle_span_m", "frame_spacing_m", "ground_storey_m",
             "upper_storey_m", "office_live_kn_m2")
    steps = (LENGTH_STEP_M, LENGTH_STEP_M, LENGTH_STEP_M, HEIGHT_STEP_M, HEIGHT_STEP_M,
             LIVE_STEP_KN_M2)
    cols = {}
    for name, step in zip(names, steps):
        u = (rng.permutation(n) + rng.random(n)) / n
        cols[name] = _grid(*FAMILY[name], step, u)
    out = []
    for k in range(n):
        st, pga = cells[k % len(cells)]
        out.append(Sample(f"RC{k + 1:05d}", st, pga, *(float(cols[m][k]) for m in names)))
    return out


def building_input(smp: Sample, alpha_max: float) -> g.BuildingInput:
    """Turn a sample into generator inputs, with the anchor's fixed values."""
    f = FIXED
    spans = (smp.side_span_m, smp.middle_span_m, smp.side_span_m)
    heights = (smp.ground_storey_m,) + (smp.upper_storey_m,) * (smp.storeys - 1)
    return g.BuildingInput(
        spans_m=spans, storey_heights_m=heights, tributary_width_m=smp.frame_spacing_m,
        slab_panel_m=smp.frame_spacing_m / 2.0, floor_dead_kn_m2=f["floor_dead_kn_m2"],
        roof_dead_kn_m2=f["roof_dead_kn_m2"],
        live_kn_m2=(smp.office_live_kn_m2, f["corridor_live_kn_m2"], smp.office_live_kn_m2),
        roof_live_kn_m2=f["roof_live_kn_m2"], floor_secondary_kn_m=(f["secondary_kn_m"],) * 3,
        roof_secondary_kn_m=(f["secondary_kn_m"],) * 3,
        floor_beam_wall_kn_m=(f["beam_wall_kn_m"], 0.0, f["beam_wall_kn_m"]),
        exterior_wall_kn_m=f["exterior_wall_kn_m"], interior_wall_kn_m=f["interior_wall_kn_m"],
        longitudinal_beam_kn_m=f["longitudinal_beam_kn_m"], parapet_kn_m=f["parapet_kn_m"],
        alpha_max=alpha_max, tg_s=f["tg_s"], psi_t=f["psi_t"],
        concrete_e_mpa=f["concrete_e_mpa"], beam_i_factor=f["beam_i_factor"])


def carbon_factors(path: Path = CARBON_CSV, factor_set: str = FACTOR_SET) -> dict[str, float]:
    """Read the author's factors in place: C40 [kgCO2e/m^3] and HRB400 [kgCO2e/kg]."""
    out = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["set [text]"] == factor_set:
                v = float(row["value"])
                out[row["material [text]"]] = v / 1000.0 if row["unit [text]"].endswith("/t") else v
    return out


def git_commit() -> str:
    """Short commit of the code that made the row, or "unknown"."""
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True,
                              capture_output=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def run_building(smp: Sample, factors: dict[str, float], commit: str) -> dict:
    """Size one building and return its row (every column of COLUMNS)."""
    row = {c: "" for c in COLUMNS}
    row.update(asdict(smp))
    row.update(intensity=INTENSITY_FOR_PGA[smp.pga_g], floor_system="rc_slab",
               factor_set=FACTOR_SET, generator_version=__version__, git_commit=commit)
    try:
        alpha = s.alpha_max_frequent(row["intensity"], smp.pga_g)
    except KeyError as err:
        row.update(status="not_run", reason=f"GB 50011 Table 5.1.4-1 value [?]: {err.args[0]}")
        return row
    try:
        res = g.generate(building_input(smp, alpha))
    except (RuntimeError, ValueError) as err:
        row.update(status="failed", reason=str(err))
        return row
    z, q = res.final, res.quantities
    carbon = q["concrete_m3_per_m2"] * factors["C40"] + q["bar_steel_kg_per_m2"] * factors["HRB400"]
    row.update(status="ok", slab_mm=z.slab_mm, column_mm=z.column_mm,
               side_beam_b_mm=z.beams_mm[0][0], side_beam_h_mm=z.beams_mm[0][1],
               middle_beam_b_mm=z.beams_mm[1][0], middle_beam_h_mm=z.beams_mm[1][1],
               period_s=round(res.period_s, 4), max_drift_ratio=round(max(res.drift_ratios), 6),
               axial_ratio=round(res.axial_ratio, 4), resizes=len(res.history) - 1,
               concrete_m3_per_m2=round(q["concrete_m3_per_m2"], 5),
               bar_steel_kg_per_m2=round(q["bar_steel_kg_per_m2"], 3),
               carbon_kgco2e_per_m2=round(carbon, 2))
    return row


def run_family(n: int, out_dir: Path, seed: int = SEED) -> list[dict]:
    """Run n buildings and write family_rc.csv (and .parquet if pyarrow is present)."""
    factors, commit = carbon_factors(), git_commit()
    rows = [run_building(smp, factors, commit) for smp in sample_family(n, seed)]
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "family_rc.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        return rows
    pq.write_table(pa.Table.from_pylist(rows), out_dir / "family_rc.parquet")
    return rows


def main() -> None:
    """Command line: --n buildings, --out folder, --seed."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "family_sample")
    ap.add_argument("--seed", type=int, default=SEED)
    a = ap.parse_args()
    rows = run_family(a.n, a.out, a.seed)
    for st in ("ok", "failed", "not_run"):
        print(st, sum(r["status"] == st for r in rows))


if __name__ == "__main__":
    main()
