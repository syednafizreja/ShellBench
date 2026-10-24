---
description: Daily sync with the cloud work: pull, reproduce, report, hand off. Run once at the end of each day.
---

Do the daily sync for ShellBench. Do every step yourself without asking me, then report. No quiz.

Use the conda env `research` for every command: `C:\Users\ASUS\miniconda3\Scripts\conda.exe run -n research <command>`.

1. `git checkout main` and `git pull origin main`. Read the newest entry in `docs/handoff.md` and the newest day in `LOG.md`.
2. `pip install -e . --no-deps`, then `pytest`. Note the pass count.
3. Run `python -m shellbench.anchor_frame` from the repo root (and any other entry point the newest handoff entry names). Run `git status`. Every file in `results/` must be unchanged. If any changed, do not commit it: run `git diff --stat`, restore it with `git checkout -- results/`, and report the file names.
4. If the newest handoff entry asks for a local step on this laptop, do it.
5. Add a dated entry at the top of `docs/handoff.md` ("Claude Code in VS Code"): pytest result, whether results were byte-identical, anything else done, anything open.
6. Commit as me (Syed Nafiz Reja Hasib <syednafiz2811@gmail.com>) on a branch named `dayNN-sync` (NN = the day number from the newest LOG entry), push, open a PR, and merge it if the tests passed. No Claude attribution anywhere.
7. Report to me in at most five lines: the last handoff in one line, the pytest result, results identical or not, the PR number, and anything that needs me.
