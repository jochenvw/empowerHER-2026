# agent-inclusion-lab

This repository is a minimal Python scaffold for a 50-minute workshop on building and evaluating agent behavior for inclusive hiring content.

Participants will build and improve a baseline agent workflow that starts from legacy guidance, reviews inclusion risks, and rewrites outputs using modern inclusive principles.

## 5-minute quick start

1. Install Python 3.11+ and `uv`.
2. Run `uv sync`.
3. Run `uv run python scripts/health_check.py`.
4. Run `uv run python scripts/run_evals.py`.

## Setup

1. `uv sync`
2. Copy `.env.example` to `.env`
3. Fill environment variables if running against a real Foundry model

## VS Code quick start

1. Open the repository folder in VS Code.
2. Accept the recommended extensions prompt (or run **Extensions: Show Recommended Extensions**).
3. Install Azure AI Foundry Toolkit / AI Toolkit from the VS Code Marketplace (extension ID may vary).
4. Open an integrated terminal and run `uv sync`.
5. Run `uv run pytest` to confirm your environment works.

## Run

- `uv run python scripts/health_check.py`
- `uv run python scripts/run_baseline.py`
- `uv run python scripts/run_reviewed.py`
- `uv run python scripts/run_evals.py`
- `uv run pytest`

## Contribution paths

- Local development
- GitHub web edits
- GitHub Codespaces
- GitHub issue + Copilot coding agent assignment

Contributions can include:

- New agents
- Improved instructions/prompts
- New eval cases
- Better rubrics
- Better bias checks

## Multi-agent extension model (PR-friendly)

The workflow is plugin-based and stage-oriented (`draft -> review -> rewrite`):

- Add a new agent by creating a new file in `src/agent_inclusion_lab/agents/`.
- Export an `AGENT_PLUGIN` object from that file.
- Keep changes isolated to your new file and tests to reduce merge conflicts.

Optional stage selection via environment variables:

- `INCLUSION_DRAFT_AGENT`
- `INCLUSION_REVIEW_AGENT`
- `INCLUSION_REWRITE_AGENT`

If these are not set, the default agents are auto-discovered and used.

## Facilitator guide

If you are running the workshop, use `DEMO_GIVER.md` for model/deployment guidance, key distribution options, participant credential setup, and the recommended demo timeline.

## Teaching point

The baseline agent is not explicitly instructed to be biased. It inherits biased assumptions from weak instructions and legacy source material.

## Secrets and safety warning

Do not commit API keys, endpoints, or tokens. Use environment variables and secrets management.

Repository/Codespaces secrets are useful for workshop speed, but they are not perfect isolation if participants can run arbitrary code. For stronger isolation, use a server-side proxy, Azure Function, API Management proxy, or a managed identity-backed service.

## VS Code note

Recommended extensions are listed in `.vscode/extensions.json`.

## LLM coding standards (auto-loaded)

For VS Code Copilot and compatible agents, coding standards are committed in default auto-discovery locations:

- `.github/copilot-instructions.md` (always-on, repository-wide)
- `.github/instructions/python.instructions.md` (Python-only rules via `applyTo`)
- `AGENTS.md` (always-on agent guidance)

## Reference implementation branch

Keep a separate facilitator-only branch named `solution/reference-implementation` for richer examples (improved reviewer/rewrite agent, more eval cases, example PRs, expected before/after outputs) instead of placing full solutions on `main`.
