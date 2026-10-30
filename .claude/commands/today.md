---
description: Do the whole day without asking: finish today's playbook task, then sync, pull and close the day.
---

Do today's ShellBench work end to end. Never ask me questions; pick the best default, record it, and carry on. Stop only if something cannot be done even with all permissions, and then say exactly what and why.

1. `git checkout main` and `git pull origin main`. Read the newest `docs/handoff.md` entry and the newest `LOG.md` day. Find today's task and its Done-when line in the playbook and the LOG.
2. Finish everything due up to and including today: any earlier day not yet done, then today's task, to its Done-when line. Follow CLAUDE.md rules (no invented numbers, SI units, docstrings, plain British English, [J] for judgement, no former-employer data, thesis_source/ never committed). Skip quizzes.
3. Follow the daily close routine in memory: LOG entry with compliance line, `dayNN` branch, PR, merge, week-issue comment.
4. Then run the `/sync` command in full (pytest, anchor_frame, results/ unchanged, handoff entry, `dayNN-sync` branch, PR, merge).
5. Finish with `git checkout main` and `git pull origin main`.
6. No Claude attribution anywhere. Commit as Syed Nafiz Reja Hasib <syednafiz2811@gmail.com>.
7. Report in at most five lines: what was done, pytest result, results identical or not, PR numbers, and anything that needs me.
