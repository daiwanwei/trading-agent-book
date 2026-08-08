import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from check_book import (
    parse_summary,
    check_summary_files,
    find_upstream_links,
    check_upstream_links,
    find_halfwidth_punct,
    check_punctuation,
    main,
)


def make_book(tmp_path):
    book = tmp_path / "book"
    (book / "part1").mkdir(parents=True)
    (book / "SUMMARY.md").write_text(
        "# Summary\n\n- [首頁](README.md)\n- [一章](part1/ch1.md)\n- [缺頁](part1/missing.md)\n",
        encoding="utf-8",
    )
    (book / "README.md").write_text("# 首頁\n", encoding="utf-8")
    (book / "part1" / "ch1.md").write_text(
        "看 [SKILL](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/vcp-screener/SKILL.md)\n"
        "壞連結 [x](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/no-such/SKILL.md)\n",
        encoding="utf-8",
    )
    (book / "part1" / "orphan.md").write_text("# 孤兒頁\n", encoding="utf-8")
    return book


def make_upstream(tmp_path):
    upstream = tmp_path / "upstream"
    (upstream / "skills" / "vcp-screener").mkdir(parents=True)
    (upstream / "skills" / "vcp-screener" / "SKILL.md").write_text("x", encoding="utf-8")
    return upstream


def test_parse_summary():
    text = "- [a](README.md)\n- [b](p/c.md)\n"
    assert parse_summary(text) == ["README.md", "p/c.md"]


def test_check_summary_files_finds_missing_and_orphan(tmp_path):
    issues = check_summary_files(make_book(tmp_path))
    assert any("missing.md" in i for i in issues)
    assert any("orphan.md" in i for i in issues)
    assert not any("ch1.md" in i for i in issues)


def test_find_upstream_links():
    text = "[a](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/x/SKILL.md#sec)"
    assert find_upstream_links(text) == ["skills/x/SKILL.md"]


def test_check_upstream_links(tmp_path):
    issues = check_upstream_links(make_book(tmp_path), make_upstream(tmp_path))
    assert len(issues) == 1
    assert "no-such" in issues[0]


def test_main_exit_code(tmp_path):
    book = make_book(tmp_path)
    upstream = make_upstream(tmp_path)
    assert main(["--book", str(book), "--upstream", str(upstream)]) == 1


def test_find_halfwidth_punct_flags_cjk_adjacent():
    text = "這是一句,有問題的話\n正常句子，沒問題\n時間 07:35 不算\ncode `a:b` 不算\n比例 2:1 不算\n這句也錯:後面接中文"
    hits = find_halfwidth_punct(text)
    assert len(hits) == 2
    assert hits[0][0] == 1
    assert hits[1][0] == 6


def test_find_halfwidth_punct_ignores_english_quote_closed_by_bracket():
    # A verbatim English quotation wrapped in full-width brackets legitimately
    # ends with its own halfwidth punctuation right against the closing
    # bracket (e.g. "...cash-priority?」"). The closing bracket itself is
    # CJK *punctuation*, not a Han ideograph, so this must not be flagged --
    # a real false positive found when running the real book (see
    # book/part1-regime/05-exposure-posture.md:7).
    text = "他問「is this allowed?」然後點頭"
    assert find_halfwidth_punct(text) == []


def test_check_punctuation_on_clean_book(tmp_path):
    book = tmp_path / "book"
    book.mkdir()
    (book / "SUMMARY.md").write_text("# Summary\n\n- [a](ok.md)\n", encoding="utf-8")
    (book / "ok.md").write_text("# a\n\n全形標點，沒問題。時間 07:35。\n", encoding="utf-8")
    assert check_punctuation(book) == []


def test_main_friendly_error_on_missing_summary(tmp_path, capsys):
    empty = tmp_path / "nobook"
    empty.mkdir()
    code = main(["--book", str(empty), "--upstream", str(tmp_path / "noup")])
    assert code == 1
    err = capsys.readouterr().err
    assert "SUMMARY.md not found" in err
