from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal

AgentStage = Literal["draft", "review", "rewrite"]
AgentState = dict[str, Any]
AgentRunner = Callable[[AgentState], dict[str, Any]]


@dataclass(frozen=True)
class AgentPlugin:
    agent_id: str
    stage: AgentStage
    description: str
    runner: AgentRunner
