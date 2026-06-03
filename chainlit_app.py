from __future__ import annotations

from pathlib import Path

import chainlit as cl

from agent_inclusion_lab.workflow import run_inclusion_workflow

_STARTER_PROMPTS = [
    "List current job openings.",
    "Show me the Regional Operations Manager opening.",
    "Show baseline text and calculate bias score.",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def _load_workshop_sources() -> tuple[str, str]:
    root = _repo_root()
    legacy_path = root / "data" / "legacy" / "hiring_guidelines_legacy.md"
    clean_path = root / "data" / "clean" / "inclusive_hiring_principles.md"
    clean = clean_path.read_text(encoding="utf-8")
    return str(legacy_path), clean


@cl.on_chat_start
async def on_chat_start() -> None:
    legacy_path, clean = _load_workshop_sources()
    cl.user_session.set("legacy_path", legacy_path)
    cl.user_session.set("inclusive_principles", clean)

    prompt_hints = "\n".join(f"- {prompt}" for prompt in _STARTER_PROMPTS)
    await cl.Message(
        content=(
            "Welcome to the inclusion workflow demo.\n\n"
            "Current baseline workflow:\n"
            "- return the legacy job ad verbatim\n"
            "- calculate and show inclusion/bias score\n\n"
            "Later, additional agents can rewrite the text and reduce bias score.\n\n"
            "Starter prompts:\n"
            f"{prompt_hints}"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    user_request = message.content.strip()
    if not user_request:
        await cl.Message(content="Please provide a drafting request.").send()
        return

    legacy_path = str(cl.user_session.get("legacy_path"))
    inclusive_principles = str(cl.user_session.get("inclusive_principles"))

    result = run_inclusion_workflow(
        job_post_path=legacy_path,
        inclusive_principles=inclusive_principles,
    )

    findings = [f"{item['eval_name']}: {item['rationale']}" for item in result.baseline_eval["evals"]]
    findings_text = "\n".join(f"- {item}" for item in findings) if findings else "- None"
    eval_rows = []
    for item in result.baseline_eval["evals"]:
        evidence = ", ".join(item.get("evidence_spans", [])) or "-"
        eval_rows.append(
            f"- **{item.get('eval_name')}**: score={item.get('score')} "
            f"pass={item.get('pass')} | evidence: {evidence}"
        )
    eval_text = "\n".join(eval_rows) if eval_rows else "- None"

    await cl.Message(
        content=(
            f"### Request\n{user_request}\n\n"
            f"### Baseline inclusion score\n"
            f"- **{result.baseline_eval['overall_score']}** "
            f"(overall_pass={result.baseline_eval['overall_pass']})\n\n"
            f"### Reviewer findings\n{findings_text}\n\n"
            f"### LLM eval details\n{eval_text}\n\n"
            "### Baseline job opening (verbatim)\n"
            f"{result.baseline_output}\n\n"
            f"### Feedback summary\n"
            + ("\n".join(f"- {item}" for item in result.feedback_summary) if result.feedback_summary else "- None") +
            "\n\n### Improved job opening\n"
            f"{result.rewritten_output}"
        )
    ).send()
