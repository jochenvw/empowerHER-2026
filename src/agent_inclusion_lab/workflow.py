from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_inclusion_lab.agents.registry import discover_agent_plugins, resolve_agent
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


def _normalize_review_item(updates: dict[str, Any], fallback_reviewer: str) -> dict[str, Any]:
    review = updates.get("review")
    if isinstance(review, dict):
        return {
            "reviewer": str(review.get("reviewer", fallback_reviewer)),
            "summary": str(review.get("summary", "No improvements suggested.")).strip()
            or "No improvements suggested.",
            "suggestions": [str(item).strip() for item in review.get("suggestions", []) if str(item).strip()],
            "evidence_spans": [str(item).strip() for item in review.get("evidence_spans", []) if str(item).strip()],
        }
    return {
        "reviewer": fallback_reviewer,
        "summary": "No improvements suggested.",
        "suggestions": [],
        "evidence_spans": [],
    }


def _run_review_panel(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Run review-stage agents and collect one panel entry per reviewer.

    When ``INCLUSION_REVIEW_AGENT`` is set, only that reviewer runs. Otherwise
    every discovered review-stage agent runs, so each contributed reviewer agent
    adds its own entry to the reasoning panel.
    """
    requested = _selected_agent_id("INCLUSION_REVIEW_AGENT")
    if requested:
        reviewers = [resolve_agent(stage="review", requested_agent_id=requested)]
    else:
        reviewers = [
            plugin
            for plugin in discover_agent_plugins().values()
            if plugin.stage == "review"
        ]

    panel: list[dict[str, Any]] = []
    for plugin in reviewers:
        updates = plugin.runner(state)
        panel.append(_normalize_review_item(updates, fallback_reviewer=plugin.agent_id))
    return panel


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

    review_panel = _run_review_panel(state)
    primary_review = review_panel[0] if review_panel else _normalize_review_item({}, "reviewer.default")
    # The rewrite stage reads a single ``review`` for back-compat; expose the
    # aggregated panel separately so rewriters can consume every reviewer.
    state["review"] = primary_review
    state["review_panel"] = review_panel

    baseline_output = str(state.get("baseline_output", "")).strip()

    rewrite = resolve_agent(
        stage="rewrite",
        requested_agent_id=_selected_agent_id("INCLUSION_REWRITE_AGENT"),
    )
    state.update(rewrite.runner(state))
    rewritten_output = str(state.get("rewritten_output", baseline_output)).strip()

    feedback_summary = [
        f"{item['reviewer']}: {item['summary']}"
        for item in review_panel
    ] or ["No reviewers ran."]

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
