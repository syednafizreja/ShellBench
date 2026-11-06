# Review panel: Methods skeleton (5 Nov 2026)

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

Panel (standing rule, 5 Nov 2026): research professor (research-method-playbook professor mode), hostile JBE Reviewer 2, and three PhD-level passes: structural and seismic design, LCA and carbon accounting, reproducibility and statistics. Each pass is checked against the author's manuscript skills (workflow §1-2, writing §1-9, humanizer Layer 4). The skeleton is an outline, so the voice passes (human-voice, humanizer Layers 1-3) run on the prose later.

Severity: **major** = a reviewer could reject on it; **minor** = must be fixed or disclosed; **note** = for the author's awareness.

| # | Pass | Finding | Severity | What was changed in the skeleton | Author action |
|---|---|---|---|---|---|
| P1 | Professor | The baseline is a lean 120 mm slab on beams, not the long-span flat slab of Hawkins et al. (2020) or Oval et al. (2023). Their 48-58 % savings cannot carry over, and a reader who expects them will read a small saving as failure. The narrative has to be "how much survives", which is the research question, not "shells save carbon". | major | 2.4 now requires the baseline difference to be stated before the results. | Keep this framing in your rough sentences. |
| P2 | Reviewer 2 | 36 buildings on one plan, one site class and one concrete grade. "Why should a designer elsewhere trust this?" | major | 2.6 frames the family as a controlled sweep, not a sample, and requires the limit to be stated. | Your answer to "36 is small" (rough sentence). |
| P3 | Statistics | H2 uses Spearman with a permutation test per slice. With n points the smallest exact two-sided p is 2/n!. The 0.40 g slice has 4 buildings (storeys 3-6, since 7 and 8 are outside Table 6.1.1), so its smallest p is 0.083 and it can never be significant at α = 0.05. Slices at 7 and 8 storeys have 5 points (smallest p 0.017). The verdict rule ("more than half of slices") is frozen and is not changed. Readers must be told before the result that one slice cannot pass. | minor | 2.8 now states the arithmetic. | None; disclosure only. Any failed building lowers n further, which Results must report. |
| P4 | LCA | anchor_report §5 and anchor_notes D29 say factor uncertainty is "carried by the planned Monte Carlo band". preregistration.md does not list that analysis, and skills_check C7 says no unplanned analysis. As written, the anchor report promises something the plan does not contain. | major | 2.7 flags it as an author decision. | **Decision 3 below.** |
| P5 | Structural | The take-off scope that gives S_b is not built yet (stirrups, footings, full-plan lateral elements). data_card row 4 says S_b is biased high until it is. Strong column/weak beam and shear checks are also not in the generator yet. | major | 2.3 and 2.7 say no S_b is quoted until both are closed. | None here; this work is with the day build thread. |
| P6 | Structural | The charter says the generator is "proven by reproducing my member sizes". Beams match (300 × 600); columns do not (500 against 600), because R5 uses the code values (decision 2, 31 Oct). The paper must not claim full reproduction. | minor | 2.3 states the column difference and its cause. | Confirm the wording in your rough sentences. |
| P7 | Seismic | The default rigid-diaphragm rule (in-plane deformation ≤ 2 × mean storey drift) comes from US practice. In a GB-code study a reviewer will ask why. Day 27 has not run. | major | 2.5 is blocked until Day 27, and the rule needs a primary source. | None now; Day 27 output. |
| P8 | Reproducibility | Pilot hand-check tolerances were set after the run. Codes, MacNeal-Harder values and some AAM pages were read in third-party copies. | minor | 2.9 table gets a "set before or after the run" column. 2.2, 2.4 list the [?] sources. | Your own-copy checks already logged stay on record; the remaining [?] items are listed in the skeleton. |
| P9 | Reviewer 2 | The thesis is unpublished, yet it is the anchor. "How can I check it?" | minor | 2.2 proposes citing the thesis plus the repo's validation files as the public record. | Confirm you are happy for the thesis tables used (not the thesis itself) to stay public in the repo. They already are. |
| P10 | Professor | Methods currently lists more than a JBE Methods section can carry (D-flags, clause readings, spot checks). | note | Length target set at about 3,000-3,500 words; detail moves to Supplementary Material. | None. |
| P11 | Skills check | Writing rule 0.1: from scratch, give an outline only. This file is an outline; no prose was written. | note | Rough-sentence prompts added to every subsection. | Send rough sentences. |

## Decision 3 (for the author): factor uncertainty

- **A (recommended).** Add a one-at-a-time factor sensitivity now, before any DOI-data result exists, as a dated entry in the preregistration change log. The bounds come only from rows already in Table D.0.1: concrete C30 and C50 around C40, and tie steel EAF (high) and BOF (low). It is a sensitivity, not an input to any verdict. It needs no new source and no factor from me, and it is cheap to run. Why: a single database with no uncertainty is the first thing an LCA reviewer attacks, and S_b is a ratio in which shared factors partly cancel, which the sensitivity will show.
- **B.** No factor sensitivity. Edit the anchor report and anchor_notes to remove "planned Monte Carlo", and state the single factor set as a limitation.

A full Monte Carlo is not offered, because it would need a distribution for each factor and there is no sourced one [J].

## Author's answers (6 Nov 2026)

- **Decision 3: A.** Logged as preregistration change log C1. anchor_report §5 and anchor_notes D29 updated so that no Monte Carlo is promised. P4 closed.
- **P6: confirmed.** The column difference is a deliberate code-based redesign. Wording in 2.3 corrected on one point: the axial-ratio limit is GB 50011 Table 6.3.6, but minimum longitudinal steel is GB 50010 Table 11.4.12-1, not GB 50011. P6 closed.

## Verdict of the panel

The skeleton is fit to draft from once the author's rough sentences arrive, except 2.5 (waits for Days 27 and 29) and the numbers in 2.7 (wait for the take-off scope). Four majors (P1, P2, P4, P7) need either the author's words or later build steps. None of them needs a change to H1-H4.
