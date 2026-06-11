from __future__ import annotations

from pathlib import Path

import pytest

from agent_inclusion_lab.skills.agent_scaffolder import scaffold_agent_from_issue


def test_scaffold_agent_from_issue_creates_agent_files(tmp_path: Path) -> None:
    issue_body = """
### Agent name
accessibility-reviewer

### What should it do?
Review-stage agent that flags inaccessible job-posting language and suggests inclusive wording.

### Preferred stage (optional)
review

### Anything else? (optional)
Consider accommodations and avoid assumptions about physical ability.

"""

    agent_dir = scaffold_agent_from_issue(issue_body, root=tmp_path)

    assert agent_dir == tmp_path / "src" / "agent_inclusion_lab" / "agents" / "accessibility_reviewer"
    assert (agent_dir / "__init__.py").exists()
    assert (agent_dir / "system_prompt.md").exists()

    init_text = (agent_dir / "__init__.py").read_text(encoding="utf-8")
    prompt_text = (agent_dir / "system_prompt.md").read_text(encoding="utf-8")
    test_text = (tmp_path / "tests" / "test_accessibility_reviewer_agent.py").read_text(encoding="utf-8")

    assert 'agent_id="review.accessibility_reviewer"' in init_text
    assert 'stage="review"' in init_text
    assert "inaccessible job-posting language" in prompt_text
    assert "workflow.py or registry.py" in prompt_text
    assert "resolve_agent(stage=\"review\"" in test_text


def test_scaffold_agent_from_issue_rejects_missing_name(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="agent name"):
        scaffold_agent_from_issue(
            """
### What should it do?
Review-stage agent.
""",
            root=tmp_path,
        )
