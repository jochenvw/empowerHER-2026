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

## Extending

Each agent lives in `src/agent_inclusion_lab/agents/<name>/` and exports an
`AGENT_PLUGIN` with a `stage` of `draft`, `review`, or `rewrite`. The workflow
runs draft → review → rewrite, then scores baseline vs. rewritten output.

To make the reviewed flow actually improve the after-score, add a `rewrite`
plugin and select it without editing `workflow.py`:

```bash
INCLUSION_REWRITE_AGENT=<your.rewrite.agent_id> uv run eh reviewed
```

A worked example ships in `src/agent_inclusion_lab/agents/rewrite_agent_llm/`: a real
`agent_framework.Agent` wired into the `rewrite` stage. Try it with:

```bash
INCLUSION_REWRITE_AGENT=rewrite.llm uv run eh reviewed
```

### Reviewers show up automatically

The `review` stage fans out: every agent with `stage="review"` runs and gets its own card
in the Chainlit UI's left column. Add a reviewer by dropping a new folder under
`agents/` that exports an `AGENT_PLUGIN` (stage `review`) — no `workflow.py` edits needed.
Set `INCLUSION_REVIEW_AGENT=<agent_id>` to restrict the panel to a single reviewer.

### Chainlit UI layout

`uv run eh ui` renders each request as a three-column `InclusionResult` element
(`public/elements/InclusionResult.jsx`): **left** = agent reasoning (one card per reviewer),
**center** = the job posting outcome, **right** = the inclusion eval score for that posting.
More contributed agents → more left-column cards and a higher right-column score on re-run.

The defaults on `main` are intentionally no-ops; keep the reference solution on
a separate `solution/reference-implementation` branch.

Do not commit secrets.
