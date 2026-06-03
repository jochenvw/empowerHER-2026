---
applyTo: "**"
---
# Copilot instructions for this repository

- Keep the repo small, readable, and beginner-friendly.
- Place one agent per file in `src/agent_inclusion_lab/agents`.
- Place reusable helpers in `src/agent_inclusion_lab/skills`.
- Keep orchestration in `src/agent_inclusion_lab/workflow.py`.
- Keep eval logic in `src/agent_inclusion_lab/evals`.
- Use typed, explicit Python and small functions.
- Never commit secrets or endpoints in source.
- Add tests for new behaviors.
- Prefer structured findings to vague summaries.
- Keep changes explicit over clever abstractions.
- Keep scripts runnable with `uv run ...` in Windows-friendly paths.
- Add new agent behavior by creating a new `agents/*.py` plugin file, not by expanding a single shared file.
