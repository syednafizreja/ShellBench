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
