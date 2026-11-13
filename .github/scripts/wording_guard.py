"""Keep assistant product names out of tracked files.

The AI-use disclosure (docs/ai_use.md) is the one place that names the tool.
Anywhere else, the name is replaced by "the AI assistant". With --check-commits
BASE HEAD, also fails if a commit message in BASE..HEAD carries an assistant
trailer, which cannot be fixed without rewriting history.

Run: python .github/scripts/wording_guard.py [--check-commits BASE HEAD]
"""
import re
import subprocess
import sys

KEEP = {"docs/ai_use.md"}
NAME = "C" + "laude"  # built in two parts so this file does not match itself
FIND = re.compile(NAME, re.I)
RULES = [
    (NAME + r" Code in VS Code", "the AI assistant"),
    (r"VS Code " + NAME, "the AI assistant"),
    (NAME + r" in the (?:" + NAME + r" )?app", "the AI assistant"),
    (r"[Bb]oth " + NAME + "s", "two separate AI-assisted runs"),
    (NAME + r" Pro", "the AI-assistance subscription"),
    (NAME.upper() + r"\.md rule (\d)", r"project rule \1"),
    (NAME.upper() + r"\.md", "the project rules"),
    (NAME + r" Code", "the AI assistant"),
    (NAME + r"'s", "the AI assistant's"),
    (NAME + r"s\b", "AI assistants"),
    (r"\b" + NAME + r"\b", "the AI assistant"),
    (r"(?i)" + NAME, "AI assistant"),  # any leftover form, e.g. lower case
]


def tracked_matches() -> list[str]:
    out = subprocess.run(["git", "grep", "-I", "-il", NAME], capture_output=True, text=True).stdout
    return [f for f in out.split() if f not in KEEP]


def scrub(path: str) -> None:
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    s = raw.decode("utf-8-sig")
    crlf = "\r\n" in s
    s = s.replace("\r\n", "\n")
    for pattern, repl in RULES:
        s = re.sub(pattern, repl, s)
    s = re.sub(r"\b([Tt])he the AI", r"\1he AI", s)
    s = re.sub(r"(^|[.!?]\s+|\*\*|\| |- |\()the AI assistant",
               lambda m: m.group(1) + "The AI assistant", s, flags=re.M)
    if crlf:
        s = s.replace("\n", "\r\n")
    open(path, "wb").write((b"\xef\xbb\xbf" if bom else b"") + s.encode("utf-8"))
    print("cleaned", path)


def bad_commits(base: str, head: str) -> list[str]:
    log = subprocess.run(["git", "log", "--format=%h %an <%ae>%n%B%x00", f"{base}..{head}"],
                         capture_output=True, text=True).stdout
    return [c.strip().splitlines()[0] for c in log.split("\x00") if FIND.search(c)]


def main() -> int:
    for f in tracked_matches():
        scrub(f)
    if len(sys.argv) == 4 and sys.argv[1] == "--check-commits":
        bad = bad_commits(sys.argv[2], sys.argv[3])
        if bad:
            print("Commit messages or authors name the assistant; reword them before merging:")
            print("\n".join("  " + b for b in bad))
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
