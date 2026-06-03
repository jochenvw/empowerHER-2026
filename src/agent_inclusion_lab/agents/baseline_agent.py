from __future__ import annotations

from agent_inclusion_lab.agents.contracts import AgentPlugin


def run_baseline_agent(legacy_guidance: str) -> str:
    return legacy_guidance.strip()


def _run_plugin(state: dict[str, object]) -> dict[str, object]:
    legacy_guidance = str(state["legacy_guidance"])
    return {"baseline_output": run_baseline_agent(legacy_guidance)}


AGENT_PLUGIN = AgentPlugin(
    agent_id="baseline.default",
    stage="draft",
    description="Returns the legacy job opening text verbatim as the baseline output.",
    runner=_run_plugin,
)
