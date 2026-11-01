"""SessionStart hook: give a cleared or compacted session its project state.

Claude Code adds this script's stdout to the new session's context. It runs
only for the `clear` and `compact` sources (see .claude/settings.local.json).
It prints a short briefing so that a one-word "continue" is enough to resume.
"""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / "docs" / "handoff.md"
MAX_HANDOFF_CHARS = 1500  # keeps the briefing small; the hook must not feed a thrash
GIT_TIMEOUT_S = 10


def newest_entry(text):
    """Return the first '## ' section of a markdown file, or '' if none."""
    parts = re.split(r"(?m)^(?=## )", text)
    return parts[1].strip() if len(parts) > 1 else ""


def git(*args):
    """Run a git command in the repo and return its trimmed stdout."""
    try:
        done = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT_S,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "(git unavailable)"
    return done.stdout.rstrip()


def main():
    """Print the resume briefing to stdout."""
    try:
        entry = newest_entry(HANDOFF.read_text(encoding="utf-8"))
    except OSError:
        entry = "(docs/handoff.md could not be read)"
    if len(entry) > MAX_HANDOFF_CHARS:
        entry = entry[:MAX_HANDOFF_CHARS] + " ... [cut; read the file for the rest]"

    print("Context was just cleared or compacted. Resume the ShellBench work.")
    print("If the user's message is only 'continue', pick up the open task")
    print("from the state below. Read files in small chunks and keep tool")
    print("output short, because a large read may be what filled the context.")
    print()
    print(f"Branch: {git('branch', '--show-current')}")
    print(f"Uncommitted files:\n{git('status', '--short') or '(none)'}")
    print(f"Last commits:\n{git('log', '--oneline', '-3')}")
    print()
    print(f"Newest handoff entry:\n{entry}")


if __name__ == "__main__":
    main()
