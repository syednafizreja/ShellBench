"""Capacity design, shear and detailing of the generator frame by seismic grade (R14).

File: src/shellbench/capacity.py

Playbook Day 20 (design_rules.md decision 5, 31 Oct 2026: shear and
strong-column checks before the family run [J]). The generator calls these
functions after R13. They are pure: section sizes, forces and the seismic
grade in, steel out, so each one can be checked by hand (tests/test_capacity.py).

Clauses (English editions; page = printed page):

* GB 50011-2010 cl. 6.2.2-6.2.5 (pp. 50-52): strong column (eta_c), base
  moment factor, beam shear (eta_vb), column shear (eta_vc).
* GB 50010-2010 cl. 6.2.3-6.2.5, 6.2.17 (pp. 33-43): second order, accidental
  eccentricity, eccentric compression.
* GB 50010-2010 cl. 6.3.1, 6.3.4, 6.6.3 (pp. 50-51, 72): beta_c, alpha_cv,
  volumetric stirrup ratio.
* GB 50010-2010 Chapter 11 (pp. 152-166): gamma_RE, beam and column
  section limits, shear capacity, minimum steel and confinement.

Checked by the AI assistant from the PDFs on 6 Nov 2026; author to confirm in the
printed copies.

Grade 1 frame structures must meet the capacity forms of cl. 6.2.2-6.2.5
(1.2 sum M_bua, 1.1 sum M_bua, 1.2 sum M_cua), which need the actual flexural
capacity with characteristic strengths. Here the eta values of the same
clauses are used instead [J] (limitation, design_rules.md R14).

Units: N and mm inside the section formulas; kN, kN m and m at the interface.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from shellbench import checks as c

GRADES: tuple[int, ...] = (1, 2, 3, 4)

# ---------------------------------------------------------------------------
# Force magnification, GB 50011-2010 (p. 50-52)
# ---------------------------------------------------------------------------

#: Column-end moment factor eta_c, frame structures, cl. 6.2.2 (p. 50). Grade 1
#: should use 1.2 sum M_bua (6.2.2-2); 1.7 is used instead [J].
ETA_C: dict[int, float] = {1: 1.7, 2: 1.5, 3: 1.3, 4: 1.2}
#: Factor on the lower-end moment of bottom-storey columns, cl. 6.2.3 (p. 51).
ETA_BASE: dict[int, float] = {1: 1.7, 2: 1.5, 3: 1.3, 4: 1.2}
#: Beam-end shear factor eta_vb, cl. 6.2.4 (p. 51). Grade 4 uses the combined
#: shear (GB 50010 cl. 11.3.2, p. 155), written here as None.
ETA_VB: dict[int, float | None] = {1: 1.3, 2: 1.2, 3: 1.1, 4: None}
#: Column shear factor eta_vc, frame structures, cl. 6.2.5 (p. 52).
ETA_VC: dict[int, float] = {1: 1.5, 2: 1.3, 3: 1.2, 4: 1.1}
#: Joints whose column axial ratio is below this are exempt from cl. 6.2.2 (p. 50).
STRONG_COLUMN_MIN_MU: float = 0.15

# ---------------------------------------------------------------------------
# Section values, GB 50010-2010
# ---------------------------------------------------------------------------

#: gamma_RE, Table 11.1.6 (p. 152): shear 0.85; eccentric compression 0.75
#: below axial ratio 0.15, else 0.80.
GAMMA_RE_SHEAR: float = 0.85
GAMMA_RE_COLUMN_LOW_MU: float = 0.75
GAMMA_RE_COLUMN: float = 0.80
#: Design strength of HPB300 stirrups [N/mm^2], Table 4.2.3-1 (p. 21).
FYV_N_MM2: float = 270.0
#: Concrete strength factor, C50 and below, cl. 6.3.1 (p. 50).
BETA_C: float = 1.0
#: Concrete shear factor of a general flexural member, cl. 6.3.4 (p. 51).
ALPHA_CV: float = 0.7
#: Beam section limit, cl. 11.3.3 (p. 155): 0.20 if l_n/h > 2.5, else 0.15.
#: Column section limit, cl. 11.4.6 (p. 160): 0.20 if lambda > 2, else 0.15.
SECTION_LIMIT_SLENDER: float = 0.20
SECTION_LIMIT_SQUAT: float = 0.15
BEAM_SLENDER_SPAN_DEPTH: float = 2.5
COLUMN_SLENDER_LAMBDA: float = 2.0
#: Beam shear capacity, cl. 11.3.4 (p. 156): 0.6 alpha_cv f_t b h0 + f_yv A_sv/s h0.
BEAM_CONCRETE_SHEAR_FACTOR: float = 0.6
#: Column shear capacity, cl. 11.4.7 (p. 161): 1.05/(lambda+1) f_t b h0
#: + f_yv A_sv/s h0 + 0.056 N, lambda in [1, 3], N <= 0.3 f_c A.
COLUMN_CONCRETE_SHEAR_FACTOR: float = 1.05
COLUMN_AXIAL_SHEAR_FACTOR: float = 0.056
COLUMN_LAMBDA_RANGE: tuple[float, float] = (1.0, 3.0)
COLUMN_N_SHEAR_CAP: float = 0.3

#: Minimum total steel of a frame column of a frame structure [-], Table
#: 11.4.12-1 (p. 163), plus 0.05 % for 400 MPa bars (note 1).
COLUMN_RHO_MIN: dict[int, float] = {1: 0.010, 2: 0.008, 3: 0.007, 4: 0.006}
COLUMN_RHO_400_ADD: float = 0.0005
#: Largest total column steel ratio [-], cl. 11.4.13 (p. 164).
COLUMN_RHO_MAX: float = 0.05
#: Column steel above which the generator grows the column instead of the bars [J].
COLUMN_RHO_CAP: float = 0.03
#: Largest bar spacing of a column wider than 400 mm [mm], cl. 11.4.13 (p. 164).
COLUMN_BAR_SPACING_MM: float = 200.0
#: Smallest column side for grades 1-3 above two storeys, and for grade 4 [mm],
#: cl. 11.4.11 (p. 162).
COLUMN_MIN_MM: dict[int, int] = {1: 400, 2: 400, 3: 400, 4: 300}
#: Bars per column face at least 3 (4 corner + 4 side bars, the R12 layout) [J].
COLUMN_MIN_BARS_PER_SIDE: int = 3
#: Least clear spacing of column bars [mm], GB 50010 cl. 9.3.1 item 2 (PDF p. 123).
#: Checked by the AI assistant, author to confirm.
COLUMN_MIN_CLEAR_MM: float = 50.0

#: Accidental eccentricity, cl. 6.2.5 (p. 34): max(20 mm, h/30).
E_A_MIN_MM: float = 20.0
E_A_DIVISOR: float = 30.0
#: Second order may be ignored, cl. 6.2.3 (p. 33): M1/M2 <= 0.9, axial ratio
#: <= 0.9 and l_c/i <= 34 - 12 M1/M2.
SECOND_ORDER_RATIO_MAX: float = 0.9
SECOND_ORDER_MU_MAX: float = 0.9
SECOND_ORDER_A: float = 34.0
SECOND_ORDER_B: float = 12.0
#: Small-eccentricity factor of formula 6.2.17-8 (p. 43).
SMALL_ECC_FACTOR: float = 0.43

# ---------------------------------------------------------------------------
# Stirrups
# ---------------------------------------------------------------------------

#: Beam end confinement, Table 11.3.6-2 (p. 157): (zone length on h, spacing
#: multiplier on the smallest longitudinal bar, spacing cap [mm], least
#: diameter [mm]); zone >= 500 mm and spacing <= h/4.
BEAM_ZONE: dict[int, tuple[float, float, float, int]] = {
    1: (2.0, 6.0, 100.0, 10), 2: (1.5, 8.0, 100.0, 8), 3: (1.5, 8.0, 150.0, 8), 4: (1.5, 8.0, 150.0, 6)}
BEAM_ZONE_MIN_MM: float = 500.0
BEAM_ZONE_H_DIVISOR: float = 4.0
#: Least diameter rises by 2 mm when the end tension steel exceeds 2 % (Table 11.3.6-2 note).
BEAM_HEAVY_STEEL_RATIO: float = 0.02
BEAM_HEAVY_STEEL_ADD_MM: int = 2
#: Least stirrup ratio along the beam, rho_sv >= k f_t / f_yv, cl. 11.3.9 (p. 157).
BEAM_RHO_SV: dict[int, float] = {1: 0.30, 2: 0.28, 3: 0.26, 4: 0.26}
#: Outside the end zone the spacing may be twice the zone spacing, cl. 11.3.9.
OUTSIDE_SPACING_FACTOR: float = 2.0
#: Stirrup leg spacing in the end zone [mm], cl. 11.3.8 (beams) and 11.4.15
#: (columns): grade 1 200; grades 2-3 max(250, 20 d); grade 4 300.
LEG_SPACING_MM: dict[int, float] = {1: 200.0, 2: 250.0, 3: 250.0, 4: 300.0}
LEG_SPACING_D_FACTOR: dict[int, float] = {1: 0.0, 2: 20.0, 3: 20.0, 4: 0.0}

#: Column end confinement, Table 11.4.12-2 (p. 163): (spacing multiplier on the
#: smallest longitudinal bar, spacing cap [mm], least diameter [mm]).
COLUMN_ZONE: dict[int, tuple[float, float, int]] = {
    1: (6.0, 100.0, 10), 2: (8.0, 100.0, 8), 3: (8.0, 150.0, 8), 4: (8.0, 150.0, 6)}
#: At the bottom-storey column root: spacing 100 mm (grades 3, 4) and diameter
#: 8 mm (grade 4), Table 11.4.12-2.
COLUMN_ROOT_SPACING_MM: float = 100.0
COLUMN_ROOT_MIN_DIAMETER_MM: int = 8
#: Zone length, cl. 11.4.14 (p. 164): max(h, H_n/6, 500); root of the bottom storey >= H_n/3.
COLUMN_ZONE_MIN_MM: float = 500.0
COLUMN_ZONE_HN_DIVISOR: float = 6.0
COLUMN_ROOT_HN_DIVISOR: float = 3.0
#: Least stirrup characteristic value lambda_v, ordinary or compound hoops,
#: Table 11.4.17 (p. 165), by axial ratio.
LAMBDA_V_MU: tuple[float, ...] = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.05)
LAMBDA_V: dict[int, tuple[float, ...]] = {
    1: (0.10, 0.11, 0.13, 0.15, 0.17, 0.20, 0.23),
    2: (0.08, 0.09, 0.11, 0.13, 0.15, 0.17, 0.19, 0.22, 0.24),
    3: (0.06, 0.07, 0.09, 0.11, 0.13, 0.15, 0.17, 0.20, 0.22),
    4: (0.06, 0.07, 0.09, 0.11, 0.13, 0.15, 0.17, 0.20, 0.22)}
#: Least volumetric ratio in the zone, cl. 11.4.17 item 2 (p. 166).
COLUMN_RHO_V_MIN: dict[int, float] = {1: 0.008, 2: 0.006, 3: 0.004, 4: 0.004}
#: Outside the zone: rho_v >= half the zone value; spacing <= 10 d (grades 1-2)
#: or 15 d (grades 3-4), cl. 11.4.18 (p. 166).
COLUMN_OUTSIDE_RHO_V_FACTOR: float = 0.5
COLUMN_OUTSIDE_SPACING_D: dict[int, float] = {1: 10.0, 2: 10.0, 3: 15.0, 4: 15.0}

#: Stirrup diameters and spacings the generator chooses from [J] (R16).
STIRRUP_DIAMETERS_MM: tuple[int, ...] = (6, 8, 10, 12)
STIRRUP_SPACINGS_MM: tuple[int, ...] = (75, 100, 125, 150, 200)
#: Largest stirrup spacing tried anywhere [mm] [J]; GB 50010 cl. 9.2.9 not yet opened [?].
STIRRUP_SPACING_MAX_MM: float = 200.0
STEEL_DENSITY_KG_M3: float = 7850.0  # as generator.quantities


def check_grade(grade: int) -> None:
    """Raise ValueError unless ``grade`` is 1, 2, 3 or 4."""
    if grade not in GRADES:
        raise ValueError(f"seismic grade must be one of {GRADES}, not {grade!r}")


def bar_area(d_mm: float) -> float:
    """Area of one bar of diameter ``d_mm`` [mm^2]."""
    return math.pi * d_mm * d_mm / 4.0


# ---------------------------------------------------------------------------
# Columns: eccentric compression (GB 50010 cl. 6.2.17)
# ---------------------------------------------------------------------------


def gamma_re_column(mu: float) -> float:
    """gamma_RE of an eccentrically compressed column, Table 11.1.6 (p. 152)."""
    return GAMMA_RE_COLUMN_LOW_MU if mu < STRONG_COLUMN_MIN_MU else GAMMA_RE_COLUMN


def accidental_eccentricity_mm(h_mm: float) -> float:
    """e_a = max(20 mm, h/30), cl. 6.2.5 (p. 34)."""
    return max(E_A_MIN_MM, h_mm / E_A_DIVISOR)


def column_side_steel_mm2(n_kn: float, m_knm: float, b_mm: float, h_mm: float) -> float:
    """Steel on each face of a symmetric rectangular column [mm^2], cl. 6.2.17.

    ``n_kn`` and ``m_knm`` are design values, already times gamma_RE where it
    applies; compression positive. e_i = M/N + e_a, e = e_i + h/2 - a.

    * Large eccentricity (x = N/(alpha1 f_c b) <= xi_b h0):
      A_s = [N e - alpha1 f_c b x (h0 - x/2)] / [f_y (h0 - a')], formula 6.2.17-2;
      if x < 2a', moments are taken about the compression steel:
      A_s = N (e_i - h/2 + a') / [f_y (h0 - a')] (cl. 6.2.17 item 2, cl. 6.2.14).
    * Small eccentricity: xi from formula 6.2.17-8, then A_s from 6.2.17-7.
    * Tension (N <= 0): A_s = M/[f_y (h0 - a')] + |N|/(2 f_y) [J]; the frames
      of the family have no column in net tension, so this branch is a guard.

    Args:
        n_kn: Axial force [kN], compression positive.
        m_knm: Bending moment, magnitude used [kN m].
        b_mm: Width [mm].
        h_mm: Depth in the bending direction [mm].

    Returns:
        A_s = A_s' >= 0 [mm^2] (before minimum steel).
    """
    a = c.A_S_MM
    h0 = h_mm - a
    fc, fy = c.FC_N_MM2, c.FY_N_MM2
    n, m = n_kn * 1e3, abs(m_knm) * 1e6
    if n <= 0.0:
        return max(0.0, m / (fy * (h0 - a)) + abs(n) / (2.0 * fy))
    e_i = m / n + accidental_eccentricity_mm(h_mm)
    e = e_i + h_mm / 2.0 - a
    x = n / (c.ALPHA1 * fc * b_mm)
    xi_b = c.xi_b()
    if x <= xi_b * h0:
        if x < 2.0 * a:
            a_s = n * (e_i - h_mm / 2.0 + a) / (fy * (h0 - a))
        else:
            a_s = (n * e - c.ALPHA1 * fc * b_mm * x * (h0 - x / 2.0)) / (fy * (h0 - a))
        return max(0.0, a_s)
    k = c.ALPHA1 * fc * b_mm * h0
    xi = (n - xi_b * k) / ((n * e - SMALL_ECC_FACTOR * k * h0) / ((c.BETA1 - xi_b) * (h0 - a)) + k) + xi_b
    a_s = (n * e - xi * (1.0 - 0.5 * xi) * k * h0) / (fy * (h0 - a))
    return max(0.0, a_s)


def second_order_negligible(m_bottom: float, m_top: float, mu: float, length_m: float,
                            h_mm: float) -> bool:
    """True if cl. 6.2.3 (p. 33) lets the second-order effect be ignored.

    The end moments are member-end values in one rotational sense: the same
    sign means double curvature, so M1/M2 is negative. i = h/sqrt(12).
    """
    big, small = max(abs(m_bottom), abs(m_top)), min(abs(m_bottom), abs(m_top))
    if big == 0.0:
        return mu <= SECOND_ORDER_MU_MAX
    ratio = -math.copysign(small / big, m_bottom * m_top) if m_bottom * m_top != 0.0 else 0.0
    slender = length_m * 1000.0 / (h_mm / math.sqrt(12.0))
    return (ratio <= SECOND_ORDER_RATIO_MAX and mu <= SECOND_ORDER_MU_MAX
            and slender <= SECOND_ORDER_A - SECOND_ORDER_B * ratio)


@dataclass(frozen=True)
class ColumnBars:
    """Longitudinal bars of a square column.

    Attributes:
        side_req_mm2: Steel needed on each face [mm^2].
        total_min_mm2: Minimum total steel for the grade [mm^2].
        per_side: Bars on each face (corners counted on both faces).
        diameter_mm: Bar diameter [mm].
        label: Bar label such as ``"12C25"``.
        area_mm2: Area of all bars [mm^2].
        rho: area / h^2 [-].
    """

    side_req_mm2: float
    total_min_mm2: float
    per_side: int
    diameter_mm: int
    label: str
    area_mm2: float
    rho: float


def column_bars(h_mm: int, side_req_mm2: float, grade: int,
                diameters_mm: tuple[int, ...]) -> ColumnBars | None:
    """Choose the column bars: one diameter, equal bars on the four faces [J].

    Bars per face: enough for a spacing <= 200 mm when h > 400 mm (cl. 11.4.13),
    at least 3. Each face must carry ``side_req_mm2`` and 0.2 % of b h
    (cl. 11.4.12); the total must reach Table 11.4.12-1 + 0.05 %. The smallest
    diameter that meets all three is taken. If no diameter is enough, more
    bars per face are tried, one at a time, while the clear spacing stays
    >= 50 mm (cl. 9.3.1 item 2). None if no layout fits or the ratio passes
    5 % (cl. 11.4.13).
    """
    check_grade(grade)
    first = COLUMN_MIN_BARS_PER_SIDE
    if h_mm > 400:
        first = max(first, math.ceil((h_mm - 2.0 * c.A_S_MM) / COLUMN_BAR_SPACING_MM - 1e-9) + 1)
    gross = float(h_mm * h_mm)
    total_min = (COLUMN_RHO_MIN[grade] + COLUMN_RHO_400_ADD) * gross
    side_need = max(side_req_mm2, c.RHO_MIN_COLUMN_SIDE * gross)
    per_side = first
    while True:
        total = 4 * (per_side - 1)
        fits_any = False
        for d in diameters_mm:
            clear = (h_mm - 2.0 * c.A_S_MM) / (per_side - 1) - d
            if per_side > first and clear < COLUMN_MIN_CLEAR_MM:
                continue
            fits_any = True
            a1 = bar_area(d)
            if per_side * a1 >= side_need and total * a1 >= total_min:
                area = total * a1
                if area / gross > COLUMN_RHO_MAX:
                    return None
                return ColumnBars(side_req_mm2, total_min, per_side, d, f"{total}C{d}", area, area / gross)
        if not fits_any:
            return None
        per_side += 1


# ---------------------------------------------------------------------------
# Shear demand and capacity
# ---------------------------------------------------------------------------


def beam_shear_kn(grade: int, sum_end_moments_knm: float, clear_span_m: float,
                  v_gravity_kn: float, v_combined_kn: float) -> float:
    """Design shear at a beam end [kN], GB 50011 cl. 6.2.4 / GB 50010 cl. 11.3.2.

    Grades 1-3: eta_vb (M_l + M_r)/l_n + V_Gb (grade 1 with eta, [J]).
    Grade 4: the combined shear ``v_combined_kn``.
    """
    check_grade(grade)
    eta = ETA_VB[grade]
    if eta is None:
        return abs(v_combined_kn)
    return eta * abs(sum_end_moments_knm) / clear_span_m + abs(v_gravity_kn)


def column_shear_kn(grade: int, m_top_knm: float, m_bottom_knm: float, clear_height_m: float) -> float:
    """Design column shear [kN], eta_vc (M_t + M_b)/H_n, GB 50011 cl. 6.2.5."""
    check_grade(grade)
    return ETA_VC[grade] * (abs(m_top_knm) + abs(m_bottom_knm)) / clear_height_m


def section_limit_kn(b_mm: float, h_mm: float, slender: bool) -> float:
    """Largest seismic shear of a section [kN]: (1/gamma_RE) k beta_c f_c b h0.

    k = 0.20 for a slender member, 0.15 otherwise (cl. 11.3.3, 11.4.6).
    """
    k = SECTION_LIMIT_SLENDER if slender else SECTION_LIMIT_SQUAT
    return k * BETA_C * c.FC_N_MM2 * b_mm * (h_mm - c.A_S_MM) / GAMMA_RE_SHEAR / 1e3


def beam_asv_per_s(v_kn: float, b_mm: float, h_mm: float, seismic: bool = True) -> float:
    """Stirrup area per spacing A_sv/s [mm^2/mm] for a beam shear.

    Seismic (cl. 11.3.4): gamma_RE V <= 0.6 alpha_cv f_t b h0 + f_yv A_sv/s h0.
    Gravity (cl. 6.3.4): V <= alpha_cv f_t b h0 + f_yv A_sv/s h0.
    """
    h0 = h_mm - c.A_S_MM
    v = abs(v_kn) * 1e3
    if seismic:
        need = GAMMA_RE_SHEAR * v - BEAM_CONCRETE_SHEAR_FACTOR * ALPHA_CV * c.FT_N_MM2 * b_mm * h0
    else:
        need = v - ALPHA_CV * c.FT_N_MM2 * b_mm * h0
    return max(0.0, need / (FYV_N_MM2 * h0))


def column_lambda(clear_height_m: float, h_mm: float) -> float:
    """Shear span ratio lambda = H_n / (2 h0), allowed by cl. 11.4.6 (p. 160)."""
    return clear_height_m * 1000.0 / (2.0 * (h_mm - c.A_S_MM))


def column_asv_per_s(v_kn: float, n_kn: float, h_mm: float, clear_height_m: float) -> float:
    """Stirrup area per spacing in one direction A_sv/s [mm^2/mm], cl. 11.4.7.

    gamma_RE V <= 1.05/(lambda+1) f_t b h0 + f_yv A_sv/s h0 + 0.056 N, with
    lambda clamped to [1, 3] and 0 <= N <= 0.3 f_c A (square column, b = h).
    """
    h0 = h_mm - c.A_S_MM
    lam = min(max(column_lambda(clear_height_m, h_mm), COLUMN_LAMBDA_RANGE[0]), COLUMN_LAMBDA_RANGE[1])
    n = min(max(0.0, n_kn * 1e3), COLUMN_N_SHEAR_CAP * c.FC_N_MM2 * h_mm * h_mm)
    need = (GAMMA_RE_SHEAR * abs(v_kn) * 1e3 - COLUMN_CONCRETE_SHEAR_FACTOR / (lam + 1.0) * c.FT_N_MM2 * h_mm * h0
            - COLUMN_AXIAL_SHEAR_FACTOR * n)
    return max(0.0, need / (FYV_N_MM2 * h0))


# ---------------------------------------------------------------------------
# Stirrup choice
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Stirrups:
    """One stirrup arrangement.

    Attributes:
        diameter_mm: Stirrup diameter [mm].
        spacing_mm: Spacing along the member [mm].
        legs: Legs in the shear direction (for a column, in each direction).
        zone_mm: Length over which it is used at each end [mm]; 0 outside the zones.
    """

    diameter_mm: int
    spacing_mm: int
    legs: int
    zone_mm: float = 0.0

    @property
    def label(self) -> str:
        """Short label, for example ``"A8@100x2"`` (A = HPB300, legs after x)."""
        return f"A{self.diameter_mm}@{self.spacing_mm}x{self.legs}"

    @property
    def asv_per_s(self) -> float:
        """Leg area per spacing [mm^2/mm]."""
        return self.legs * bar_area(self.diameter_mm) / self.spacing_mm


def leg_spacing_limit_mm(grade: int, d_mm: float) -> float:
    """Largest leg spacing in a confinement zone [mm], cl. 11.3.8 and 11.4.15."""
    return max(LEG_SPACING_MM[grade], LEG_SPACING_D_FACTOR[grade] * d_mm)


def legs_for(core_mm: float, grade: int, d_mm: float, least: int = 2) -> int:
    """Legs across a core width so that the leg spacing meets the limit."""
    return max(least, math.ceil(core_mm / leg_spacing_limit_mm(grade, d_mm) - 1e-9) + 1)


def core_mm(side_mm: float, bar_d_mm: float) -> float:
    """Width inside the stirrup [mm]: side - 2 (a_s - d/2), from a_s = 50 mm [J]."""
    return side_mm - 2.0 * (c.A_S_MM - bar_d_mm / 2.0)


def beam_stirrups(grade: int, b_mm: float, h_mm: float, asv_req: float, bar_d_mm: float,
                  end_steel_ratio: float) -> tuple[Stirrups, Stirrups] | None:
    """Beam stirrups at the ends (zone) and in the middle [J choice].

    End zone (Table 11.3.6-2): spacing <= min(k d, h/4, cap), diameter >= the
    grade's least (+2 mm above 2 % steel), leg spacing (cl. 11.3.8). Both
    parts meet A_sv/s >= ``asv_req`` and rho_sv >= k f_t/f_yv (cl. 11.3.9).
    The middle spacing is at most twice the zone spacing. The arrangement
    with the least steel per length is taken; ties go to the wider spacing.
    None if no candidate works.
    """
    check_grade(grade)
    zone_k, d_mult, cap, d_least = BEAM_ZONE[grade]
    if end_steel_ratio > BEAM_HEAVY_STEEL_RATIO:
        d_least += BEAM_HEAVY_STEEL_ADD_MM
    s_zone_max = min(d_mult * bar_d_mm, h_mm / BEAM_ZONE_H_DIVISOR, cap)
    zone = max(zone_k * h_mm, BEAM_ZONE_MIN_MM)
    rho_sv = BEAM_RHO_SV[grade] * c.FT_N_MM2 / FYV_N_MM2
    width = core_mm(b_mm, bar_d_mm)

    def best(s_max: float, d_min: int, zone_mm: float) -> Stirrups | None:
        pick = None
        for d in STIRRUP_DIAMETERS_MM:
            if d < d_min:
                continue
            legs = legs_for(width, grade, d)
            for s in STIRRUP_SPACINGS_MM:
                cand = Stirrups(d, s, legs, zone_mm)
                if s > s_max or cand.asv_per_s < asv_req or cand.asv_per_s / b_mm < rho_sv:
                    continue
                if pick is None or (cand.asv_per_s, -s) < (pick.asv_per_s, -pick.spacing_mm):
                    pick = cand
        return pick

    end = best(s_zone_max, d_least, zone)
    if end is None:
        return None
    mid = best(min(OUTSIDE_SPACING_FACTOR * end.spacing_mm, STIRRUP_SPACING_MAX_MM), STIRRUP_DIAMETERS_MM[0], 0.0)
    return (end, mid) if mid is not None else None


def lambda_v(grade: int, mu: float) -> float:
    """Least stirrup characteristic value, Table 11.4.17, linear in mu between columns."""
    check_grade(grade)
    vals = LAMBDA_V[grade]
    xs = LAMBDA_V_MU[:len(vals)]
    if mu <= xs[0]:
        return vals[0]
    if mu > xs[-1]:
        raise ValueError(f"axial ratio {mu:.3f} is beyond Table 11.4.17 for grade {grade}")
    for x0, x1, y0, y1 in zip(xs, xs[1:], vals, vals[1:]):
        if mu <= x1:
            return y0 + (y1 - y0) * (mu - x0) / (x1 - x0)
    return vals[-1]


def column_rho_v(st: Stirrups, core: float) -> float:
    """Volumetric ratio of a square hoop set, formula 6.6.3-2 (p. 72).

    rho_v = (n1 A_s1 l1 + n2 A_s2 l2)/(A_cor s) with n1 = n2 = legs and
    l1 = l2 = A_cor^0.5 = core width.
    """
    return 2.0 * st.legs * bar_area(st.diameter_mm) * core / (core * core * st.spacing_mm)


def column_zone_mm(h_mm: float, clear_height_m: float, root: bool) -> float:
    """Confinement zone length at a column end [mm], cl. 11.4.14."""
    hn = clear_height_m * 1000.0
    zone = max(h_mm, hn / COLUMN_ZONE_HN_DIVISOR, COLUMN_ZONE_MIN_MM)
    return max(zone, hn / COLUMN_ROOT_HN_DIVISOR) if root else zone


def column_stirrups(grade: int, h_mm: float, asv_req: float, mu: float, bars: ColumnBars,
                    clear_height_m: float, root: bool) -> tuple[Stirrups, Stirrups] | None:
    """Column hoops at the end zones and in the middle [J choice].

    Zone (Table 11.4.12-2, cl. 11.4.14-11.4.17): spacing <= min(k d, cap), 100 mm
    at the bottom-storey root for grades 3-4; least diameter; legs at most the
    leg spacing apart and restraining every other bar (cl. 11.4.15);
    rho_v >= max(lambda_v f_c/f_yv, rho_v,min) (f_c of C40 is above C35, used
    as is). Outside: rho_v >= half the zone requirement, spacing <= 10 d or
    15 d (cl. 11.4.18). Both parts meet A_sv/s >= ``asv_req`` in each direction.
    None if no candidate works.
    """
    check_grade(grade)
    d_mult, cap, d_least = COLUMN_ZONE[grade]
    s_zone_max = min(d_mult * bars.diameter_mm, cap)
    if root:
        s_zone_max = min(s_zone_max, COLUMN_ROOT_SPACING_MM)
        d_least = max(d_least, COLUMN_ROOT_MIN_DIAMETER_MM)
    rho_v_req = max(lambda_v(grade, mu) * c.FC_N_MM2 / FYV_N_MM2, COLUMN_RHO_V_MIN[grade])
    core = core_mm(h_mm, bars.diameter_mm)
    every_other = math.ceil((bars.per_side - 1) / 2.0 - 1e-9) + 1
    zone = column_zone_mm(h_mm, clear_height_m, root)

    def best(s_max: float, d_min: int, rho_req: float, zone_mm: float) -> Stirrups | None:
        pick = None
        for d in STIRRUP_DIAMETERS_MM:
            if d < d_min:
                continue
            legs = legs_for(core, grade, d, least=every_other)
            for s in STIRRUP_SPACINGS_MM:
                cand = Stirrups(d, s, legs, zone_mm)
                if s > s_max or cand.asv_per_s < asv_req or column_rho_v(cand, core) < rho_req:
                    continue
                if pick is None or (cand.asv_per_s, -s) < (pick.asv_per_s, -pick.spacing_mm):
                    pick = cand
        return pick

    end = best(s_zone_max, d_least, rho_v_req, zone)
    if end is None:
        return None
    s_out = min(COLUMN_OUTSIDE_SPACING_D[grade] * bars.diameter_mm, STIRRUP_SPACING_MAX_MM)
    mid = best(s_out, STIRRUP_DIAMETERS_MM[0], COLUMN_OUTSIDE_RHO_V_FACTOR * rho_v_req, 0.0)
    return (end, mid) if mid is not None else None


# ---------------------------------------------------------------------------
# Stirrup mass
# ---------------------------------------------------------------------------


def beam_stirrup_kg(b_mm: float, h_mm: float, bar_d_mm: float, clear_span_m: float,
                    end: Stirrups, mid: Stirrups) -> float:
    """Stirrup mass of one beam over its clear span [kg] [J].

    One closed hoop (two legs) per set plus (legs - 2) single legs; hooks and
    the joint core are left out. Lengths are inside the stirrup.
    """
    bw, hh = core_mm(b_mm, bar_d_mm), core_mm(h_mm, bar_d_mm)
    ln = clear_span_m * 1000.0
    zone = min(end.zone_mm, ln / 2.0)

    def kg(st: Stirrups, length_mm: float) -> float:
        per_set = (2.0 * (bw + hh) + (st.legs - 2) * hh) * bar_area(st.diameter_mm)  # mm^3
        return per_set * length_mm / st.spacing_mm * 1e-9 * STEEL_DENSITY_KG_M3

    return 2.0 * kg(end, zone) + kg(mid, ln - 2.0 * zone)


def column_stirrup_kg(h_mm: float, bar_d_mm: float, clear_height_m: float,
                      top: Stirrups, bottom: Stirrups, mid: Stirrups) -> float:
    """Hoop mass of one column over its clear height [kg] [J].

    Each set has ``legs`` legs in both directions across the core:
    2 legs core in all. Hooks and the joint core are left out.
    """
    core = core_mm(h_mm, bar_d_mm)
    hn = clear_height_m * 1000.0
    z_b = min(bottom.zone_mm, hn / 2.0)
    z_t = min(top.zone_mm, hn - z_b)

    def kg(st: Stirrups, length_mm: float) -> float:
        return 2.0 * st.legs * core * bar_area(st.diameter_mm) * length_mm / st.spacing_mm * 1e-9 * STEEL_DENSITY_KG_M3

    return kg(bottom, z_b) + kg(top, z_t) + kg(mid, max(0.0, hn - z_b - z_t))
