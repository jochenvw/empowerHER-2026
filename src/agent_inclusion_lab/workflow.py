from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from agent_inclusion_lab.agents.contracts import AgentStage
from agent_inclusion_lab.agents.registry import resolve_agent
from agent_inclusion_lab.evals.inclusion_eval import evaluate_text

_STAGES: tuple[AgentStage, ...] = ("draft",)
_SELECTION_ENV_BY_STAGE: dict[AgentStage, str] = {
    "draft": "INCLUSION_DRAFT_AGENT",
}


@dataclass(frozen=True)
class WorkflowResult:
    baseline_output: str
    review: dict[str, Any]
    rewritten_output: str
    baseline_eval: dict[str, Any]
    rewritten_eval: dict[str, Any]


def _build_initial_state(legacy_guidance: str, inclusive_principles: str) -> dict[str, Any]:
    return {
        "legacy_guidance": legacy_guidance,
        "inclusive_principles": inclusive_principles,
        "baseline_output": "",
        "review": {},
        "rewritten_output": "",
    }


def _selected_agent_id(stage: AgentStage) -> str | None:
    env_var = _SELECTION_ENV_BY_STAGE[stage]
    return os.getenv(env_var)


def run_inclusion_workflow(legacy_guidance: str, inclusive_principles: str) -> WorkflowResult:
    state = _build_initial_state(legacy_guidance, inclusive_principles)

    for stage in _STAGES:
        agent = resolve_agent(stage=stage, requested_agent_id=_selected_agent_id(stage))
        updates = agent.runner(state)
        if not updates:
            raise RuntimeError(f"Agent {agent.agent_id} returned no state updates.")
        state.update(updates)

    baseline_output = str(state["baseline_output"])
    review: dict[str, Any] = {}
    rewritten_output = baseline_output

    baseline_eval = evaluate_text(baseline_output)
    rewritten_eval = baseline_eval
    return WorkflowResult(
        baseline_output=baseline_output,
        review=review,
        rewritten_output=rewritten_output,
        baseline_eval=baseline_eval,
        rewritten_eval=rewritten_eval,
    )
