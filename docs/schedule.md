# Schedule: the 17 Nov plan with author check days (approved 28 Oct 2026)

Approved by the author on 28 Oct 2026, in two steps: "you must do it the best quality even under this time constraints" (the 17 Nov plan, PR #63), then "I should have a few days in hand to check things, so must finish few days earlier than the Claude Pro ends". This file replaces the PR #63 version from the next daily run.

## What changed from PR #63

- **All building ends on Sat 14 Nov.** **Sun 15 to Tue 17 Nov are the author's check days.** In them Claude only fixes what the author or the harsh review finds: no new analysis, no new results.
- **Dataset DOI moves from 12 to 11 Nov.** The 11 Nov spare day is used for it, and the check days take over as the plan's safety margin.
- **The surrogate study (Days 43-48), v1.0 and Paper 2 move to after 17 Nov.** They could only fit by squeezing the Paper 1 review or the check days. By the charter's priority order (Paper 1, then the dataset DOI, then the anchor report, then Paper 2), Paper 2 gives way [J].
- **v0.5 "Paper 1 release" on 14 Nov gets a software DOI** (Zenodo archives every release). v1.0 follows with Paper 2.

Nothing else changes. The two parallel build tracks of PR #63 stay: the shell floor module (Days 22-27) needs only the anchor's storey seismic force, so it runs alongside the generator (Days 15-21). Every Playbook "Done when" line stands, every GATE stays, and H1-H4 stay frozen.

## Where we stand on 28 Oct

Days 9, 10 and 11 are done (LOG.md). pytest 114 passed. Day 12 waits on the carbon factors (GATE).

## Charter dates

| Output | PR #63 plan | This plan | Note |
|---|---|---|---|
| Anchor report and v0.1 | 31 Oct | 31 Oct | Unchanged |
| Hypotheses and analysis plan | 3 Nov | 3 Nov | GATE: before any family row |
| Floor library and v0.3 (ShellForm early data) | 5 Nov | 5 Nov | Floor-level data for ShellForm from 6 Nov |
| Dataset DOI | 12 Nov | **11 Nov** | **ShellForm full start** |
| Paper 1 files ready | 17 Nov | 17 Nov, after the author's check days | |
| Paper 1 submitted | by 22 Nov | by 22 Nov | Author submits |
| Software release with DOI | v1.0, 17 Nov | **v0.5 "Paper 1 release", 14 Nov** | v1.0 comes with Paper 2 |
| Surrogate study, H4 verdict | 17 Nov | **after 17 Nov** | With every check, never rushed |
| Paper 2 submitted | 8 Dec | **8 Dec if Claude Pro renews; otherwise January 2027** | Playbook: Paper 2 can slip to January without harm |
| CV, statement, video | 13 Dec | 13 Dec | Author alone |
| JOSS | from 19 Apr 2027 | from 19 Apr 2027 | Unchanged |

## Day map, 29 Oct to 17 Nov

A day's date is the latest it may finish; work ahead is allowed. GATE days never start early.

| Date | Track A: anchor and generator | Track B: shell floor | Track C: Paper 1 |
|---|---|---|---|
| Thu 29 Oct | Day 12 quantities and carbon (GATE: carbon factors today) | | |
| Fri 30 Oct | Day 12 finish | Day 22 floor concept and CalculiX | |
| Sat 31 Oct | **Day 13 anchor report, v0.1** | Day 23 form-finding | |
| Sun 1 Nov | Day 14 review (half) + Day 15 design rules | Day 24 shell benchmark (GATE: MacNeal-Harder values) | |
| Mon 2 Nov | Day 16 generator reproduces the thesis | Day 24 finish (2 % on both benchmarks) | |
| Tue 3 Nov | **Day 17 pre-registration** (GATE) | Day 25 size one panel | |
| Wed 4 Nov | Day 18 batch runner | Day 26 floor library (60+ cases) | Methods: author starts drafting |
| Thu 5 Nov | Day 19 200-building pilot | **Day 27 diaphragm, topping rule, v0.3** | Methods continue |
| Fri 6 Nov | Day 20 v0.2, overnight run | Day 28 review (half). **ShellForm may start on the floor library** | Methods continue |
| Sat 7 Nov | Day 21 review (half) + Day 29 shell floor in the generator | | |
| Sun 8 Nov | Day 30 anchor headline number | | Day 36 skeleton and gap paragraph |
| Mon 9 Nov | Day 31 full family, both floors (overnight) | | Day 37 methods finished |
| Tue 10 Nov | Day 31 checks + data card | | |
| Wed 11 Nov | **Day 33 v0.4 and dataset DOI** (GATE: Day 31 checks). **ShellForm full start** | | |
| Thu 12 Nov | Day 32 H1-H3 verdicts on the published data + Day 33 sensitivities | | |
| Fri 13 Nov | Day 34 frozen figures | | Day 38 results |
| Sat 14 Nov | **v0.5 "Paper 1 release" with software DOI** | | Day 39 discussion and abstract; Day 40 harsh review |
| **Sun 15 Nov** | **Author check day** | | Day 41: fix the harsh review |
| **Mon 16 Nov** | **Author check day** | | Day 41: reference check, fix what the author finds |
| **Tue 17 Nov** | **Author check day** | | Day 41: every submission file ready |
| After 17 Nov | Surrogate study Days 43-48 and v1.0 | | Author: **Day 42 submit Paper 1 by 22 Nov**; Paper 2 (Days 50-55); profile, statement, video (Days 54, 56) |

## What the check days are for

The author checks, with Claude fixing only what is found:

1. Every number in Paper 1 against a results file (Day 38 rule), highlighted as checked.
2. The H1-H3 verdicts against docs/preregistration.md: the hypothesis text unchanged, each verdict with its number.
3. Three random family buildings checked by hand against the parquet files.
4. Every cited paper opened, with author, year, title, journal and DOI confirmed (Day 41 rule).
5. The harsh-review table in paper1/review_response.md: each comment answered.
6. The dataset record on Zenodo and the data card read as a stranger would.

## What the author must supply, and by when

This list is the real limit on the plan. A day's delay on any GATE item moves its track by a day, and then the check days shrink. If they would shrink below two days, Paper 1 moves (see the fallback rules); the checks do not.

| Item | Needed by | For |
|---|---|---|
| Carbon factors C30, C35, C40, HRB400 (GB/T 51366 and ICE) in data/carbon_factors.csv | Thu 29 Oct | Day 12 (GATE) |
| Zenodo-GitHub link and ORCID | Fri 30 Oct | v0.1 DOI |
| D26, D27 and the Day 11 hand checks | Fri 30 Oct | Anchor report |
| MacNeal and Harder (1985) reference values copied with page | Sat 31 Oct | Day 24 (GATE) |
| Approve the floor concept, including the fill material | Sat 31 Oct | Days 22-26 |
| Approve the design rules | Sun 1 Nov | Day 15 |
| Approve the analysis plan | Tue 3 Nov | Day 17 (GATE) |
| Pilot hand checks (three) | Thu 5 Nov | Day 19 |
| Topping rule decision with its source, and 5 library spot checks | Thu 5 Nov | Days 26-27 |
| Carbon factors for floor-only materials (fill, tie steel recycled-content high and low) [?] | Fri 6 Nov | Days 29 and 33 |
| Paper 1 methods draft (author's own words) | Mon 9 Nov | Day 37 |
| Zenodo dataset publish click | Wed 11 Nov | Dataset DOI |
| Rough sentences for results and discussion | Fri 13 Nov | Days 38-39 |
| Zenodo v0.5 release click | Sat 14 Nov | Software DOI |
| Check days | 15-17 Nov | See above |
| Paper 1 submission | by Sun 22 Nov | Day 42 |

## Fallback rules

- **Check on 6 Nov.** If v0.2 or v0.3 has slipped by one day, Days 31-33 move one day and the dataset DOI goes to 12 Nov; the check days become two (16-17 Nov). If it slips more, the DOI moves day for day, and Paper 1 moves to 29 Nov rather than losing its harsh review or its check days.
- **Check on 12 Nov.** If the dataset DOI is not out, the H1-H3 verdicts wait for it (they are written on the published data). Paper 1 then goes in on 29 Nov.
- **The check days are never given back to building.** If something is not built by 14 Nov, it moves after 17 Nov.
- A slipped day never shrinks the next one. A check is never cut to save a date.

## Risks [J]

- **The author is the bottleneck, not the code.** The first ten days need two approvals a day on some days. Late inputs move the plan; they do not rush it.
- **Results and discussion in two days (13-14 Nov).** The methods are drafted earlier while the family runs, and the harsh review and three check days come after, so a weak draft is caught before submission.
- **A data bug after 11 Nov.** Zenodo keeps one concept DOI across versions, so a fix becomes version 2 of the dataset, and ShellForm is told. It is reported, never hidden.
- **ShellForm and ShellBench share one set of Claude Pro usage limits.** From 11 Nov both run at once. ShellBench's Paper 1 days (13-17 Nov) come first, or the check days are lost.
- **Paper 2 after 17 Nov.** Its numbers do not exist yet. Renewing Claude Pro for one month would let the surrogate study and Paper 2 keep the same standard. That is the author's choice, and nothing here assumes it.
- **What ShellForm needs from ShellBench is not yet written down [?].** The 6 Nov floor library is final at floor level (v0.3 tagged). Anything at whole-building level waits for the 11 Nov DOI.
