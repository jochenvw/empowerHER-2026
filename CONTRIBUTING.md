# Contributing

Thanks for contributing to the workshop scaffold.

## Principles

- Keep the code beginner-friendly and explicit.
- Keep files short and functions small.
- Add tests for any agent or evaluation behavior changes.
- Do not add secrets to source code.

## Typical changes

- Add or improve an agent under `src/agent_inclusion_lab/agents`
- Add helper logic under `src/agent_inclusion_lab/skills`
- Add eval logic under `src/agent_inclusion_lab/evals`
- Add or update test cases under `tests/`

## Validation

Run:

1. `uv sync`
2. `uv run pytest`
3. `uv run python scripts/run_evals.py`
