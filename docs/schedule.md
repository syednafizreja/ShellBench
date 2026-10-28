# Schedule: the 17 Nov plan (PROPOSED 28 Oct 2026, awaiting the author's approval)

Status: **proposal**. Until the author approves it, the daily routine keeps following the 26 Oct plan (PR #50, dates to 8 Dec). On approval, this file replaces it from the next run.

## Why a new plan

On 28 Oct the author asked to finish the project by Tue 17 Nov 2026, the date the author's Claude Pro subscription renews, without losing quality. A second project, ShellForm, needs ShellBench data before it can start, so the plan should hand that data over as early as possible.

17 Nov is the end of Claude's help, not a journal deadline. Anything that needs only the author's hands (writing, submission clicks) can still happen after it, and nothing in this plan treats 17 Nov as a reason to drop a check.

## Where we stand on 28 Oct

Days 9, 10 and 11 are done (LOG.md), one day ahead of the 26 Oct plan. pytest 114 passed. Day 12 is waiting on the carbon factors (GATE). That leaves Playbook Days 12-56 in 20 calendar days (29 Oct to 17 Nov).

## The honest answer [J]

Not everything fits, if quality stays where it is. The 26 Oct plan needed 41 calendar days for these 45 Playbook days. Compressing them into 20 without cutting checks needs one real structural change, plus the author answering every reserved item on the day it is asked.

The structural change is that **the shell floor module (Days 22-27) runs in parallel with the generator (Days 15-21)**. It does not depend on the generator. Its only input from the building is the anchor's storey seismic force, which already exists from Day 9. In the Playbook the two run one after the other only because a single person works through them in order. Running them side by side saves about 7 days and costs no check.

What fits by 17 Nov with every check kept:

- the anchor report and v0.1 (31 Oct, unchanged);
- the pre-registration before any family row (3 Nov, gate unchanged);
- the floor library and v0.3, which ShellForm can use from **6 Nov**;
- the family with both floors, and the dataset DOI on **12 Nov**, which is ShellForm's full start;
- the H1-H3 verdicts, sensitivities and frozen Paper 1 figures (14 Nov);
- the whole surrogate study with the H4 verdict, frozen Paper 2 figures and v0.5 (17 Nov);
- v1.0 with a software DOI (17 Nov), meaning the code frozen, tested and archived;
- Paper 1 drafted, harshly reviewed and fixed, with **submission targeted for 17 Nov**.

What does not fit without weakening something:

- **Writing Paper 2 with Claude's help.** Every Paper 2 number and figure will exist by 17 Nov, but the drafting, the harsh review and the files take about 5 more days. The author writes it after 17 Nov. Target submission is still 8 Dec, the current charter date.
- **Polish:** the JOSS-ready documentation and two tutorials, the GitHub Pages site, the profile (Day 54), the statement of purpose and the walkthrough video (Day 56). By the charter's priority order these come last. They move to after 17 Nov and are done by the author. JOSS is not before 19 Apr 2027 anyway.

## Proposed charter dates

| Output | Charter now (26 Oct) | Proposed | Note |
|---|---|---|---|
| Anchor report and v0.1 | 31 Oct | 31 Oct | Unchanged |
| Hypotheses and analysis plan | 4 Nov | 3 Nov | GATE: before any family row |
| Floor library and v0.3 (ShellForm early data) | (14 Nov in Playbook) | 5 Nov | New hand-over point |
| Dataset DOI | 17 Nov | **12 Nov** | ShellForm full start |
| Paper 1 submitted | 29 Nov | **17 Nov** target, **22 Nov** latest | Fallback is still a week early |
| ShellBench v1.0 with software DOI | 8 Dec | **17 Nov** | Code freeze; tutorials come later as v1.0.x |
| Paper 2 submitted | 8 Dec | 8 Dec | All numbers by 17 Nov; author writes after |
| CV, statement, video | 13 Dec | 13 Dec | Author alone |
| JOSS | from 19 Apr 2027 | from 19 Apr 2027 | Unchanged |

## Day map, 29 Oct to 17 Nov

Three tracks. A track's date is the latest the day may finish; work ahead is allowed as before. GATE days never start early.

| Date | Track A: anchor and generator | Track B: shell floor | Track C: papers and surrogate |
|---|---|---|---|
| Thu 29 Oct | Day 12 quantities and carbon (GATE: carbon factors today) | | |
| Fri 30 Oct | Day 12 finish | Day 22 floor concept and CalculiX | |
| Sat 31 Oct | **Day 13 anchor report, v0.1** | Day 23 form-finding | |
| Sun 1 Nov | Day 14 review (half) + Day 15 design rules | Day 24 shell benchmark (GATE: MacNeal-Harder values) | |
| Mon 2 Nov | Day 16 generator reproduces the thesis | Day 24 finish (2 % on both benchmarks) | |
| Tue 3 Nov | **Day 17 pre-registration** (GATE) | Day 25 size one panel | |
| Wed 4 Nov | Day 18 batch runner | Day 26 floor library (60+ cases) | Paper 1 methods: author starts drafting |
| Thu 5 Nov | Day 19 200-building pilot | **Day 27 diaphragm, topping rule, v0.3** | Methods continue |
| Fri 6 Nov | Day 20 v0.2, overnight run | Day 28 review (half). **ShellForm may start on the floor library** | Methods continue |
| Sat 7 Nov | Day 21 review (half) + Day 29 shell floor in the generator | | |
| Sun 8 Nov | Day 30 anchor headline number | | Day 36 skeleton and gap paragraph |
| Mon 9 Nov | Day 31 full family, both floors (overnight) | | Day 37 methods finished |
| Tue 10 Nov | Day 31 checks + data card | | |
| Wed 11 Nov | Spare day for Tracks A and B | | |
| Thu 12 Nov | **Day 33 v0.4 and dataset DOI** (GATE: Day 31 checks). **ShellForm full start** | | Day 43 surrogate splits |
| Fri 13 Nov | Day 32 H1-H3 verdicts on the published data | | Day 44 three models |
| Sat 14 Nov | Day 33 sensitivities + Day 34 frozen figures | | Day 38 Paper 1 results; Day 45 conformal |
| Sun 15 Nov | Day 35 review (half) | | Day 39 discussion and abstract; Day 46 decision test |
| Mon 16 Nov | | | Day 40 harsh review + Day 41 fixes; Day 47 H4 verdict and leakage test |
| Tue 17 Nov | | | **Day 42 submit Paper 1** (or by 22 Nov); Day 48 frozen figures, v0.5; **Day 52 v1.0 and software DOI** |
| After 17 Nov | | | Author: Paper 2 writing (Days 50, 51, 53), submit by 8 Dec (Day 55); profile, statement and video by 13 Dec (Days 54, 56); tutorials and JOSS docs |

Every Playbook "Done when" line stands unchanged: 2 % on the benchmarks, a failure rate below 2 % with three hand checks on the pilot, 60 or more library cases with 5 spot checks, the same building IDs in both family files, a leakage test, and every number in Results checked against a file.

## What the author must supply, and by when

This list is the real limit on the plan. In the 26 Oct plan these items were spread over six weeks; here they come in under three. A day's delay on any GATE item moves its track by a day.

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
| Zenodo dataset publish click | Thu 12 Nov | Dataset DOI |
| Paper 1 methods draft (author's own words) | Mon 9 Nov | Day 37 |
| Paper 1 results and discussion drafts | Sun 15 Nov | Days 38-39 |
| Paper 1 submission | Tue 17 Nov (latest 22 Nov) | Day 42 |
| Zenodo v1.0 release click | Tue 17 Nov | Day 52 |

## Fallback rules

- **Check on 6 Nov.** If v0.2 or v0.3 has slipped more than one day, the spare day on 11 Nov absorbs it. If it slips more than two days, the dataset DOI moves day for day, up to 17 Nov, and Paper 1 submission moves to 22 Nov.
- **Check on 14 Nov.** If the H1-H3 verdicts or the frozen figures are not done, Paper 1 submits by 22 Nov rather than 17 Nov. The author finishes it alone from complete, checked files.
- **Surrogate.** If Day 47 (the H4 verdict and the leakage test) is not done by 17 Nov, it is not run without its checks. The surrogate code and splits are archived in v1.0, and Paper 2 moves to after Claude Pro renews, or is finished by the author.
- A slipped day never shrinks the next one. A check is never cut to save a date.

## Risks [J]

- **The author is the bottleneck, not the code.** Two build tracks mean twice the approvals per day for the first ten days. If the reserved items arrive late, the plan slips; it does not get rushed.
- **Paper 1 in parallel with the analysis.** Drafting the methods while the family runs is normal practice and safe, because the methods do not depend on results. The results and discussion get only two days (14-15 Nov). That is why the 22 Nov fallback exists.
- **A data bug after 12 Nov.** Zenodo keeps one concept DOI across versions, so a fix becomes version 2 of the dataset, and ShellForm is told. It is reported, never hidden.
- **Paper 2 without Claude's harsh review.** The numbers will be checked. The prose will not get the same review unless Claude Pro renews for one more month. Renewing would be the cheapest way to protect Paper 2's quality, but that is the author's choice, and nothing in this plan assumes it.
- **ShellForm on early data.** The 6 Nov floor library is final for floor-level work (v0.3 is tagged). Anything ShellForm needs at whole-building level must wait for the 12 Nov DOI. What ShellForm actually needs is not known yet [?].
