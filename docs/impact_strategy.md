# Impact and reuse strategy (25 Oct 2026)

This note answers a question the author raised on 25 Oct 2026: is ShellBench too tied to the author's own thesis building to be used and cited by others, and should the work be made general and public? It sets out what the charter already covers, what actually limits reuse, and which additions fit inside the charter without moving a date. Items that do not fit are parked in `LOG.md` under "Later" and wait for the author's answer.

[J] = judgement. [?] = not yet checked against a primary source. Time costs are estimates [J].

## Short answer

The worry is half right. The anchor report on its own is a single-building study and few people will cite it. But the anchor was never meant to be the product. It is the validation case. The products are the generator, the 2,000-building family, the floor plug-in and the dataset, and those are already planned as open outputs (MIT code, CC BY 4.0 dataset on Zenodo, JOSS).

So the study does not need a new public version. It needs to be built and presented so that a stranger can pick it up, run it on their own building or floor, and check their own code against ours. That is mostly a matter of how we do Weeks 3 to 8, not extra outputs.

The thesis building is actually the strongest part of the reuse story [J]. Most parametric carbon studies have no independent design to check their generator against. Ours has a complete hand design, with every disagreement written down (flags D1-D21). That is what lets someone trust the family.

## What the charter already covers

| Reuse need | Already planned | Where |
|---|---|---|
| Open code anyone can run | MIT licence, public repo, tests in CI | `LICENSE`, `.github/workflows/tests.yml` |
| Other floor systems can be added | Floor type is a plug-in | Charter, Layer 3 |
| Results beyond one building | Family of about 2,000 code-designed buildings, 3-8 storeys, PGA sweep 0.05-0.40 g | Charter, `docs/research_question.md` |
| Citable data | Zenodo dataset with DOI by 20 Nov, CC BY 4.0 | Charter |
| Citable software | v1.0 software DOI by 13 Dec; JOSS from 19 Apr 2027 | Charter |
| Fair comparison | Best code-compliant conventional floor as the baseline | `docs/goal_stress_test.md`, H2 fix |
| Carbon factor sensitivity | Chinese factors primary, ICE as sensitivity | `docs/goal_stress_test.md`, H6 fix |
| Early visibility | Paper 1 preprint at submission | README roadmap, Week 6 |

## What actually limits reuse (red team)

1. **Presentation, not substance.** The README and the papers start from "the author's thesis building". A reader then files the work as a case study. The fix is framing: the thesis building is validation case 0, and the method and family are the result.
2. **Hard-wired inputs.** If the generator holds thesis numbers in its code, nobody can run it on their own building without editing source files. This is the biggest practical barrier and it is decided in the first days of Week 3.
3. **One design code and one country's carbon factors.** A reader in Europe or the US may see GB 50010/50011 and Chinese factors and stop. A second code is outside the charter. What we can do inside it is make the carbon factors a swappable input file and keep every code clause in one module, so the work is transferable in principle and the limitation is honest.
4. **A plug-in nobody else can write.** "Floor type is a plug-in" means little unless the interface is written down and tested on more than one floor. The conventional baselines we already need (flat slab, and one ribbed or hollow-core floor) can be the first plug-ins, so the interface is proven before anyone else touches it.
5. **A dataset without a datasheet.** 2,000 rows with unclear units, missing failed designs and no record of how each row was made will not be reused. Documentation is what turns a file into a dataset.
6. **No reference answers.** The name promises a benchmark. MacNeal and Harder (1985) is still cited because it gives fixed problems with known answers that everyone checks their elements against. ShellBench can do the same for whole-building floor comparisons, with a small published set of reference buildings and their full intermediate results.

## Additions adopted (in scope, no date moves)

Each item passed the drift test in the charter: it serves a dated output, it is in scope, it can be checked externally, it fits without moving a submission date, and a reviewer would notice if it were missing.

| # | Addition | Week | Serves | Cost [J] | Done when |
|---|---|---|---|---|---|
| A1 | Reframe the README and both paper introductions: the thesis building is validation case 0; the generator, family and floor interface are the result | 2 (README), 6 and 8 (papers) | Paper 1, Paper 2 | 1 h | README "Approach" says this; paper intros follow it |
| A2 | Building as data: the generator reads a building definition file (units in every key); the thesis building is one such file; no thesis numbers in generator code | 3 | Generator, dataset, v1.0 | 2-3 h, saves rework later | `generator` runs from a definition file; a test builds the thesis frame from its file |
| A3 | Floor plug-in contract: a written interface (inputs, outputs, checks) and a conformance test every floor must pass; the conventional baselines are implemented as plug-ins | 4 | Paper 1, v1.0, JOSS | 4 h | `docs/floor_plugin_contract.md` and a conformance test pass for at least three floors (flat slab, one ribbed or hollow-core, shell) |
| A4 | Carbon factors as data: each factor set is a file with source, version and table reference per row; the author copies the values from the primary sources | 2 (Day 12) | Anchor report, Paper 1 | 1 h | Factor files load by name; changing the file changes the result; no factor in code |
| A5 | Reference problems: a small fixed set (the anchor plus about six family members across storeys and PGA [J]) published with periods, base shear, member sizes, quantities and carbon by element | 5 | Dataset, Paper 1 | 4 h | A `reference_problems/` table in the dataset, with a test that the code reproduces it |
| A6 | Dataset documentation: datasheet (Gebru et al. 2021), data dictionary with units, FAIR checklist (Wilkinson et al. 2016); designs that fail a code check are kept and flagged, not dropped | 5 | Dataset DOI | 4 h | Datasheet and dictionary in the Zenodo record; every column defined |
| A7 | Software archiving from v0.1: Zenodo-GitHub link so every release gets a DOI; author ORCID in `CITATION.cff`; `preferred-citation` updated when Paper 1 appears (FAIR4RS, Barker et al. 2022) | 2 (before 31 Oct) | Anchor report, v1.0 | 20 min, author's hands | v0.1 release has a Zenodo DOI |
| A8 | One-command reproduction: a script that rebuilds every table and figure in Paper 1 (and later Paper 2) from the Zenodo dataset, named in the data availability statement | 6, 8 | Papers 1 and 2 | 3 h | A clean checkout plus the dataset reproduces the paper figures |
| A9 | JOSS readiness inside v1.0: statement of need, install guide, example usage, API docs, community guidelines (`CONTRIBUTING.md`, issue templates) | 8 | v1.0, JOSS | 4 h | JOSS review checklist items met at v1.0 [?] (check the current JOSS rules, including any minimum public-history period) |
| A10 | Two short tutorials: "reproduce the anchor" and "add your own floor" | 8 | v1.0, JOSS | 4 h | Both run end to end in CI |

Total about 28 h over seven weeks [J], spread inside work each week already does. If we fall behind, the charter priority holds (Paper 1, then dataset DOI, then anchor report, then Paper 2, then polish). Cut order for these items: A10 first, then the documentation parts of A9. A2, A3 and A4 are never cut, because adding them later means redoing the generator.

## Parked under Later (outside the charter)

These would add reach, but each adds a paper, a code or a week. They are logged in `LOG.md` under "Later" and wait for the author's decision.

| # | Idea | Why it is outside | Cost [J] | Would delay |
|---|---|---|---|---|
| L1 | Data descriptor paper (for example Data in Brief or Scientific Data) | Adds a third paper; both journals are open access with an article charge [?], which breaks the never-pay rule | About 1 week | Paper 2 (12 Dec) |
| L2 | Second design code module (Eurocode 8 or ASCE 7) | Second design code is out of scope | 2-3 weeks | Paper 1 (29 Nov) |
| L3 | More floor systems beyond the baselines (CLT, composite, voided slabs) | Widens the study | About 1 week each | Dataset DOI (20 Nov) |
| L4 | Documentation website, GUI or web app | Polish beyond v1.0 | 3-5 days | v1.0 (13 Dec) |
| L5 | Conference talk or webinar on the benchmark | Extra output | 2-3 days | Paper 2 |

A2, A3 and A4 keep the door open for L2 and L3 at almost no cost, so nothing is lost by parking them now.

## Open questions for the author

- When Paper 1 goes up as a preprint, should the LinkedIn series start linking to the repo and dataset? The current rule (25 Oct) shares no research details. A preprint makes the work public anyway, so the rule could relax then.
- Do you have an ORCID iD? A7 needs it.

## Sources

- Wilkinson, M.D. et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data* 3, 160018. https://doi.org/10.1038/sdata.2016.18 (open access)
- Barker, M. et al. (2022). Introducing the FAIR Principles for research software. *Scientific Data* 9, 622. https://doi.org/10.1038/s41597-022-01710-x (open access)
- Gebru, T. et al. (2021). Datasheets for datasets. *Communications of the ACM* 64(12), 86-92. https://doi.org/10.1145/3458723 (free preprint arXiv:1803.09010 [?], link not reachable from the cloud on 25 Oct)
- MacNeal, R.H. and Harder, R.L. (1985). A proposed standard set of problems to test finite element accuracy. *Finite Elements in Analysis and Design* 1(1), 3-20. https://doi.org/10.1016/0168-874X(85)90003-4 (pre-2020 method foundation, already in the charter; paywalled).

All four DOIs checked on Crossref, 25 Oct 2026. These are method references for how we document data and software; they are not literature claims about the research gap, so they do not go in `docs/gap_matrix.md`.
