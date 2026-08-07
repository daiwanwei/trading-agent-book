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

    issues = check_summary_files(args.book)
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
