# scripts/strip_factor_bound.py
"""Bound H1's S_b for the strip-versus-plan lateral gap (data_card row 4).

The ``building_v2`` take-off counts columns and frame beams of one frame strip.
The anchor grid plan holds 1.3125 times the strip's columns and frame beams per
m² (edge frames; data_card row 4, LOG Day 20). The data card asks that S_b is
not quoted until this gap is closed or bounded at factors 1.0 and 1.3125.

This script repeats ``verdicts.building_table`` for the primary case with the
whole lateral carbon of both systems multiplied by the factor. That overstates
the gap, because the longitudinal beams in ``building_v2`` are already per plan
m², so the 1.3125 row is a conservative (low) bound on S_b. The shell row is
not re-chosen under the factor; re-choosing could only lower the shell carbon,
so this also keeps the bound low. Exploratory check,
not a preregistered sensitivity case; the frozen verdicts are not changed.

Run: python scripts/strip_factor_bound.py
"""

import pandas as pd

from shellbench import verdicts

#: Plan-to-strip ratio of columns and frame beams per m² (data_card row 4) [-].
PLAN_OVER_STRIP: float = 1.3125


def bound(factor: float) -> dict:
    """H1 numbers with the lateral carbon of both systems times ``factor``."""
    rc, sh = verdicts.load()
    base = verdicts.cases()[0]
    t = verdicts.building_table(rc, sh, base)
    t["c_bld"] = t["c_floor"] + factor * t["c_lat"]
    t["s_bld"] = t["s_floor"] + factor * t["s_lat"]
    t["s_b"] = 1.0 - t["s_bld"] / t["c_bld"]
    out = verdicts.h1(t)
    out["lateral_factor"] = factor
    return out


def main() -> None:
    """Print S_b at lateral factors 1.0 and 1.3125."""
    rows = pd.DataFrame([bound(1.0), bound(PLAN_OVER_STRIP)])
    cols = ["lateral_factor", "verdict", "n_buildings", "n_s_b_positive", "n_s_b_below_s_f",
            "s_b_min", "s_b_median", "s_b_max"]
    print(rows[cols].to_string(index=False))


if __name__ == "__main__":
    main()
