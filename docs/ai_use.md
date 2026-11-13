# Use of AI assistance

© 2026 Syed Nafiz Reja Hasib.

This statement is for journal editors and reviewers (Elsevier and Springer Nature policies on generative AI).

**Tool.** Claude (Anthropic), used through the Claude app and Claude Code, October-November 2026.

**What it did.**
- Drafted and tested code in `src/shellbench/`, `scripts/` and `tests/` to the author's specification.
- Drafted working documents in `docs/` and `paper/paper1/` (specifications, reading rules, reports, checklists).
- Searched for and summarised open-access literature; the author reviewed the rows (`docs/gap_matrix.md`, review status).
- Read code clauses from the author's copies or from open sources, and recomputed numbers as a cross-check.

Where the repository says "the AI assistant", it means this tool.

**What it did not do.**
- It is not an author.
- It did not set the hypotheses or their thresholds; the author approved them before any family row existed (`docs/preregistration.md`).
- Where it proposed a choice or read a clause under the author's standing instruction, the record marks it [J] or "author to confirm", and the author accepted or changed it.

**How the work was checked.**
- Every number in a result traces to the thesis, a code clause or a file in `results/` (`paper/paper1/numbers.md`).
- Judgement that is not a sourced value is marked [J]. Items read by the assistant carry "author to confirm" until the author confirms them.
- The test suite (275 tests) and global equilibrium checks run on every analysis.
- The author reviewed the outputs and takes full responsibility for the content.
