"""Agent implementations."""

from .contracts import AgentPlugin
from .baseline_agent import run_baseline_agent
from .inclusion_reviewer import run_inclusion_reviewer
from .registry import discover_agent_plugins
from .rewrite_agent import run_revision_synthesizer

__all__ = [
    "AgentPlugin",
    "discover_agent_plugins",
    "run_baseline_agent",
    "run_inclusion_reviewer",
    "run_revision_synthesizer",
]
