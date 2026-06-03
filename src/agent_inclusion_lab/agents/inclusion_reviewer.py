from __future__ import annotations

from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin


def run_inclusion_reviewer(text: str) -> dict[str, Any]:
    return {
        "reviewer": "reviewer.accept_all",
        "summary": "No improvements suggested.",
        "suggestions": [],
    }


def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
    baseline_output = str(state["baseline_output"])
    return {"review": run_inclusion_reviewer(baseline_output)}


AGENT_PLUGIN = AgentPlugin(
    agent_id="reviewer.default",
    stage="review",
    description="Main-branch placeholder reviewer that suggests no changes.",
    runner=_run_plugin,
)
