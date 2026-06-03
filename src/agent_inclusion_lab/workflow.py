from __future__ import annotations

import asyncio
import json
import os
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

warnings.filterwarnings(
    "ignore",
    message=".*experimental.*",
    module="agent_framework.*",
)

import agent_framework as af

from agent_inclusion_lab.agents.prompt_loader import build_agent_instructions
from agent_inclusion_lab.evals.inclusion_eval import evaluate_text
from agent_inclusion_lab.model_client import create_framework_chat_client
from agent_inclusion_lab.skills.job_post_reader import read_job_post
_REVIEWER_IDS = {
    "reviewer.gender_eligibility",
    "reviewer.leadership_framing",
    "reviewer.equal_access",
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


def _selected_review_agent_ids() -> list[str]:
    raw = os.getenv("INCLUSION_REVIEW_AGENTS", "")
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if values:
        valid = [item for item in values if item in _REVIEWER_IDS]
        if valid:
            return valid
    return sorted(_REVIEWER_IDS)


def _extract_json_payload(text: str) -> dict[str, Any]:
    candidate = text.strip()
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("No JSON object found in model output.")
    parsed = json.loads(candidate[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("Model output JSON was not an object.")
    return parsed


def _coerce_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()
    value = getattr(response, "value", None)
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError("Agent response did not include text output.")


async def run_review_panel(
    baseline_output: str,
    inclusive_principles: str,
) -> list[dict[str, Any]]:
    client = create_framework_chat_client()
    review_panel: list[dict[str, Any]] = []
    for reviewer_id in _selected_review_agent_ids():
        reviewer = af.Agent(
            id=reviewer_id,
            name=reviewer_id,
            instructions=build_agent_instructions(reviewer_id),
            client=client,
        )
        response = await reviewer.run(
            "Evaluate this job posting text only.\n"
            "Do not assume intent. Use exact text evidence.\n\n"
            f"Job posting:\n{baseline_output}\n\n"
            f"Inclusive principles context:\n{inclusive_principles}"
        )
        parsed = _extract_json_payload(_coerce_text(response))
        summary = str(parsed.get("summary", "")).strip()
        suggestions = [
            str(item).strip()
            for item in parsed.get("suggestions", [])
            if str(item).strip()
        ]
        evidence_spans = [
            str(item).strip()
            for item in parsed.get("evidence_spans", [])
            if str(item).strip()
        ]
        review_panel.append(
            {
                "reviewer": reviewer_id,
                "summary": summary,
                "suggestions": suggestions,
                "evidence_spans": evidence_spans,
            }
        )
    return review_panel


async def run_editor_agent(
    baseline_output: str,
    review_panel: list[dict[str, Any]],
    inclusive_principles: str,
) -> tuple[list[str], str]:
    client = create_framework_chat_client()
    editor = af.Agent(
        id="editor.synthesizer",
        name="editor.synthesizer",
        instructions=build_agent_instructions("editor.synthesizer"),
        client=client,
    )
    response = await editor.run(
        "Baseline posting:\n"
        f"{baseline_output}\n\n"
        "Review panel feedback (JSON):\n"
        f"{json.dumps(review_panel, ensure_ascii=True)}\n\n"
        "Inclusive principles:\n"
        f"{inclusive_principles}"
    )
    parsed = _extract_json_payload(_coerce_text(response))
    feedback_summary = [
        str(item).strip()
        for item in parsed.get("feedback_summary", [])
        if str(item).strip()
    ]
    improved = str(parsed.get("improved_job_posting", "")).strip()
    if not bool(parsed.get("change_required", False)):
        improved = baseline_output
    if not improved:
        improved = baseline_output
    if not feedback_summary:
        feedback_summary = [
            str(item.get("summary", "")).strip()
            for item in review_panel
            if str(item.get("summary", "")).strip()
        ]
    return feedback_summary, improved


async def run_inclusion_workflow_async(
    job_post_path: str | Path, inclusive_principles: str
) -> WorkflowResult:
    path = str(job_post_path)

    async def _workflow_impl(message: dict[str, str] | None = None) -> dict[str, Any]:
        if not message or "job_post_path" not in message:
            raise RuntimeError("Workflow input must include 'job_post_path'.")
        baseline_output = read_job_post(message["job_post_path"]).strip()
        review_panel = await run_review_panel(
            baseline_output=baseline_output,
            inclusive_principles=inclusive_principles,
        )
        feedback_summary, rewritten_output = await run_editor_agent(
            baseline_output=baseline_output,
            review_panel=review_panel,
            inclusive_principles=inclusive_principles,
        )
        return {
            "baseline_output": baseline_output,
            "review_panel": review_panel,
            "feedback_summary": feedback_summary,
            "rewritten_output": rewritten_output,
        }

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=".*FUNCTIONAL_WORKFLOWS.*",
        )
        workflow = af.FunctionalWorkflow(
            _workflow_impl,
            name="inclusion-workflow",
            description="Reader skill -> review panel agents -> editor agent.",
        )
    run_result = await workflow.run({"job_post_path": path})
    outputs = run_result.get_outputs()
    if not outputs:
        raise RuntimeError("Workflow produced no outputs.")
    state = outputs[-1]
    if not isinstance(state, dict):
        raise RuntimeError("Workflow output was not a state object.")

    baseline_output = str(state["baseline_output"])
    rewritten_output = str(state["rewritten_output"])
    review_panel = list(state["review_panel"])
    feedback_summary = list(state["feedback_summary"])

    baseline_eval = evaluate_text(baseline_output)
    rewritten_eval = evaluate_text(rewritten_output)
    return WorkflowResult(
        job_post_path=path,
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
