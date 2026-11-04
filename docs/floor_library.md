# Floor library (Day 26)

File: docs/floor_library.md. Built by `python -m shellbench.floorlib` ([../src/shellbench/floorlib.py](../src/shellbench/floorlib.py)); output [../results/floor_library.csv](../results/floor_library.csv); checked by [../tests/test_floor_library.py](../tests/test_floor_library.py).

**Done-when (Day 26):** 60 or more library cases with 5 spot checks. **Result:** 72 cases, all 72 sized, at 70-100 mm. The 5 spot checks pass on every case they apply to.

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
- **Two-layer mesh.** a = a′ = cover + 1.5 × mesh bar = 24 mm [J]. The capacity is GB 50010 6.2.17 with A_s = A_s′. In these shells x < 2a′, so the rule in the last paragraph of 6.2.17 (as in 6.2.14) applies: moments are taken about the compression steel. 6.2.17 also allows the check with the compression steel not counted, so the capacity is the larger of the two valid branches (Claude's reading of 6.2.17, author to confirm). When x > ξ_b h₀ the steel is ignored, as in the one-layer check [J]. Each face carries the minimum ratio, so the mesh mass is 2 × layers × ρ × t × arc factor × 7850 kg/m³ [J].
- With true fill, the Day 25 ratio check (closed form against FE) is not a pass condition. Spot check 5 replaces it.
- Buckling is linear, with no imperfection allowance. JGJ 22-2012 asks for a stability analysis (3.2.9), but chapter 7 gives no stability formula for cylindrical shells (LOG, 3 Nov). Decision of 4 Nov 2026 [J]: stability enters through the linear FE buckling factor λ, in two ways:
  - the 1/(1 − 1/λ) amplifier in the 6.2.17 check;
  - the lowest λ in the library is 9.0, far above 1.

  A separate knock-down factor is not added. This item is closed; author to confirm.

`panel.py` gained these as optional keyword arguments only. Rerunning `python -m shellbench.panel` leaves `results/panel_day25.csv` byte-identical.

## Results

Sized thickness [mm]:

| L [m] | f/L | foamed m1 | foamed m2 | raised m1 | raised m2 | recycled m1 | recycled m2 |
|---|---|---|---|---|---|---|---|
| 6.0 | 1/8 | 90 | 80 | 80 | 70 | 90 | 80 |
| 6.0 | 1/10 | 80 | 80 | 80 | 70 | 90 | 80 |
| 6.0 | 1/12 | 80 | 80 | 80 | 70 | 90 | 80 |
| 6.0 | 1/15 | 80 | 80 | 80 | 70 | 90 | 80 |
| 6.0 | 1/18 | 90 | 80 | 80 | 80 | 90 | 80 |
| 6.0 | 1/20 | 90 | 80 | 90 | 80 | 90 | 80 |
| 6.6 | 1/8 | 90 | 80 | 80 | 80 | 100 | 90 |
| 6.6 | 1/10 | 90 | 80 | 80 | 80 | 100 | 90 |
| 6.6 | 1/12 | 90 | 80 | 90 | 80 | 100 | 90 |
| 6.6 | 1/15 | 90 | 80 | 90 | 80 | 90 | 80 |
| 6.6 | 1/18 | 90 | 80 | 90 | 80 | 100 | 80 |
| 6.6 | 1/20 | 100 | 80 | 90 | 80 | 100 | 90 |

Ranges over the library:

- concrete 0.071-0.104 m³/m²;
- mesh 2.7-6.3 kg/m²;
- tie bars 16-32 mm;
- linear buckling factor 9.0-33.2.

Findings:

1. **The two-layer mesh is 0-20 mm thinner than one layer in every case.** A first run had it 10-30 mm thicker. That came from checking only the x < 2a′ branch, which leaves N a lever arm of only t/2 − a′. The capacity now takes the larger of that branch and the branch with the compression steel not counted, and a test checks that two layers never give less capacity than one [J].
2. Recycled fill is heavier, so it governs at 6.6 m. Foamed fill and the raised floor come out much the same.
3. In each column the flattest vault (1/20) is at least as thick as any of 1/10-1/15. The thinnest case (70 mm) is the raised floor with two layers at 6.0 m, 1/8-1/15.

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
