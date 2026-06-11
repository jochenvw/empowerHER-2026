"""Accessibility-reviewer agent plugin.

Review-stage agent that flags job-posting language likely to exclude candidates
with disabilities — for example physical demands, transportation requirements, or
sensory assumptions that are not essential to the role — and suggests
accommodation-aware alternatives.

It is NOT the default reviewer. The fan-out review stage runs it automatically
alongside any other discovered review agents, or it can be run exclusively with::

    INCLUSION_REVIEW_AGENT=reviewer.accessibility uv run eh reviewed
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_inclusion_lab.agents.contracts import AgentPlugin

from .tools import review_with_agent

_SYSTEM_PROMPT = (Path(__file__).resolve().parent / "system_prompt.md").read_text(encoding="utf-8")


def _run_plugin(state: dict[str, Any]) -> dict[str, Any]:
    job_posting = str(state.get("baseline_output", "")).strip()
    findings = review_with_agent(_SYSTEM_PROMPT, job_posting)
    return {
        "review": {
            "reviewer": "reviewer.accessibility",
            **findings,
        }
    }


AGENT_PLUGIN = AgentPlugin(
    agent_id="reviewer.accessibility",
    stage="review",
    description=(
        "LLM-backed accessibility reviewer that flags physical, mobility, sensory, "
        "and transportation barriers in job postings and suggests accommodation-aware wording."
    ),
    runner=_run_plugin,
)
