# Paper 1 core (academic-manuscript-workflow §1, §12 steps 1-2)

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

Status: 6 Nov 2026. A core file, not prose for the paper. Items 1, 3 and 5 are taken from the author's own approved wording (charter, research_question.md, gap_matrix.md) and are the author's to rewrite. Items 2, 4, 6 and 7 are the professor-mode test (workflow §1) and are the AI assistant's, marked (judgement). The headline number stays (unverified) until the H1-H3 verdicts are frozen (schedule: 12 Nov).

## 1. Contribution in one sentence (author's to rewrite)

Built from research_question.md (22 Oct 2026) and charter contribution 1:

> We design one GB 50010 / GB 50011 RC frame office twice, once with a conventional floor and once with a tied thin-shell floor, across 3-8 storeys and PGA 0.05-0.40 g. We then measure how much of the floor's A1-A3 embodied-carbon saving is left at whole-building level, after the frame is redesigned for the lighter floor and the ties, levelling, topping and diaphragm needs are counted.

Humanizer pass, 6 Nov 2026 (academic-humanizer Layers 1-4): one 63-word sentence split into two (Layer 2.11); "this study" changed to "we" (Layer 3 and writing skill §6); "the same ... office" changed to "one ... office ... twice" so the comparison is explicit; the order of the two conditions after "once" now matches the order in which the method applies them. No number, clause or citation changed.

Who cites it, and for what (judgement): shell-floor researchers (Hawkins et al. 2020; Oval et al. 2023), for the first seismic-frame boundary on their floors; seismic-carbon reviewers (Krieg et al. 2026), as a case where the floor is designed, not held fixed; and anyone using the open generator to test another floor system.

## 2. Professor-mode answers (judgement)

| Test (workflow §1) | Answer now | Weak point |
|---|---|---|
| 1. Contribution | Item 1. | "First" claims need the gap-matrix search behind them, with pages. No "novel" or "first" without it. |
| 2. Evidence quantified | S_f and S_b for every building, min/median/max, per element; factor sensitivity (C1). | Single factor set; no uncertainty band, only bounds. Elastic, code-level only. |
| 3. Strongest counter-argument | See item 6. | |
| 4. Alternatives and falsification | H1 is falsified if S_b ≤ 0 in more than 10 % of buildings; H2 if the trend is flat or negative; H3 if the untopped floor passes in most buildings. Alternative explanation for any saving: a lean or heavy conventional baseline, not the floor itself. The primary baseline (best code-compliant conventional floor) is the control for this. | The pilot shows the floor share of carbon is about 0.50 (Day 20, building_v2), so S_b cannot exceed about half of S_f before the lateral knock-on [J, arithmetic]. |
| 5. Validation | Anchor against the thesis; pilot hand checks; MacNeal-Harder within 2 %; closed-form thrust; spot checks. | Hand-drift gap at 0.30-0.40 g; grade-I family rows not yet credible (Day 20). |
| 6. Feasibility | Free tools; the build ends 13 Nov. | The take-off scope, the shell floor in the generator (Day 29) and the diaphragm check (Day 27) are not built yet. |
| 7. Story fit | Lightweight structure under seismic demand, cutting carbon, by computation. Fits. | |

## 3. Gap (from gap_matrix.md G1-G3; author's to rewrite)

- **Gap in one sentence (writing skill §1; author's to rewrite):** No study in our search (gap_matrix.md, 2020-2026) measures how much of a thin-shell floor's embodied-carbon saving survives in a code-designed RC frame in a seismic region, where the frame is redesigned for the lighter floor and the floor's own ties, levelling, topping and diaphragm needs are counted (G1-G3).
  - Humanizer pass, 6 Nov 2026: "no study has measured" became "no study in our search ... measures" (Layer 4: the verb must not be stronger than the evidence, which is a documented search, not proof of absence). The context moved after the verb so the sentence leads with the claim. Still one sentence, as §1 asks; at 52 words it is long, so the Introduction should split it (judgement).
- Context + variable + outcome: code-designed RC frames in seismic regions + thin-shell floor replacing the slab + whole-building A1-A3 embodied carbon.
- Gap type (judgement): an **evidence and methodological gap**. Shell-floor studies 2020-2026 are gravity-only and hold the frame fixed (rows 1, 4, 5, 8, 9). Seismic-carbon studies hold the floor fixed (row 12) or do not design it (rows 13, 14). Row 10 assumes seismic loads would not change its floor ranking. No study found combines a designed shell floor, a seismically redesigned frame and carbon (gap_matrix G1, G3).
- Why it matters: floors are the largest share of structural embodied carbon (42 %, row 17), and seismic base shear scales with mass (row 15). Ties, fill and topping add material back. So neither the sign nor the size of the whole-building saving can be read from floor-level studies.
- Page numbers: every claim above is a row in docs/gap_matrix.md, which carries the pages. The Introduction cites those pages, not this summary.

## 4. Master narrative (judgement)

Lead candidates (workflow §1): **quantify costs and benefits** (the saving and each penalty, split by element), with **expose an unintended consequence** as the second line if ties, fill or topping take back a large share. The lead is chosen after the verdicts, from what the data support, not before.

## 5. Headline result

(unverified) Waits for the frozen H1-H3 verdicts on the DOI data (12 Nov). It will read: "The whole-building saving was X-Y % (median Z %) against the best conventional floor, compared with a floor-level saving of A-B %, under the stated assumptions." No number goes here before then.

## 6. Strongest Reviewer 2 objection and the answer (judgement)

**Objection.** "The baseline is a 120 mm slab on beams, the family is 36 buildings on one plan, and the analysis is elastic. The result is one building type, not a general finding."

**Answer.**
- The lean baseline is deliberate. It is the hardest fair comparison, and the paper says the literature's 48-58 % savings came against long-span flat slabs (floor_concept §6).
- The 36 buildings are a controlled sweep over storey count and PGA, so the trend is the result, not a population mean.
- The open generator lets others rerun the same test on their own plan and floor.
- Elastic, code-level design is how these buildings are designed in practice under GB 50011. The paper claims nothing about collapse safety.

## 7. Five-journal shortlist (workflow §5)

Publication goal (judgement): reach the people who design and assess floors in seismic regions, with a citable dataset, at no cost.

| Role | Journal | Why | Checked |
|---|---|---|---|
| Target | Journal of Building Engineering (Elsevier) | Charter first choice; scope names seismic hazards and innovative structural components (q1_standards §1); cited rows 11, 20 published there | Q1, SJR 2025 1.703 (q1_standards S2); abstract ≤ 250 words, 3-5 highlights ≤ 85 characters. Subscription (no-fee) route (unverified), confirm on the Guide for Authors at submission |
| Reach | Engineering Structures (Elsevier) | Charter fallback; the shell papers rows 1 and Liew et al. (2017) published there | Quartile and no-fee route (unverified) |
| Safe | Journal of Cleaner Production (Elsevier) | Charter list; rows 2 and 4 published there | Quartile and no-fee route (unverified) |
| Specialist | Bulletin of Earthquake Engineering (Springer) | Charter list; rows 16 and 23 published there | Quartile and no-fee route (unverified); Springer AI rules (q1_standards §3) |
| Speed | (unverified) | Not chosen. Structures (Elsevier) was ruled out of scope earlier, which is why the writing skill's "Structures second" is not used | Author decides, or the shortlist stays at four |

## 7a. Article type and three JBE papers to model (writing skill §1)

- Article type: research article (ScienceDirect labels JBE papers "Research article"; the Guide for Authors article-type list is to be checked at submission (unverified)).
- Three recent JBE papers to model for structure and reporting, found and checked against Crossref on 6 Nov 2026. These are models of how JBE reports this kind of study; they are not yet in the gap matrix and the author has not opened them:

| Paper | DOI | Why model it | Open copy |
|---|---|---|---|
| Zhang, Wen, Niu, Han, Li, Guo, Lv (2025). Low embodied carbon optimization design of concrete frame structures. JBE 111, 113213 | 10.1016/j.jobe.2025.113213 | Closest method: carbon-driven design of concrete frames, reported in JBE | SSRN preprint 10.2139/ssrn.4918421 |
| Chang, Ma, Chiang, Lai (2025). The effects of structural design alternatives on the embodied carbon emissions of steel buildings. JBE 99, 111603 | 10.1016/j.jobe.2024.111603 | Same question shape (design alternative against whole-building embodied carbon), steel instead of RC | (unverified) |
| Krieg, Rodgers, Pujol et al. (2026). The environmental impact of earthquake resilience: a quantitative review of embodied carbon and seismic design. JBE 130, 117119 | 10.1016/j.jobe.2026.117119 | Already gap_matrix row 11; how JBE frames seismic carbon and what its readers expect reported | Yes (reading_list) |

Action for the author: open the first two and decide whether either belongs in the gap matrix. A paper read only as a model is not cited for any claim.

## 8. Frozen names (workflow §12 step 2)

- Repository: syednafizreja/ShellBench. Package: `shellbench`. Never renamed (workflow §7).
- Working title (judgement), to be rewritten last (writing order): "Whole-building embodied carbon of thin-shell concrete floors in seismically designed reinforced concrete frames".
- CITATION.cff title "ShellBench" is the software's title, not the paper's. The paper is cited from the README with its own title when submitted (judgement).

## 9. Figure and table list (status 16 Nov 2026)

Every figure is made by a script in the repo from results/ (q1_standards R9). Paper copies: figures/paper/ (`python -m shellbench.figures`). Tables: paper/paper1/tables/ as CSV and booktabs LaTeX (`python scripts/paper1_tables.py`, checked by tests/test_paper1_tables.py). (judgement) on the choice and order.

| # | What | File | Status |
|---|---|---|---|
| Fig. 1 | Workflow: anchor, generator, floor library, family, carbon, hypotheses | README mermaid diagram (draft) | Schematic still to draw for the journal |
| Fig. 2 | Floor build-up section and layout A plan | none | Schematic still to draw (docs/floor_concept.md gives the dimensions) |
| Fig. 3 | Anchor validation | anchor_waterfall, anchor_seismic_compare, anchor_quantities, anchor_carbon | Done; Table 1 carries the numbers |
| Fig. 4 | S_f against S_b per building (H1) | verdict_h1 | Done |
| Fig. 5 | S_b against PGA and storeys (H2) | verdict_h2 | Done |
| Fig. 6 | Saving split per building: floor saving and lateral-system saving [kgCO2e/m2] | verdict_split | Done; medians 8.26 and -2.53. Tie, levelling and topping penalties are inside the floor term, not drawn apart (judgement) |
| Fig. 7 | Topping needed and its share R (H3) | none | Dropped (judgement): R = 0 in all 33 buildings, so the Table 5 H3 row says it in one line |
| Fig. 8 | Factor sensitivity (C1) | verdict_sensitivity | Done |
| Fig. S1-S3 | Surrogate (H4) | surrogate_parity, surrogate_coverage, surrogate_decision | Done (supplementary or Paper 2) |
| Fig. S4 | Shell benchmark convergence | benchmarks_convergence | Done |
| Table 1 | Anchor validation | table1_anchor_validation | Done |
| Table 2 | Floor library summary by span | table2_floor_library | Done |
| Table 3 | Carbon factors with page | table3_carbon_factors | Done; official-copy check recorded in data/carbon_factors.csv |
| Table 4 | Shell benchmark convergence | table4_benchmarks | Done |
| Table 5 | H1-H4 verdicts | table5_verdicts | Done |

## 10. Gaps against the workflow's verification standard (§2)

| Workflow requirement | ShellBench now | Action |
|---|---|---|
| One command reproduces everything, plus a fast self-test | Done: `scripts/reproduce.py` and `--quick` (16 Nov 2026 status) | Build thread: add a single `run_all` entry point before the DOI (11 Nov) (judgement) |
| Fixed random seed; versions in the output | Done: H2 permutation test uses seed `provenance.SEED` (src/shellbench/verdicts.py) | Fix the seed in the analysis script when it is written; write package versions into the results file |
| Closed-form checks | Done (thrust, cantilever, benchmarks) | None |
| Mesh convergence | Done for the benchmarks; panel mesh convergence (unverified) | Check floorlib mesh doubling before Methods 2.4 |
| Sensitivity | C1 factor sensitivity; beam I 1.5; drift rule | Monte Carlo is not used (C1, skills_check C7) |
| Decompose the headline into channels | Done: Fig. 6 (verdict_split) | Results |
| Regression tests on headline numbers | Done: tests/test_verdicts.py, test_paper1_tables.py, test_checksums.py | None |
| Ratios where absolutes are uncertain | S_b is a ratio already | State it in the abstract and conclusion |
