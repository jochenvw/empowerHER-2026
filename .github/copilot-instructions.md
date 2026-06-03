---
applyTo: "**"
---
# Copilot instructions for this repository

- Keep the repo small, readable, and beginner-friendly.
- Use Microsoft Agent Framework native concepts for orchestration and evals.
- Build runtime around `agent_framework.Agent`, `ClassSkill`, and workflow primitives.
- Use Agent Framework eval APIs (`evaluate_agent`, `evaluate_workflow`, `LocalEvaluator`/custom `Evaluator`) for bespoke evals.
- Place each agent in its own folder under `src/agent_inclusion_lab/agents/<agent_name>/`.
- In each agent folder:
  - `system_prompt.md` is required.
  - `skills.md` is required when the agent uses skills.
  - `tools.py` is required when the agent has helper tools.
  - `__init__.py` contains the agent/plugin runtime code.
- Place reusable helpers in `src/agent_inclusion_lab/skills`.
- Keep orchestration in `src/agent_inclusion_lab/workflow.py`.
- Keep eval logic in `src/agent_inclusion_lab/evals`.
- Use typed, explicit Python and small functions.
- Never commit secrets or endpoints in source.
- Add tests for new behaviors.
- Prefer structured findings to vague summaries.
- Keep changes explicit over clever abstractions.
- Keep scripts runnable with `uv run ...` in Windows-friendly paths.
- Do not introduce parallel, non-Agent-Framework orchestration or eval stacks.
