"""GB 50011 base-shear method on the anchor frame, compared with thesis Table 8-12.

File: src/shellbench/seismic.py

What this module does
---------------------
It implements the base-shear method (底部剪力法) of GB 50011-2010 for a
regular frame and applies it to the 2D frame on axis (2) of the author's
thesis building (``shellbench.anchor_frame``):

1. storey weights G_i from the thesis loads (cl. 5.1.3, Table 5.1.3);
2. the fundamental period T1 of the bare OpenSeesPy frame, an optional infill
   period factor psi_T, and a Rayleigh check of the eigenvalue;
3. the seismic influence coefficient alpha1 from the design spectrum
   (cl. 5.1.4, 5.1.5);
4. F_Ek = alpha1 G_eq with G_eq = 0.85 sum(G_i) (cl. 5.2.1);
5. storey forces F_i by G_i H_i with the top additional force delta_n F_Ek
   (cl. 5.2.1, Table 5.2.1);
6. the minimum shear check V_i >= lambda sum(G_j) (cl. 5.2.5) and the
   elastic drift limit 1/550 (cl. 5.5.1, spec S11).

The forces are applied to the frame and the storey forces, shears and drifts
are compared with Table 8-12 (Th §8.4), following the reading rules written
before the first run (docs/anchor_notes.md, "How the seismic comparison is
read", 27 Oct 2026).

Code values
-----------
Only the values the author confirmed, or that were read from the author's
English translation of GB 50011-2010 on 26 Oct 2026
(notes/gb50011_base_shear_primer.md, with page numbers), are used. They still
have to be checked against the Chinese 2016 copy. Values for other
intensities, damping ratios or site classes are deliberately not included:
the functions raise instead of guessing.

Units: kN, m, s inside OpenSees (mass in kN s^2/m = t); drifts reported in mm.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import openseespy.opensees as ops

from shellbench import anchor_frame as af
from shellbench import anchor_wind as aw

# ---------------------------------------------------------------------------
# Code values (GB 50011-2010; see the module docstring for their status)
# ---------------------------------------------------------------------------

#: Standard acceleration of gravity [m/s^2]. Conventional value of the 3rd
#: CGPM (1901), ISO 80000-3. Converts weight [kN] to mass [t].
G_ACCEL_M_S2: float = 9.80665

#: Maximum seismic influence coefficient for frequent earthquakes [-], keyed by
#: (intensity degree, design basic acceleration in g). GB 50011-2010 Table
#: 5.1.4-1; 7 degrees, 0.10 g confirmed by the author on 25 Oct 2026
#: (docs/anchor_notes.md, lateral-load decision 3). No other entry is confirmed.
ALPHA_MAX_FREQUENT: dict[tuple[int, float], float] = {(7, 0.10): 0.08}

#: Characteristic period of the anchor site [s]. Spec S4, decision B5 (site
#: class II, design group 1, GB 50011-2010 Table 5.1.4-2).
TG_ANCHOR_S: float = 0.35

#: Damping ratio for which the spectrum constants below hold [-].
#: GB 50011-2010 cl. 5.1.5 (pp. 30-31 of the translation).
DAMPING_RATIO: float = 0.05

#: Exponent of the curved descending branch [-], cl. 5.1.5, 5 % damping.
GAMMA: float = 0.9

#: Slope adjusting factor of the straight descending branch [-], cl. 5.1.5.
ETA1: float = 0.02

#: Damping adjusting factor [-], cl. 5.1.5, 5 % damping.
ETA2: float = 1.0

#: Period at which the rising branch ends [s]. GB 50011-2010 Fig. 5.1.5.
T_PLATEAU_START_S: float = 0.1

#: Ordinate of the spectrum at T = 0 as a fraction of alpha_max [-].
#: GB 50011-2010 Fig. 5.1.5.
ALPHA_AT_ZERO_FACTOR: float = 0.45

#: Longest period the design spectrum covers [s]. GB 50011-2010 Fig. 5.1.5.
T_SPECTRUM_END_S: float = 6.0

#: Factor from total representative gravity load to equivalent load for
#: multi-mass systems [-]. GB 50011-2010 cl. 5.2.1, formula 5.2.1-1.
GEQ_FACTOR: float = 0.85

#: Combination coefficient for floor live load treated as an equivalent
#: uniform load in civil buildings other than libraries and archives [-].
#: GB 50011-2010 Table 5.1.3 (p. 29). Office floor, so 0.5 [J].
LIVE_COMBINATION_COEFF_FLOOR: float = 0.5

#: Combination coefficient for roof live load [-]. Table 5.1.3: "not
#: considered".
LIVE_COMBINATION_COEFF_ROOF: float = 0.0

#: Minimum seismic shear coefficient lambda for 7 degrees, 0.10 g, structures
#: with T1 < 3.5 s [-]. GB 50011-2010 cl. 5.2.5, Table 5.2.5 (p. 36).
LAMBDA_MIN_7_010_SHORT: float = 0.016

#: Period below which ``LAMBDA_MIN_7_010_SHORT`` applies [s]. Table 5.2.5.
LAMBDA_SHORT_PERIOD_LIMIT_S: float = 3.5

#: Elastic drift limit for RC frames [-]. Spec S11 (GB 50011-2010 Table 5.5.1).
DRIFT_LIMIT: float = aw.DRIFT_LIMIT

# ---------------------------------------------------------------------------
# Thesis values and decisions
# ---------------------------------------------------------------------------

#: Level-5 force of Table 8-12 [kN] (98.29), the row judged spurious (B4).
#: Lateral-load decision 2: not applied, and subtracted from the printed shears
#: to give the four-storey shears the comparison uses.
THESIS_LEVEL5_FORCE_KN: float = 98.29

#: Trial infill period factors reported as a sensitivity only (reading rule
#: 4). Trial values spanning the range the primer cites from JGJ 3-2010
#: cl. 4.3.17 [?]; not code values. The primary run uses 1.0 until the author
#: decides.
PSI_T_TRIALS: tuple[float, ...] = (0.9, 0.8, 0.7, 0.6)

#: Infill period factor for the anchor building [-]. JGJ 3-2010 cl. 4.3.17
#: gives 0.6-0.7 for frame structures with infill walls [?]: the clause was not
#: opened; the range is as cited by Zhou (2024), "框架结构计算中对周期折减系数
#: 合理取值的研究", 建筑监督检测与造价 (9). JGJ 3 covers high-rise buildings, so
#: using it for a four-storey frame is a borrowed practice rule [J]. 0.7, the
#: smaller reduction, chosen by Claude on 27 Oct 2026 at the author's request,
#: after the Day 9 run and not from the sensitivity table (0.8 would match the
#: thesis best) [J]. The bare-frame runs (psi_T = 1.0) stay as the method
#: comparison; downstream days (design checks, carbon) use this value.
ANCHOR_PSI_T: float = 0.7

# ---------------------------------------------------------------------------
# Code functions
# ---------------------------------------------------------------------------


def alpha_max_frequent(intensity: int, pga_g: float) -> float:
    """Return alpha_max for frequent earthquakes (GB 50011-2010 Table 5.1.4-1).

    Args:
        intensity: Seismic fortification intensity [degree].
        pga_g: Design basic acceleration of ground motion [g].

    Returns:
        alpha_max [-].

    Raises:
        KeyError: If the entry has not been confirmed from the code.
    """
    key = (intensity, round(pga_g, 3))
    if key not in ALPHA_MAX_FREQUENT:
        raise KeyError(f"alpha_max for {key} not confirmed from Table 5.1.4-1")
    return ALPHA_MAX_FREQUENT[key]


def alpha_spectrum(period_s: float, alpha_max: float, tg_s: float,
                   damping_ratio: float = DAMPING_RATIO) -> float:
    """Return the seismic influence coefficient alpha (GB 50011-2010 cl. 5.1.5).

    Four branches of Fig. 5.1.5: a straight rise from 0.45 alpha_max at T = 0
    to eta2 alpha_max at 0.1 s; a plateau to Tg; a curved fall
    (Tg/T)^gamma eta2 alpha_max to 5 Tg; a straight fall
    [eta2 0.2^gamma - eta1 (T - 5 Tg)] alpha_max to 6.0 s.

    Args:
        period_s: Structural period T [s], 0 <= T <= 6.0.
        alpha_max: Maximum influence coefficient [-] (Table 5.1.4-1).
        tg_s: Characteristic period [s] (Table 5.1.4-2).
        damping_ratio: Must be 0.05; other ratios need formulas 5.1.5-1 to
            5.1.5-3, which are not confirmed here.

    Returns:
        alpha [-].

    Raises:
        ValueError: For a damping ratio other than 0.05 or T outside 0-6 s.
    """
    if abs(damping_ratio - DAMPING_RATIO) > 1e-12:
        raise ValueError("only 5 % damping is implemented (cl. 5.1.5)")
    t = period_s
    if t < 0.0 or t > T_SPECTRUM_END_S:
        raise ValueError(f"T = {t} s is outside the 0-6 s design spectrum")
    if t < T_PLATEAU_START_S:
        return (ALPHA_AT_ZERO_FACTOR + (ETA2 - ALPHA_AT_ZERO_FACTOR) * t / T_PLATEAU_START_S) * alpha_max
    if t <= tg_s:
        return ETA2 * alpha_max
    if t <= 5.0 * tg_s:
        return (tg_s / t) ** GAMMA * ETA2 * alpha_max
    return (ETA2 * 0.2 ** GAMMA - ETA1 * (t - 5.0 * tg_s)) * alpha_max


def period_for_alpha(alpha: float, alpha_max: float, tg_s: float) -> float | None:
    """Return the period on the descending branches that gives a target alpha.

    Used only for the implied-period diagnostic (reading rule 5).

    Args:
        alpha: Target influence coefficient [-].
        alpha_max: Maximum influence coefficient [-].
        tg_s: Characteristic period [s].

    Returns:
        The period [s] in (Tg, 6.0] with alpha_spectrum = alpha, or None if
        alpha lies outside the range of the descending branches.
    """
    lo, hi = tg_s, T_SPECTRUM_END_S
    if not alpha_spectrum(hi, alpha_max, tg_s) <= alpha <= alpha_spectrum(lo, alpha_max, tg_s):
        return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if alpha_spectrum(mid, alpha_max, tg_s) > alpha:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def top_additional_factor(period_s: float, tg_s: float) -> float:
    """Return delta_n for multi-storey RC and steel buildings (GB 50011-2010 Table 5.2.1).

    Args:
        period_s: Fundamental period T1 [s].
        tg_s: Characteristic period [s].

    Returns:
        delta_n [-]: 0 when T1 <= 1.4 Tg; otherwise 0.08 T1 + 0.07
        (Tg <= 0.35 s), 0.08 T1 + 0.01 (0.35 < Tg <= 0.55 s) or
        0.08 T1 - 0.02 (Tg > 0.55 s).
    """
    # The 1e-12 s guard keeps T1 = 1.4 Tg on the "no top force" side despite
    # floating-point rounding (1.4 x 0.35 = 0.48999...).
    if period_s <= 1.4 * tg_s + 1e-12:
        return 0.0
    if tg_s <= 0.35:
        return 0.08 * period_s + 0.07
    if tg_s <= 0.55:
        return 0.08 * period_s + 0.01
    return 0.08 * period_s - 0.02


def minimum_shear_coefficient(period_s: float) -> float:
    """Return lambda for 7 degrees, 0.10 g (GB 50011-2010 cl. 5.2.5, Table 5.2.5).

    Args:
        period_s: Fundamental period T1 [s].

    Returns:
        lambda [-].

    Raises:
        ValueError: For T1 >= 3.5 s, where the long-period value and the
            interpolation are not implemented.
    """
    if period_s >= LAMBDA_SHORT_PERIOD_LIMIT_S:
        raise ValueError("lambda for T1 >= 3.5 s is not implemented")
    return LAMBDA_MIN_7_010_SHORT


def storey_forces(weights_kn: list[float], heights_m: list[float], base_shear_kn: float,
                  delta_n: float) -> list[float]:
    """Distribute the base shear over the height (GB 50011-2010 cl. 5.2.1).

    F_i = G_i H_i / sum(G_j H_j) F_Ek (1 - delta_n), plus
    Delta F_n = delta_n F_Ek added at the top level (formulas 5.2.1-2, 5.2.1-3).

    Args:
        weights_kn: Representative gravity loads G_i, level 1 first [kN].
        heights_m: Height H_i of each level above the base [m].
        base_shear_kn: F_Ek [kN].
        delta_n: Top additional factor [-] (Table 5.2.1).

    Returns:
        Storey forces F_i [kN], level 1 first, including Delta F_n at the top.
    """
    gh = [g * h for g, h in zip(weights_kn, heights_m)]
    forces = [base_shear_kn * (1.0 - delta_n) * x / sum(gh) for x in gh]
    forces[-1] += delta_n * base_shear_kn
    return forces


# ---------------------------------------------------------------------------
# Storey weights from the thesis loads
# ---------------------------------------------------------------------------


def beam_line_load_total(load_model: af.LoadModel, kind: str) -> float:
    """Return the total beam line load of one level of the frame [kN].

    Integrates each span's load with the same mid-point rule as
    ``anchor_frame.apply_gravity_case``, so the weights match what the frame
    carries.

    Args:
        load_model: Beam line-load description.
        kind: ``"roof"`` or ``"floor"``.

    Returns:
        Sum over spans AB, BC, CD of the integrated line load [kN].
    """
    total = 0.0
    for span, length in zip(af.SPAN_LABELS, af.SPANS_M):
        beam = load_model.beams[(kind, "mid" if span == "BC" else "side")]
        n_sub = round(length * af.BEAM_SUBELEMENTS_PER_M)
        seg = length / n_sub
        total += sum(beam.intensity((k + 0.5) * seg, length) * seg for k in range(n_sub))
    return total


def joint_load_total(joint_loads: dict[tuple[str, str], float], kind: str) -> float:
    """Return the sum of the four concentrated joint loads of one level [kN].

    Args:
        joint_loads: Joint loads keyed as ``anchor_frame.JOINT_LOADS_KN``.
        kind: ``"roof"`` or ``"floor"``.

    Returns:
        2 x exterior + 2 x interior joint load [kN].
    """
    return 2.0 * joint_loads[("exterior", kind)] + 2.0 * joint_loads[("interior", kind)]


@dataclass
class StoreyWeight:
    """Representative gravity load of one level (GB 50011-2010 cl. 5.1.3).

    Attributes:
        level: Level number, 1 = first floor.
        dead_kn: Dead load lumped at the level, column halves included [kN].
        live_kn: Full live load on the level [kN].
        live_coeff: Combination coefficient applied to the live load [-].
        g_kn: G_i = dead + coefficient x live [kN].
    """

    level: int
    dead_kn: float
    live_kn: float
    live_coeff: float
    g_kn: float


def storey_weights(dead_model: str = "actual_shape", live_model: str = "actual_shape",
                   storey_heights_m: tuple[float, ...] | None = None) -> list[StoreyWeight]:
    """Return G_i for each level of the anchor frame (reading rule 2).

    Dead: beam line loads + joint loads of the level + half the column
    self-weight of the storeys above and below (the lower half of the ground
    storey goes to the foundation). Live: beam line loads + joint loads,
    times 0.5 on floors and 0 at the roof (Table 5.1.3).

    Args:
        dead_model: Key of ``anchor_frame.LOAD_MODELS``.
        live_model: Key of ``anchor_frame.LIVE_LOAD_MODELS``.
        storey_heights_m: Storey heights [m]; defaults to the model's.

    Returns:
        One StoreyWeight per level, level 1 first.
    """
    heights = tuple(storey_heights_m or af.STOREY_HEIGHTS_M)
    n = len(heights)
    col_w = af.COLUMN_SELF_WEIGHT_KN_M * len(af.AXES)
    out = []
    for lvl in range(1, n + 1):
        kind = "roof" if lvl == n else "floor"
        dead = (beam_line_load_total(af.LOAD_MODELS[dead_model], kind)
                + joint_load_total(af.JOINT_LOADS_KN, kind)
                + col_w * heights[lvl - 1] / 2.0
                + (col_w * heights[lvl] / 2.0 if lvl < n else 0.0))
        live = (beam_line_load_total(af.LIVE_LOAD_MODELS[live_model], kind)
                + joint_load_total(af.LIVE_JOINT_LOADS_KN, kind))
        coeff = LIVE_COMBINATION_COEFF_ROOF if kind == "roof" else LIVE_COMBINATION_COEFF_FLOOR
        out.append(StoreyWeight(lvl, dead, live, coeff, dead + coeff * live))
    return out


# ---------------------------------------------------------------------------
# Period
# ---------------------------------------------------------------------------


def assign_level_masses(fm: af.FrameModel, weights_kn: list[float]) -> None:
    """Lump G_i / g as horizontal mass, split equally over the four column-line nodes.

    Args:
        fm: The frame returned by ``anchor_frame.build_frame``.
        weights_kn: G_i, level 1 first [kN].
    """
    for lvl, g in enumerate(weights_kn, start=1):
        m = g / G_ACCEL_M_S2 / len(af.AXES)
        for ax in af.AXES:
            ops.mass(fm.node[(ax, lvl)], m, 0.0, 0.0)


def modal_periods(weights_kn: list[float], n_modes: int = 1,
                  storey_heights_m: tuple[float, ...] | None = None) -> list[float]:
    """Return the first periods of the bare frame with lumped horizontal masses [s].

    Args:
        weights_kn: G_i, level 1 first [kN].
        n_modes: Number of modes (at most the number of levels).
        storey_heights_m: Storey heights [m]; defaults to the model's.

    Returns:
        Periods T_1..T_n [s], longest first.
    """
    fm = af.build_frame(storey_heights_m=storey_heights_m)
    assign_level_masses(fm, weights_kn)
    eig = ops.eigen(n_modes)
    ops.wipe()
    return [2.0 * math.pi / math.sqrt(lam) for lam in eig]


@dataclass
class LateralResult:
    """Output of one static lateral run.

    Attributes:
        u_mm: Mean horizontal displacement of each level [mm].
        du_mm: Inter-storey drift [mm].
        theta: Δu / h [-].
        column_shear_kn: Sum of column shears in each storey [kN].
        base_shear_kn: Sum of horizontal base reactions [kN] (opposite sign).
    """

    u_mm: list[float]
    du_mm: list[float]
    theta: list[float]
    column_shear_kn: list[float]
    base_shear_kn: float


def run_lateral(forces_kn: list[float],
                storey_heights_m: tuple[float, ...] | None = None) -> LateralResult:
    """Apply storey forces at the axis-A nodes and solve the bare frame.

    Uses ``anchor_wind.run_wind``, so wind and earthquake share one solver and
    one way of reading displacements and shears (reading rule 7).

    Args:
        forces_kn: Horizontal force at each level, level 1 first [kN].
        storey_heights_m: Storey heights [m]; defaults to the model's.

    Returns:
        A LateralResult.
    """
    w = aw.run_wind(forces_kn, storey_heights_m=storey_heights_m, variant="seismic")
    return LateralResult(w.u_mm, w.du_mm, w.theta, w.column_shear_kn, w.base_shear_kn)


def rayleigh_period(weights_kn: list[float]) -> float:
    """Return the Rayleigh period from the static deflection under lateral forces G_i [s].

    T = 2 pi sqrt( sum G_i u_i^2 / (g sum G_i u_i) ), a check of the
    eigenvalue (reading rule 3), not a code method.

    Args:
        weights_kn: G_i, level 1 first [kN].

    Returns:
        Period [s].
    """
    res = run_lateral(weights_kn)
    u = [x / 1000.0 for x in res.u_mm]
    num = sum(g * x * x for g, x in zip(weights_kn, u))
    den = sum(g * x for g, x in zip(weights_kn, u))
    return 2.0 * math.pi * math.sqrt(num / (G_ACCEL_M_S2 * den))


# ---------------------------------------------------------------------------
# The base-shear method run
# ---------------------------------------------------------------------------


@dataclass
class SeismicResult:
    """Output of one base-shear-method run on the anchor frame.

    Attributes:
        variant: Name of the run.
        weights: Storey weights.
        t1_bare_s: First-mode period of the bare frame [s].
        psi_t: Infill period factor applied [-].
        t1_s: Period used for alpha1, psi_t x t1_bare_s [s].
        alpha1: Seismic influence coefficient [-].
        g_eq_kn: Equivalent gravity load [kN].
        f_ek_kn: Base shear F_Ek [kN].
        delta_n: Top additional factor [-].
        forces_kn: Storey forces F_i, Delta F_n included [kN].
        shears_kn: Storey shears from the forces [kN].
        lam: Minimum shear coefficient [-].
        lateral: Static response of the frame to ``forces_kn``.
    """

    variant: str
    weights: list[StoreyWeight]
    t1_bare_s: float
    psi_t: float
    t1_s: float
    alpha1: float
    g_eq_kn: float
    f_ek_kn: float
    delta_n: float
    forces_kn: list[float]
    shears_kn: list[float]
    lam: float
    lateral: LateralResult


def run_base_shear(dead_model: str = "actual_shape", live_model: str = "actual_shape",
                   psi_t: float = 1.0, variant: str = "primary") -> SeismicResult:
    """Run the GB 50011 base-shear method on the anchor frame (cl. 5.1.3-5.2.5).

    Args:
        dead_model: Key of ``anchor_frame.LOAD_MODELS`` for the weights.
        live_model: Key of ``anchor_frame.LIVE_LOAD_MODELS`` for the weights.
        psi_t: Infill period factor on the bare-frame period [-]; 1.0 is the
            bare frame (reading rule 4).
        variant: Name of the run.

    Returns:
        A SeismicResult.
    """
    weights = storey_weights(dead_model, live_model)
    g = [w.g_kn for w in weights]
    t_bare = modal_periods(g, 1)[0]
    t1 = psi_t * t_bare
    a_max = alpha_max_frequent(7, 0.10)
    alpha1 = alpha_spectrum(t1, a_max, TG_ANCHOR_S)
    g_eq = GEQ_FACTOR * sum(g)
    f_ek = alpha1 * g_eq
    d_n = top_additional_factor(t1, TG_ANCHOR_S)
    heights = af.level_y_coordinates()[1:]
    forces = storey_forces(g, heights, f_ek, d_n)
    shears = [sum(forces[i:]) for i in range(len(forces))]
    return SeismicResult(variant, weights, t_bare, psi_t, t1, alpha1, g_eq, f_ek, d_n,
                         forces, shears, minimum_shear_coefficient(t1), run_lateral(forces))


#: The runs reported. ``primary`` is the comparison run (reading rules 2 and
#: 4); each other run changes one thing.
SEISMIC_VARIANTS: dict[str, dict] = {
    "primary": {},
    "thesis_shear_weights": {"dead_model": "thesis_text", "live_model": "thesis_shear"},
    **{f"psi_t_{p:.1f}": {"psi_t": p} for p in PSI_T_TRIALS},
}

# ---------------------------------------------------------------------------
# Thesis comparison and output
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ThesisSeismicRow:
    """One level of thesis Table 8-12 as typed on Day 3.

    Attributes:
        level: Level number.
        v_kn: Printed storey shear V_i [kN].
        sum_d_n_mm: Printed sum of D-values [N/mm].
        du_mm: Printed inter-storey drift [mm].
        h_mm: Printed storey height [mm].
    """

    level: int
    v_kn: float
    sum_d_n_mm: float
    du_mm: float
    h_mm: float


def read_thesis_seismic(repo_root: Path) -> list[ThesisSeismicRow]:
    """Read Table 8-12 from ``validation/thesis_values/seismic_storey_shear_drift.csv``.

    Args:
        repo_root: Repository root.

    Returns:
        All five printed rows, level 1 first (level 5 is the spurious row, B4).
    """
    path = repo_root / "validation" / "thesis_values" / "seismic_storey_shear_drift.csv"
    with path.open(newline="", encoding="utf-8") as f:
        return [ThesisSeismicRow(int(r["level [text]"]), float(r["V [kN]"]),
                                 float(r["sum_D [N/mm]"]), float(r["du [mm]"]),
                                 float(r["h [mm]"]))
                for r in csv.DictReader(f)]


def thesis_storey_forces(thesis: list[ThesisSeismicRow]) -> list[float]:
    """Return F_i = V_i - V_(i+1) of Table 8-12 for levels 1-4 [kN] (decision 2).

    Args:
        thesis: Rows from ``read_thesis_seismic``.

    Returns:
        Four storey forces, level 1 first.
    """
    v = [t.v_kn for t in thesis]
    return [v[i] - v[i + 1] for i in range(4)]


def percent_difference(model: float, reference: float) -> float:
    """Return (model - reference) / |reference| x 100.

    Args:
        model: Model value.
        reference: Reference value (non-zero).

    Returns:
        Percentage difference.
    """
    return (model - reference) / abs(reference) * 100.0


def comparison_rows(res: SeismicResult, thesis: list[ThesisSeismicRow],
                    thesis_force_run: LateralResult) -> list[dict]:
    """Build ``results/anchor_seismic.csv``: levels 1-4 next to Table 8-12.

    Args:
        res: The primary base-shear run.
        thesis: Rows from ``read_thesis_seismic``.
        thesis_force_run: The frame's response to the thesis F_1-F_4.

    Returns:
        One dict per level.
    """
    f_thesis = thesis_storey_forces(thesis)
    rows = []
    for i in range(4):
        t = thesis[i]
        v4 = t.v_kn - THESIS_LEVEL5_FORCE_KN
        du_vd = v4 * 1000.0 / t.sum_d_n_mm
        lam_req = res.lam * sum(w.g_kn for w in res.weights[i:])
        rows.append({
            "level [text]": t.level,
            "G_i [kN]": round(res.weights[i].g_kn, 2),
            "H_i [m]": round(af.level_y_coordinates()[i + 1], 3),
            "F_model [kN]": round(res.forces_kn[i], 2),
            "F_thesis [kN]": round(f_thesis[i], 2),
            "F_pct_vs_thesis [%]": round(percent_difference(res.forces_kn[i], f_thesis[i]), 1),
            "V_model [kN]": round(res.shears_kn[i], 2),
            "V_model_columns [kN]": round(res.lateral.column_shear_kn[i], 2),
            "V_thesis_4storey [kN]": round(v4, 2),
            "V_pct_vs_thesis_4storey [%]": round(percent_difference(res.shears_kn[i], v4), 1),
            "V_thesis_printed [kN]": t.v_kn,
            "lambda_sum_G [kN]": round(lam_req, 2),
            "min_shear_met [text]": str(res.shears_kn[i] >= lam_req),
            "du_model [mm]": round(res.lateral.du_mm[i], 3),
            "du_thesis_printed [mm]": t.du_mm,
            "du_pct_vs_thesis_printed [%]": round(percent_difference(res.lateral.du_mm[i], t.du_mm), 1),
            "du_thesis_V4_over_sumD [mm]": round(du_vd, 3),
            "du_pct_vs_V4_over_sumD [%]": round(percent_difference(res.lateral.du_mm[i], du_vd), 1),
            "du_model_thesis_forces [mm]": round(thesis_force_run.du_mm[i], 3),
            "du_thesis_forces_pct_vs_V4_over_sumD [%]": round(
                percent_difference(thesis_force_run.du_mm[i], du_vd), 1),
            "theta_model [-]": round(res.lateral.theta[i], 7),
            "drift_limit_met [text]": str(res.lateral.theta[i] <= DRIFT_LIMIT),
        })
    return rows


def runs_rows(results: dict[str, SeismicResult], thesis: list[ThesisSeismicRow]) -> list[dict]:
    """Build ``results/anchor_seismic_runs.csv``: one row per run.

    Includes the implied-period diagnostic (reading rule 5): the period at
    which the spectrum gives the thesis four-storey base shear with this
    run's G_eq. It is never used to choose psi_T.

    Args:
        results: Runs keyed by variant.
        thesis: Rows from ``read_thesis_seismic``.

    Returns:
        One dict per run.
    """
    v1 = thesis[0].v_kn - THESIS_LEVEL5_FORCE_KN
    a_max = alpha_max_frequent(7, 0.10)
    rows = []
    for name, r in results.items():
        t_imp = period_for_alpha(v1 / r.g_eq_kn, a_max, TG_ANCHOR_S)
        rows.append({
            "variant [text]": name,
            "weights [text]": " / ".join(f"{k}" for k in (
                SEISMIC_VARIANTS.get(name, {}).get("dead_model", "actual_shape"),
                SEISMIC_VARIANTS.get(name, {}).get("live_model", "actual_shape"))),
            "sum_G [kN]": round(sum(w.g_kn for w in r.weights), 2),
            "G_eq [kN]": round(r.g_eq_kn, 2),
            "T1_bare [s]": round(r.t1_bare_s, 4),
            "psi_T [-]": r.psi_t,
            "T1_used [s]": round(r.t1_s, 4),
            "alpha1 [-]": round(r.alpha1, 5),
            "delta_n [-]": round(r.delta_n, 4),
            "F_Ek [kN]": round(r.f_ek_kn, 2),
            "F_Ek_pct_vs_thesis_4storey [%]": round(percent_difference(r.f_ek_kn, v1), 1),
            "base_shear_reaction [kN]": round(-r.lateral.base_shear_kn, 2),
            "roof_displacement [mm]": round(r.lateral.u_mm[-1], 3),
            "max_theta [-]": round(max(r.lateral.theta), 7),
            "max_theta_over_limit [-]": round(max(r.lateral.theta) / DRIFT_LIMIT, 4),
            "base_shear_over_lambda_sum_G [-]": round(r.f_ek_kn / (r.lam * sum(w.g_kn for w in r.weights)), 3),
            "T_implied_by_thesis_V [s]": "" if t_imp is None else round(t_imp, 4),
        })
    return rows


def weight_rows(results: dict[str, SeismicResult]) -> list[dict]:
    """Build ``results/anchor_seismic_weights.csv``: G_i for each weight model.

    Args:
        results: Runs keyed by variant (only distinct weight models are kept).

    Returns:
        One dict per (weight model, level).
    """
    rows = []
    for name in ("primary", "thesis_shear_weights"):
        for w in results[name].weights:
            rows.append({
                "variant [text]": name,
                "level [text]": w.level,
                "dead [kN]": round(w.dead_kn, 2),
                "live_full [kN]": round(w.live_kn, 2),
                "live_coeff [-]": w.live_coeff,
                "G_i [kN]": round(w.g_kn, 2),
            })
    return rows


def main(repo_root: Path | None = None) -> dict[str, list[dict]]:
    """Run every seismic variant, compare with Table 8-12 and save the tables.

    Writes to ``results/``: ``anchor_seismic.csv`` (levels 1-4, primary run),
    ``anchor_seismic_runs.csv`` (one row per run, with T1, alpha1, F_Ek and
    the implied-period diagnostic), ``anchor_seismic_weights.csv`` (G_i) and
    ``anchor_seismic_period_check.csv`` (eigenvalue against Rayleigh).

    Args:
        repo_root: Repository root; defaults to two levels above this file's
            package folder.

    Returns:
        The rows written, keyed ``"seismic"``, ``"runs"``, ``"weights"`` and
        ``"period"``.
    """
    root = repo_root or Path(__file__).resolve().parents[2]
    out = root / "results"
    thesis = read_thesis_seismic(root)
    results = {name: run_base_shear(variant=name, **kw) for name, kw in SEISMIC_VARIANTS.items()}
    thesis_run = run_lateral(thesis_storey_forces(thesis))
    g = [w.g_kn for w in results["primary"].weights]
    periods = modal_periods(g, len(g))
    period_rows = [{"mode [text]": i + 1, "T_eigen [s]": round(t, 4)} for i, t in enumerate(periods)]
    period_rows.append({"mode [text]": "rayleigh_1", "T_eigen [s]": round(rayleigh_period(g), 4)})
    tables = {
        "seismic": comparison_rows(results["primary"], thesis, thesis_run),
        "runs": runs_rows(results, thesis),
        "weights": weight_rows(results),
        "period": period_rows,
    }
    af.write_csv(tables["seismic"], out / "anchor_seismic.csv")
    af.write_csv(tables["runs"], out / "anchor_seismic_runs.csv")
    af.write_csv(tables["weights"], out / "anchor_seismic_weights.csv")
    af.write_csv(tables["period"], out / "anchor_seismic_period_check.csv")
    return tables


if __name__ == "__main__":
    t = main()
    for r in t["runs"]:
        print(r)
    for r in t["seismic"]:
        print(r)
