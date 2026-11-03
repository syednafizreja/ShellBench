# Floor concept: a shallow concrete vault between the frame beams

Playbook Day 22, drafted by the AI assistant on 30 Oct 2026 for the author's review and approval (schedule: floor concept approval by 31 Oct). Nothing here is a design yet. Day 23 finds the form, Day 24 checks the shell solver, and Day 25 sizes one panel. Values taken from a paper carry the paper, the section and the page; my choices are marked [J]; code clauses I could not read are marked [?] for the author to confirm.

## 1. What the floor replaces, and what it keeps

The anchor floor is a 120 mm cast-in-place slab (spec G10) on a beam grid. The slab spans between the frame beams, the longitudinal beams and, in six bays, secondary beams at mid-span of the 7.2 m spans (docs/anchor_notes.md, Day 12 rules). The thesis designed the slab as a two-way plate with net spans of 3.3 m by 7.05 m (Th §3.3), so the slab the shell floor has to beat is already thin for its span. It holds 0.119 m³ of concrete and 5.6 kg of bar steel per m² of floor (results/anchor_quantities.csv, grid plan).

The shell floor replaces the slab and the secondary beams. It keeps the columns, the frame beams and the longitudinal beams, because they are the lateral system that GB 50011 checks and that the generator designs. This is the main difference from the floors in the literature: Hawkins et al. (2020) and Oval et al. (2023) put the shell straight onto columns with no beams (Hawkins 2020 §2.1, AAM p. 2; Oval 2023 §2.1, AAM pp. 6-7), and Liew et al. (2017) test a single 5 m by 5 m class of unit on corner supports (abstract and §1, p. 323). None of these papers designs a floor for a seismic frame [J, from the gap matrix, docs/gap_matrix.md].

## 2. The floor build-up

From the bottom up, one panel between two beams holds:

1. **The vault.** A singly curved (barrel) concrete shell, thickness t, spanning L between two parallel beams, with rise f at mid-span. It springs from the beam sides near the beam soffit.
2. **Steel ties** across each vault at the springing line, at spacing s along the vault, to carry the horizontal thrust that the beams cannot.
3. **Levelling.** Lightweight fill from the vault surface up to the crown, or a raised floor on pedestals with no fill (option discussed in section 4.3).
4. **An optional cast-in-place topping**, thickness t_top = 0, 40, 50 or 60 mm, for the diaphragm (H3).
5. **The finishes of the anchor** (terrazzo, levelling mortar, ceiling plaster; Th §4.1), the same on both floors, so they cancel in the comparison.

A singly curved vault fits the beam grid better than the groin vault of Hawkins (2018, §3.2) and Hawkins et al. (2020, §2.2), which needs four corner supports and no edge beams [J]. Its geometry is also one curve, so Day 23 form-finding is a 2D problem for each panel.

## 3. Which way the vault spans

Two layouts fit the grid (spec G3, G4). I recommend layout A [J]; the author decides (section 8).

| | Layout A (recommended) | Layout B |
|---|---|---|
| Vault spans | Along the building, between the transverse frame beams on axes 1-7 | Across the building, between the longitudinal beams on axes A-D |
| Span L | 6.0 m (end bays) and 6.6 m | 7.2 m (AB, CD) and 6.6 m (BC) |
| Thrust goes into | The frame beams, in their weak axis | The longitudinal beams, in their weak axis |
| Balanced at | Every interior frame beam under uniform load | Lines B and C under uniform load |
| Unbalanced at | Axes 1 and 7 (end frames) | Axes A and D (façades) |
| Secondary beams | Removed | Removed |

Layout A gives the shorter, nearly uniform span (6.0 or 6.6 m in every panel), so one form-found curve covers most of the floor. Layout B gives the longest span the grid has, 7.2 m, which raises the thrust per metre by 7.2 / 6.6 = 1.09 for the same rise-to-span ratio and load, since H = w L² / (8 f) = w L / (8 f/L) [J, from section 4.5].

In both layouts the ties are needed everywhere, not only at the ends, for three reasons [J]: pattern live load leaves the thrusts on a beam unbalanced; during construction one vault is cast before its neighbour; and in an earthquake the beam may rotate or lose one neighbouring vault. Hawkins (2018) takes the thrust by "a grid of steel ties spanning between columns" (§2.1); Liew et al. (2017) note that "in a building with a main skeleton frame structure, the floor system could be integrated without explicit ties, relying on the frame to absorb the horizontal thrusts" (§1, the open introduction on the publisher's page; page to confirm [?]). I do not rely on the frame, because the frame beams are designed for seismic flexure in their strong axis, not for thrust in their weak axis [J].

## 4. Parameters and where each value comes from

### 4.1 Geometry

| Parameter | Anchor value or range | Source |
|---|---|---|
| Span L | Set by the grid: 6.0 / 6.6 m (layout A) | Spec G4 |
| Rise-to-span f / L | 1/8 to 1/20, Day 23 picks one | Oval et al. (2023): rise 59 cm on a 4.5 m span, "a rise-to-span ratio of around 1/8" (§2.1, AAM p. 6). Hawkins et al. (2020): structural depth h = l/10 in every case of Table 3 (§4.5, AAM p. 15) and "h = 800 mm would be a reasonable design choice" at 8 m (§4.3, AAM p. 13). The lower end, 1/20, is mine [J], to keep the fill small (section 4.3). |
| Shell thickness t | 50 to 80 mm | Hawkins et al. (2020), lowest-carbon textile-reinforced shells: 60 mm at 6 m and 70 mm at 8 m (Table 3, AAM p. 15). Oval et al. (2023): 30 mm at the apex to 60 mm at the supports, mean 45 mm, "1/100th of the span" (§2.1, AAM pp. 6-7). Liew et al. (2017): 20 mm, unreinforced ultra-high strength concrete with ribs (highlights and abstract, p. 323). The 50 mm floor is mine [J]: steel mesh in normal concrete needs cover on both faces (section 4.2). |
| Tie spacing s | 1.2 m [J] | None of the papers gives a spacing for a barrel vault. Day 25 checks it. |

The thinner shells in these papers use textile reinforcement or ultra-high strength concrete. GB 50010 does not cover textile reinforcement, and the anchor is a C40, HRB400 building. So I take the shell as normal-strength concrete with a light steel mesh [J]. That puts t towards the upper end of the range, and it is the main reason the savings in Hawkins et al. (2020) cannot be carried over to this building as they stand.

### 4.2 Shell reinforcement

Lightly reinforced: one layer of mesh at mid-thickness, to control shrinkage cracks, to carry the bending from pattern load and to hold the shell together if it cracks [J]. Checked on 30 Oct 2026 in the author's English translation of GB 50010-2010 (page numbers of the translation, ±1):

- **Cover.** Table 8.2.1 (cl. 8.2.1, p. 95-96) gives a separate row for "slab, wall and shell": 15 mm in environment category I and 20 mm in II-a. A dry indoor floor is category I [J], so 15 mm, with at least one bar diameter (cl. 8.2.1 item 1). One mesh at mid-thickness therefore needs t ≥ 2 × 15 mm + the mesh bars, which a 50 mm shell meets [J].
- **Minimum steel.** Table 8.5.1 (cl. 8.5.1, p. 101-102), note 2: for the tension steel of a flexural slab with 400 MPa bars, the larger of 0.15 % and 45 f_t / f_y. For C40 and HRB400 that is 45 × 1.71 / 360 = 0.214 %. The shell is mostly in compression, so applying the slab rule to it is my reading, not a clause written for shells [J]; Day 25 checks whether bending anywhere needs more.
- **Plain concrete.** Appendix D, cl. D.1.1: "Plain concrete flexural members are only allowed to be used when horizontally located on the base and not carrying any live loads." A floor vault carries live load, so an unreinforced shell is outside GB 50010. This settles decision 5 below on code grounds as well as robustness.

Textile reinforcement (the author's alternative) is not covered by GB 50010. It stays out of the family unless a design basis outside the code is chosen and stated [J].

### 4.3 Levelling: fill or raised floor

| Option | Density | Source |
|---|---|---|
| Foamed concrete fill | 800 kg/m³ dry (target), 1.0 MPa (target) | Hawkins (2018), §4.3 |
| Recycled aggregate fill | 1 400 kg/m³ | Hawkins et al. (2020), Table 2 (AAM p. 9); proposed there "as a low-carbon, low-cost and widely available alternative" (§2.1, AAM p. 2) |
| Raised floor on pedestals, no fill | 29 kg per m² of floor (the "flooring system" of the prototype) | Oval et al. (2023), Table 6 (AAM p. 19) |

For a parabolic vault filled level with its crown, the mean fill depth is f / 3 (the area between a parabola and its chord is two thirds of the enclosing rectangle) [J, geometry]. The fill is the term that decides whether the floor saves mass at all. Section 6 shows why.

### 4.4 Topping

Topping thickness t_top is a variable of the family: 0, 40, 50 or 60 mm (playbook Day 22; charter, H3). The rule that sets the minimum for a rigid diaphragm comes from GB 50011 and JGJ 3 (for example JGJ 3 cl. 3.6.2 on the topping of precast floors [?]); I could not read either clause today, so this is an author item. The topping is C40 with a light mesh, the same as the shell [J].

### 4.5 Ties

Steel ties, HRB400 bars anchored into the beam at the springing [J]. Hawkins (2018) and Hawkins et al. (2020) prestress threaded rods to control the shell's bending (Hawkins 2018 §2.1; Hawkins 2020 Table 3, pre-strain 0.94 to 1.10 mm/m, AAM p. 15). Oval et al. (2023) use "M20 S520 stainless steel tie-bars with mid-span turnbuckles" (§4.1); their Table 6 counts 4.2 kg of ties per m² (AAM p. 19). I start without prestress, because unstressed bars need no special site work, and let Day 25 show whether the shell needs it [J].

For a parabolic vault under a uniform load w per m² (all of the shell, fill, topping, finishes and live load above it), the thrust per metre of vault is H = w L² / (8 f), and the tie area per metre is A_t = H / f_y, with f_y = 360 N/mm² for HRB400 (GB 50010 Table 4.2.3-1, p. 21-22 of the translation, checked 30 Oct 2026; spec X5). This is statics for a three-hinged parabolic arch, not a design rule from a paper; Day 25 replaces it with the shell analysis.

## 5. How each component enters the whole-building model

| Component | Mass (seismic weight G_E) | Quantities and carbon (`carbon.py`) | Storey height | Frame model |
|---|---|---|---|---|
| Vault | t × arc length × 25 kN/m³ (spec X7) per m² of panel; arc length of a parabola ≈ L (1 + 8/3 (f/L)²) | Concrete m³ and mesh kg, element "floors" | Sets the depth below the beam top (section 7) | Load on the beams: vertical w L / 2 and horizontal H per metre at the springing |
| Ties | Steel, small | HRB400 kg | None | Axial members between the beams in the 3D model (Day 27); in the 2D frame, the horizontal reaction is closed inside the panel |
| Fill | Fill density × f / 3 per m² | Volume × fill factor (author's floor-only factor, schedule: 6 Nov) | None | Dead load only; no stiffness [J]. Hawkins et al. (2020) do the same: the fill's weight is a dead load, and "its contribution to stiffness and load-spreading is conservatively ignored" (§2.3, AAM p. 4) |
| Raised floor (if chosen) | Its mass per m² | Its mass × its factor (author) | Adds the pedestal height above the crown | Dead load only |
| Topping | t_top × 25 kN/m³ | Concrete m³ and mesh kg | Adds t_top | Diaphragm stiffness (Day 27, H3) |
| Removed slab and secondary beams | Minus 3.00 kN/m² (spec L1) and minus the secondary beams | Removed from the take-off | | Removed |

The anchor's floor dead load (4.05 kN/m², spec L1) splits into 3.00 kN/m² of slab and 1.05 kN/m² of finishes (Th §4.1). The shell floor replaces the 3.00 and keeps the 1.05.

## 6. Red team: can this floor save anything in this building?

The papers report large savings: 53-58 % embodied carbon and 43-53 % self-weight against flat slabs of 6-18 m span (Hawkins et al. 2020, abstract and §5.2, AAM pp. 1, 17-18); about 48 % against a 250 mm flat slab, with 100 kg/m² of shell (Oval et al. 2023, §2.1 and §5.2, AAM pp. 7, 19). But in every case the comparison is with a flat slab that spans column to column, 220 mm thick at 6 m in Hawkins et al. (2020, Table 4, AAM p. 17). The anchor slab is 120 mm because it spans about 3.3 m between beams. The baseline here is much leaner, so the saving will be much smaller. This needs saying in Paper 1 before a reviewer says it [J].

A rough check with the values above, per m² of floor, for L = 6.6 m, f / L = 1/12 (f = 0.55 m), t = 60 mm, all at 25 kN/m³ for concrete [J, my arithmetic, not a design]:

| Floor | Concrete [m³/m²] | Structural self-weight [kN/m²] |
|---|---|---|
| Anchor slab, 120 mm | 0.120 | 3.00 |
| Vault only | 0.061 | 1.53 |
| Vault + foamed fill to crown (0.183 m at 800 kg/m³) | 0.061 | 2.97 |
| Vault + foamed fill + 50 mm topping | 0.111 | 4.22 |
| Vault + raised floor (29 kg/m², Oval et al. 2023) + 50 mm topping | 0.111 | 3.06 |

So, with fill to the crown and a 50 mm topping, the shell floor is heavier than the slab it replaces and uses almost the same concrete. The vault alone saves half the concrete and half the weight; the fill takes back the weight, and the topping takes back the concrete. The steel saving is real in every case: the slab carries 5.6 kg/m² of bars (Day 12) and the secondary beams go, against a light mesh and the ties.

What this means [J]:

- **H1 is at risk, not safe.** The whole-building saving may be close to zero, or negative, for the fill-and-topping variants. H1 stays as written (it is frozen), but the family must include the low-rise and no-fill variants, or the result will only show that this floor fails here.
- **H2 depends on mass, and the fill is mass.** If the fill makes the floor heavier, the seismic weight goes up, not down, and H2 turns round. The fill density, the rise and the levelling option are therefore the first variables of the family, ahead of thickness.
- **H3 is the topping question,** and the table already shows the size of it: 50 mm of topping is 0.05 m³/m², about 40 % of the anchor slab's concrete.
- **The fair baseline.** The charter compares against the best code-compliant conventional floor. A 120 mm slab on secondary beams may well be that floor for a 6.6 m by 7.2 m grid. The shell floor could look better against a flat slab without secondary beams, but that would be the wrong comparison.

Two ways to give the shell a fair chance, both within the charter [J]: a low rise (f / L near 1/20) with a raised floor and no fill, and a thinner shell if Day 25 shows that normal-strength concrete with mesh can go below 60 mm. Both go into the Day 26 floor library.

## 7. Storey height

The frame beams are 600 mm deep (spec M1). If the vault springs 100 mm above the beam soffit and its crown sits at the beam top, the rise available inside the beam depth is about 0.6 − 0.1 − t ≈ 0.44 m for t = 60 mm, or f / L ≈ 1/15 at 6.6 m [J]. A flatter vault needs no extra height. A steeper one (1/8 to 1/12) rises above the beam top by f − 0.44 m, and the storey height grows by that amount plus any topping and raised-floor depth above the anchor's 120 mm slab. A taller storey makes the columns longer and adds façade area (outside the boundary, but a reviewer will ask) [J]. In the model the extra height changes the column length, the period and the wind load; the generator takes it as Δh = max(0, f + t − 0.5 m) + t_top + h_raised − 0.12 m [J].

## 8. Decisions by the author (30 Oct 2026)

1. **Concept approved**, and PR #77 to be merged.
2. **Layout A**: vaults span along the building between the transverse frame beams, 6.0 / 6.6 m. The author's reason: shorter spans keep the thrust and the required rise smaller, reduce the fill volume, and match the drawn bay widths more cleanly than the 7.2 m direction.
3. **All three levelling options stay in the family**: foamed-concrete fill, recycled-aggregate fill, and a raised floor with no structural fill.
4. **Rise-to-span 1/8 to 1/20**, and the low-rise end (about 1/15 to 1/20) must be included, so that H1 and H2 are not failed by the weight of the fill alone.
5. **Unreinforced shell dropped.** Light reinforcement is required for handling, crack control and robustness. GB 50010 Appendix D cl. D.1.1 also rules it out (section 4.2).
6. **Code clauses.** The author could not confirm them, so the AI assistant checked the four GB 50010 items in the author's uploaded English translation:

| Item | Status |
|---|---|
| GB 50010 Table 4.2.3-1, f_y = 360 N/mm² for HRB400 | ✓ Checked, p. 21-22 |
| GB 50010 Table 8.2.1, cover for shells | ✓ Checked: 15 mm (category I), 20 mm (II-a), p. 95-96 |
| GB 50010 cl. 8.5.1, minimum steel | ✓ Checked: Table 8.5.1 note 2, max(0.15 %, 45 f_t / f_y) = 0.214 %, p. 101-102; applied to the shell as a slab [J] |
| GB 50010 Appendix D, plain concrete | ✓ Checked: cl. D.1.1 forbids plain flexural members that carry live load |
| GB 50011 / JGJ 3, topping for a rigid diaphragm | Still [?]. Neither code is in the project files. Needed before Day 27 |

7. **Red-team point accepted.** The family must contain the no-fill and raised-floor cases.

## CalculiX

CalculiX 2.21 runs in the cloud container (`ccx -v`: "This is Version 2.21"). `src/shellbench/calculix.py` writes a deck, runs it and reads the displacements back. Its smoke test is a 1.0 m cantilever strip of 20 × 2 S8R shell elements (t = 10 mm, E = 30 GPa, ν = 0) under a 10 N tip load: CalculiX gives 13.334 mm against P L³ / (3 E I) = 13.333 mm, a difference of 0.005 %. The test (`tests/test_calculix.py`) now also runs in CI. The author's environment pins CalculiX 2.23 (environment.yml); /sync confirms that version runs on the laptop. The shell benchmark proper is Day 24, below.

## Shell benchmarks (Day 24, 2 Nov 2026)

`src/shellbench/shellfe.py` writes the S8R deck, runs ccx and reads displacements, stresses and buckling factors. `tests/test_benchmarks.py` runs both problems of MacNeal and Harder (1985) from `validation/benchmarks.csv`, where every value carries its page. CalculiX 2.23 on the laptop gives:

| Elements per side of the patch | Roof, u / 0.3024 | Hemisphere, u / 0.0940 |
|---|---|---|
| 4 | 1.0028 | 0.7769 |
| 8 | 0.9985 | 0.9906 |
| 16 | 0.9984 | 0.9965 |

Both finest meshes are within the 2 % Done-when. The figure is `figures/benchmarks_convergence.png`; the numbers are in `results/benchmarks_convergence.csv`.

1. **Where the values came from.** On 2 Nov the author waived the copy-by-hand step and told the AI assistant to find the values. They were read from a third-party copy of the paper on a University of Modena server. The licence of that copy was not verified, so neither the file nor its link is in this repo. Pages are the paper's own (PDF page + 2). The 40° half-angle, the 18° hole and F = 2.0 were read from the drawings in Figs 8 and 9. COMSOL's and Altair's verification pages agree on the roof data. Pages should be checked against the publisher's version before Paper 1 cites them [?].
2. **Reference values.** The test normalises by the values the paper itself normalises by: 0.3024 and 0.0940. Table 5 also quotes 0.3086 for the roof (reference [5]) and 0.0924 for the hemisphere with the hole closed (reference [7]). The roof result is 2.2 % below 0.3086 by arithmetic, so the choice of reference matters and Paper 1 should state it.
3. **F = 2.0 "(on quadrant)".** Fig. 9 prints this label. It is taken as the force at each of the four points of the whole shell [J]. That gives 0.0937 on the finest mesh. Taking 2.0 as a quadrant's half share of each point would double the force and give about 0.187, which contradicts Table 5(b).
4. **Whole models, no rotational supports.** CalculiX expands S8R shells to solids. Rotational supports on symmetry lines made the shell far too stiff: the quarter roof settled at 0.13 of the reference and the hemisphere at about 0.024, however fine the mesh. Both problems are therefore modelled whole, with translational supports that carry no reaction. Elements per side still counts the patch the paper meshes, so 16 means 32 × 32 on the roof and 16 × 64 on the sphere. **This matters for Day 25:** a floor panel must not rely on rotational restraint along a symmetry line in S8R [J].
5. **Read-back.** A flat strip checks the other two outputs against closed forms: stress in tension against F / (b t), buckling against π² E I / L² within 2 %. The strip's values are chosen for the test, not taken from a source.

## Panel sizing (Day 25, 3 Nov 2026)

`src/shellbench/panel.py` sizes one vault panel: a 6.6 m span, f/L = 1/15 and one 1.2 m tie bay, modelled in S8R through `shellfe.py`. Springing A is pinned and B sits on a roller. Four linear runs give the tie force by compatibility: self-weight, 1 Pa of plan load on the full span, 1 Pa on half the span, and a unit inward edge force. All results are in `results/panel_day25.csv`, and `tests/test_panel.py` checks them.

1. **Done-when.** With a rigid tie, the FE thrust is between 0.994 and 0.997 of wL²/8f in all 24 rows. The Done-when asks for 10 %.
2. **Unstressed ties fail.** Tie stretch lowers the thrust by 4-17 %. The lost thrust turns into bending, and the pattern-load section check fails at every trial thickness, even with a 32 mm tie. A tie prestressed to hold the dead-load spread at zero passes, because only the live load then stretches it. The author approved prestressed ties on 3 Nov 2026.
3. **Section check (corrected 3 Nov 2026).** JGJ 22-2012 3.2.1 says shell resistance is calculated to GB 50010, with γRE = 1.0 for shells. The check is therefore GB 50010-2010 6.2.17 (rectangular section, eccentric compression), with the mesh at mid-depth. It includes the additional eccentricity e_a = max(20 mm, t/30) from 6.2.5. GB 50010 6.2.3 does not allow second-order moments to be ignored here, so the moment is multiplied by 1/(1 − 1/λ), where λ is the FE buckling factor [J]. At 60 mm, e_a is a third of the thickness, and the earlier 60 mm result no longer holds.
4. **Sized panel.** t = 90 mm with prestressed ties every 1.2 m. This is the thinnest trial thickness at which all three levelling options pass. At 80 mm, recycled fill reaches a pattern utilisation of 1.003.

| Levelling | Tie (mm) | Pattern utilisation | Buckling factor | Tie steel (kg/m²) |
|---|---|---|---|---|
| Foamed fill | 25 | 0.978 | 14.7 | 3.21 |
| Recycled fill | 25 | 0.958 | 13.2 | 3.21 |
| Raised floor | 28 | 0.954 | 16.7 | 4.03 |

   All three options at 90 mm use 0.0911 m³/m² of concrete and 3.06 kg/m² of mesh, which is 1.5 times the concrete of the withdrawn 60 mm result. This feeds directly into the red team in §6.
5. **Clauses behind the constants.** All are from GB 50010-2010:
   - ν = 0.2: 4.1.5 (not 4.1.8)
   - E_s = 2.00 × 10⁵ N/mm² for HRB400: Table 4.2.5
   - α1 = 1.0 and β1 = 0.8 for grades up to C50: 6.2.6
   - εcu: 6.2.1-5, capped at 0.0033
   - ξb: formula 6.2.7-1, computed in the code as 0.5176
   - e_a: 6.2.5
   - minimum shell thickness of 50 mm: JGJ 22-2012 3.3.2
   - g: there is no code clause. Standard gravity is 9.80665 m/s² (3rd CGPM 1901, Declaration 2), rounded to 9.81 [J].

   The clauses were read on 3 Nov in third-party web copies, of the 2015 and 2024 editions. Their licence was not checked, so the copies and their links are not in this repo. The author checked each clause against their own copies of the codes on 3 Nov 2026.
6. **Limits.**
   - Buckling uses linear eigenvalues, with no imperfection knock-down.
   - JGJ 22-2012 3.2.9 requires a stability check. For non-uniform loads it calls for a dedicated stability analysis. That analysis has not been done.
   - JGJ 22-2012 gives no stability formula for cylindrical shells. Its contents list stability checks only in 5.3 (rotational shells) and 6.4 (double-curved shallow shells). Chapter 7 (cylindrical shells) has none. The 3.2.9 requirement for a dedicated analysis therefore governs this vault [J]. Checked in a third-party contents page on 3 Nov 2026; the author checked it against their own copy the same day.
   - The 6.2.4 member formula for second-order moments is replaced here by the FE-based amplifier [J].
   - A two-layer mesh might allow a thinner shell. It is a design change for Day 26 [J].

## Sources read for this note (Day 25 additions)

- GB 50010-2010 (2015 edition), clauses 4.1.1, 4.1.5, 4.2.5, 6.2.1, 6.2.3, 6.2.5-6.2.7; GB 50010-2010 (2024 edition), 6.2.17 (formula images); JGJ 22-2012, 3.2.1, 3.2.9, 3.3.2. All were read on 3 Nov 2026 in third-party web copies, which are not linked here.
- BIPM, Declaration 2 of the 3rd CGPM (1901): <https://www.bipm.org/en/committees/cg/cgpm/3-1901/resolution-2>.

## Sources read for this note

The texts came from open copies. The papers' own page numbers are given where the copy shows them. The direct PDF download failed today, so I read text extracted from each PDF; the author should check each page number against the PDF before Paper 1 cites it [?].

- MacNeal RH, Harder RL (1985). A proposed standard set of problems to test finite element accuracy. *Finite Elements in Analysis and Design* 1(1), 3-20. https://doi.org/10.1016/0168-874X(85)90003-4. Paywalled; read as described under Shell benchmarks, item 1.
- Hawkins W, Orr J, Shepherd P, Ibell T (2019, online 2018). Design, construction and testing of a low carbon thin-shell concrete flooring system. *Structures* 18, 60-71. https://doi.org/10.1016/j.istruc.2018.10.006. Accepted manuscript, University of Bath: https://purehost.bath.ac.uk/ws/files/187512150/Author_Accepted.pdf. Cited by section; the extracted text had no page numbers.
- Hawkins W, Orr J, Ibell T, Shepherd P (2020). A design methodology to reduce the embodied carbon of concrete buildings using thin-shell floors. *Engineering Structures* 207, 110195. https://doi.org/10.1016/j.engstruct.2020.110195. Accepted manuscript: https://researchportal.bath.ac.uk/files/203056865/Accepted_manuscript.pdf. Pages are AAM pages.
- Oval R, Nuh M, Costa E, et al. (2023). A prototype low-carbon segmented concrete shell building floor system. *Structures* 49. https://doi.org/10.1016/j.istruc.2023.01.063. Accepted manuscript: https://purehost.bath.ac.uk/ws/files/266267594/AuthorAccepted_small.pdf. Pages as in docs/gap_matrix.md (AAM).
- Liew A, López López D, Van Mele T, Block P (2017). Design, fabrication and testing of a prototype, thin-vaulted, unreinforced concrete floor. *Engineering Structures* 137, 323-335. https://doi.org/10.1016/j.engstruct.2017.01.075. Only the abstract, highlights and introduction are open; the full text is paywalled, so no other value is taken from it.

Not used, and why: Jayasinghe et al. (2021, 2022) compare conventional floors (flat, troughed, hollowcore and others) and give no shell geometry; they matter for the baseline argument in section 6, not for this concept. Reksowardojo et al. (2023) study rib-stiffened slabs with adaptive tensioning, a different system. Hawkins (2018) and Liew et al. (2017) are older than the 2020-2026 window; they are cited as method foundations, as allowed for the gap matrix.

© 2026 Syed Nafiz Reja Hasib. All rights reserved.
