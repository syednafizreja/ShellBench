# Schedule: the compressed day map (from 27 Oct 2026)

Approved by the author on 26 Oct 2026: finish earlier, but without dropping or weakening any check, test or validation. This file replaces the Playbook's calendar dates from Day 9 onwards. The Playbook's daily tasks and their "Done when" lines are unchanged; only the dates move. The dates in the charter are in [research_question.md](research_question.md), "Dates".

## How to read this map

- The date next to each Playbook day is the **latest** day it should be finished. Work ahead is allowed: when a day's "Done when" is met and checked, the next day starts in the same run.
- A day never starts early if it is behind a **gate** (marked GATE below). Gates exist for integrity, not speed.
- If a day slips past its date, the next days do not shrink to catch up. The slip goes into the next spare day, and if there is none, the review on 15 Nov (or 1 Dec for Paper 2) decides what moves. A check is never cut to save a date.

## Charter dates

| Output | Old date | New date | Changed? |
|---|---|---|---|
| Anchor report and release v0.1 | 31 Oct | 31 Oct | No |
| Hypotheses and analysis plan committed | 4 Nov | 4 Nov (planned 3 Nov) | No |
| Dataset DOI on Zenodo | 20 Nov | **17 Nov** | Yes |
| Paper 1 submitted | 29 Nov | 29 Nov | No |
| Paper 2 submitted | 12 Dec | **8 Dec** | Yes |
| ShellBench v1.0 with software DOI | 13 Dec | **8 Dec** (planned 6 Dec) | Yes |
| CV, statement of purpose draft, walkthrough video | 13 Dec | 13 Dec | No |
| JOSS submission | from 19 Apr 2027 | from 19 Apr 2027 | No |

## Where the days come from

Nothing in the research is shortened. The time comes from four places [J]:

1. The five half-day weekly reviews (Days 14, 21, 28, 35, 49) share their day with the next task instead of taking a whole day. The review itself keeps its full checklist.
2. The overnight family run (Day 20) and the full both-floor run (Day 31) run while other work goes on, instead of blocking a day.
3. The pre-registration (Day 17) is done on 3 Nov, a day before its charter date. It must come before the batch runner produces any family row anyway.
4. Two surrogate days (Days 43 and 44: splits and the three models) move before Paper 1 week, onto the published dataset, and the Paper 2 methods section is written as each surrogate piece is finished. In the old plan Paper 2 began from nothing on 30 Nov.

## Day map

| Date | Playbook day(s) | Notes |
|---|---|---|
| Tue 27 Oct | Day 9, seismic base-shear method | Author chooses the infill period factor. Reading rules written before the run, as on Day 8 |
| Wed 28 Oct | Day 10, response-spectrum check | |
| Thu 29 Oct | Day 11, design checks | Author's carbon factors due today |
| Fri 30 Oct | Day 12, quantities and embodied carbon | GATE: needs the author's carbon factors in data/carbon_factors.csv |
| Sat 31 Oct | Day 13, anchor report and v0.1 | Charter date. Needs Zenodo-GitHub link and ORCID so v0.1 gets a DOI |
| Sun 1 Nov | Day 14 review (half) + Day 15 design rules | |
| Mon 2 Nov | Day 16, generator reproduces the thesis | |
| Tue 3 Nov | Day 17, pre-registration (analysis plan) | GATE: committed before any family row exists. Author approves the plan |
| Wed 4 Nov | Day 18, design space and batch runner | Charter date for the hypotheses is met the day before |
| Thu 5 Nov | Day 19, 200-building pilot | Failure rate below 2 % and three hand checks, unchanged |
| Fri 6 Nov | Day 20 v0.2 + overnight run; Day 21 review (half) | |
| Sat 7 Nov | Day 22, floor concept and CalculiX | |
| Sun 8 Nov | Day 23, form-finding | |
| Mon 9 Nov | Day 24, shell solver benchmark | GATE: needs the author's MacNeal and Harder (1985) reference values. Within 2 %, unchanged |
| Tue 10 Nov | Day 25, analyse and size one panel | |
| Wed 11 Nov | Day 26, floor library | At least 60 cases and 5 spot checks, unchanged |
| Thu 12 Nov | Day 27, diaphragm check and v0.3 | Topping rule needs a source; author decides it |
| Fri 13 Nov | Day 28 review (half) + Day 29 shell floor in the generator | |
| Sat 14 Nov | Day 30, anchor headline number | |
| Sun 15 Nov | Day 31, full family with both floors | Runs overnight. **Date review with the coordinator** (is the lead real?) |
| Mon 16 Nov | Day 31 checks + Day 33 data card | Same building IDs in both parquet files; data card finished |
| Tue 17 Nov | Day 33 dataset part: v0.4 and Zenodo DOI | Charter date. GATE: Day 31 checks passed. Author publishes on Zenodo |
| Wed 18 Nov | Day 32, trends and H1-H3 verdicts | Verdicts are written on the published (frozen) data |
| Thu 19 Nov | Day 33 sensitivities | Tornado figure and results/sensitivities.csv, unchanged |
| Fri 20 Nov | Day 34, freeze the Paper 1 figures | |
| Sat 21 Nov | Day 35 review (half) + Day 43 surrogate splits | Splits built on the DOI version of the dataset |
| Sun 22 Nov | Day 36, Paper 1 skeleton and gap paragraph | Paper 1 starts a day earlier than the Playbook |
| Mon 23 Nov | Day 37, methods | |
| Tue 24 Nov | Day 38, results | |
| Wed 25 Nov | Day 39, discussion, conclusions, abstract | |
| Thu 26 Nov | Day 40, harsh review | |
| Fri 27 Nov | Day 41, fixes, references, files | |
| Sat 28 Nov | **Spare day for Paper 1** | Also Day 44 model training runs in the background (no Paper 2 writing this week) |
| Sun 29 Nov | Day 42, submit Paper 1 | Charter date |
| Mon 30 Nov | Day 44 checks + Day 45 calibrated uncertainty | Accuracy table for 3 models x 3 splits x 4 targets checked |
| Tue 1 Dec | Day 46, decision test | **Go/no-go for 8 Dec** (see below) |
| Wed 2 Dec | Day 47, H4 verdict and leakage test | |
| Thu 3 Dec | Day 48 figures and v0.5; Day 49 review (half) | |
| Fri 4 Dec | Day 50, Paper 2 methods and results | Methods already drafted during Days 43-47 |
| Sat 5 Dec | Day 51, discussion, abstract, harsh review | |
| Sun 6 Dec | Day 52, v1.0 and software DOI | Author publishes the Zenodo release |
| Mon 7 Dec | Day 53, finish Paper 2 files | Spare half day |
| Tue 8 Dec | Day 55, submit Paper 2 | New charter date |
| 9-13 Dec | Day 54 profile; Day 56 statement of purpose and video | Charter date 13 Dec unchanged |

## The go/no-go check on 1 Dec

8 Dec holds only if, on 1 Dec, all three are true:

1. The accuracy table (Day 44) and the conformal coverage results (Day 45) exist and have been checked.
2. Paper 1 was submitted on 29 Nov without using the spare day for anything other than Paper 1 fixes.
3. No data bug has been found since the dataset DOI that needs a new dataset version.

If any is false, Paper 2 and v1.0 go back to 12 and 13 Dec. That is a return to the original plan, not a failure, and it is logged in LOG.md with the reason.

## What the author must supply, and by when

These are reserved for the author by the charter. Claude cannot supply them.

| Item | Needed by | For |
|---|---|---|
| Infill period factor decision | Tue 27 Oct | Day 9 |
| GB 50011 primer values checked against the Chinese 2016 copy | Wed 28 Oct | Days 9-10 |
| Carbon factors C30, C35, C40, HRB400 from GB/T 51366 and ICE, copied into data/carbon_factors.csv | Thu 29 Oct | Day 12 |
| Zenodo-GitHub link and ORCID in CITATION.cff | Fri 30 Oct | v0.1 DOI on 31 Oct |
| Approval of the design rules | Sun 1 Nov | Day 15 |
| Approval of the analysis plan | Tue 3 Nov | Day 17 |
| MacNeal and Harder (1985) benchmark reference values, copied from the paper with page | Sun 8 Nov | Day 24 |
| Carbon factors for any floor material the floor concept adds (fill, tie steel recycled-content high and low) [?] | Wed 11 Nov | Days 26 and 33 |
| Topping rule decision with its source | Thu 12 Nov | Day 27 |
| Zenodo dataset publish click | Tue 17 Nov | Dataset DOI |
| Journal account and submission for Paper 1 | Sun 29 Nov | Day 42 |
| Zenodo v1.0 release and Paper 2 submission | Sun 6 Dec and Tue 8 Dec | Days 52 and 55 |

The bottleneck is this list, not the code [J]. Each item answered a day early gives a day of lead.

## Risks in this plan [J]

- **Paper 2 writing is thin.** Five days (4-8 Dec) for discussion, harsh review and files, against six in the Playbook. The mitigation is writing the methods during Days 43-47, so the last week is results and discussion only. If the harsh review on 5 Dec finds a real problem, the 1 Dec rule is applied again and 12 Dec comes back.
- **The 17 Nov DOI needs the floor module to go to plan.** Week 4 has two gates (benchmark values, topping rule). A failed benchmark at 2 % cannot be rushed. If Day 24 slips, the DOI moves day for day, up to the old 20 Nov.
- **A bug found after the DOI.** Zenodo keeps one concept DOI across versions, so a fix becomes version 2 of the dataset. It is reported, never hidden.
- **Background training during Paper 1 week** must not take the author's attention. Claude runs and checks it; the author looks at it on 30 Nov.
