"""Validate book structure: SUMMARY <-> files, upstream link targets."""

import argparse
import re
import sys
from pathlib import Path

DEFAULT_UPSTREAM = Path.home() / "Projects/wade/math/claude-trading-skills"
SUMMARY_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#]+\.md)\)")
UPSTREAM_LINK_RE = re.compile(
    r"https://github\.com/tradermonty/claude-trading-skills/(?:tree|blob)/main/([^)\s#]+)"
)

# Halfwidth punctuation next to CJK text is a common mixed-width slip in a
# CJK-prose book. `()` are intentionally excluded: English citations and
# inline tags rely on halfwidth parens far too often to lint them.
#
# CJK_RE covers only Han ideographs (U+4E00-U+9FFF), not the wider CJK
# Symbols/Punctuation block (U+3000-U+303F). That block contains the
# full-width quote/bracket delimiters (e.g. `「」『』`) this book uses to
# wrap verbatim English quotations -- an English quote's own halfwidth
# punctuation legitimately touches its closing full-width bracket
# (`...cash-priority?」`), which is correct style, not a mixed-width slip.
CJK_RE = r"[一-鿿]"
HALFWIDTH_NEAR_CJK_RE = re.compile(
    rf"(?:{CJK_RE}[,;:?!])|(?:[,;:?!]{CJK_RE})"
)
CODE_SPAN_RE = re.compile(r"`[^`]*`")
LINK_DEST_RE = re.compile(r"\]\([^)]*\)")
FENCE_MARKER_RE = re.compile(r"^\s*```")


def parse_summary(text: str) -> list:
    return SUMMARY_LINK_RE.findall(text)


def check_summary_files(book_dir: Path) -> list:
    issues = []
    targets = parse_summary((book_dir / "SUMMARY.md").read_text(encoding="utf-8"))
    for target in targets:
        if not (book_dir / target).exists():
            issues.append(f"SUMMARY links to missing file: {target}")
    listed = set(targets)
    for md in book_dir.rglob("*.md"):
        rel = md.relative_to(book_dir).as_posix()
        if rel != "SUMMARY.md" and rel not in listed:
            issues.append(f"file not listed in SUMMARY: {rel}")
    return issues


def find_halfwidth_punct(text: str) -> list:
    """Find halfwidth `,;:?!` immediately adjacent to CJK text.

    Fenced code blocks are tracked with a line-preserving state machine
    (toggle in/out on each ``` marker line) so reported line numbers match
    the original file exactly -- unlike a whole-text regex substitution,
    which would shift every line number after a removed fence.
    """
    hits = []
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if FENCE_MARKER_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        clean = CODE_SPAN_RE.sub("", line)
        clean = LINK_DEST_RE.sub("]()", clean)
        m = HALFWIDTH_NEAR_CJK_RE.search(clean)
        if m:
            hits.append((lineno, m.group(0)))
    return hits


def check_punctuation(book_dir: Path) -> list:
    issues = []
    for md in sorted(book_dir.rglob("*.md")):
        rel = md.relative_to(book_dir).as_posix()
        text = md.read_text(encoding="utf-8")
        for lineno, frag in find_halfwidth_punct(text):
            issues.append(f"{rel}:{lineno}: halfwidth punct near CJK: {frag}")
    return issues


def find_upstream_links(text: str) -> list:
    return UPSTREAM_LINK_RE.findall(text)


def check_upstream_links(book_dir: Path, upstream: Path) -> list:
    issues = []
    for md in sorted(book_dir.rglob("*.md")):
        for rel in find_upstream_links(md.read_text(encoding="utf-8")):
            if not (upstream / rel).exists():
                issues.append(
                    f"{md.relative_to(book_dir).as_posix()}: upstream path missing: {rel}"
                )
    return issues


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate book structure and links")
    parser.add_argument(
        "--book",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "book",
    )
    parser.add_argument("--upstream", type=Path, default=DEFAULT_UPSTREAM)
    args = parser.parse_args(argv)

    if not (args.book / "SUMMARY.md").exists():
        print(f"error: SUMMARY.md not found at {args.book}", file=sys.stderr)
        return 1

    issues = check_summary_files(args.book)
    issues += check_punctuation(args.book)
    if args.upstream.exists():
        issues += check_upstream_links(args.book, args.upstream)
    else:
        print(f"warning: upstream not found at {args.upstream}; link check skipped")

    for issue in issues:
        print(issue)
    print(f"{len(issues)} issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
