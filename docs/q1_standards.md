# Journal rules we follow every day (Q1 compliance)

Purpose: follow the target journals' and publishers' rules from day one, so that Paper 1 and Paper 2 cannot be desk-rejected or retracted for a policy reason. This file is the checklist. Claude applies it every working day and records the result in [LOG.md](../LOG.md).

Written 22 Oct 2026 from the sources listed at the end, each read on that date. Policies change, so every rule is re-checked against the live guide for authors in Week 6, before submission. [J] = my judgement. [?] = not verified.

## 1. The target journal

- **Journal of Building Engineering (JOBE), Elsevier.** First choice for Paper 1 in the charter.
- **Q1 status:** SCImago lists SJR 2025 = 1.703, Q1 in Civil and Structural Engineering, Building and Construction, and Architecture (source S2).
- **Other journals in the charter:**
  - Engineering Structures, J. Cleaner Production and Automation in Construction are Elsevier, so the Elsevier rules below apply.
  - Bulletin of Earthquake Engineering is Springer, so the Springer Nature rules in section 3 apply as well.
  - Their quartiles are not yet checked [?]. Check them in Week 6.
- **Scope:** JOBE covers "Effects of hazards on building structures (seismic, wind, gravity ...)" and "Innovative building structural components and systems" (S1, Aims and scope). ShellBench is in scope.
- **Novelty bar:** "JOBE only publishes papers that clearly demonstrate significant scientific novelty in building engineering" (S1). We show novelty with the gap matrix evidence, not with adjectives. This matches CLAUDE.md rule 8: no "novel" or "first" without evidence.

## 2. Rules that can sink a submission, and what we do about them

| # | Rule (source) | Risk for ShellBench | What we do, every day |
|---|---|---|---|
| R1 | **No fabricated references.** AI-generated references "can be incorrect or fabricated"; "Inclusion of fabricated references may lead to rejection" (S3, FAQ). | High: AI helps with the literature. | Every reference has a DOI checked against OpenAlex or Crossref, and the author has opened it (reading_list.md). Nothing is cited from memory. |
| R2 | **AI is not an author, and its use is declared.** Authors must not list AI as an author. Use of AI in writing needs a declaration titled "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process", placed before the references (S1, S3). AI tools "cannot meet the requirements for authorship" (S6, COPE). | Certain: Claude is used. | Keep a running AI-use record (section 4). Write the declaration from it at submission. |
| R3 | **AI used in the research (code, analysis) is described in Methods.** "If authors write or edit code using AI tools as part of their research, they should declare this in detail in the Methods section" (S3, FAQ). | Certain: Claude writes code. | Each LOG.md entry says which code Claude wrote and how the author checked it. The Methods section gets a paragraph built from this. |
| R4 | **The author writes the science.** Not permitted: AI "writing results or discussion independently; generating scientific claims or interpretations" (S4, Springer Nature "Red"). Elsevier: AI must not be "a substitute for human critical thinking" (S1). | High if Claude drafts the paper. | Already the charter rule (writing manual p. 6). The author writes the research question, the first draft of every section, the interpretation and the conclusions. Claude questions, checks and edits. |
| R5 | **No prior or parallel publication.** The work must not have been published before "except in the form of a preprint, abstract, published lecture, academic thesis" and must not be under consideration elsewhere (S1, Submission declaration). | Medium: the anchor building comes from the author's 2023 thesis. | A thesis is allowed. Cite the thesis, write all text fresh (screening tools check overlap, S1), and say in the cover letter that the anchor design comes from the author's thesis [J]. Submit to one journal at a time. Do not resubmit a rejected paper to JOBE without an invitation (S1). |
| R6 | **Research data must be deposited and cited.** JOBE uses Elsevier "Option C": deposit the data in a repository, cite and link it, or explain why it cannot be shared. A data statement is required at submission (S1, Research data). | Medium. | All code, inputs and results go in the public repo with an MIT licence. A Zenodo DOI is minted for the dataset (charter plan). The thesis PDF stays private. The data statement will say that the inputs typed from it are in validation/ and docs/baseline_spec.md. |
| R7 | **Competing interests and funding must be declared** (S1). | Low. | State "none" if true. No former-employer data, processes or product names anywhere (CLAUDE.md rule 7). This also avoids intellectual-property and confidentiality conflicts. |
| R8 | **Authorship and CRediT.** Each author must have contributed to the design or analysis, drafting or critical revision, and final approval. Contributions are stated with CRediT roles (S1). | Low. | Add a CRediT statement at submission. Anyone who helps but does not qualify goes in the Acknowledgements (S1). |
| R9 | **Figures must come from the data.** AI-made data figures must be "directly derived from underlying data using reproducible methods". General-purpose AI image tools "must not be used to create graphical abstracts" (S3). | Low. | All plots come from scripts in the repo that read results/. The graphical abstract is drawn by the author with an illustration tool, not an AI image generator. |
| R10 | **Methods must allow replication; limitations must be stated; conclusions must follow from the data; references must be up to date.** These are what Elsevier asks reviewers to check (S5). | This is where Q1 papers usually fail [J]. | The validation table against the thesis, code-clause tracing, a sensitivity analysis (stress test H1-H9) and an open repo. Literature limited to 2020-2026 plus the method foundations. |
| R11 | **Format limits for JOBE:** abstract up to 250 words, standalone, no references; 1-7 keywords; highlights optional but encouraged, 3-5 bullets of up to 85 characters each; numbered sections (S1). | Easy to miss at the end. | Checked in Week 6 with the submission checklist (S1, "Submission checklist"). |
| R12 | **Preprints are allowed.** "Sharing preprints ... will not count as prior publication" (S1). Springer Nature "encourages posting of preprints" (S4b). | None. | The engrXiv preprint in the charter plan is allowed. |
| R13 | **Legal sources only.** No pirate copies, and respect each paper's licence. | Already handled. | Open-access or accepted-manuscript copies only (reading_list.md access statement). |
| R14 | **LCA reporting must be transparent and standard.** The NIST review found that consistent and standardised LCA practice is the most frequent research need (33% of reviews, S7 §7). | Reviewers will ask about factors and boundaries [J]. | State module A1-A3 (EN 15978), the functional unit, the carbon factors and their source (GB/T 51366-2019 for China [?]: confirm in the user's copy), and a factor sensitivity. Follow the free IStructE guide *How to calculate embodied carbon*, 3rd ed. (2025) for structural carbon reporting [J]. |

## 3. Springer Nature extras (Bulletin of Earthquake Engineering)

Springer Nature uses a risk scale for AI in writing (S4):

- **Green:** "Grammar and language editing; improving readability". Allowed if declared.
- **Amber:** "Generating outlines; drafting sections based on author input ... reference management support". Allowed with care and declared, and "references are real and have been checked".
- **Red:** not permitted. This includes "writing results or discussion independently; generating scientific claims or interpretations".

The charter rules above keep us in Green and Amber.

## 4. Daily routine (what Claude does at the end of each working day)

Each day's LOG.md entry ends with a short "Compliance" line covering:

1. **Sources:** any new reference has a checked DOI and a legal copy (R1, R13).
2. **AI use:** what Claude did today (code, documents, literature search) and how the author checked it (R2, R3, R4).
3. **Numbers:** every new number traces to the thesis, a code clause or the code (CLAUDE.md rule 2, R10).
4. **Data:** nothing confidential committed, thesis_source/ still git-ignored, no former-employer material (R6, R7).
5. **Repo:** work committed on a branch, PR opened and merged, and the week's issue updated (daily close routine).

## Sources (all read 22 Oct 2026)

- S1. Elsevier. *Journal of Building Engineering: Guide for authors.* https://www.sciencedirect.com/journal/journal-of-building-engineering/publish/guide-for-authors
- S2. SCImago Journal & Country Rank. *Journal of Building Engineering.* https://www.scimagojr.com/journalsearch.php?q=21100389518&tip=sid
- S3. Elsevier. *Generative AI policies for journals* (updated June 2026). https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals
- S4. Springer Nature. *AI use in manuscript preparation.* https://www.springernature.com/gp/policies/editorial-policies/ai-manuscript-preparation
- S4b. Springer Nature. *Editorial policies* (preprints, author contributions, research data). https://www.springernature.com/gp/policies/editorial-policies
- S5. Elsevier. *How to conduct a review* (what reviewers assess). https://www.elsevier.com/reviewer/how-to-review
- S6. COPE Council. *COPE position: Authorship and AI tools.* https://doi.org/10.24318/cCVRZBms
- S7. Zhang Y., Sattar S., Cook D.T., Johnson K.J., Fung J.F. (2024). *Systematic review of embodied carbon assessment and reduction in building life cycles.* NIST SP 1324. https://doi.org/10.6028/NIST.SP.1324
- S8. Gibbons O.P., Orr J.J., Arnold W. (2025). *How to calculate embodied carbon*, 3rd ed. IStructE. https://www.istructe.org/resources/guidance/how-to-calculate-embodied-carbon/ (free PDF; not yet read in full [?])
