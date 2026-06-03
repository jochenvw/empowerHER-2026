from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Any

from agent_inclusion_lab.agents.contracts import AgentStage
from agent_inclusion_lab.agents.registry import resolve_agent
from agent_inclusion_lab.evals.inclusion_eval import evaluate_text

_SELECTION_ENV_BY_STAGE: dict[AgentStage, str] = {
    "draft": "INCLUSION_DRAFT_AGENT",
    "rewrite": "INCLUSION_REWRITE_AGENT",
}


@dataclass(frozen=True)
class WorkflowResult:
    job_post_path: str
    baseline_output: str
    feedback_summary: list[str]
    review_panel: list[dict[str, Any]]
    rewritten_output: str
    baseline_eval: dict[str, Any]
    rewritten_eval: dict[str, Any]


def _build_initial_state(job_post_path: str | Path, inclusive_principles: str) -> dict[str, Any]:
    return {
        "job_post_path": str(job_post_path),
        "inclusive_principles": inclusive_principles,
        "baseline_output": "",
        "reviews": [],
        "rewritten_output": "",
    }


def _selected_agent_id(stage: AgentStage) -> str | None:
    env_var = _SELECTION_ENV_BY_STAGE[stage]
    return os.getenv(env_var)


def _selected_review_agent_ids() -> list[str]:
    raw = os.getenv("INCLUSION_REVIEW_AGENTS", "")
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if values:
        return values
    configured_default = os.getenv("INCLUSION_REVIEW_AGENT")
    if configured_default:
        default = resolve_agent(stage="review", requested_agent_id=configured_default)
        return [default.agent_id]
    return [
        "reviewer.gender_eligibility",
        "reviewer.leadership_framing",
        "reviewer.equal_access",
    ]


def run_inclusion_workflow(job_post_path: str | Path, inclusive_principles: str) -> WorkflowResult:
    state = _build_initial_state(job_post_path, inclusive_principles)
    draft_agent = resolve_agent(stage="draft", requested_agent_id=_selected_agent_id("draft"))
    updates = draft_agent.runner(state)
    if not updates:
        raise RuntimeError(f"Agent {draft_agent.agent_id} returned no state updates.")
    state.update(updates)

    review_panel: list[dict[str, Any]] = []
    for reviewer_id in _selected_review_agent_ids():
        reviewer = resolve_agent(stage="review", requested_agent_id=reviewer_id)
        updates = reviewer.runner(state)
        review = updates.get("review")
        if isinstance(review, dict):
            review_panel.append(review)
    state["reviews"] = review_panel

    rewrite_agent = resolve_agent(stage="rewrite", requested_agent_id=_selected_agent_id("rewrite"))
    rewrite_updates = rewrite_agent.runner(state)
    if rewrite_updates:
        state.update(rewrite_updates)

    baseline_output = str(state["baseline_output"])
    rewritten_output = baseline_output

    baseline_eval = evaluate_text(baseline_output)
    rewritten_output = str(state.get("rewritten_output", baseline_output))
    rewritten_eval = evaluate_text(rewritten_output)
    feedback_summary = [
        str(item.get("summary", "")).strip()
        for item in review_panel
        if str(item.get("summary", "")).strip()
    ]
    return WorkflowResult(
        job_post_path=str(state["job_post_path"]),
        baseline_output=baseline_output,
        feedback_summary=feedback_summary,
        review_panel=review_panel,
        rewritten_output=rewritten_output,
        baseline_eval=baseline_eval,
        rewritten_eval=rewritten_eval,
    )
