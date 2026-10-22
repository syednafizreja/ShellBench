# Stress test of the ShellBench research goal (Day 4, 22 Oct 2026)

Purpose: attack our own research question the way a Q1 reviewer would, before we build anything. For each hole: what the problem is, the evidence, and the fix. [J] = my judgement. [?] = check in your copy of the code or paper.

Original question (charter, before 22 Oct 2026): what is the whole-building embodied carbon of thin-shell floors in a seismic RC frame designed to GB 50010 / GB 50011, anchored on the 4-storey Panzhihua frame (intensity 7, 0.10 g, site class II)?

## Originality check (done first)

- Searched OpenAlex (Fast_Track) and the open web for 2020-2026 work on thin-shell or vaulted floors in seismically designed buildings, and on lightweight floors and seismic knock-on carbon.
- Found **no paper** that designs thin-shell floors inside a seismic frame. The nearest work is gravity-only shells (gap matrix rows 4, 5, 8, 9), seismic EC with fixed floors (rows 12-14), and diaphragm studies on timber and masonry vaults (for example, Bull. Earthquake Eng. 2026, doi:10.1007/s10518-026-02623-5, not read [?]).
- Caveat: a zero count can be a vocabulary artefact. I will repeat the search with reviewers' words ("funicular floor", "vaulted slab", "diaphragm") before submission [J].

Verdict: the gap is real. The weak spots are in **how** we answer it, not **whether** it is new.

## Holes and fixes

| # | Hole (what a reviewer would say) | Evidence | Severity [J] | Fix |
|---|---|---|---|---|
| H1 | "At 0.10 g the earthquake hardly sizes anything, so your 'seismic knock-on' is close to zero. The paper's headline collapses." | Anchor columns are 600 × 600 with 4C22, already flagged as below the GB 50011 minimum (baseline_spec R1, B6). Minimum detailing, not seismic force, may govern. Krieg 2026 §6.4: EC rises sharply with PGA (+19% from 0.1 to 0.2 g) | **High** | Keep 0.10 g as the validated anchor, and add a **PGA sweep** with the same building: 0.05, 0.10, 0.15, 0.20, 0.30 and 0.40 g (intensities 6 to 9, GB 50011 Table 3.2.2 [?]). The result becomes "saving against seismic intensity", which turns a possible null result into a finding. This also answers Krieg 2026 §9.2.1 item 2 (sensitivity across seismic hazard levels) |
| H2 | "You compare a novel shell with a 1990s-style 120 mm beam-slab. Of course it wins. Compare with the best conventional floor." | Belizario-Silva 2025: beam-supported floors span 48-167 kgCO2/m². Jayasinghe 2022: conventional alternatives already save 21-36% | **High** | Use three baselines on the same grid and storey height: (a) anchor as built; (b) best code-compliant conventional floor (thinnest slab that passes GB 50010, plus one ribbed or hollow-core option); (c) shell variants. Report the shell saving against (b) as the honest number |
| H3 | "A shell with loose fill is not a rigid diaphragm. GB 50011 frame analysis assumes one. Your seismic design is invalid, or you need a topping slab that eats the saving." | Çelebi & Kırtel 2025: lower in-plane floor stiffness lengthened periods and changed the failure mode. No shell paper checks diaphragm action (rows 4-9) | **High**, and also our **main novelty** | Make the RC topping thickness a variable (for example 0, 40, 60 mm [J]). Model the floor's in-plane stiffness in OpenSeesPy, check diaphragm flexibility and periods, and report the carbon cost of making the shell floor seismically adequate. Check the rigid-floor and topping rules in your GB 50011 copy (§3.4, §6.1 [?]) |
| H4 | "Shells and ties under vertical earthquake?" | Çelebi & Kırtel 2025: vertical inertia doubled first-storey second-order effects | Medium (only at high intensity) | In the PGA sweep, include the vertical seismic action where GB 50011 requires it (§5.3, intensity 8-9, long-span [?]). Check the ties for it |
| H5 | "One building is a case study, not a result." | Krieg 2026 §9.2: most studies are single, regular buildings | Medium | Paper 1: anchor + PGA sweep + bay sweep (6.0 / 7.2 / 9.0 m) as a small factorial. Paper 2 (surrogate family) covers generality |
| H6 | "Why UK carbon factors for a building in China?" | Chinese standard GB/T 51366-2019 gives building carbon factors [?]; Gu et al. 2026 (doi:10.1007/s44290-026-00501-2) used Chinese bills of materials for Chinese slabs [not read] | Medium | Primary: Chinese factors (GB/T 51366 or CLCD [?]). Sensitivity: ICE v3. Add Monte Carlo on the factors so each saving has an uncertainty band |
| H7 | "Is your shell model right?" | We have no test of our own | Medium | Validate the shell FE against MacNeal-Harder benchmarks (shell week) and against the Hawkins et al. 2018 prototype test (pre-2020, method use only) |
| H8 | "Shell rise makes the floor deeper, so storeys get taller and columns longer." | Shell depth includes rise and fill (row 4 §3.3: overall height is a design output) | Low to medium | Fix floor-to-floor height at 3.6 m and check the clear height. If the shell needs more depth, count the extra column and facade height |
| H9 | "No one can build TRC shells in China, and there is no code for them." | GB 50010 does not cover textile-reinforced concrete [J] | Low (scope) | Frame it as a design study. Include an RC or fibre-concrete shell variant inside GB 50010 scope. State constructability, fire, acoustics and vibration as limitations (row 4 lists them) |

## Revised question (adopted by the author, 22 Oct 2026: all three fixes)

> How much does replacing conventional floors with thin-shell floors reduce the whole-building A1-A3 embodied carbon of an RC frame designed to GB 50010 / GB 50011, and how does that saving change with seismic intensity once diaphragm, tie and topping requirements are met?

What changes from the charter: the PGA sweep (H1), the fair baseline (H2) and the diaphragm/topping check (H3). The anchor building, the codes and the 0.10 g validation stay the same. Workload (corrected 22 Oct): the sweep is not compute only. At intensities 8 and 9 the frame's seismic grade changes (GB 50011 Table 6.1.2 [?]), so the design loop must apply grade-dependent detailing and axial-ratio limits, and the frame may need larger members. Build those rules into the redesign loop in week 3, not as an afterthought [J].

## What does not change

Gap statements G1-G4 stand. H1 and H3 make G1 and G3 sharper, because the paper would now say *when* seismic design matters for shell floors, not only *whether*.
