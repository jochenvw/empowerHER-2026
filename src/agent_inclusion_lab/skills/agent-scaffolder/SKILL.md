---
name: agent-scaffolder
description: Scaffold a new workshop agent in its own folder without touching shared workflow code.
---

# Agent Scaffolder

Use this skill to turn a new-agent issue into a plugin folder.

- Copy `src/agent_inclusion_lab/agents/rewrite_agent_llm/` as the reference.
- Create `src/agent_inclusion_lab/agents/<name>/` with `__init__.py` and `system_prompt.md`.
- Export `AGENT_PLUGIN` and rely on auto-discovery; do not edit `workflow.py` or `registry.py`.
- Add a deterministic test under `tests/` for the new agent.
