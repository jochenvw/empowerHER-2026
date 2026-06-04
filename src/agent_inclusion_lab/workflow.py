from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_inclusion_lab.agents.registry import resolve_agent
from agent_inclusion_lab.evals.inclusion_eval import evaluate_text_async


@dataclass(frozen=True)
class WorkflowResult:
    job_post_path: str
    baseline_output: str
    feedback_summary: list[str]
    review_panel: list[dict[str, Any]]
    rewritten_output: str
    baseline_eval: dict[str, Any]
    rewritten_eval: dict[str, Any]


def _selected_agent_id(env_var: str) -> str | None:
    selected = os.getenv(env_var)
    return selected.strip() if selected else None


def _extract_review_item(updates: dict[str, Any]) -> dict[str, Any]:
    review = updates.get("review")
    if isinstance(review, dict):
        return review
    return {
        "reviewer": "reviewer.default",
        "summary": "No improvements suggested.",
        "suggestions": [],
        "evidence_spans": [],
    }


async def run_inclusion_workflow_async(
    job_post_path: str | Path, inclusive_principles: str
) -> WorkflowResult:
    state: dict[str, Any] = {
        "job_post_path": str(job_post_path),
        "inclusive_principles": inclusive_principles,
    }

    draft = resolve_agent(
        stage="draft",
        requested_agent_id=_selected_agent_id("INCLUSION_DRAFT_AGENT"),
    )
    state.update(draft.runner(state))

    review = resolve_agent(
        stage="review",
        requested_agent_id=_selected_agent_id("INCLUSION_REVIEW_AGENT"),
    )
    review_item = _extract_review_item(review.runner(state))
    review_panel = [review_item]
    state["review"] = review_item

    baseline_output = str(state.get("baseline_output", "")).strip()

    rewrite = resolve_agent(
        stage="rewrite",
        requested_agent_id=_selected_agent_id("INCLUSION_REWRITE_AGENT"),
    )
    state.update(rewrite.runner(state))
    rewritten_output = str(state.get("rewritten_output", baseline_output)).strip()

    feedback_summary = [str(review_item.get("summary", "")).strip() or "No improvements suggested."]

    baseline_eval = await evaluate_text_async(baseline_output)
    # The LLM judge is nondeterministic, so re-judging identical text could show a
    # misleading score change. Reuse the baseline result when no rewrite happened.
    if rewritten_output == baseline_output:
        rewritten_eval = baseline_eval
    else:
        rewritten_eval = await evaluate_text_async(rewritten_output)

    return WorkflowResult(
        job_post_path=str(state["job_post_path"]),
        baseline_output=baseline_output,
        feedback_summary=feedback_summary,
        review_panel=review_panel,
        rewritten_output=rewritten_output,
        baseline_eval=baseline_eval,
        rewritten_eval=rewritten_eval,
    )


def run_inclusion_workflow(job_post_path: str | Path, inclusive_principles: str) -> WorkflowResult:
    return asyncio.run(
        run_inclusion_workflow_async(
            job_post_path=job_post_path,
            inclusive_principles=inclusive_principles,
        )
    )
