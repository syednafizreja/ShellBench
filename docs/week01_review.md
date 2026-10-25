# Week 1 review (19-25 Oct 2026)

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

Written on Day 7 (Sun 25 Oct 2026), the weekly review in the 8-Week Playbook (p. 10). It checks every Week 1 "Done when" line against a file in this repository, lists what carries into Week 2, and looks for weak points before the anchor report (due Sat 31 Oct, release v0.1). My judgement is marked [J]; anything unverified is marked [?].

## 1. Did Week 1 meet its goal?

The Week 1 issue (#1) asked for four things: a public repository with an audited baseline specification, thesis results typed into validation CSVs, a checked gap matrix, and the frame in OpenSeesPy matching the thesis gravity calculations. All four exist.

| Day | Playbook "Done when" | Met? | Evidence |
|---|---|---|---|
| 0 (18 Oct) | Environment and tools installed | Yes | LOG.md Day 0 |
| 1 (19 Oct) | Package layout, CLAUDE.md, week issues | Yes | LOG.md Day 1; issues #1-#8 |
| 2 (20 Oct) | Every model input listed with its source; inconsistencies decided | Yes | docs/baseline_spec.md (A1-A8, B1-B16, all decided by the author) |
| 3 (21 Oct) | Six CSVs; two hand checks match | Yes | validation/thesis_values/ (now eight CSVs); LOG.md Day 3 hand checks (D-value 0.3 %, drift row 1 explained) |
| 4 (22 Oct) | Gap matrix committed, every row ticked by the author | Yes | docs/gap_matrix.md (23 rows, all ticked, every row with a page); docs/research_question.md |
| 5 (23 Oct) | Dead-load comparison table; method vs mistake separated | Yes | results/anchor_gravity_dead.csv; docs/anchor_notes.md; flags D13-D15 |
| 6 (24 Oct) | Release v0.0.1; every difference above 10 % has a reason | Yes | release v0.0.1; results/anchor_gravity_live.csv and _combination.csv; flags D16-D21 accepted |

The repository is public (GitHub API returns 200 without a token, checked 25 Oct 2026). PRs #11-#37 were merged this week. The test suite passes: 64 passed on 25 Oct 2026 in a Linux cloud run (Python 3.13, OpenSeesPy 3.8.0.0), the same count as the Windows run on 24 Oct (Python 3.12, LOG.md Day 6).

## 2. What the week found about the thesis

Twenty-one flags (D1-D21) now sit in validation/thesis_values/README.md, each with the author's decision. Three kinds of finding matter for the anchor report:

- Arithmetic slips in the thesis tables. Joints A1 and B1-B4 in table 6.3 do not balance (D15, checked by hand at B4: −51.81 kN·m). Table 7.2 finals at floors 2-4 are not the sums of their columns (D18).
- Load-path inconsistencies. Three roof dead-load sets (Day 5), and live-load moments that match 2.0 kN/m² while shears match 2.5/3.0 kN/m² (D20).
- Combination factors. Table 8-13 used 1.0 D + 1.5 L, not the stated 1.3 D + 1.5 L (D16), and it is no longer a validation target. The thesis seismic factors (1.2/1.3) follow GB 50011-2010 cl. 5.4.1 but sit below GB 55002-2021 cl. 4.3.2 (D21).

None of these stops the anchor. They do mean the report must say clearly that the anchor reproduces the thesis method, including its stated loads, and that it does not certify the thesis numbers [J].

## 3. Weak points before Week 2 (red team)

These are the places a reviewer would push. Each one comes with what I suggest; the choices stay with the author.

**3.1 The wind tolerance must be fixed before the wind run.** Day 8 asks for a tolerance (for example 15 %) with a reason. If the number is chosen after seeing the drifts, it looks tuned. I suggest writing it in docs/anchor_notes.md first thing on Monday, with a reason that comes from the method: D7 already shows Table 8-2 Δu does not equal V/ΣD, so the thesis itself carries a few per cent of arithmetic noise [J].

**3.2 Table 8-12 is not a clean four-storey target.** Its shears are cumulative and every row includes the level-5 force of 98.29 kN (decision B4). A four-storey model with no fifth level cannot reproduce rows 1-4 as printed. Two honest options for Day 9 [J]: compare storey forces F_i (differences of consecutive shears) for levels 1-4, or add the level-5 force as a roof point load and say so. Either way the choice should be written down before the run.

**3.3 Separate stiffness from loading in the seismic check.** If the model's drifts differ from Table 8-12, two things could be wrong: the frame stiffness (the D-value method against a full frame analysis) or the seismic forces (period, α1, weights). Running the model twice separates them [J]: once with the thesis storey forces applied, which tests stiffness alone, and once with the forces seismic.py computes, which tests the force chain.

**3.4 There is no thesis period to compare with.** The Day 9 prompt says "use the value or formula my thesis used", but the thesis prints no T1, α1 or G_i (baseline_spec S7-S9, decision B9). The period comparison can only be a plausibility check. The primer in notes/gb50011_base_shear_primer.md back-calculates which periods are consistent with the printed base shear; a T1 near 0.55-0.65 s would fit a normal floor weight [J].

**3.5 Carbon factors are on the critical path.** Day 12 (Fri 30 Oct) needs factors for C30, C35, C40 and HRB400 from GB/T 51366-2019 (or the database it points to) and from the ICE database, copied by the author with source, page and unit. Claude must not supply them. If the copies of those sources are not to hand by Thursday, Day 12 and the 31 Oct report slip.

**3.6 Hypotheses file.** The project instructions say H1-H4 are frozen in docs/preregistration.md, but that file does not exist yet. The charter date for committing hypotheses is 4 Nov (Week 3). Nothing is late, but the file must be committed, unchanged in wording, before any family result exists.

**3.7 Week 2 is the heaviest week so far.** Six working days carry wind, seismic, response spectrum with a 3D check, design checks, carbon and the report. If a day overruns, the charter priority order applies (Paper 1, then dataset DOI, then anchor report). The 3D model on Day 10 is the item I would cut to a short note first [J].

## 4. Carried into Week 2

- Day 8: wind tolerance chosen and written before the run (3.1). Wind heights use 4.05 m in Table 8-1 (baseline_spec W7, B4); the model uses 4.55 m, so the comparison needs that note.
- Day 9: seismic.py with every constant checked in the author's copy of GB 50011 (primer clause list); decide on 3.2 and 3.3.
- Day 12: carbon factors from primary sources (3.5).
- Day 13: anchor report names flags D1-D21 and says what the anchor can and cannot claim.

## 5. Day 7 tasks themselves

- 10-question quiz on direct stiffness, load paths and D-values: set in the Claude app (quizzes stay in the app, CLAUDE.md "Sync with cloud Claude").
- Finished issues closed: Week 1 (#1) closed with a summary comment.
- LOG.md and docs/baseline_spec.md copied to the project files for the Claude Project.
- Learn for Monday: notes/gb50011_base_shear_primer.md.

Compliance: sources, none new; the primer's code values are marked [?] until checked in the author's copy of GB 50011. AI use: Claude drafted this review and the primer, and ran the tests; the author reviews both before either is cited. Numbers: every number traces to a thesis table, a repository file or an arithmetic step shown in the primer. Data: nothing confidential; thesis_source/ not tracked.

© 2026 Syed Nafiz Reja Hasib. All rights reserved.
