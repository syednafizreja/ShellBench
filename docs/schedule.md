# Schedule: build ends 13 Nov, author checks 14-17 Nov (approved 28 Oct 2026)

On 28 Oct 2026 the author approved finishing within Claude Pro (it renews on 17 Nov), at the best quality, with Paper 1 submitted by 22 Nov. Later the same day the author added one condition: "i should have a few days in hands to check things, so must finish few days earlier than the claude pro ends". So the build ends on **Fri 13 Nov**, and **14-17 Nov is the author's check window**, while Claude can still make fixes. This file replaces the 26 Oct plan (PR #50) from the next daily run.

17 Nov is the end of Claude's help, not a journal deadline. Anything that needs only the author's hands (writing, submission clicks) can still happen after it, and nothing in this plan treats a date as a reason to drop a check.

## Where we stand on 28 Oct

Days 9, 10 and 11 are done (LOG.md). pytest 114 passed. Day 12 is waiting on the carbon factors (GATE). The build now has 16 calendar days (29 Oct to 13 Nov) instead of 20.

## How it fits [J]

There are two structural changes. Neither removes a check.

1. **The shell floor module (Days 22-27) runs alongside the generator (Days 15-21).** It does not depend on the generator. Its only input from the building is the anchor's storey seismic force, which already exists from Day 9. In the Playbook the two run one after the other only because one person works through them in order. Running them side by side saves about 7 days.
2. **The surrogate code is built and frozen before the dataset exists.** Once the floor module is done (6 Nov), Track B builds the surrogate pipeline (splits, three models, conformal intervals, decision test, leakage test) and tests it on the conventional-floor family from the Day 20 run. Its code and hyperparameters are committed **before the DOI**, and then run once on the published data. This is a stricter protocol than the Playbook's: the final test data cannot influence any modelling choice, which a Q1 reviewer will value [J]. It saves about 4 days.

What is done by Fri 13 Nov:

- the anchor report and v0.1 (31 Oct, unchanged);
- the pre-registration before any family row (3 Nov, gate unchanged);
- the floor library and v0.3, which ShellForm can use from **6 Nov**;
- the family with both floors, and the dataset DOI on **11 Nov**, which is ShellForm's full start;
- the H1-H3 verdicts and sensitivities, and the frozen figures for both papers;
- the H4 verdict with the leakage test, and v0.5.

The check window, 14-17 Nov: the author checks the anchor report, the dataset, every verdict and the Paper 1 draft. Claude fixes what the author finds, runs the Paper 1 harsh review (Day 40) on 15 Nov, and tags v1.0 on 17 Nov only after the checks pass.

What does not fit:

- **Writing Paper 2 with Claude's help.** All its numbers and figures exist by 13 Nov and are checked in the window. The author writes it after 17 Nov. Target submission is still 8 Dec.
- **Polish:** the JOSS documentation and two tutorials, the GitHub Pages site, the profile (Day 54), the statement of purpose and the video (Day 56). These go to the author after 17 Nov. JOSS is not before 19 Apr 2027 anyway.

## Charter dates

| Output | Charter on 26 Oct | Now | Note |
|---|---|---|---|
| Anchor report and v0.1 | 31 Oct | 31 Oct | Unchanged |
| Hypotheses and analysis plan | 4 Nov | 3 Nov | GATE: before any family row |
| Floor library and v0.3 (first ShellForm data) | (14 Nov in Playbook) | 5 Nov | |
| Dataset DOI | 17 Nov | **11 Nov** | ShellForm full start |
| All results and frozen figures, both papers | (6 Dec in Playbook) | **13 Nov** | End of the build |
| Author's check window | | **14-17 Nov** | Claude fixes only; no new analysis |
| ShellBench v1.0 with software DOI | 8 Dec | **17 Nov** | After the checks; tutorials follow as v1.0.x |
| Paper 1 submitted | 29 Nov | **22 Nov** | Files ready 17 Nov |
| Paper 2 submitted | 8 Dec | 8 Dec | Author writes after 17 Nov |
| CV, statement, video | 13 Dec | 13 Dec | Author alone |
| JOSS | from 19 Apr 2027 | from 19 Apr 2027 | Unchanged |

## Day map, 29 Oct to 17 Nov

A day's date is the latest it may finish; work ahead is allowed. GATE days never start early.

| Date | Track A: anchor, generator, family | Track B: shell floor, then surrogate | Paper 1 (author writes, Claude checks) |
|---|---|---|---|
| Thu 29 Oct | Day 12 quantities and carbon (GATE: carbon factors today) | | |
| Fri 30 Oct | Day 12 finish | Day 22 floor concept and CalculiX | |
| Sat 31 Oct | **Day 13 anchor report, v0.1** | Day 23 form-finding | |
| Sun 1 Nov | Day 14 review (half) + Day 15 design rules | Day 24 shell benchmark (GATE: MacNeal-Harder values) | |
| Mon 2 Nov | Day 16 generator reproduces the thesis | Day 24 finish (2 % on both benchmarks) | |
| Tue 3 Nov | **Day 17 pre-registration** (GATE) | Day 25 size one panel | |
| Wed 4 Nov | Day 18 batch runner | Day 26 floor library (60+ cases) | Methods: author starts |
| Thu 5 Nov | Day 19 200-building pilot | **Day 27 diaphragm, topping rule, v0.3** | Methods |
| Fri 6 Nov | Day 20 v0.2, overnight run (conventional family) | Day 28 review (half). **ShellForm may start on the floor library** | Methods |
| Sat 7 Nov | Day 21 review (half) + Day 29 shell floor in the generator | Day 43 splits code, on the conventional family | Day 36 skeleton and gap paragraph |
| Sun 8 Nov | Day 30 anchor headline number | Day 44 three models, on the conventional family | Methods |
| Mon 9 Nov | Day 31 full family, both floors (overnight) | Day 45 conformal intervals | Day 37 methods finished |
| Tue 10 Nov | Day 31 checks + data card | Day 46 decision test + leakage test code; **surrogate code and hyperparameters frozen (commit) before the DOI** | |
| Wed 11 Nov | **Day 33 v0.4 and dataset DOI** (GATE: Day 31 checks). **ShellForm full start** | | |
| Thu 12 Nov | Day 32 H1-H3 verdicts on the published data; Day 33 sensitivities run | One final surrogate run on the published data (Days 44-46) | Day 38 results draft starts |
| Fri 13 Nov | Day 34 frozen Paper 1 figures | Day 47 H4 verdict and leakage test; Day 48 Paper 2 figures, v0.5. **End of build** | Day 38 results |
| Sat 14 Nov | Check window: author checks the anchor report, the dataset and H1-H3 | Check window: author checks H4 | Day 39 discussion and abstract |
| Sun 15 Nov | Check window (Day 35 review) | Check window | **Day 40 harsh review** |
| Mon 16 Nov | Check window: Claude fixes | Check window: Claude fixes | Day 41 fixes, references, files |
| Tue 17 Nov | **Day 52 v1.0 and software DOI** after the checks pass | | Paper 1 files ready |
| After 17 Nov | | | Author: **Day 42 submit Paper 1 by 22 Nov**; Paper 2 writing (Days 50, 51, 53), submit by 8 Dec (Day 55); profile, statement and video by 13 Dec (Days 54, 56); tutorials and JOSS docs |

Every Playbook "Done when" line stands unchanged: 2 % on the benchmarks, a failure rate below 2 % with three hand checks on the pilot, 60 or more library cases with 5 spot checks, the same building IDs in both family files, a leakage test, and every number in Results checked against a file.

## What the author must supply, and by when

This list is the real limit on the plan. A day's delay on any GATE item moves its track by a day.

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
| Approve the surrogate freeze (models, hyperparameters, split rules) | Tue 10 Nov | Before the DOI |
| Zenodo dataset publish click | Wed 11 Nov | Dataset DOI |
| Paper 1 results and discussion drafts | Sat 14 Nov | Days 38-39 |
| Checks of every verdict and the dataset | 14-16 Nov | Check window |
| Zenodo v1.0 release click | Tue 17 Nov | Day 52 |
| Paper 1 submission | Sun 22 Nov | Day 42 |

## ShellForm hand-over points (added 28 Oct 2026)

The author's next project, ShellForm, starts from ShellBench data and should finish in the same window. So ShellBench hands data over in stages, each one as soon as its layer has passed its own checks. Nothing is handed over before its validation, because ShellForm would then inherit an unchecked number [J]. Each stage is a tagged release, so ShellForm can cite exactly what it used.

| Date (latest) | What ShellForm gets | Validated by | Tag |
|---|---|---|---|
| Sat 31 Oct | The anchor building: geometry, loads, storey seismic and wind forces, member sizes, quantities and carbon | Anchor report (Days 5-13) | v0.1 |
| Sat 31 Oct | Force density form-finding code (vault geometry for any bay, span and rise) | Parabola and thrust tests within 1 % (Day 23) | in v0.1.x |
| Mon 2 Nov | CalculiX shell analysis wrapper | Scordelis-Lo roof and pinched hemisphere within 2 % (Day 24) | v0.2.0-shell |
| Tue 3 Nov | One sized panel at the thesis span: thickness, tie, buckling factor, quantities | Tie force within 10 % of the closed form (Day 25) | v0.2.1-shell |
| Thu 5 Nov | Floor library (60+ cases) and the topping rule | 5 spot checks; topping rule with a source (Days 26-27) | v0.3 |
| Wed 11 Nov | The full building family with both floors | Day 31 checks, data card | Dataset DOI |

Each stage can come a day earlier if the GATE item behind it (MacNeal-Harder values, floor concept approval) arrives a day early. That is the only way to bring the dates forward without cutting a check.

What ShellForm needs from this list is not known yet [?]. If the floor-level stages are enough, ShellForm can start on 31 Oct.

## Fallback rules

- **The check window is protected.** At least 15-17 Nov stays for checking and fixing, whatever slips. The build may run into Sat 14 Nov, but no further.
- **Check on 6 Nov.** If v0.2 or v0.3 has slipped by more than one day, the surrogate code (Track B, 7-10 Nov) gives way first, because Paper 2 is lower priority than Paper 1 and the dataset.
- **If the surrogate is not finished with its checks by 14 Nov,** it is not run without them. The frozen code and splits are archived in v1.0, and the final surrogate run waits until Claude is available again or is done by the author. Paper 2 then moves past 8 Dec. Paper 1 and the dataset are not touched.
- **If the dataset DOI slips past 12 Nov,** the H1-H3 verdicts and Paper 1 figures still come before the check window, and the surrogate gives way.
- **Paper 1 goes in only after its harsh review.** If the review on 15 Nov finds a real problem that cannot be fixed by 17 Nov, the author fixes it alone and submits by 29 Nov (the old charter date) rather than going in unreviewed.
- A slipped day never shrinks the next one. A check is never cut to save a date.

## Risks [J]

- **The author is the bottleneck, not the code.** Two build tracks mean twice the approvals per day until 6 Nov. If the reserved items arrive late, the plan slips; it does not get rushed.
- **No spare day in the build.** The spare day of the earlier draft (11 Nov) became the DOI day. The check window is the buffer now, which is why the surrogate is the first thing to give way.
- **Surrogate developed on part of the family.** The conventional-floor family (from 6 Nov) is enough to build and test the pipeline, but not the decision test, which needs both floors. The decision test code is checked on the anchor and the pilot in both floors (from Day 30), then run once on the published data.
- **A data bug after 11 Nov.** Zenodo keeps one concept DOI across versions, so a fix becomes version 2 of the dataset, and ShellForm is told. It is reported, never hidden.
- **Paper 2 without Claude's harsh review.** The numbers are checked in the window. The prose will not get the same review unless Claude Pro renews. That is the author's choice, and nothing in this plan assumes it.
- **ShellForm on early data.** The 6 Nov floor library is final for floor-level work (v0.3 is tagged). Anything ShellForm needs at whole-building level must wait for the 11 Nov DOI. What ShellForm actually needs is not known yet [?].
