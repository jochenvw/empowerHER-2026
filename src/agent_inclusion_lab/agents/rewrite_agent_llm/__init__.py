"""Example LLM-backed rewrite agent.

This is the kind of agent a workshop participant builds: it plugs into the
``rewrite`` stage and actually improves the inclusion eval score, unlike the
no-op ``rewrite.default`` on ``main``.

It is NOT the default. The first-discovered rewrite plugin (``rewrite.default``)
stays the default; opt in to this one with::

    INCLUSION_REWRITE_AGENT=rewrite.llm uv run eh reviewed
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin

from .tools import rewrite_with_agent

_SYSTEM_PROMPT = (Path(__file__).resolve().parent / "system_prompt.md").read_text(encoding="utf-8")


def _build_user_request(state: dict[str, Any]) -> str:
    baseline = str(state.get("baseline_output", "")).strip()
    principles = str(state.get("inclusive_principles", "")).strip()
    review = state.get("review")
    suggestions = review.get("suggestions", []) if isinstance(review, dict) else []
    suggestion_text = "\n".join(f"- {item}" for item in suggestions) or "- (none provided)"
    return (
        "Inclusive hiring principles:\n"
        f"{principles}\n\n"
        "Reviewer suggestions:\n"
        f"{suggestion_text}\n\n"
        "Job posting to rewrite:\n"
        f"{baseline}"
    )


def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
    rewritten = rewrite_with_agent(_SYSTEM_PROMPT, _build_user_request(state))
    return {"rewritten_output": rewritten}


AGENT_PLUGIN = AgentPlugin(
    agent_id="rewrite.llm",
    stage="rewrite",
    description="Example LLM-backed rewriter built on agent_framework.Agent; opt in via INCLUSION_REWRITE_AGENT=rewrite.llm.",
    runner=_run_plugin,
)
