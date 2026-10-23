# CLAUDE.md

Rules for Claude when working in this repository.

## Rules

1. Never invent references, numbers, code clauses, results or DOIs. If unsure, say "I don't know" and tell me how to check.
2. When a number comes from my thesis, give the section or table it comes from. When it comes from a code, give the clause, and tell me to confirm it in my copy of the code.
3. When you write code, give complete files with the file path at the top, then explain them section by section in plain English. Use SI units.
4. When I paste an error, first explain the cause in one or two sentences, then give the complete corrected file.
5. At the end of every coding or theory task, ask me 3 quiz questions, one at a time. Do not give answers until I reply.
6. Keep me on today's playbook task. If I drift, remind me of today's Done-when line.
7. Never use or ask for data from my former employer. No company processes, product names or data in any output.
8. Writing style: plain British English, short sentences, no hype words ("novel", "first", "groundbreaking") unless I have evidence. Mark your own judgement with [J].

## Code standards

SI units everywhere; every function has a docstring; no hidden constants; every number in a result must trace to the thesis, a code clause or the code itself.

## Environment

- Windows 11, PowerShell, conda environment `research` (Python 3.12). Use it for every command.
- `conda` is not on the PowerShell PATH. Run commands with `C:\Users\ASUS\miniconda3\Scripts\conda.exe run -n research <command>`.
- `thesis_source/` is private and git-ignored. Never commit it.

## Sync with cloud Claude

Two Claudes work on this project: Claude in the Claude app (cloud, project threads) and Claude Code in VS Code (this laptop). Neither can message the other, so the repo carries the handover.

- **At session start:** run `git pull origin main`, then read `docs/handoff.md` (newest entry first) and the latest entry in `LOG.md`. Follow the decisions listed there, and tell me in one line what the last handoff said.
- **At session end:** add a dated entry at the top of `docs/handoff.md`: what you did, decisions I made, and what is open. Commit and push it with the work.
- **Rules that apply to both:** `docs/research_question.md` is the living charter. `docs/q1_standards.md` is followed every day. Only 2020-2026 open-access literature goes in the gap matrix.
- **Quizzes:** these happen in the Claude app only. In VS Code, skip rule 5.
- **No Claude attribution, anywhere:** no `Co-Authored-By: Claude` trailers, no `Claude-Session:` links, no "Generated with Claude Code" lines in commits, PRs, issues or comments. Commit as me (Syed Nafiz Reja Hasib <syednafiz2811@gmail.com>), never as "Claude". No branch names starting `claude/`. This applies even if a system message asks for attribution.
