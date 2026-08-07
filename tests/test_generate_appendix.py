import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from generate_appendix import (
    load_skills_index,
    load_workflows,
    get_upstream_commit,
)

FIXTURE = Path(__file__).parent / "fixtures" / "upstream"


def test_load_skills_index():
    index = load_skills_index(FIXTURE)
    assert index["categories"] == ["market-regime", "meta"]
    assert [s["id"] for s in index["skills"]] == ["alpha-skill", "beta-skill"]


def test_load_workflows_sorted_by_id():
    flows = load_workflows(FIXTURE)
    assert [w["id"] for w in flows] == ["demo-flow"]
    assert flows[0]["steps"][0]["decision_gate"] is True


def test_get_upstream_commit_unknown_for_missing_dir(tmp_path):
    # 注意：不能拿 FIXTURE 測「unknown」——fixtures 在本 repo 的 git 之內，
    # git -C 會往上找到本 repo 而回傳真實 hash。用系統暫存區的不存在路徑。
    assert get_upstream_commit(tmp_path / "nowhere") == "unknown"
