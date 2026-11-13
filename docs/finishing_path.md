# Finishing path for a paper (same route as ShellForm)

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

Added 14 Nov 2026 at the author's request ("make ShellBench follow the same path to finishing as ShellForm"). It replaces the older rule "the author writes, the AI assistant checks" for Paper 1 and Paper 2. The author's rule of 10 Nov 2026: the AI assistant writes the manuscript prose itself, in the author's voice (skills: academic-manuscript-writing, syed-academic-voice-dna, academic-humanizer); the author reads, changes and owns every sentence. No rough-sentence slots are handed to the author. The Elsevier generative-AI declaration says so.

ShellForm reached a complete, self-reviewed Computers & Structures manuscript in this order (ShellForm `paper/`, 10-14 Nov). Each step is one day's task with a Done-when line.

| Step | What the AI assistant does | Done when |
|---|---|---|
| 1. Core | `paper/paperN/00_core.md`: gap, contribution, headline number, narrative, Reviewer-2 objection, target journal | exists (Paper 1: done 6 Nov) |
| 2. Tables and figures | built by scripts from the frozen results; never edited by hand | every planned table and figure exists and names its tag |
| 3. Methods draft | `10_methods_draft.md`, prose in the author's voice; every number a `numbers.md` row | draft 1 committed |
| 4. Results draft | `11_results_draft.md`, ISCT per figure and table | draft 1 committed |
| 5. Discussion draft | `12_discussion_draft.md`: mechanism, strongest objection answered, design meaning, limits each with its remedy | draft 1 committed |
| 6. Literature search, Introduction | documented search (`13_literature_search.md`, queries, screening, inclusion), then `14_introduction_draft.md`; never "first" or "novel" | draft 1 committed |
| 7. Abstract, highlights, title, Conclusions | `15_abstract_conclusion_draft.md`; word and character limits counted by script against the journal guide | draft 1 committed |
| 8. Verification add-ons (optional) | cheap checks that strengthen the method without touching frozen results | results beside the frozen record |
| 9. Assemble | one LaTeX manuscript in `paper/paperN/manuscript/` (Elsevier `elsarticle`, the journal's reference style, line numbers), supplement, `highlights.txt`, `references.bib`; review marks [check] / [J] / [?] visible; PDFs committed | both PDFs build without errors |
| 10. Self-review | `16_self_review.md`: every number **recomputed from the result files** (not copied from `numbers.md`), every DOI checked against Crossref, cross-section consistency, claim-to-evidence, humanizer pass; fixes made, open items listed for the author | review committed, fixes in the manuscript |
| 11. Author check | the author reads the PDF, opens the [check] sources, accepts or cuts each [J], signs the statements | author's ticks |
| 12. Submit | cover letter, suggested reviewers, journal checklist | submitted |

Rules that carry over: frozen results are never edited; drafts are superseded once the manuscript is assembled (edit the .tex from then on); commit as the author with no the AI assistant attribution; every result names its tag.
