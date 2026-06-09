from __future__ import annotations

from pathlib import Path

import chainlit as cl

from agent_inclusion_lab.config import get_settings
from agent_inclusion_lab.workflow import run_inclusion_workflow_async

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


def _runtime_info_lines() -> list[str]:
    settings = get_settings()
    endpoint = (
        settings.foundry_openai_endpoint
        or settings.foundry_project_endpoint
        or settings.foundry_endpoint
        or "not configured"
    )
    model = settings.foundry_model_deployment or "not configured"
    return [
        f"- **Endpoint:** `{endpoint}`",
        f"- **Model deployment:** `{model}`",
    ]


@cl.on_chat_start
async def on_chat_start() -> None:
    legacy_path, clean = _load_workshop_sources()
    cl.user_session.set("legacy_path", legacy_path)
    cl.user_session.set("inclusive_principles", clean)

    prompt_hints = "\n".join(f"- {prompt}" for prompt in _STARTER_PROMPTS)
    runtime_info = "\n".join(_runtime_info_lines())
    await cl.Message(
        content=(
            "## empowerHER inclusion workflow\n\n"
            f"{runtime_info}\n\n"
            "Ask for the job posting to see **reasoning · posting · eval score** side by side.\n\n"
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

    result = await run_inclusion_workflow_async(
        job_post_path=legacy_path,
        inclusive_principles=inclusive_principles,
    )

    inclusion_panel = cl.CustomElement(
        name="InclusionResult",
        props={
            "request": user_request,
            "jobPosting": result.rewritten_output,
            "reviewers": result.review_panel,
            "evalResult": result.rewritten_eval,
        },
    )

    await cl.Message(content="", elements=[inclusion_panel]).send()

