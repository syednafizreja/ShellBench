"""Wind load case on the anchor frame and the drift check against thesis Table 8-2.

File: src/shellbench/anchor_wind.py

What this module does
---------------------
It applies the wind storey forces of the author's thesis (Th §8.2, Table 8-2,
typed on Day 3 in ``validation/thesis_values/wind_drift.csv``) to the 2D
elastic frame built by ``shellbench.anchor_frame.build_frame``, and compares
storey displacements and inter-storey drifts with Table 8-2. The forces are
taken as printed; they are not recomputed (Playbook Day 8).

Reading rules (docs/anchor_notes.md, "How the wind comparison is read",
written before the first run):

1. Pass/fail: model inter-storey drift Δu against the printed Δu of Table 8-2,
   storey by storey, with the author's 15 % tolerance (decision of 25 Oct 2026).
2. Diagnostics only: Δu against V/ΣD with the printed V and ΣD (the thesis
   method with its own numbers, flag D7), and against V/ΣD with D-values
   recomputed from the model's own section stiffnesses (``d_value_method``).
3. Model storey displacement is the mean horizontal displacement of the four
   column-line nodes of a level. The drift ratio checked against 1/550 is
   Δu / h with the model storey heights.
4. Check runs change one thing each (``WIND_VARIANTS``).

A separate check recomputes W_k from the Table 8-1 inputs (docs/baseline_spec.md
W1-W6) to test the typing and the thesis arithmetic; the loads applied are
always the printed W_k.

Units: kN, m inside OpenSees; drifts are reported in mm because Table 8-2 is
printed in mm. kN/m equals N/mm, so D-values in N/mm need no conversion.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import openseespy.opensees as ops

from shellbench import anchor_frame as af

# ---------------------------------------------------------------------------
# Decisions and limits
# ---------------------------------------------------------------------------

#: Tolerance on storey drift against Table 8-2 [%]. Author's decision of
#: 25 Oct 2026, made before any wind run (docs/anchor_notes.md, "Lateral
#: loads: decisions made before the runs", item 1).
WIND_DRIFT_TOLERANCE_PCT: float = 15.0

#: Elastic inter-storey drift limit for RC frames [-]. Spec S11 (Th §8.2,
#: §8.4: 1/550).
DRIFT_LIMIT: float = 1.0 / 550.0

#: Ground storey height used by the thesis wind tables [m]. Spec G7 and W7
#: (Th Tables 8-1, 8-2: 4.05 m; decision B4 keeps 4.55 m for the model).
THESIS_WIND_GROUND_STOREY_M: float = 4.05

# ---------------------------------------------------------------------------
# Table 8-1 inputs, used only for the consistency check of the printed W_k
# ---------------------------------------------------------------------------

#: Basic wind pressure w0 [kN/m^2]. Spec W1 (Th §1.3, §8.1, Table 8-1).
W0_KN_M2: float = 0.30

#: Shape factor mu_s [-]. Spec W3 (Th Table 8-1).
MU_S: float = 1.3

#: Height factor mu_z at levels 1-4 [-]. Spec W4 (Th Table 8-1).
MU_Z: tuple[float, ...] = (1.00, 1.00, 1.03, 1.13)

#: Gust factor beta_z [-]. Spec W5 (Th Table 8-1).
BETA_Z: float = 1.00

#: Loaded width of the frame on axis (2) [m]. Spec W6 (Th Table 8-1, B10).
LOADED_WIDTH_M: float = 7.2

#: Parapet height [m]. Th §4.2, parapet wall "1.2 x 0.24 x 5.5" (240 mm wall,
#: 1.2 m high).
PARAPET_HEIGHT_M: float = 1.2

#: Tributary height of each level implied by the wind-table storey heights
#: (spec W7: 4.05 m ground, 3.6 m above): half the storey below plus half the
#: storey above, and at the roof half the top storey plus the parapet [m] [J].
#: Th Table 8-1 uses hj = 3.6 m at the roof instead (flag D23).
EXPECTED_TRIBUTARY_M: tuple[float, ...] = (
    (THESIS_WIND_GROUND_STOREY_M + 3.6) / 2.0, 3.6, 3.6, 3.6 / 2.0 + PARAPET_HEIGHT_M)

# ---------------------------------------------------------------------------
# Thesis values
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ThesisWindRow:
    """One storey of Table 8-2 as typed on Day 3.

    Attributes:
        level: Storey number, 1 = ground storey.
        w_kn: Wind force applied at the top of this storey [kN].
        v_kn: Storey shear [kN].
        sum_d_n_mm: Storey lateral stiffness ΣD [N/mm] (from Table 7-6).
        du_mm: Printed inter-storey drift [mm].
        u_mm: Printed cumulative displacement [mm].
        h_mm: Storey height used by the thesis [mm].
        theta: Printed drift ratio [-] (u / h, flag D8).
        flag: Day 3 flag text.
    """

    level: int
    w_kn: float
    v_kn: float
    sum_d_n_mm: float
    du_mm: float
    u_mm: float
    h_mm: float
    theta: float
    flag: str


def read_thesis_wind(repo_root: Path) -> list[ThesisWindRow]:
    """Read Table 8-2 from ``validation/thesis_values/wind_drift.csv``.

    Args:
        repo_root: Repository root.

    Returns:
        One row per storey, ground storey first.
    """
    path = repo_root / "validation" / "thesis_values" / "wind_drift.csv"
    with open(path, newline="", encoding="utf-8") as fh:
        rows = [ThesisWindRow(
            level=int(r["level [text]"]), w_kn=float(r["W_k [kN]"]),
            v_kn=float(r["V [kN]"]), sum_d_n_mm=float(r["sum_D [N/mm]"]),
            du_mm=float(r["du [mm]"]), u_mm=float(r["u [mm]"]),
            h_mm=float(r["h [mm]"]), theta=float(r["theta [-]"]),
            flag=r["flag [text]"]) for r in csv.DictReader(fh)]
    return sorted(rows, key=lambda r: r.level)


def wind_force_check_rows(thesis: list[ThesisWindRow]) -> list[dict]:
    """Recompute W_k from the Table 8-1 inputs and compare with Table 8-2.

    W_k = beta_z mu_s mu_z w0 B h_trib (GB 50009 characteristic wind load on a
    tributary area, as Th §8.1 applies it). The implied tributary height is
    W_k / (beta_z mu_s mu_z w0 B). The check also confirms that the printed
    storey shears are the running sums of the printed forces.

    Args:
        thesis: Output of ``read_thesis_wind``.

    Returns:
        One dict per level with the implied and expected tributary heights and
        the shear-sum check.
    """
    rows = []
    for i, t in enumerate(thesis):
        per_m = BETA_Z * MU_S * MU_Z[i] * W0_KN_M2 * LOADED_WIDTH_M
        implied = t.w_kn / per_m
        expected = EXPECTED_TRIBUTARY_M[i]
        shear_sum = sum(r.w_kn for r in thesis[i:])
        rows.append({
            "level [text]": str(t.level),
            "W_k_printed [kN]": t.w_kn,
            "wind_per_m_height [kN/m]": round(per_m, 4),
            "implied_tributary_height [m]": round(implied, 3),
            "expected_tributary_height [m]": round(expected, 3),
            "W_k_from_expected [kN]": round(per_m * expected, 2),
            "V_printed [kN]": t.v_kn,
            "sum_W_above [kN]": round(shear_sum, 2),
            "note [text]": ("roof: Table 8-1 uses hj = 3.6 m; half the top storey plus the "
                            "1.2 m parapet (Th s4.2) gives 3.0 m (flag D23)"
                            if i == len(thesis) - 1 else ""),
        })
    return rows


# ---------------------------------------------------------------------------
# D-value method with the model's own stiffnesses (diagnostic)
# ---------------------------------------------------------------------------


def d_value_method(storey_heights_m: tuple[float, ...] | None = None) -> list[dict]:
    """Storey stiffness ΣD by the D-value method, from the model's sections.

    Same formulas the thesis uses in §7.3 (Table 7-6): i = EI/L; general
    storey K = Σi_b / (2 i_c), α_c = K / (2 + K); ground storey (fixed base)
    K = Σi_b / i_c, α_c = (0.5 + K) / (2 + K); D = α_c 12 i_c / h². Beam I is
    BEAM_INERTIA_FACTOR x I0, as in the model. Beams above and below a
    general-storey column are the same sections, so Σi_b counts each beam
    twice.

    Args:
        storey_heights_m: Storey heights, ground first [m]; defaults to
            ``anchor_frame.STOREY_HEIGHTS_M``.

    Returns:
        One dict per storey with K, α_c and D for an exterior (A/D) and an
        interior (B/C) column and ΣD for the frame [N/mm].
    """
    heights = storey_heights_m or af.STOREY_HEIGHTS_M
    e = af.E_KN_M2
    bc, hc = af.COLUMN_BH_M
    i_col = bc * hc**3 / 12.0

    def i_beam(span: str, length: float) -> float:
        """Return EI/L of one frame beam [kN*m]."""
        bb, hb = af.BEAM_BH_M[span]
        return e * af.BEAM_INERTIA_FACTOR * bb * hb**3 / 12.0 / length

    ib_side = i_beam("AB", af.SPANS_M[0])
    ib_mid = i_beam("BC", af.SPANS_M[1])
    rows = []
    for storey, h in enumerate(heights, start=1):
        ic = e * i_col / h
        out = {"storey [text]": str(storey), "h [m]": h}
        total = 0.0
        for label, sum_ib in (("A/D", ib_side), ("B/C", ib_side + ib_mid)):
            if storey == 1:
                k = sum_ib / ic
                alpha = (0.5 + k) / (2.0 + k)
            else:
                k = 2.0 * sum_ib / (2.0 * ic)
                alpha = k / (2.0 + k)
            d = alpha * 12.0 * ic / h**2  # kN/m = N/mm
            out[f"K_{label} [-]"] = round(k, 4)
            out[f"alpha_c_{label} [-]"] = round(alpha, 4)
            out[f"D_{label} [N/mm]"] = round(d, 0)
            total += 2.0 * d
        out["sum_D [N/mm]"] = round(total, 0)
        rows.append(out)
    return rows


# ---------------------------------------------------------------------------
# Wind analysis
# ---------------------------------------------------------------------------


def apply_wind(fm: af.FrameModel, forces_kn: list[float]) -> float:
    """Apply wind from the left as horizontal forces at the windward joints.

    The forces act at the axis-A node of each level, the joint the façade load
    reaches first [J]. With ``rigid_floor`` the point of application along a
    level does not matter.

    Args:
        fm: The frame returned by ``anchor_frame.build_frame``.
        forces_kn: W_k for levels 1..n [kN], positive to the right.

    Returns:
        Total applied horizontal load [kN].
    """
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)
    for lvl, w in enumerate(forces_kn, start=1):
        ops.load(fm.node[("A", lvl)], w, 0.0, 0.0)
    return sum(forces_kn)


def make_floors_rigid(fm: af.FrameModel) -> None:
    """Tie the horizontal displacement of every node of a level to its axis-A node.

    This removes beam axial deformation, the in-plane rigid-floor assumption
    of the D-value method. A check run only.

    Args:
        fm: The frame returned by ``anchor_frame.build_frame``.
    """
    n_levels = max(lvl for (_, lvl) in fm.node)
    for lvl in range(1, n_levels + 1):
        master = fm.node[("A", lvl)]
        slaves = {fm.node[(ax, lvl)] for ax in af.AXES[1:]}
        for span in af.SPAN_LABELS:
            slaves.update(fm.beam_nodes[(span, lvl)])
        slaves.discard(master)
        for s in sorted(slaves):
            ops.equalDOF(master, s, 1)


@dataclass
class WindResult:
    """Output of one wind run.

    Attributes:
        variant: Name of the run.
        heights_m: Storey heights used [m].
        u_mm: Mean horizontal displacement of each level [mm], level 1 first.
        du_mm: Inter-storey drift [mm].
        theta: Δu / h [-].
        column_shear_kn: Sum of column shears in each storey [kN].
        applied_kn: Total applied horizontal load [kN].
        base_shear_kn: Sum of horizontal base reactions [kN] (opposite sign).
    """

    variant: str
    heights_m: tuple[float, ...]
    u_mm: list[float]
    du_mm: list[float]
    theta: list[float]
    column_shear_kn: list[float]
    applied_kn: float
    base_shear_kn: float


def run_wind(forces_kn: list[float], axially_rigid_columns: bool = False,
             rigid_floor: bool = False, storey_heights_m: tuple[float, ...] | None = None,
             beam_inertia_factor: float | None = None, variant: str = "primary") -> WindResult:
    """Build, load and solve the frame for one wind run.

    Args:
        forces_kn: W_k for levels 1..n [kN].
        axially_rigid_columns: See ``anchor_frame.build_frame``.
        rigid_floor: If True, apply ``make_floors_rigid``.
        storey_heights_m: See ``anchor_frame.build_frame``.
        beam_inertia_factor: See ``anchor_frame.build_frame``.
        variant: Name of the run.

    Returns:
        A WindResult.
    """
    heights = tuple(storey_heights_m or af.STOREY_HEIGHTS_M)
    fm = af.build_frame(axially_rigid_columns, heights, beam_inertia_factor)
    if rigid_floor:
        make_floors_rigid(fm)
    applied = apply_wind(fm, forces_kn)
    if rigid_floor:
        ops.system("BandGeneral")
        ops.numberer("RCM")
        ops.constraints("Transformation")
        ops.integrator("LoadControl", 1.0)
        ops.algorithm("Linear")
        ops.analysis("Static")
        if ops.analyze(1) != 0:
            raise RuntimeError("OpenSees static analysis failed")
        ops.reactions()
    else:
        af.solve_static()

    n = len(heights)
    u = [1000.0 * sum(ops.nodeDisp(fm.node[(ax, lvl)], 1) for ax in af.AXES) / len(af.AXES)
         for lvl in range(1, n + 1)]
    du = [u[0]] + [u[i] - u[i - 1] for i in range(1, n)]
    theta = [d / (1000.0 * h) for d, h in zip(du, heights)]
    shear = []
    for storey in range(1, n + 1):
        # localForce[1] is the shear acting on the element at its bottom end,
        # along local y; for a column drawn upwards local y points to -x, so
        # it equals the storey shear carried, positive with the wind.
        shear.append(sum(ops.eleResponse(fm.column[(ax, storey)], "localForce")[1]
                         for ax in af.AXES))
    base = sum(ops.nodeReaction(fm.node[(ax, 0)], 1) for ax in af.AXES)
    ops.wipe()
    return WindResult(variant, heights, u, du, theta, shear, applied, base)


#: The wind runs reported. The first is the pass/fail run; the others each
#: change one thing (docs/anchor_notes.md reading rule 5).
WIND_VARIANTS: dict[str, dict] = {
    "primary": {},
    "rigid_column_axial": {"axially_rigid_columns": True},
    "rigid_floor": {"rigid_floor": True},
    "ground_4_05": {"storey_heights_m": (THESIS_WIND_GROUND_STOREY_M,) + af.STOREY_HEIGHTS_M[1:]},
}


def percent_difference(model: float, reference: float) -> float:
    """Return (model - reference) / |reference| x 100.

    Args:
        model: Model value.
        reference: Reference value (non-zero).

    Returns:
        Signed percentage difference.
    """
    return (model - reference) / abs(reference) * 100.0


def comparison_rows(results: dict[str, WindResult], thesis: list[ThesisWindRow],
                    d_redone: list[dict]) -> list[dict]:
    """Build the rows of ``results/anchor_wind.csv``.

    Args:
        results: Wind runs keyed by variant; must include ``"primary"``.
        thesis: Output of ``read_thesis_wind``.
        d_redone: Output of ``d_value_method`` for the model storey heights.

    Returns:
        One dict per storey: thesis values, primary model values, % differences
        against the three references, the pass/fail verdict on the
        tolerance, the 1/550 check, and each check run's Δu difference.
    """
    p = results["primary"]
    rows = []
    for i, t in enumerate(thesis):
        du_thesis_method = t.v_kn * 1000.0 / t.sum_d_n_mm
        du_redone = t.v_kn * 1000.0 / d_redone[i]["sum_D [N/mm]"]
        pct = percent_difference(p.du_mm[i], t.du_mm)
        row = {
            "level [text]": str(t.level),
            "W_k [kN]": t.w_kn,
            "V_thesis [kN]": t.v_kn,
            "V_model_columns [kN]": round(p.column_shear_kn[i], 2),
            "du_thesis [mm]": t.du_mm,
            "du_model [mm]": round(p.du_mm[i], 3),
            "du_pct_vs_thesis [%]": round(pct, 1),
            "within_tolerance [text]": "yes" if abs(pct) <= WIND_DRIFT_TOLERANCE_PCT else "no",
            "tolerance [%]": WIND_DRIFT_TOLERANCE_PCT,
            "du_V_over_sumD_thesis [mm]": round(du_thesis_method, 3),
            "du_pct_vs_V_over_sumD_thesis [%]": round(percent_difference(p.du_mm[i], du_thesis_method), 1),
            "sumD_redone [N/mm]": d_redone[i]["sum_D [N/mm]"],
            "du_V_over_sumD_redone [mm]": round(du_redone, 3),
            "du_pct_vs_V_over_sumD_redone [%]": round(percent_difference(p.du_mm[i], du_redone), 1),
            "K_model_V_over_du [N/mm]": round(p.column_shear_kn[i] * 1000.0 / p.du_mm[i], 0),
            "u_thesis [mm]": t.u_mm,
            "u_model [mm]": round(p.u_mm[i], 3),
            "u_pct_vs_thesis [%]": round(percent_difference(p.u_mm[i], t.u_mm), 1),
            "h_thesis [mm]": t.h_mm,
            "h_model [mm]": round(1000.0 * p.heights_m[i], 0),
            "theta_thesis_printed [-]": t.theta,
            "theta_model [-]": round(p.theta[i], 7),
            "theta_limit [-]": round(DRIFT_LIMIT, 7),
            "theta_model_over_limit [-]": round(p.theta[i] / DRIFT_LIMIT, 4),
            "drift_limit_met [text]": "yes" if p.theta[i] <= DRIFT_LIMIT else "no",
        }
        for name, res in results.items():
            if name != "primary":
                row[f"du_pct_{name}_vs_thesis [%]"] = round(percent_difference(res.du_mm[i], t.du_mm), 1)
        row["thesis_flag [text]"] = t.flag
        rows.append(row)
    return rows


def runs_rows(results: dict[str, WindResult]) -> list[dict]:
    """Build the per-run summary of ``results/anchor_wind_runs.csv``.

    Args:
        results: Wind runs keyed by variant.

    Returns:
        One dict per run with its settings, equilibrium totals, roof
        displacement and largest drift ratio.
    """
    rows = []
    for name, res in results.items():
        kw = WIND_VARIANTS.get(name, {})
        rows.append({
            "variant [text]": name,
            "axially_rigid_columns [text]": str(kw.get("axially_rigid_columns", False)),
            "rigid_floor [text]": str(kw.get("rigid_floor", False)),
            "storey_heights [m]": " ".join(f"{h:g}" for h in res.heights_m),
            "applied_horizontal_load [kN]": round(res.applied_kn, 2),
            "base_shear_reaction [kN]": round(-res.base_shear_kn, 2),
            "roof_displacement [mm]": round(res.u_mm[-1], 3),
            "max_theta [-]": round(max(res.theta), 7),
            "max_theta_over_limit [-]": round(max(res.theta) / DRIFT_LIMIT, 4),
        })
    return rows


def main(repo_root: Path | None = None) -> dict[str, list[dict]]:
    """Run every wind variant, compare with Table 8-2 and save the tables.

    Writes to ``results/``: ``anchor_wind.csv`` (storey comparison),
    ``anchor_wind_runs.csv`` (one row per run), ``anchor_wind_d_values.csv``
    (D-value method redone with the model's stiffnesses) and
    ``thesis_table_8_2_forces_check.csv`` (W_k against the Table 8-1 inputs).

    Args:
        repo_root: Repository root; defaults to two levels above this file's
            package folder.

    Returns:
        The rows written, keyed ``"wind"``, ``"runs"``, ``"d_values"`` and
        ``"forces"``.
    """
    root = repo_root or Path(__file__).resolve().parents[2]
    out = root / "results"
    thesis = read_thesis_wind(root)
    forces = [t.w_kn for t in thesis]
    results = {name: run_wind(forces, variant=name, **kw) for name, kw in WIND_VARIANTS.items()}
    d_redone = d_value_method()
    tables = {
        "wind": comparison_rows(results, thesis, d_redone),
        "runs": runs_rows(results),
        "d_values": d_redone,
        "forces": wind_force_check_rows(thesis),
    }
    af.write_csv(tables["wind"], out / "anchor_wind.csv")
    af.write_csv(tables["runs"], out / "anchor_wind_runs.csv")
    af.write_csv(tables["d_values"], out / "anchor_wind_d_values.csv")
    af.write_csv(tables["forces"], out / "thesis_table_8_2_forces_check.csv")
    return tables


if __name__ == "__main__":
    for r in main()["wind"]:
        print(f"level {r['level [text]']}: du thesis {r['du_thesis [mm]']:.2f} mm, "
              f"model {r['du_model [mm]']:.3f} mm ({r['du_pct_vs_thesis [%]']:+.1f} %, "
              f"within {r['tolerance [%]']:.0f} %: {r['within_tolerance [text]']}); "
              f"theta {r['theta_model [-]']:.6f} vs 1/550: {r['drift_limit_met [text]']}")
