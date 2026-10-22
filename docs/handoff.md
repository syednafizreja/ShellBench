# Handoff between Claude in the app and Claude Code in VS Code

Newest entry first. Each Claude reads this at the start of a session and adds an entry at the end (see "Sync with cloud Claude" in CLAUDE.md).

## 22 Oct 2026, Claude in the app (Day 4 closed)

**Decisions made by the author today:**
- **Living charter:** `docs/research_question.md` is the charter. It overrides the charter PDF, which has been replaced in the claude.ai project by this file.
- **Revised question (Option A):** "How much do thin-shell floors cut the whole-building A1-A3 embodied carbon of an RC frame designed to GB 50010 / GB 50011, and how does that saving change with seismic intensity once diaphragm, tie and topping needs are met?" The three fixes:
  1. a PGA sweep from 0.05 to 0.40 g, with 0.10 g as the validated anchor;
  2. the best code-compliant conventional floor as the baseline;
  3. topping thickness as a variable, with an in-plane diaphragm check.
- **Literature:** only 2020-2026 papers go in the gap matrix. Older papers are cited for method only. Only legal open-access copies or authors' accepted manuscripts are used, because the author has no institutional login.
- **Journal rules:** `docs/q1_standards.md` (Elsevier, Springer Nature and COPE rules) is followed every day. Each LOG.md day entry ends with a "Compliance:" line covering sources, AI use, numbers and data.
- **Who writes what:** the author writes the first draft of results, discussion and conclusions. AI-written code is described in Methods, and the AI declaration goes before the references.
- **Daily close:** Claude does the LOG.md entry, the README update, the branch, the PR and merge, and the week-issue comment at the end of each day. The author does not do these by hand.
- **Quizzes:** these happen in the Claude app only, with all 3 questions in one message.

**Merged today:** PRs #13 (gap matrix, stress test, revised question), #14 (page numbers), #15 (open-access sources), #16 (q1_standards.md, gap-matrix rows 21-24).

**Open:**
- Fang et al. 2023 review (gap matrix row 20) is unread. The MIT repository blocks automated downloads; a retry is scheduled. Row 24 (NIST SP 1324) covers the general-review role meanwhile.
- Gap-matrix rows 21-24 await the author's review.
- Page numbers marked `p. [?]†` are checked when a sentence is quoted in the manuscript.
- Grade-dependent detailing for intensities 8-9 (GB 50011 Table 6.1.2, to confirm) must be in the redesign loop from Week 3.

**Next:** Day 5 of the playbook.
