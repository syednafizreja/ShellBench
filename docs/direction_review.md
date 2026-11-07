# Direction review, 6 Nov 2026

Written by the AI assistant at the author's request: "what would a research professor advise?" The author adopted it as standing guidance on 6 Nov 2026. Everything here is the AI assistant's judgement [J], not an external review. Author to confirm each item.

It does not move any date in docs/schedule.md. It sets the priority order inside those dates.

## Verdict

The method and openness are strong: preregistration, clause-traced numbers, open code and data, a hand-checked anchor, failures reported. The risk is breadth. Narrow the claim, fix or exclude the implausible rows, add one independent validation, and make Paper 1 excellent before anything else.

## Priority order (highest first)

| # | Action | Done when | Owner |
|---|---|---|---|
| P1 | Credibility of the family. Fix the grade-I design logic (cl. 6.3.1 h/b limit on R14 beam growth; decide actual beam capacity for grade I), or limit claims to grades II-IV and say why. | No row in the family has member sizes or carbon a reviewer would reject on sight; each grade-I row hand-checked or excluded with a stated reason. | The AI assistant builds; author confirms clauses |
| P2 | Independent validation of the anchor building against a design not made by ShellBench: a published, citable worked example or commercial software output. | A table of ShellBench vs independent values (member sizes, steel, drift) with differences explained. | Author supplies the source or software run (physical); the AI assistant does the comparison |
| P3 | Carbon-factor sensitivity (decision 3, change log C1) shown prominently in Paper 1. | Sensitivity table and one figure in the Paper 1 Results, not only in the supplement. | The AI assistant |
| P4 | H4 surrogate stated modestly: with 36 buildings it is a feasibility test with conformal intervals, not a predictive model. More rows only if cheap and preregistered. | Paper wording and data card say "feasibility"; no accuracy claim beyond what the intervals support. | The AI assistant drafts; author decides |
| P5 | Transfer statement: one paragraph on how the findings relate to Eurocode or ACI practice (qualitative, cited). | Paragraph in the Paper 1 Discussion with open-access sources. | Author writes; the AI assistant checks sources |

## Papers

- **Paper 1 is the flagship:** the benchmark and the carbon findings, with the shell-floor comparison as the headline result if it holds. Most effort goes here.
- **Paper 2 (surrogate):** a separate paper only if H4 supports a real claim. If not, fold a short version into Paper 1 and drop Paper 2. Decide after the H4 verdict.
- **JOSS:** kept, as planned (from 19 Apr 2027).
- **ShellForm:** a later paper. No ShellForm work displaces Paper 1 work before 22 Nov.
- Do not split the dataset into several small papers.

## Presentation

- Lead with the engineering question and the answer, not the software.
- One headline figure readable in ten seconds.
- README: one screen with question, finding, DOI and a one-command reproduction.
- A short limitations section near the front of Paper 1.
- A preprint of Paper 1 at submission, if the journal's policy allows (author to check the policy).

## Postponed until after Paper 1 is submitted

GitHub Pages site, tutorials, video, and any polish not needed for the papers. This matches docs/schedule.md "What does not fit".

## Needs the author

- P2 source: a citable worked design example, or a run in design software you have a licence for.
- Confirm the grade-I decision (fix, or exclude and state why).
- Journal preprint policy for Paper 1.
