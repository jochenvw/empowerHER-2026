# empowerHER

Minimal workshop project for evaluating and improving biased job-posting text.

## Quick start

1. Install Python 3.11+ and `uv`.
2. Run `uv sync`.
3. Copy `.env.example` to `.env` and set:
   - `FOUNDRY_MODEL_DEPLOYMENT`
   - one endpoint (`FOUNDRY_OPENAI_ENDPOINT` or `FOUNDRY_PROJECT_ENDPOINT` or `FOUNDRY_ENDPOINT`)
   - auth (`FOUNDRY_API_KEY` or Azure Identity env credentials)
4. Run `uv run eh health`.

## Run

- Baseline text + LLM eval: `uv run eh baseline`
- Baseline workflow report: `uv run eh reviewed`
- Full eval table: `uv run eh evals`
- Chainlit UI: `uv run eh ui`

Do not commit secrets.
