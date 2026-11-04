# Floor library (Day 26)

File: docs/floor_library.md. Built by `python -m shellbench.floorlib` ([../src/shellbench/floorlib.py](../src/shellbench/floorlib.py)); output [../results/floor_library.csv](../results/floor_library.csv); checked by [../tests/test_floor_library.py](../tests/test_floor_library.py).

**Done-when (Day 26):** 60 or more library cases with 5 spot checks. **Result:** 72 cases, all 72 sized. The 5 spot checks pass on every case they apply to.

## What a case is

A case is one floor variant of layout A, sized to the smallest trial thickness that passes every check in `panel.size_row`. A case that never passes stays in the CSV with `sized = False` and is not dropped. This run had none.

| Variable | Values | Source |
|---|---|---|
| Span L | 6.0, 6.6 m | the two bays of layout A (spec G4, floor_concept decision 2) |
| Rise f/L | 1/8, 1/10, 1/12, 1/15, 1/18, 1/20 | floor_concept decision 4 [J] |
| Levelling | foamed fill, recycled fill, raised floor | floor_concept 4.3 |
| Mesh | 1 layer at mid-depth, or 2 layers (one near each face) | Day 25; handoff of 3 Nov (Day 26 to-do) |
| Tie | prestressed, every 1.2 m | approved by the author on 3 Nov |
| Trial thickness | 50-150 mm in 10 mm steps | [J] |

2 × 6 × 3 × 2 = 72 cases. The case ID is `L{span×10}-r{n}-{ff|rf|rs}-m{layers}`, for example `L66-r15-ff-m1`.

What changed from Day 25:

- **Fill at its true depth.** The fill is f − z(x), deepest at the springings, not a uniform f/3. CalculiX runs a fifth unit case with this shaped load. The buckling run carries the same shaped fill.
- **Two-layer mesh.** a = a′ = cover + 1.5 × mesh bar = 24 mm [J]. The capacity is GB 50010 6.2.17 with A_s = A_s′. In these shells x < 2a′, so the rule in the last paragraph of 6.2.17 (as in 6.2.14) applies: moments are taken about the compression steel. When x > ξ_b h₀ the steel is ignored, as in the one-layer check [J]. Each face carries the minimum ratio, so the mesh mass is 2 × layers × ρ × t × arc factor × 7850 kg/m³ [J].
- With true fill, the Day 25 ratio check (closed form against FE) is not a pass condition. Spot check 5 replaces it.
- Buckling is linear, with no imperfection allowance. JGJ 22-2012 asks for a stability analysis (3.2.9), but chapter 7 gives no stability formula for cylindrical shells (LOG, 3 Nov). Decision of 4 Nov 2026 [J]: stability enters through the linear FE buckling factor λ, in two ways:
  - the 1/(1 − 1/λ) amplifier in the 6.2.17 check;
  - the lowest λ in the library is 12.8, far above 1.

  A separate knock-down factor is not added. This item is closed; author to confirm.

`panel.py` gained these as optional keyword arguments only. Rerunning `python -m shellbench.panel` leaves `results/panel_day25.csv` byte-identical.

## Results

Sized thickness [mm]:

| L [m] | f/L | foamed m1 | foamed m2 | raised m1 | raised m2 | recycled m1 | recycled m2 |
|---|---|---|---|---|---|---|---|
| 6.0 | 1/8 | 90 | 100 | 80 | 90 | 90 | 100 |
| 6.0 | 1/10 | 80 | 100 | 80 | 90 | 90 | 100 |
| 6.0 | 1/12 | 80 | 100 | 80 | 90 | 90 | 100 |
| 6.0 | 1/15 | 80 | 100 | 80 | 100 | 90 | 100 |
| 6.0 | 1/18 | 90 | 100 | 80 | 110 | 90 | 100 |
| 6.0 | 1/20 | 90 | 120 | 90 | 120 | 90 | 110 |
| 6.6 | 1/8 | 90 | 100 | 80 | 100 | 100 | 110 |
| 6.6 | 1/10 | 90 | 100 | 80 | 100 | 100 | 110 |
| 6.6 | 1/12 | 90 | 100 | 90 | 100 | 100 | 110 |
| 6.6 | 1/15 | 90 | 110 | 90 | 100 | 90 | 110 |
| 6.6 | 1/18 | 90 | 110 | 90 | 110 | 100 | 110 |
| 6.6 | 1/20 | 100 | 120 | 90 | 120 | 100 | 110 |

Ranges over the library:

- concrete 0.081-0.121 m³/m²;
- mesh 2.7-8.1 kg/m²;
- tie bars 16-32 mm;
- linear buckling factor 12.8-44.0.

Findings:

1. **The two-layer mesh needs 10-30 mm more shell in every case.** The cause is the x < 2a′ rule. With one mid-depth layer, N acts about (t − x)/2 from the compression block. With two layers, the rule leaves N only t/2 − a′, about 21 mm at t = 90 mm. The extra face steel does not make up for this. The rule is conservative, because it ignores the concrete above a′. A full strain-compatibility check could narrow the gap [J]. **Author to confirm** that 6.2.17 with the 6.2.14 rule is the check to use.
2. Recycled fill is heavier, so it governs at 6.6 m. Foamed fill and the raised floor come out much the same.
3. The flattest vault (1/20) is the thickest in each column. The thinnest (80 mm) is at 1/8-1/15.

## Five spot checks

Each check recomputes a library value from closed forms, without calling the functions of `panel.py` (it uses only its input constants). Each runs on every sized case it applies to.

| # | Check | Cases | Tolerance |
|---|---|---|---|
| 1 | Raised floor: w recomputed from t, the closed-form arc factor and the loads; H = wL²/(8f) × 1/(1 + (15/8)(t²/12)/f²) | 24 | w 0.1 %, H 1 % |
| 2 | Raised floor: σ = √(H² + (wL/2)²)/t at the springing | 24 | 1 % |
| 3 | Every tie: A f_y ≥ H × 1.2 m (HRB400, f_y = 360 MPa) | 72 | — |
| 4 | Concrete = t × closed-form parabola arc factor; mesh = 2 × layers × ρ × t × k × 7850 | 72 | 0.1 % |
| 5 | True-depth fill: H = ∫M₀ z ds / ∫z² ds (two-pinned arch), with the same shortening factor | 48 | 5 % |

Note on check 1: in the first run the plain wL²/(8f) missed by up to 2.5 % on the flattest, thickest cases (L60-r20-rs-m2: model/closed form = 0.9755). The shortfall grows with t/f, which points to axial shortening. For a shallow parabolic two-pinned arch of constant section, the closed form divides by 1 + (15/8) i²/f² with i² = t²/12. That gives 0.9756 for this case. With the factor included, all 24 raised-floor cases agree within 1 %. The CalculiX model includes axial shortening; the Day 25 ratio check did not.
