"""Arithmetic checks on the thesis hand calculations (anchor, Layer 1).

File: src/shellbench/thesis_checks.py

What this module does
---------------------
The anchor model is compared with tables from the author's thesis. When a
difference is large, it helps to know whether the thesis table is consistent
with itself before blaming the model. This module runs two such checks on the
live-load moment-distribution table (Th §7.2, table "7.2"), typed in
``validation/thesis_values/live_distribution_table_7_2.csv``, and one check on
the combination table (Th Table 8-13, roof rows,
``validation/thesis_values/combination_beam_roof.csv``):

1. Column sums. In a moment-distribution table the final moment at a member
   end is the fixed-end moment plus every distribution and carry-over step
   below it. ``column_sums`` recomputes that sum and sets it next to the
   printed final value.
2. Joint balance. After the last distribution step, the final member-end
   moments at a joint add up to minus the external joint moment (the sign
   used in the thesis tables; Day 5, docs/anchor_notes.md). ``joint_balance``
   gives that sum, both for the printed finals and for the column sums.
3. Combination factors. ``combination_factor_check`` recomputes the first
   combination column of Table 8-13 with 1.3 D + 1.5 L and with 1.0 D + 1.5 L.

Nothing here corrects a thesis value. The checks are arithmetic on printed
numbers, and their findings are judgements for the author to confirm [J].

Units: kN*m for moments, kN for shears; distribution factors are [-].
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

#: Row labels of the typed distribution table that are summed into a final
#: moment (fixed-end moment and the distribution / carry-over steps).
SUMMED_ROW_PREFIXES: tuple[str, ...] = ("fixed_end_moment", "step_")


def read_distribution_table(path: Path) -> list[dict]:
    """Read the typed live-load distribution table.

    Args:
        path: ``live_distribution_table_7_2.csv``.

    Returns:
        One dict per cell with keys floor, row, joint, member_end, value.
    """
    with open(path, newline="", encoding="utf-8") as fh:
        return [{
            "floor": r["floor [text]"], "row": r["row [text]"], "joint": r["joint [text]"],
            "member_end": r["member_end [text]"], "value": float(r["value [mixed]"]),
        } for r in csv.DictReader(fh)]


def column_sums(cells: list[dict]) -> list[dict]:
    """Recompute each final member-end moment as the sum of its column.

    Args:
        cells: Output of ``read_distribution_table``.

    Returns:
        One dict per (floor, joint, member end) that has a printed final value,
        with the column sum, the printed final and their difference
        (printed - sum) [kN*m].
    """
    sums: dict[tuple[str, str, str], float] = defaultdict(float)
    finals: dict[tuple[str, str, str], float] = {}
    for c in cells:
        key = (c["floor"], c["joint"], c["member_end"])
        if c["row"] == "final":
            finals[key] = c["value"]
        elif c["row"].startswith(SUMMED_ROW_PREFIXES):
            sums[key] += c["value"]
    return [{
        "floor": k[0], "joint": k[1], "member_end": k[2],
        "column_sum": round(sums[k], 2), "printed_final": v,
        "printed_minus_sum": round(v - sums[k], 2),
    } for k, v in finals.items()]


def joint_balance(cells: list[dict]) -> list[dict]:
    """Sum the final member-end moments at every joint.

    Args:
        cells: Output of ``read_distribution_table``.

    Returns:
        One dict per (floor, joint) with the sum of printed finals, the sum of
        column sums, and the external joint moment printed in the table's
        first load row (0 where none is printed). A balanced joint has a sum
        equal to minus that moment, or to 0 if the moment was not applied.
    """
    ext = {(c["floor"], c["joint"]): c["value"] for c in cells if c["row"] == "joint_moment"}
    printed: dict[tuple[str, str], float] = defaultdict(float)
    summed: dict[tuple[str, str], float] = defaultdict(float)
    for r in column_sums(cells):
        printed[(r["floor"], r["joint"])] += r["printed_final"]
        summed[(r["floor"], r["joint"])] += r["column_sum"]
    return [{
        "floor": k[0], "joint": k[1],
        "sum_printed_finals": round(printed[k], 2),
        "sum_column_sums": round(summed[k], 2),
        "external_moment_printed": ext.get(k, 0.0),
    } for k in printed]


def read_combination_table(path: Path) -> list[dict]:
    """Read the typed roof rows of thesis Table 8-13.

    Args:
        path: ``combination_beam_roof.csv``.

    Returns:
        One dict per row with location, force, dead, live, wind and the
        printed first combination value.
    """
    with open(path, newline="", encoding="utf-8") as fh:
        return [{
            "location": r["location [text]"], "force": r["force [text]"],
            "dead": float(r["dead [mixed]"]), "live": float(r["live [mixed]"]),
            "wind": float(r["wind [mixed]"]),
            "printed": float(r["combo_1_3D_1_5L_printed [mixed]"]),
        } for r in csv.DictReader(fh)]


def combination_factor_check(rows: list[dict], gamma_g: float, gamma_q: float) -> list[dict]:
    """Recompute the first combination column of Table 8-13.

    Args:
        rows: Output of ``read_combination_table``.
        gamma_g: Dead-load factor to test.
        gamma_q: Live-load factor to test.

    Returns:
        One dict per row with the recomputed value and printed - recomputed.
    """
    return [{
        "location": r["location"], "force": r["force"],
        "recomputed": round(gamma_g * r["dead"] + gamma_q * r["live"], 3),
        "printed": r["printed"],
        "printed_minus_recomputed": round(r["printed"] - (gamma_g * r["dead"] + gamma_q * r["live"]), 3),
    } for r in rows]
