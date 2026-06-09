---
applyTo: "**"
---
# Copilot instructions for this repository

empowerHER (`agent-inclusion-lab`) is a small, beginner-friendly workshop project for
evaluating and improving biased job-posting text. It is an **easy introduction to
Microsoft Agent Framework** (`agent_framework`, pinned to `1.7.0`): the goal is to keep
config and ceremony minimal so the framework primitives stand out. Do not introduce a
parallel, non-Agent-Framework orchestration or eval stack, and do not add noise/complexity
that obscures the primitives.

## The workshop narrative (read this first)

`main` is a deliberately minimal **skeleton**: an agent reads a job posting, the text
passes through a draft → review → rewrite pipeline unchanged, and the inclusion evals score
it. The review and rewrite stages on `main` are intentional **no-ops**.

The point of the workshop is that newcomers (with LLM-assisted coding) **author a new agent,
plug it into a pipeline stage without touching shared code, and watch the eval score improve.**
Keep these three things healthy and obvious at all times:
1. the passthrough skeleton on `main`,
2. the extension points (auto-discovery + env-var stage selection),
3. the ready-to-use evals.

`src/agent_inclusion_lab/agents/rewrite_agent_llm/` is the **reference example** of that
journey: a real `agent_framework.Agent` wired into the `rewrite` stage, opt-in via
`INCLUSION_REWRITE_AGENT=rewrite.llm`. Use it as the template when adding agents.

## Build, test, and run

Uses Python 3.11–3.13 and `uv`. All commands are Windows-friendly and run via `uv`.

- Install / sync deps: `uv sync`
- Run all tests: `uv run pytest`
- Run a single test file: `uv run pytest tests/test_workflow_smoke.py`
- Run a single test: `uv run pytest tests/test_workflow_smoke.py::test_workflow_smoke_verbatim_baseline_flow`
- End-to-end eval script (CONTRIBUTING validation step): `uv run python scripts/run_evals.py`

The `eh` CLI (entry point `agent_inclusion_lab.cli:main`) is the main interface:
- `uv run eh health` — environment + Foundry config health check
- `uv run eh baseline` — baseline draft text + LLM-judge inclusion score
- `uv run eh reviewed` — full draft→review→rewrite workflow, before/after scores
- `uv run eh evals` — CSV-style eval table for baseline vs. rewritten
- `uv run eh ui` — Chainlit UI (`chainlit_app.py`)

There is no configured linter; keep code idiomatic and typed.

## Configuration

Copy `.env.example` to `.env`. Required: `FOUNDRY_MODEL_DEPLOYMENT` plus one endpoint
(`FOUNDRY_OPENAI_ENDPOINT`, `FOUNDRY_PROJECT_ENDPOINT`, or `FOUNDRY_ENDPOINT`), plus auth
(`FOUNDRY_API_KEY` or Azure Identity env credentials). `config.py` validates these and
`model_client.py` calls the Foundry model through the OpenAI client. Never commit secrets
or endpoints in source.

## Architecture (the big picture)

The system is a three-stage pipeline over a job-posting document:

1. **draft** → 2. **review** → 3. **rewrite**, then **score baseline vs. rewritten**.

`workflow.py` (`run_inclusion_workflow` / `run_inclusion_workflow_async`) is the single
orchestration point. It threads a mutable `state: dict` through each stage, resolving the
agent for each stage via `agents/registry.py`, then evaluates both baseline and rewritten
text with `evals/inclusion_eval.py`.

- **Agent plugins** live one-per-folder under `src/agent_inclusion_lab/agents/<name>/` and
  each exports a module-level `AGENT_PLUGIN` (an `AgentPlugin` from `agents/contracts.py`)
  with `agent_id`, `stage` (`draft`/`review`/`rewrite`), `description`, and a `runner`
  callable `(state) -> dict` that merges its outputs back into `state`. The `runner` is
  **synchronous**; if it drives an async `af.Agent`, bridge to a loop (see
  `rewrite_agent_llm/tools.py`, which creates the coroutine *inside* the loop to avoid an
  Agent Framework telemetry context-var error).
- **The skeleton "agents" on `main` are plain Python functions, not LLM agents.** `baseline`
  reads the file, `reviewer.default` returns no suggestions, `rewrite.default` returns the
  draft unchanged. The first real `agent_framework.Agent` is `rewrite_agent_llm`
  (`agent_id="rewrite.llm"`); it adapts `model_client.generate_text` into an
  `af.BaseChatClient` (`FoundryChatClient`) and runs an `af.Agent`. Note the model call
  itself uses the **raw OpenAI SDK** in `model_client.py`, not an AF stock client.
- **Discovery is automatic**: `registry.discover_agent_plugins()` imports every module and
  package under `agents/` (skipping `__init__.py`, `contracts.py`, `registry.py`) and
  registers any `AGENT_PLUGIN`. To add a variant, drop in a new folder/module that exports
  `AGENT_PLUGIN` — do **not** edit `workflow.py` or `registry.py`.
- **Stage selection at runtime** via env vars: `INCLUSION_DRAFT_AGENT`,
  `INCLUSION_REVIEW_AGENT`, `INCLUSION_REWRITE_AGENT` pick an `agent_id`; otherwise the
  first-discovered plugin for that stage (by sorted module/folder name) is the default.
  `resolve_agent` enforces that a requested agent's `stage` matches. When adding a variant,
  name its folder so it sorts **after** the `main` default to keep the no-op default
  (e.g. `rewrite_agent_llm` sorts after `rewrite_agent`).
- **Evaluation**: `inclusion_eval.py` defines bespoke checks as `EvalSpec`s and runs them
  through a native Agent Framework `InclusionJudgeEvaluator` (used with `af.evaluate_agent`,
  `af.EvalItem`, `af.EvalResults`). The judge is an LLM scoring 1–5 against penalize/reward
  patterns; results degrade gracefully on unparseable JSON rather than aborting.
- **Skills** live under `src/agent_inclusion_lab/skills/`. `job_post_reader.py` is an
  **intentional** demonstration of the Agent Framework `FileSkill`/`FileSkillsSource`
  pattern (it loads the `job-post-reader` file skill and runs its script via subprocess).
  Do not "simplify" it to a plain file read — that machinery is the teaching point. For an
  ordinary file read elsewhere, use `document_loader.load_text` (which the CLI/tests/scripts
  use).

## Key conventions

- The `main` branch defaults are intentional **no-ops** so the before/after scores match
  until a participant adds a real agent. Keep them no-ops; the reference solution belongs on
  a separate `solution/reference-implementation` branch, not in `main` defaults.
- A real workshop solution is a new agent plugin selected via the `INCLUSION_*_AGENT` env
  vars, not edits to shared workflow logic. `rewrite_agent_llm` is the canonical example.
- The LLM judge is nondeterministic, so `workflow.py` reuses the baseline eval result when
  rewritten text is unchanged, to avoid a misleading score delta. Preserve this behavior.
- Do not "fix bias" with a single hardcoded string replacement; prefer structured findings
  (scores, rationale, evidence spans, advice) over vague prose.

## Per-agent folder contract

Each `agents/<name>/` folder must contain:
- `system_prompt.md` (required)
- `skills.md` (when the agent uses skills)
- `tools.py` (when the agent has helper tools)
- `__init__.py` (agent/plugin runtime code exporting `AGENT_PLUGIN`)

Reusable helpers go in `skills/`; orchestration only in `workflow.py`; eval logic only in
`evals/`. See `.github/instructions/python.instructions.md` for Python specifics (type hints,
`pathlib`, small explicit functions, deterministic tests, no broad/silent exception handling).

## Testing conventions

Tests live in `tests/` and run with `pythonpath = ["src"]` (configured in `pyproject.toml`).
Smoke and workflow tests monkeypatch `workflow.resolve_agent` and `workflow.evaluate_text_async`
so they run without live Foundry calls (see `tests/test_workflow_smoke.py`). Add tests for any
new agent or eval behavior, and keep them deterministic.
