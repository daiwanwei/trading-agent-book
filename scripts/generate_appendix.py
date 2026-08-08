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


def _md_escape(text: str) -> str:
    """Escape pipe characters for Markdown table cells."""
    return str(text).replace("|", "\\|")


def load_workflows(upstream: Path) -> list:
    workflows_dir = upstream / "workflows"
    if not workflows_dir.is_dir():
        raise FileNotFoundError(f"workflows directory not found at {workflows_dir}")
    flows = []
    for path in sorted(workflows_dir.glob("*.yaml")):
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
    rendered_skill_ids = []
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
            rendered_skill_ids.append(skill["id"])
            link = f"[{skill['display_name']}]({UPSTREAM_URL}/tree/main/skills/{skill['id']})"
            summary = _md_escape(" ".join(str(skill.get("summary", "")).split()))
            lines.append(
                f"| {link} | {summary} | {_md_escape(str(skill.get('timeframe', '—')))} "
                f"| {_md_escape(str(skill.get('difficulty', '—')))} | {_md_escape(_api_cell(skill))} |"
            )

    # Fail-closed: check that all skills were rendered
    all_skill_ids = {s["id"] for s in index["skills"]}
    rendered_ids = set(rendered_skill_ids)
    uncovered_ids = all_skill_ids - rendered_ids
    if uncovered_ids:
        uncovered_with_cats = []
        for skill in index["skills"]:
            if skill["id"] in uncovered_ids:
                uncovered_with_cats.append(f"{skill['id']} ({skill['category']})")
        raise ValueError(f"Uncovered skills in render: {', '.join(uncovered_with_cats)}")

    return "\n".join(lines) + "\n"


def render_workflows_appendix(workflows: list, upstream_commit: str) -> str:
    lines = [
        "<!-- generated: true -->",
        f"<!-- source: tradermonty/claude-trading-skills@{upstream_commit} -->",
        "# 附錄 B：Workflows 對照表",
        "",
        f"共 {len(workflows)} 條 workflow。"
        "本頁由 `scripts/generate_appendix.py` 自動生成，請勿手動編輯。",
    ]
    for wf in workflows:
        lines += ["", f"## {wf['display_name']}（`{wf['id']}`）", ""]
        lines.append(
            f"- 節奏：{wf.get('cadence', '—')}｜預估 {wf.get('estimated_minutes', '—')} 分鐘"
            f"｜難度：{wf.get('difficulty', '—')}｜API profile：{wf.get('api_profile', '—')}"
        )
        if wf.get("when_to_run"):
            lines.append(f"- 何時執行：{' '.join(str(wf['when_to_run']).split())}")
        if wf.get("when_not_to_run"):
            lines.append(f"- 何時不執行：{' '.join(str(wf['when_not_to_run']).split())}")
        required = "、".join(f"`{s}`" for s in wf.get("required_skills", []))
        optional = "、".join(f"`{s}`" for s in wf.get("optional_skills", []))
        lines.append(f"- 必要 skills：{required or '—'}")
        if optional:
            lines.append(f"- 可選 skills：{optional}")
        for pre in wf.get("prerequisite_workflows", []):
            lines.append(f"- 前置 workflow：`{pre['id']}`（需要 artifact `{pre['artifact']}`）")
        lines += ["", "| # | 步驟 | Skill | 決策閘 |", "|---|---|---|---|"]
        for step in wf.get("steps", []):
            gate = "✅" if step.get("decision_gate") else ""
            opt_mark = "（可選）" if step.get("optional") else ""
            lines.append(
                f"| {step['step']} | {_md_escape(step['name'])}{opt_mark} "
                f"| `{step.get('skill', '—')}` | {gate} |"
            )
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate appendix A/B from the upstream claude-trading-skills repo"
    )
    parser.add_argument("--upstream", type=Path, default=DEFAULT_UPSTREAM)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "book" / "appendix",
    )
    args = parser.parse_args(argv)

    if not (args.upstream / "skills-index.yaml").exists():
        print(f"error: upstream not found at {args.upstream}", file=sys.stderr)
        return 1

    commit = get_upstream_commit(args.upstream)
    index = load_skills_index(args.upstream)
    try:
        workflows = load_workflows(args.upstream)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "a-skills-reference.md").write_text(
        render_skills_appendix(index, commit), encoding="utf-8"
    )
    (args.output / "b-workflows.md").write_text(
        render_workflows_appendix(workflows, commit), encoding="utf-8"
    )
    print(
        f"generated appendix A ({len(index['skills'])} skills) "
        f"and B ({len(workflows)} workflows) @ {commit}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
