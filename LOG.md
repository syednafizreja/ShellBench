# ShellBench log

## Day 0 - 18 Oct 2026
- Env 'research' uses Python 3.12 (OpenSeesPy needs python312.dll)
- Installed: gmsh, OpenSeesPy, CalculiX 2.23, numpy, scipy, pandas, matplotlib, scikit-learn, pytest
- Fixed: missing Documents folder, conda in PowerShell, Git PATH
- Claude Code connected; Project created with env research / Py 3.12

## Day 1 - 19 Oct 2026
Done: package layout, CLAUDE.md, README, 8 week issues; commit 148360f pushed.
Checked: pytest 2 passed; git ls-files thesis_source empty (thesis not on GitHub).
Problems: gh CLI not found in VS Code terminal (PATH); issues added by hand instead.
Tomorrow: Day 2, build docs/baseline_spec.md; have thesis calc sheets and GB 50010/50011 to hand.

## Day 2 - 20 Oct 2026
Day 2 done: docs/baseline_spec.md lists every model input with its thesis source and 16 inconsistencies (B1-B16), each with my decision and reason. Carried forward: Tg used in alpha1 unconfirmed (B5); T1 and Gi computed by OpenSeesPy (B9); T 8-12 row 5 spurious (B4); T 9.3 axial forces wrong; generator rounding rule for the 0.85 axial limit (B16); walls in the carbon boundary (B15).
