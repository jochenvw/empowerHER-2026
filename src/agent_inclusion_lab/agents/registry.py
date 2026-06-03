from __future__ import annotations

import importlib
from functools import lru_cache
from pathlib import Path

from agent_inclusion_lab.agents.contracts import AgentPlugin, AgentStage

_SKIP_FILES = {"__init__.py", "contracts.py", "registry.py"}
_STAGES: tuple[AgentStage, ...] = ("draft", "review", "rewrite")


@lru_cache(maxsize=1)
def discover_agent_plugins() -> dict[str, AgentPlugin]:
    plugins: dict[str, AgentPlugin] = {}
    package_dir = Path(__file__).resolve().parent

    for file_path in sorted(package_dir.glob("*.py")):
        if file_path.name in _SKIP_FILES:
            continue
        module_name = f"agent_inclusion_lab.agents.{file_path.stem}"
        module = importlib.import_module(module_name)
        plugin = getattr(module, "AGENT_PLUGIN", None)
        if plugin is None:
            continue
        if not isinstance(plugin, AgentPlugin):
            raise TypeError(f"{module_name}.AGENT_PLUGIN must be an AgentPlugin instance.")
        if plugin.agent_id in plugins:
            raise ValueError(f"Duplicate agent_id detected: {plugin.agent_id}")
        plugins[plugin.agent_id] = plugin

    return plugins


def get_default_agent_ids_by_stage() -> dict[AgentStage, str]:
    defaults: dict[AgentStage, str] = {}
    for plugin in discover_agent_plugins().values():
        if plugin.stage not in defaults:
            defaults[plugin.stage] = plugin.agent_id

    missing = [stage for stage in _STAGES if stage not in defaults]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing default agents for stages: {joined}")
    return defaults


def resolve_agent(stage: AgentStage, requested_agent_id: str | None = None) -> AgentPlugin:
    plugins = discover_agent_plugins()
    if requested_agent_id:
        plugin = plugins.get(requested_agent_id)
        if plugin is None:
            raise KeyError(f"Unknown agent id: {requested_agent_id}")
        if plugin.stage != stage:
            raise ValueError(
                f"Agent {requested_agent_id} is stage={plugin.stage}, expected stage={stage}."
            )
        return plugin

    default_id = get_default_agent_ids_by_stage()[stage]
    return plugins[default_id]

