# Baseline Specification: thesis anchor building

Status: **All Part B decisions recorded by the author** (Day 2, 20 Oct 2026). Values marked [J] are Claude's arithmetic or judgement; code values are the author's own readings.

Source key:
- **Th §x** = thesis, *Design of No.2 office building located at Panzhihua City, Sichuan Province* (S. N. R. Hasib, SWPU, 2023), section x.
- **Th T x** = thesis table x. Section numbers follow the thesis headings as printed.
- **Dwg 0x** = structural drawing number 0x (01 Column Details, 02 Standard Beam Design, 03 Standard Floor Beam Design, 04 Floor Slab Reinforcement, 05 Roof Slab Reinforcement, 06 Staircase).
- **[J]** = Claude's judgement or arithmetic, to be checked by the author. **[?]** = unverified.
- **Decided Bn** = the value was disputed and is fixed by the author's decision Bn in Part B.

Units: SI throughout (m, mm, kN, kN/m, kN/m², N/mm²).

---

## Part A: Inputs

### A1 Geometry

| ID | Input | Value in thesis | Source | Note |
|---|---|---|---|---|
| G1 | Structural system | Cast-in-place RC moment frame, **4 storeys**, internal corridor | Th abstract, §1.1 | Decided B4 |
| G2 | Plan shape and size | "E" shape, 38.40 m (E–W) × 27.60 m (N–S), ≈ 3 500 m² | Th §1.1 | Decided B11: quantity model uses drawing grid 38.4 × 21.0 m |
| G3 | Transverse spans (frame AB, BC, CD) | 7.2 m, 6.6 m, 7.2 m | Th §1.1, §2.6, T 8-11; Dwg 01–05 (7200/6600/7200, total 21 000) | Consistent |
| G4 | Longitudinal bays (axes 1–7) | Drawings: 6.0, 6.6, 6.6, 6.6, 6.6, 6.0 m (total 38.4 m). **Anchor frame tributary width: 7.2 m** | Dwg 01–05; Th §2.4, §5.2 | Decided B10 |
| G5 | Frame analysed | Transverse frame on axis (2) | Th §2.3, §2.6 | §2.5 says axis (3); B12 not applicable under B10 |
| G6 | Storey height, typical | 3.6 m | Th §1.1, §2.5; Dwg 01 note 8 | Consistent |
| G7 | Ground-storey column length | 4.55 m (top of foundation to level 1) | Th §2.5, T 1, T 8-12; Dwg 01 note 7 | Decided B4: 4.55 m (T 8-1/8-2 use 4.05 m for wind) |
| G8 | Indoor–outdoor level difference | 0.45 m | Th §1.4, §2.5 | |
| G9 | Top of foundation below outdoor ground | 0.50 m | Th §2.5 | |
| G10 | Slab thickness | **120 mm** | Th §3.2.1, §3.4, §4.1 | Decided B1 (§2.1 "180" is a typo) |
| G11 | Parapet height | 1.2 m | Th §4.2 | |

### A2 Member sizes

| ID | Member | b × h (mm) | Source | Note |
|---|---|---|---|---|
| M1 | Frame beam AB, CD | 300 × 600 | Th §2.3, T 1 | Decided B13: stiffness 600; printed 700-based load kept |
| M2 | Frame beam BC | 300 × 500 | Th §2.3, T 1 | |
| M3 | Longitudinal (stringer) beam | 300 × 600 | Th §2.3 | Decided B13 |
| M4 | Secondary beam | 300 × 500 | Th §2.3, §4.1 | |
| M5 | Columns, all storeys | 600 × 600 | Th §2.4, T 1, T 9.3; Dwg 01 | Consistent |
| M6 | Stair beam | 250 × 400 | Dwg 06 | Not needed for the frame model |
| M7 | Beam moment of inertia factor | I = 2.0 I₀ (middle frame), 1.5 I₀ (edge frame) | Th §2.6 | Slab–beam T-action; frame on axis 2 uses 2.0 |

### A3 Materials

| ID | Input | Value | Source | Note |
|---|---|---|---|---|
| X1 | Concrete grade | C40 | Th §9; Dwg 01–05 notes | |
| X2 | fc (design compressive) | 19.1 N/mm² | Th §2.4, §9, T 9.3; Dwg notes | |
| X3 | ft (design tensile) | 1.71 N/mm² | Th §9; Dwg notes | |
| X4 | Ec | 3.25 × 10⁴ N/mm² | Th §2.6, T 1 | |
| X5 | Longitudinal bars | **HRB400, fy = 360 N/mm²** | Th §9; T 3.1 | Decided B7 (Dwg note 270 is a copy error) |
| X6 | Stirrups | HPB300, fy = 270 N/mm² | Th §9; Dwg notes | |
| X7 | Concrete unit weight | 25 kN/m³ | Th §3.2.1, §4.1 | |
| X8 | Mortar / plaster unit weight | 20 kN/m³ | Th §3.2.1, §4.1, §4.2 | |
| X9 | Wall block (fly-ash aerated concrete) unit weight | 5.5 kN/m³ | Th §4.2 | |
| X10 | Concrete cover | 20 mm slab (Th §3.4); h₀ = h − 50 for beams (Th §9.2 table: 550, 450) | Th §3.4, §9.2 | Decided B14: slab cover 20 mm; beam/column a_s 50 mm |

### A4 Gravity loads (characteristic)

| ID | Input | Value | Source | Note |
|---|---|---|---|---|
| L1 | Floor dead load (finishes + slab) | 4.05 kN/m² | Th §3.2.1, §4.1 | Slab 25 × 0.12 = 3.00; decided B1, B2 |
| L2 | Roof dead load | 4.224 kN/m² | Th §4.1 | Slab 3.00 (B1, B2 decided); SBS 11 × 0.004 = 0.044 [J] |
| L3 | Frame beam self-weight + plaster, AB/CD | 4.934 kN/m | Th §4.1 | Uses h = 0.7 m; kept as printed (B13) |
| L4 | Frame beam self-weight + plaster, BC | 3.274 kN/m | Th §4.1 | |
| L5 | Column self-weight + plaster | 9.96 kN/m | Th §4.1 | |
| L6 | Interior wall (200 mm) line load | 5.51 kN/m | Th §4.2 | Anchor uses §5.2 value 6.36 (B15) |
| L7 | Exterior wall (240 mm) line load | 6.24 kN/m | Th §4.2 | Item arithmetic wrong; anchor uses §5.2 value 8.37 (B15) |
| L8 | Parapet line load | 3.14 kN/m | Th §4.2 | Anchor uses §5.2 value 2.54 (B15) |
| L9 | Live load, office floor | **2.5 kN/m²** | Th §6.1 line loads | Decided B3 (code value 2.0 per author) |
| L10 | Live load, corridor | **3.0 kN/m²** | Th §6.1 line loads | Decided B3 (code value 2.5 per author) |
| L11 | Live load, roof (non-accessible) | 0.5 kN/m² | Th T 6.1 | |
| L12 | Live load, bathroom | 2.5 kN/m² | Th T 6.1 | |
| L13 | Live load, stair | 3.5 kN/m² | Th T 6.1 | |
| L14 | Load path | 45° yield lines; trapezoidal/triangular loads converted to uniform with (1 − 2α₁² + α₁³) and 5/8 | Th §5.1 | |

### A5 Wind

| ID | Input | Value | Source | Note |
|---|---|---|---|---|
| W1 | Basic wind pressure w₀ | 0.30 kN/m² | Th §1.3, §8.1, T 8-1 | |
| W2 | Terrain roughness | Class B | Th §8.1 | |
| W3 | Shape factor μs | 1.3 | Th T 8-1 | |
| W4 | Height factor μz | 1.00, 1.00, 1.03, 1.13 (levels 1–4) | Th T 8-1 | |
| W5 | Gust factor βz | 1.00 | Th T 8-1 | |
| W6 | Loaded width B | 7.2 m | Th T 8-1 | Decided B10 |
| W7 | Level heights used | 4.05, 7.65, 11.25, 14.85 m | Th T 8-1 | B4: wind tables use 4.05 m; reason unconfirmed (see B4 note) |

### A6 Seismic

| ID | Input | Value | Source | Note |
|---|---|---|---|---|
| S1 | Intensity / PGA | 7 degrees, 0.10 g | Th §1.3 | |
| S2 | Design earthquake group | Group 1 | Th §1.3 | |
| S3 | Site class | **II** | Th §1.3 prints I | Decided B5 (label corrected) |
| S4 | Characteristic period Tg | **0.35 s** | Th §1.3 | Decided B5 |
| S5 | Seismic (anti-seismic) grade | Grade three | Th §2.4, §9.3 | |
| S6 | Axial compression ratio limit | **0.85** (generator); thesis calcs used 0.75 | Th §9.3; GB 50011 T 6.3.6 per author | Decided B16 |
| S7 | Fundamental period T1 | not shown | n/a | Decided B9: computed by OpenSeesPy, not a validation target |
| S8 | Seismic coefficient α1 | not shown | n/a | Decided B9: computed by OpenSeesPy, not a validation target |
| S9 | Equivalent gravity load Geq / storey weights Gi | not shown | n/a | Decided B9: computed by OpenSeesPy, not a validation target |
| S10 | Storey shears used | T 8-12 (5 levels: 363.06 … 98.29 kN) | Th T 8-12 | Validation target with B4 caveat (B9) |
| S11 | Elastic drift limit | 1/550 | Th §8.2, §8.4 | §8.2 also prints 1/5500 (typo [J]) |
| S12 | γRE | 0.75 beam flexure, 0.85 shear, 0.80 column | Th §9.1, §9.3 | Values as printed; text is garbled, author to confirm |
| S13 | Load combinations used | 1.3D + 1.5L; 1.3D + 1.5(L + 0.6W); 1.3D + 1.5(0.7L + W) | Th §8.7, T 8-13, T 8-15 | No seismic combination table found in the text [J] |
| S14 | Preliminary gravity load for column sizing | 14 kN/m² per floor, × 5 floors | Th §2.4 | B4: "× 5" is an error; building has 4 storeys |

### A7 Foundation and site

| ID | Input | Value | Source | Note |
|---|---|---|---|---|
| F1 | Foundation type | Independent (separate) footings under columns | Th abstract, §1.1 | |
| F2 | Bearing capacity fak | **220 kPa (decided B8)**. Thesis states: 240 kPa (silty layer, §1.2); 360 kPa (clay, §1.2); 220 kPa (sandy clay, §1.3); 350–450 kPa (gravel, §1.3) | Th §1.3 | Decided B8 |
| F3 | Groundwater | 20.5 m below surface, non-corrosive | Th §1.3 | |
| F4 | Fill thickness | 3 m (§1.2) or "4 feet" (§1.3) | Th §1.2, §1.3 | Units garbled; folds into B8 |

### A8 Reinforcement as built (for the generator check on Day 3 onwards)

| ID | Input | Value | Source | Note |
|---|---|---|---|---|
| R1 | Column longitudinal steel | 4C22 (As = 1520 mm²) all columns | Th §9.3 | Dwg 01: KZ-2 4C20, KZ-3/KZ-4 4C25 at floors 2–4; decided B6: 4C22, flagged below GB 50011 minimum and spacing |
| R2 | Column stirrups | φ10@100 (4 legs) in confined zones | Th T 8-16; Dwg 01 | |
| R3 | Slab steel | C8@200 both ways | Th T 3.1; Dwg 04, 05 | |
| R4 | Beam steel | Th §9.2 table; Dwg 02/03 (3C16 to 3C25) | Th §9.2; Dwg 02, 03 | Typed on Day 3 |

---

## Part B: Inconsistencies (author decides; Claude lists options only)

Each item: what the thesis says, the options, and what each option would change. "Decision" and "Reason" are for you to fill in after checking your calculation sheets and your copy of GB 50010 / GB 50011 / GB 50009.

### B1. Slab thickness: 180 mm vs 120 mm
- Says: §2.1 "the width is 180 mm"; §3.2.1, §3.4 (h₀ = 120 − 20) and §4.1 all compute with 120 mm.
- Evidence [J]: the floor total 4.05 kN/m² = 0.65 + 0.20 + 3.00 + 0.20 only with 25 × 0.12 = 3.00. The roof total 4.224 also only adds up with 3.00.
- Option A, 120 mm: every downstream number (loads, slab steel, frame forces) stays as computed. §2.1 is a typo.
- Option B, 180 mm: floor dead load becomes 5.55 kN/m² and roof 5.724 kN/m² [J]; every gravity and seismic result in the thesis would no longer match the model, so the anchor could not be validated against your tables.
- **Decision (author, 20 Oct 2026): 120 mm.** Reason: every load calculation that actually produces numbers (§3.2.1, §3.4, §4.1 and the totals that follow) uses the 0.12 m thickness.

### B2. "25 × 0.12 = 6.60" typo
- Says: §3.2.1 and §4.1 (floor and roof) print 25 × 0.12 = 6.60 kN/m²; the product is 3.00 [J], and the totals use 3.00.
- Option A: treat 6.60 as a typo; use 3.00 (consistent with the printed totals).
- Option B: treat 6.60 as intended (that implies a 264 mm slab [J]); contradicts both B1 values and every total.
- Related [J]: the roof SBS layer prints "11 × 2.40 = 2.404"; the total only works with 11 × 0.004 = 0.044. Same decision type.
- **Decision (author, 20 Oct 2026): 6.60 is a typo for 3.00.** Reason: 25 × 0.12 = 3.00, and only that value makes the printed floor total 4.05 kN/m² and roof total 4.224 kN/m² add up exactly (0.65 + 0.20 + 3.00 + 0.20 = 4.05). Evidence: thesis arithmetic; calculation sheet not yet checked.

### B3. Live loads: §3.2.2 vs Table 6.1
- Says: §3.2.2 office 2.0, corridor 2.5 kN/m²; T 6.1 floor 2.5, corridor 6.6 kN/m².
- Option A: office 2.0, corridor 2.5 (as §3.2.2 and the slab design). Check which values your frame live-load calculation in Ch 6–7 actually used.
- Option B: floor 2.5, corridor per your copy of GB 50009 (6.6 looks like a typing carry-over from the span 6.6 m [J]).
- Evidence from Ch 6 (§6.1) [J]: the frame line loads use **2.5** on the office side spans (2.5 × 3.6/2 × 2 = 9.00 kN/m) and **3.0** on the corridor span (3.0 × 6.6/2 × 2 = 19.80 kN/m). The node loads print 2.00 and 2.5, but their products do not match: 2.00 × 3.6/2 × 5/8 × 7.2 = 16.20 (printed 21.07); 2.5 × 6.6/2 × (1 − 2 × 0.92² + 0.92³) × 7.2 = 5.10 (printed 40.75). So no single pair of values reproduces all of Ch 6.
- Option C: office 2.5, corridor 3.0 (the values the Ch 6 line loads used), so that the Ch 7 live-load forces stay reachable as validation targets; node-load products logged as thesis arithmetic errors.
- Effect: live load enters the frame gravity forces, the seismic weight (via the combination coefficient), and the family's live-load range (2.0–3.5 in the charter). The anchor must use whatever Ch 6–7 used, or the Day 3 validation targets will not match.
- **Decision (author, 20 Oct 2026): Option C, office 2.5 / corridor 3.0 kN/m².** Reason: these are the exact values that produced the §6.1 line loads (2.5 × 3.6/2 × 2 = 9.00; 3.0 × 6.6/2 × 2 = 19.80), so every Ch 7 live-load moment, shear and axial-force table stays a usable validation target. Author's reading of GB 50009-2012 Table 5.1.1: office 2.0, office-building corridor 2.5 kN/m², so the anchor sits 0.5 kN/m² above the code for both.

### B4. 4 storeys vs 5 levels; 4 550 vs 4 050 mm ground storey
- Says: text and wind tables use 4 storeys; T 7-7, T 8-12, T 9.3 and the beam table show 5 levels ("5th"); §2.4 multiplies by 5 floors. Ground column 4.55 m (§2.5, T 1, T 8-12, Dwg 01) but 4.05 m (T 8-1, T 8-2). §2.5 prints 4.55 = 0.920 + 0.500 + 3.60, which sums to 5.02 [J]; 0.45 + 0.50 + 3.60 = 4.55 [J].
- Option A: 4 storeys, ground column 4.55 m (drawings + stiffness + seismic drift). Wind tables become "computed with 4.05 m" and get a note; T 8-12 level 5 must be explained (roof/parapet level?).
- Option B: 5 levels. Contradicts the title, abstract, wind table and drawings.
- Option C: 4 storeys, 4.05 m. Contradicts Dwg 01 and T 1 stiffness.
- Effect: storey count and ground height set the period, seismic weight, D-values and drift. The anchor validation compares against T 7-6, T 8-2 and T 8-12, so you must say which table each comparison will use.
- **Decision (author, 20 Oct 2026): 4 storeys; ground-storey column 4.55 m; level 5 in T 8-12 is an erroneous extra row.** Reason: four storeys in the title, abstract, §1.1 and wind tables; frame geometry has only ground 4.55 m + 3 × 3.60 m; 4.55 = 0.45 + 0.50 + 3.60. The "× 5" (§2.4) and "5th" labels do not correspond to any physical storey weight or stiffness elsewhere.
- Consequence [J]: T 8-12 shears are cumulative, so rows 1–4 (e.g. V1 = 363.06 kN) still include the level-5 force (98.29 kN). T 8-12 is therefore not a clean 4-storey target; Day 3 must note this, and the anchor report compares against it with that caveat.
- Note [J]: T 8-1/8-2 use 4.05 m = 3.60 + 0.45 (outdoor ground to level 1), which leaves out the 0.50 m foundation embedment. The wind-height choice may be deliberate; the author should confirm.

### B5. Site class I with Tg = 0.35 s
- Says: §1.3 site category I, group 1, Tg = 0.35 s.
- Look up in your copy of GB 50011 the Tg table (§5.1.4 [?]) for site class I (I₀ / I₁) and group 1, and the Tg for class II, group 1. I will not supply those values.
- Option A: site class I with the code's Tg for class I.
- Option B: keep Tg = 0.35 s and correct the site class to the one the code gives 0.35 s for.
- Option C: keep both as printed and document the mismatch.
- Effect: Tg sets α1 for T1 > Tg, so it changes base shear, column and beam sizes. The family spans Tg 0.25–0.45 s, so the anchor value also fixes where the thesis sits in the family.
- **Decision (author, 20 Oct 2026): Option B, keep Tg = 0.35 s, correct site class to II.** Reason: author's reading of GB 50011-2010 Table 5.1.4-2 for Group 1: I₀ 0.20 s, I₁ 0.25 s, II 0.35 s. Keeping the printed Tg preserves the seismic forces; only the site-class label changes.
- Open point [J]: the text never shows α1 (B9), so "0.35 s was used in α1" is not yet proven. Confirm when B9 is resolved.

### B6. Column steel 4C22 vs the code minimum
- Says: §9.3 "we must take the minimal reinforcement 4C22" (As = 1520 mm² ≈ 0.42% of 600 × 600 [J]). Dwg 01 shows 4C20, 4C22 and 4C25 by column type and floor.
- Check in your copy of GB 50011 / GB 50010 the minimum total longitudinal ratio for frame columns at seismic grade three, and the maximum bar spacing (4 bars on a 600 mm face may also fail spacing [J]).
- Option A: 4C22 is the as-designed value; the generator reproduces it and flags it as below the code minimum.
- Option B: the generator applies the code minimum; the thesis column steel is not a validation target, only the 600 × 600 size is.
- Option C: drawings (4C20/22/25) win over §9.3.
- Effect: column steel enters embodied carbon (steel mass) for every building in the family. It does not change elastic stiffness in the model.
- **Decision (author, 20 Oct 2026): Option A, 4C22 is the as-designed value; the anchor reproduces it and flags two code shortfalls.** Reason: §9.3 explicitly adopts "the minimal reinforcement 4C22" (As = 1520 mm², ≈ 0.42%). Author's reading of GB 50011-2010: Table 6.3.7-1, grade three frame, minimum total ratio 0.7% (middle/side) and 0.8% (corner), plus 0.05% for 400 MPa steel (note 2), giving 0.75% / 0.85%; §6.3.8 bar spacing ≤ 200 mm on faces > 400 mm, which four corner bars on a 600 mm face do not meet.
- Open point [J]: Dwg 01 (4C20 for KZ-2, 4C25 for KZ-3/KZ-4 at floors 2–4) is set aside in favour of §9.3. Whether the family generator applies the code minimum (needed for a fair steel-carbon count) is a generator decision for Week 2, not settled here.

### B7. HRB400 written as fy = 270
- Says: §9 and T 3.1 use HRB400, fy = 360; all drawing notes say "HRB400, fy = 270".
- Option A: fy = 360 for HRB400 (as the calcs used); the drawing note is a copy of the HPB300 line.
- Option B: fy = 270; means the bars are really HPB300, which contradicts the "C" bar symbol on every drawing.
- Check the design strength for HRB400 in your copy of GB 50010.
- **Decision (author, 20 Oct 2026): Option A, fy = 360 N/mm² for HRB400.** Reason: every calculation in §9 and T 3.1 that produces a numerical As uses 360. Author's reading of GB 50010-2010 Table 4.2.3-1: HRB400 fy = 360 N/mm² (fyk = 400). The drawing note "HRB400, fy = 270" copies the HPB300 line below it; "C" in "4C22" is the drawing mark for HRB400.

### B8. Bearing value 220 / 240 / 360 kPa
- Says: §1.2 silty layer fak = 240, clay 360; §1.3 sandy clay 220, gravel 350–450 kPa. Fill 3 m (§1.2) vs "4 feet" (§1.3).
- Option A: 220 kPa (most conservative stated value for the bearing layer).
- Option B: 240 kPa (§1.2).
- Option C: 360 kPa (clay, if footings bear on it).
- Effect: sets footing plan size, so footing concrete and steel in the carbon count. Does not change the frame analysis. Your footing calculation sheet (if any) decides which layer the footings sit on.
- **Decision (author, 20 Oct 2026): Option A, fak = 220 kPa.** Reason: the thesis contains no footing calculation recording a bearing check or a chosen fak; the two soil-profile paragraphs (§1.2, §1.3) are inconsistent, so the lowest stated usable value (sandy clay, §1.3) is retained as the conservative anchor value.
- Note [J]: a lower fak gives larger footings and so more footing carbon. Both floor options in a comparison use the same fak, so the bias mostly cancels in the saving, but it should be stated as an assumption in Paper 1.

### B9. T1, α1 and Geq not shown
- Says: T 8-12 gives storey shears, but the text shows no period, seismic coefficient, storey weights or Geq.
- Option A: recover them from your calculation sheets and add them to this spec with "calc sheet, page x" as the source.
- Option B: back-calculate them from T 8-12 shears and your stated method, and mark them [J] as reconstructed.
- Option C: let the OpenSeesPy model compute T1 and Gi, and compare only the storey shears/drifts with T 8-12.
- Effect: without these, the anchor report cannot say why its base shear differs from the thesis.
- **Decision (author, 20 Oct 2026): Option C.** OpenSeesPy computes T1 and Gi; only storey shears and drifts are compared with T 8-12, with the B4 caveat. Reason: no hand-calculation sheet recording T1, α1 or Gi is available; Option B is unreliable once row 5 is judged spurious.
- Consequences [J]: (1) the B5 open point (whether 0.35 s went into α1) cannot be closed from the thesis and stays as a stated assumption; (2) the anchor report must list the likely causes of any base-shear difference: period method (empirical vs eigenvalue, and any period reduction factor for infill walls), storey weights, and the spurious row 5.

### Further items found in this audit (not in the playbook's nine)

### B10. Longitudinal bay 7.2 m in calcs vs 6.0 / 6.6 m on drawings
- Says: §2.4 tributary (7.2 + 7.2)/2; §5.2 node loads × 7.2; T 8-1 width B = 7.2. All drawings show bays 6000, 6600 × 4, 6000 along axes 1–7.
- Option A: the calcs assumed 7.2 m; model the frame with a 7.2 m tributary width to match the thesis.
- Option B: use the drawings (axis 2 tributary (6.0 + 6.6)/2 = 6.3 m [J]); thesis gravity, wind and seismic forces will then not match.
- Effect: tributary width scales every load on the 2-D frame by up to about 14% [J].
- **Decision (author, 20 Oct 2026): Option A, 7.2 m tributary width for the anchor frame.** Reason: every load, moment and shear in the calculation chapters (§2.4, §5.2, T 8-1 and the force tables) was generated with 7.2 m; the drawings' 6.0 / 6.6 m bays are recorded as a parallel inconsistency. The anchor report must state that the model follows the calculation width, not the drawings.

### B11. Plan depth 27.60 m vs 21.00 m
- Says: §1.1 27.60 m N–S; drawings 21 000 between axes A and D.
- Option A: 21.0 m frame depth; 27.6 m includes the "E" wings outside axes A–D.
- Option B: something else you know from the architectural plan.
- Effect: only the whole-building weight and carbon; the 2-D frame uses the spans.
- **Decision (author, 20 Oct 2026): Option A.** The whole-building quantity model uses the drawing grid (38.4 × 21.0 m, bays 6.0 / 6.6 m); the 2-D anchor frame keeps 7.2 m for validation only. Reason: the 2-D frame exists to reproduce force tables computed with 7.2 m, while Paper 1's carbon inventory needs the drawn plan area and bay layout; 38.4 m is not a whole number of 7.2 m bays.
- Open point [J]: 38.4 × 21.0 × 4 ≈ 3 226 m² vs "≈ 3 500 m²" and 27.60 m in §1.1; the difference (E wings, stair cores?) is unexplained and is not counted in the quantity model unless the author adds it.

### B12. Frame on axis (2) or (3)
- Says: §2.3, §2.6 axis (2); §2.5 axis (3).
- Effect: changes tributary width under B10 Option B only.
- **Decision (author, 20 Oct 2026): not applicable.** Reason: under B10 Option A the tributary width is 7.2 m whichever axis is analysed.

### B13. Beam depth 700 mm in self-weight vs 600 mm
- Says: §4.1 frame and longitudinal beam self-weight 0.3 × (0.7 − 0.12) × 25; §4.2 wall height 3.6 − 0.7. Member sizes in §2.3 are 600 mm.
- Option A: 600 mm; self-weight becomes 0.3 × 0.48 × 25 = 3.60 kN/m plus plaster [J], and wall height 3.0 m.
- Option B: keep the printed loads because the frame forces were computed with them.
- **Decision (author, 20 Oct 2026): Option B.** The anchor applies the printed loads where each was used (4.934 kN/m on frame beams, 3.61 kN/m for longitudinal beams at the nodes); member stiffness stays 300 × 600. Reason: the gravity tables in Ch 5–8 were generated from those line loads.
- Notes [J]: (1) the anchor must not also generate self-weight from the section, or beam weight is counted twice; (2) under B11 the quantity model uses the detailed 300 × 600 section, not 700 mm.

### B14. Concrete cover 20 mm / 50 mm
- Says: §3.4 slab cover 20 mm; drawings "protective layer thickness 50 mm"; beam h₀ = h − 50.
- Effect: h₀ in the steel design only; not the elastic model.
- **Decision (author, 20 Oct 2026): Option A.** Slab cover 20 mm; beam/column a_s = 50 mm (distance to bar centroid). Reason: these produced h₀ in §3.4 and §9.2. Author's reading of GB 50010-2010 Table 8.2.1, environment class I: minimum clear cover 15 mm (slab), 20 mm (beam/column), so the thesis values meet it. The drawing's "protective layer 50 mm" is read as a_s.
- Note [J]: §3.4 takes h₀ = h − 20, i.e. it subtracts the cover only, not half the bar diameter; kept as printed. Environment class I is assumed (interior), not stated in the thesis.

### B15. Wall and parapet loads in §4.2 vs §5.2
- Says: §4.2 interior 5.51, exterior 6.24, parapet 3.14 kN/m; §5.2 node loads use 6.36, 8.37 and 2.54; longitudinal beam 3.61 vs 4.934 (§4.1). §4.2 exterior items are also off: block 2.9 × 0.24 × 5.5 = 3.83 (printed 3.19), mortar 1.16 (printed 28.80) [J].
- Option A: use the §5.2 values, because the frame results came from them.
- Option B: use corrected §4.2 values and accept a mismatch with the thesis gravity results.
- **Decision (author, 20 Oct 2026): Option A, the §5.2 values (interior wall 6.36, exterior wall 8.37, parapet 2.54, longitudinal beam 3.61 kN/m).** Reason: the node loads and the dead-load force tables were generated from these; the §4.2 values (with arithmetic errors) are not used for the anchor frame.
- Open point [J]: the source of 6.36 and 8.37 is untraced. Whether walls sit inside the Paper 1 carbon boundary is a charter question, not decided here.

### B16. Axial compression ratio limit 0.75 vs 0.85
- Says: §2.4 and T 9.3 use 0.75; §9.3 text says 0.85 for grade three. Check the limit for a grade-three frame in your copy of GB 50011 (the thesis cites §6.3.6).
- Effect: the generator's column sizing rule. With 600 × 600 the ratios are far below either limit (T 9.3), so the thesis building is unaffected; the family is not.
- **Decision (author, 20 Oct 2026): Option A, 0.85.** Reason: author's reading of GB 50011-2010 Table 6.3.6 for a grade-three frame structure; this is the limit the generator enforces for the family. The thesis used 0.75, and its tabulated ratios (≈ 0.05) are far below either limit, so the validation targets are unaffected.
- Consequence for Week 2 [J]: §2.4 sizing with the largest N = 4 347 kN gives a ≥ 551 mm at 0.75 but a ≥ 517 mm at 0.85. Whether the generator still returns 600 × 600 then depends on its rounding rule (e.g. to 50 mm gives 550). The generator reproduction test must state which limit it uses.

---

## Part C: Out of scope for this file
Thesis result values (internal forces, D-values, drifts, steel areas) are validation targets, typed on Day 3 into validation/thesis_values/. Arithmetic errors spotted in them (for example T 1 stiffness 7.74 × 10¹⁰ vs 4.875 × 10¹⁰ in §2.6, BC beam 6.68 × 10¹⁰ vs 3.08 × 10¹⁰ [J]) are logged there, not here.

### Thesis arithmetic errata (carried to Day 3 validation notes)
- §6.1 node load A1–3: printed 2.00 × 3.6/2 × 5/8 × 7.2 = 21.07 kN; product is 16.20 [J].
- §6.1 node load B1–3: printed 2.5 × 6.6/2 × (1 − 2 × 0.92² + 0.92³) × 7.2 = 40.75 kN; product is 5.10 [J].
- T 9.3 axial ratios: printed Nmax 339–469 kN give ≈ 0.05–0.07, but T 8-15 shows N up to 3 155.67 kN at the level-1 B/C column base (ratio ≈ 0.46) and §2.4 estimates 2 359–4 347 kN (≈ 0.34–0.63) [J]. T 9.3 appears to use the wrong N; the §9.3 column steel check rests on it.
