from __future__ import annotations

from agent_inclusion_lab.agents.contracts import AgentPlugin
from agent_inclusion_lab.model_client import generate_text


def run_baseline_agent(legacy_guidance: str) -> str:
    prompt = (
        "Use the available hiring guidance to draft a job description and interview "
        "rubric for a Senior Engineering Manager.\n\n"
        "Guidance:\n"
        f"{legacy_guidance}"
    )
    return generate_text(prompt)


def _run_plugin(state: dict[str, object]) -> dict[str, object]:
    legacy_guidance = str(state["legacy_guidance"])
    return {"baseline_output": run_baseline_agent(legacy_guidance)}


AGENT_PLUGIN = AgentPlugin(
    agent_id="baseline.default",
    stage="draft",
    description="Drafts a role description and interview rubric from legacy guidance.",
    runner=_run_plugin,
)
