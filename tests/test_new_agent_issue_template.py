from __future__ import annotations

from pathlib import Path


def test_new_agent_template_points_to_scaffold_skill_and_no_workflow_edits() -> None:
    template = Path(".github/ISSUE_TEMPLATE/new-agent.yml").read_text(encoding="utf-8")

    assert "agent-scaffolder" in template
    assert "workflow.py" in template
    assert "registry.py" in template
