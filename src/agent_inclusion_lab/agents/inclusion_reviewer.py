from __future__ import annotations

from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin
from agent_inclusion_lab.evals.inclusion_eval import evaluate_text


def run_inclusion_reviewer(text: str) -> dict[str, Any]:
    evaluation = evaluate_text(text)
    evals = evaluation["evals"]
    return {
        "overall_score": evaluation["overall_score"],
        "overall_pass": evaluation["overall_pass"],
        "evals": evals,
        "findings": [f"{item['eval_name']}: {item['rationale']}" for item in evals],
    }


def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
    baseline_output = str(state["baseline_output"])
    return {"review": run_inclusion_reviewer(baseline_output)}


AGENT_PLUGIN = AgentPlugin(
    agent_id="reviewer.default",
    stage="review",
    description="Reviews baseline output for inclusion risk indicators.",
    runner=_run_plugin,
)
