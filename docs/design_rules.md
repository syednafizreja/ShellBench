# Design rules for the generator

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

Playbook Day 15. Draft by Claude, 31 Oct 2026 (worked ahead of its 1 Nov slot), for the author to edit until every rule is either something done in the thesis or a clause that can be opened. These rules are what `src/shellbench/generator.py` (Day 16) will implement for a regular RC frame office building.

How to read the tags:
- **Th §** is the author's thesis, by section.
- **Clause, checked** means read in a copy, with the copy and page given in `notes/gb50010_design_values.md` or `docs/anchor_notes.md`.
- **[?]** is a clause cited from general knowledge that nobody has opened yet. It must be checked before Day 16 uses it.
- **[J]** is a choice, not code. Each one is the author's to accept or change.

## 1. Inputs and the seismic grade

Inputs: number of storeys, bay spans in both directions, storey heights, PGA, site period Tg, live loads, concrete grade (charter, Day 16 playbook).

R1. **Seismic grade.** Frame structures at 7 degrees and up to 24 m high are grade III, which is the thesis case (Th §2.4: "three-level seismic rating"). The grade for other intensities and heights comes from GB 50011-2010 Table 6.1.2 [?]. Because the PGA sweep runs from 0.05 to 0.40 g, the generator needs the whole table, and the grade then sets R6, R9, R12 and R13. Until the table is opened, the generator may only run 0.10 g (the validated anchor).

R2. **Seismic coefficient.** α_max = 0.08 for frequent earthquakes at 7 degrees, 0.10 g (GB 50011 Table 5.1.4-1, checked by the author on 25 Oct 2026). Values for the other PGA levels come from the same table [?].

## 2. Preliminary sizes

R3. **Slab thickness.** Th §2.1 gives span/thickness limits of 30 for one-way slabs and 40 for two-way slabs, with an 80 mm minimum. Rule: t = max(l/40 for a two-way panel or l/30 for a one-way panel, 80 mm), rounded up to 10 mm. Code basis: GB 50010 cl. 9.1.2 [?]. **Open point:** the thesis panel is 3.6 m (secondary beam at mid-span), so this rule gives 90 mm, not the 120 mm of decision B1. The thesis chose 120 mm without saying why. Either the rule needs a practical minimum of 120 mm for floors [J], or the generator will not reproduce B1. The author decides.

R4. **Main beam depth.** Th §2.3: h = L/14 to L/8 and b = h/3 to h/2. Secondary beams: h = L/18 to L/12. These are rules of thumb from the thesis, not clauses [J]. Rule: h = L/12 rounded up to 50 mm; b = h/2 rounded up to 50 mm, at least 250 mm [J].
**Open point:** no single span ratio, rounded either way, gives both thesis sizes. 600 mm on 7.2 m needs a ratio of 12.52 or less, and 500 mm on 6.6 m needs 12.57 or more (rounding up: 13.09 or less, and 13.2 or more). So the thesis BC beam (300 × 500, Th §2.3) was a separate choice for the corridor span. The rule above gives 300 × 600 for AB/CD and 300 × 550 for BC. Day 16 will report BC as the one size that differs, unless the author adds a rule for it.

R5. **Preliminary column size.** Th §2.4: N = β g A_trib n, with g = 14 kN/m² per floor and β = 1.3 (edge columns) or 1.25 (interior columns); then A ≥ N / (μ_lim f_c). The thesis counted five floors (n = 5, decision B4 says four storeys) and used μ_lim = 0.75. Rule: the same formula with n = the number of storeys and μ_lim from R6; a square column a = √A, rounded up to 50 mm [J]. With the thesis inputs this gives the B/C column first, and every column takes that size, as in the thesis ("the columns of lines on axes A, B, C, and D are equal", Th §2.4) [J].
**Open point:** with the thesis's own numbers (n = 5, μ_lim = 0.75) the B/C column needs a ≥ 554.89 mm, so 600 mm (Th §2.4). With n = 4 storeys and μ_lim = 0.85 the same formula gives N = 1.25 × 7.2 × 6.9 × 14 × 4 = 3 477.6 kN, A ≥ 214 197 mm², a ≥ 462.8 mm, so 500 × 500 mm. The generator would then not reproduce the thesis 600 × 600 from R5 alone; drift (R11) may or may not push it back up. The author decides whether R5 keeps the thesis's n and 0.75 as a preliminary-sizing habit [J], or uses the code values and lets Day 16 report the difference.

R6. **Axial ratio limit.** 0.85 for a grade III frame (GB 50011 Table 6.3.6, the author's reading, decision B16). Grades I and II: 0.65 and 0.75 [?]. Checked again with the final forces in R12.

R7. **Column minimum dimension and slenderness.** Clear height over section depth > 4 (Th §2.4, the shear-failure check). Minimum column side for the grade: GB 50011 cl. 6.3.5 [?].

## 3. Loads and analysis

R8. **Loads.** Dead loads from the build-up of each element (as Th §3-4 and docs/baseline_spec.md A4). Live loads 2.5 kN/m² office and 3.0 kN/m² corridor (decision B3). Wind from GB 50009 as in Th Table 8-1. Earthquake by the base-shear method of GB 50011 cl. 5.2.1, with G_i = dead + 0.5 floor live (Table 5.1.3) and the period factor ψ_T = 0.7 (anchor decision, JGJ 3-2010 cl. 4.3.17 [?]). The response-spectrum check (Day 10) stays a check, not the design method [J].

R9. **Combinations.** The generator uses the current codes (author's decision, 24 Oct 2026): 1.3 D + 1.5 L and the wind combinations from GB 55001-2021 cl. 3.1.13, and 1.3 G_E ± 1.4 E_h from GB 55002-2021 cl. 4.3.2 (both checked by Claude Code in the online texts). The anchor keeps the thesis factors (1.2 / 1.3), so the generator and the anchor differ here on purpose.

R10. **Model.** The 2D elastic OpenSeesPy frame of the anchor for member forces (Days 5-11), and the 3D model on the drawing grid for periods (Day 10, D25). Beam stiffness 2.0 I₀ for interior frames, 1.5 I₀ for edge frames (spec M7).

## 4. Checks and what to change when one fails

R11. **Drift.** Elastic storey drift ≤ 1/550 for frames (spec S11; GB 50011 Table 5.5.1 [?]). If a storey fails: first increase all columns by 50 mm and rerun; if that does not fix it after the column size reaches 1.5 times its R5 value, increase the beams by 50 mm in depth [J]. Each change reruns the whole analysis. "Columns first, then beams" is the playbook's order; the stopping rule is mine [J].

R12. **Columns.** Axial ratio μ = N / (f_c A) ≤ R6, with N from the seismic combination (GB 50011 Table 6.3.6 note [?]; GB 50010 Table 11.4.16 note 1, p. 164 of the translation, checked). If it fails, increase the column by 50 mm [J]. Longitudinal steel at least 0.75 % in total and 0.20 % per side for grade III (GB 50010 Table 11.4.12-1, p. 163, checked; other grades [?]). The thesis used 4C22 (0.42 %), which is below this (B6); the generator applies the code minimum, otherwise the conventional frame's steel carbon is too low and the shell floor's saving looks too large (anchor report §6).

R13. **Beams.** Required steel from `checks.py` as on Day 11: face moments, rectangular section, h₀ = h − 50 mm, GB 50010 cl. 6.2.10 (p. 36-37, checked), γ_RE = 0.75 for flexure (cl. 11.1.6, p. 152, checked). ξ ≤ 0.35 at the ends for grades II and III (cl. 11.3.1, p. 154, checked; grade I is 0.25 [?]). If ξ fails, increase the beam depth by 50 mm [J]. Minimum steel for grade III: max(0.25 %, 55 f_t / f_y) at supports and max(0.20 %, 45 f_t / f_y) at mid-span (Table 11.3.6-1, p. 156, checked; Th §9.1 quotes the same).

R14. **Checks not yet in `checks.py`** (Day 11 rule 10): strong-column weak-beam (GB 50011 cl. 6.2.2 [?]), strong-shear weak-bending and member shear (cl. 6.2.4, 6.2.5 [?]), crack width and deflection (GB 50010 cl. 3.4 [?]). The thesis did not do these either (Th §9). Proposed [J]: add shear and strong-column checks before Day 20, because at 8-9 degrees they can govern the column size and so the carbon. If the author prefers to leave them out, Paper 1 must say so as a limitation.

## 5. Rounding and bars

R15. **Sizes** in steps of 50 mm (playbook). **Bars** from the standard diameters 12, 14, 16, 18, 20, 22, 25, 28 and 32 mm [J; GB 1499.2 [?]]. For each section, choose the fewest bars of one diameter whose area meets the required steel, with 2 to 6 bars per layer in a 300 mm beam [J]. Spacing is not checked yet [J]. The quantity take-off uses the area of the chosen bars, not the required area [J].

R16. **Stirrups** φ10@100 four legs in columns over the full height, φ10@200 two legs in beams (drawings 01 and 03; D28 (c)). Confinement rules by grade (GB 50011 cl. 6.3.3, 6.3.7 [?]) replace these when R14 is added.

## 6. Decisions the author needs to make before Day 16

1. R3: a 120 mm practical minimum for floor slabs, or accept that the generator gives 90 mm for 3.6 m panels.
2. R5: preliminary column sizing with the thesis habit (five floors, 0.75), which gives 600 × 600, or with the code values (four storeys, 0.85), which gives 500 × 500.
3. R4: a separate rule for the corridor beam, or accept 300 × 550 for BC.
4. R11: the drift stopping rule.
5. R14: add shear and strong-column checks before the family run, or state them as a limitation.
6. R1, R2, R6, R7, R11: open GB 50011 Tables 6.1.2, 5.1.4-1 (other intensities), 6.3.6 (grades I and II), cl. 6.3.5 and Table 5.5.1, or tell me where a copy can be read.

© 2026 Syed Nafiz Reja Hasib. All rights reserved.
