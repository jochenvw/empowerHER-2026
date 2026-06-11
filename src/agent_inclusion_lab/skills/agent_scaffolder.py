from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Final, cast

from agent_inclusion_lab.agents.contracts import AgentStage

_AGENT_ROOT: Final = "src/agent_inclusion_lab/agents"
_DEFAULT_TEST_ROOT: Final = "tests"
_VALID_STAGE_VALUES: Final = {"draft", "review", "rewrite"}


@dataclass(frozen=True)
class AgentIssueSpec:
    agent_name: str
    responsibility: str
    stage: AgentStage
    details: str = ""


def scaffold_agent_from_issue(issue_body: str, root: str | Path | None = None) -> Path:
    """Create a new agent scaffold from a GitHub issue body."""
    fields = _parse_issue_body(issue_body)
    agent_name = _require_field(fields, "agent name")
    responsibility = _require_field(fields, "what should it do?")
    details = fields.get("anything else? (optional)", "")
    stage = _resolve_stage(fields, responsibility)
    spec = AgentIssueSpec(
        agent_name=agent_name,
        responsibility=responsibility,
        stage=stage,
        details=details,
    )
    return scaffold_agent_plugin(spec, root=root)


def scaffold_agent_plugin(spec: AgentIssueSpec, root: str | Path | None = None) -> Path:
    """Create a new agent folder, scaffolded test, and system prompt."""
    project_root = Path(root) if root is not None else Path.cwd()
    agent_slug = _slugify(spec.agent_name)
    agent_id = f"{spec.stage}.{agent_slug}"
    agent_dir = project_root / _AGENT_ROOT / agent_slug
    test_path = project_root / _DEFAULT_TEST_ROOT / f"test_{agent_slug}_agent.py"

    if agent_dir.exists():
        raise FileExistsError(f"Agent folder already exists: {agent_dir}")

    agent_dir.mkdir(parents=True, exist_ok=False)
    test_path.parent.mkdir(parents=True, exist_ok=True)

    (agent_dir / "__init__.py").write_text(
        _render_agent_module(agent_id=agent_id, stage=spec.stage, description=spec.responsibility),
        encoding="utf-8",
    )
    (agent_dir / "system_prompt.md").write_text(
        _render_system_prompt(spec=spec, agent_id=agent_id),
        encoding="utf-8",
    )
    (test_path).write_text(
        _render_test_module(agent_id=agent_id, stage=spec.stage, agent_slug=agent_slug),
        encoding="utf-8",
    )
    return agent_dir


def _parse_issue_body(issue_body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    current_key: str | None = None
    buffer: list[str] = []

    for raw_line in issue_body.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("- ["):
            break

        if stripped.startswith("### "):
            if current_key is not None:
                fields[current_key] = "\n".join(buffer).strip()
            current_key = stripped[4:].strip().lower()
            buffer = []
            continue

        if current_key is not None:
            buffer.append(line)

    if current_key is not None:
        fields[current_key] = "\n".join(buffer).strip()

    return fields


def _require_field(fields: dict[str, str], key_prefix: str) -> str:
    value = _lookup_field(fields, key_prefix)
    if not value:
        raise ValueError(f"Missing required issue field: {key_prefix}")
    return value


def _lookup_field(fields: dict[str, str], key_prefix: str) -> str:
    key_prefix = key_prefix.lower()
    for key, value in fields.items():
        if key.startswith(key_prefix):
            return value
    return ""


def _resolve_stage(fields: dict[str, str], responsibility: str) -> AgentStage:
    explicit = _lookup_field(fields, "preferred stage")
    normalized = _slugify(explicit) if explicit else ""
    if normalized in _VALID_STAGE_VALUES:
        return cast(AgentStage, normalized)

    text = f"{responsibility}\n{_lookup_field(fields, 'anything else')}".lower()
    if "draft" in text:
        return "draft"
    if "review" in text:
        return "review"
    return "rewrite"


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    if not slug:
        raise ValueError("Agent name must contain at least one letter or digit.")
    if slug[0].isdigit():
        raise ValueError("Agent name must not start with a digit.")
    return slug


def _render_agent_module(*, agent_id: str, stage: AgentStage, description: str) -> str:
    return dedent(
        f'''\
        from __future__ import annotations

        from typing import Any

        from agent_inclusion_lab.agents.contracts import AgentPlugin


        def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
            _ = state
            return {{}}


        AGENT_PLUGIN = AgentPlugin(
            agent_id="{agent_id}",
            stage="{stage}",
            description={description!r},
            runner=_run_plugin,
        )
        '''
    )


def _render_system_prompt(*, spec: AgentIssueSpec, agent_id: str) -> str:
    details = spec.details.strip() or "No extra context provided."
    return dedent(
        f"""\
        You are the {agent_id} agent for empowerHER.

        Goal:
        {spec.responsibility}

        Context:
        {details}

        Keep this agent in its own folder, export AGENT_PLUGIN, and do not edit workflow.py or registry.py.
        """
    )


def _render_test_module(*, agent_id: str, stage: AgentStage, agent_slug: str) -> str:
    return dedent(
        f'''\
        from agent_inclusion_lab.agents.registry import discover_agent_plugins, resolve_agent


        def test_{agent_slug}_plugin_is_discoverable() -> None:
            plugins = discover_agent_plugins()
            assert "{agent_id}" in plugins
            plugin = resolve_agent(stage="{stage}", requested_agent_id="{agent_id}")
            assert plugin.agent_id == "{agent_id}"
            assert plugin.stage == "{stage}"
            assert plugin.description
        '''
    )
