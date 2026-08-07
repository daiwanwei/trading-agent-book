"""Generate appendix A (skills) and B (workflows) from the upstream repo."""

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

DEFAULT_UPSTREAM = Path.home() / "Projects/wade/math/claude-trading-skills"
UPSTREAM_URL = "https://github.com/tradermonty/claude-trading-skills"

REQ_LABEL = {"required": "必需", "recommended": "建議", "optional": "可選"}


def load_skills_index(upstream: Path) -> dict:
    with open(upstream / "skills-index.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_workflows(upstream: Path) -> list:
    flows = []
    for path in sorted((upstream / "workflows").glob("*.yaml")):
        with open(path, encoding="utf-8") as f:
            flows.append(yaml.safe_load(f))
    return sorted(flows, key=lambda w: w["id"])


def get_upstream_commit(upstream: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(upstream), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _api_cell(skill: dict) -> str:
    parts = []
    for integ in skill.get("integrations", []):
        label = REQ_LABEL.get(integ.get("requirement"))
        if label:
            parts.append(f"{integ['id']}（{label}）")
    return "、".join(parts) if parts else "—"


def render_skills_appendix(index: dict, upstream_commit: str) -> str:
    lines = [
        "<!-- generated: true -->",
        f"<!-- source: tradermonty/claude-trading-skills@{upstream_commit} -->",
        "# 附錄 A：Skills 速查表",
        "",
        f"共 {len(index['skills'])} 個 skills，依分類排列。"
        "本頁由 `scripts/generate_appendix.py` 自動生成，請勿手動編輯。",
    ]
    for category in index["categories"]:
        cat_skills = [s for s in index["skills"] if s["category"] == category]
        if not cat_skills:
            continue
        lines += [
            "",
            f"## {category}",
            "",
            "| Skill | 摘要 | 節奏 | 難度 | API |",
            "|---|---|---|---|---|",
        ]
        for skill in cat_skills:
            link = f"[{skill['display_name']}]({UPSTREAM_URL}/tree/main/skills/{skill['id']})"
            summary = " ".join(str(skill.get("summary", "")).split())
            lines.append(
                f"| {link} | {summary} | {skill.get('timeframe', '—')} "
                f"| {skill.get('difficulty', '—')} | {_api_cell(skill)} |"
            )
    return "\n".join(lines) + "\n"
