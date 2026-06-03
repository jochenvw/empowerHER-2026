from __future__ import annotations

from .config import Settings, get_settings

_DRY_BASELINE_OUTPUT = """# Senior Engineering Manager

## Job description
We are seeking a strong, decisive leader who can command the room and drive aggressive execution.
The ideal candidate is visible in the office, always available for leadership escalations, and a natural leader who fits our culture.

## Interview rubric
- Executive presence and dominant leadership style
- Culture fit with existing management team
- Ability to stay available outside normal hours
- Track record from high-potential, elite programs
"""

_DRY_REWRITE_OUTPUT = """# Senior Engineering Manager

## Job description
We are hiring an Engineering Manager to lead teams through clear prioritization, coaching, and delivery outcomes.
Candidates can succeed in hybrid, remote, or office-based collaboration models. We value inclusive leadership, reliable decision-making, and measurable impact.

## Interview rubric
- Evidence of coaching, feedback quality, and team growth outcomes
- Decision-making using data, tradeoffs, and stakeholder communication
- Collaboration across distributed teams and diverse working styles
- Structured examples of delivery impact and role-relevant competencies
"""


def generate_text(prompt: str) -> str:
    settings = get_settings()
    if settings.dry_run:
        return _dry_run_text(prompt)
    return _call_foundry_model(prompt, settings)


def _dry_run_text(prompt: str) -> str:
    prompt_lower = prompt.lower()
    if "rewrite" in prompt_lower or "inclusive principles" in prompt_lower:
        return _DRY_REWRITE_OUTPUT
    return _DRY_BASELINE_OUTPUT


def _call_foundry_model(prompt: str, settings: Settings) -> str:
    # TODO: Replace this with Microsoft Agent Framework + Foundry model invocation.
    # This placeholder keeps the repository workshop-ready while DRY_RUN mode
    # remains fully functional without credentials.
    raise NotImplementedError(
        "Foundry model adapter is not implemented in this scaffold. "
        "Use DRY_RUN=true for deterministic workshop execution. "
        f"Configured endpoint: {settings.foundry_endpoint!r}, "
        f"deployment: {settings.foundry_model_deployment!r}."
    )

