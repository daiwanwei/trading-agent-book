"""Generate appendix A (skills) and B (workflows) from the upstream repo."""

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

DEFAULT_UPSTREAM = Path.home() / "Projects/wade/math/claude-trading-skills"
UPSTREAM_URL = "https://github.com/tradermonty/claude-trading-skills"


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
