# Demo giver instructions

Use this as a practical runbook for a live workshop.

## 1) Pre-demo setup (host)

1. Clone the repo and run `uv sync`.
2. Run `uv run eh health`.
3. Run `uv run eh evals`.
4. Optional full check: `uv run pytest`.

If all pass, your environment is ready.

## 2) Recommended model to deploy

For a workshop, deploy **one low-latency, lower-cost chat model** in Azure AI Foundry (for example, a mini/small general-purpose chat model available in your tenant/region).

Selection criteria:

- Fast responses (best for live demos)
- Lower cost per participant
- Good instruction following for short prompts

Use a single deployment and share only runtime credentials, not owner/admin credentials.

## 3) API key distribution options (recommended order)

1. **Best for speed:** provide participants a temporary workshop key + endpoint.
2. **Better isolation:** use a server-side proxy (Azure Function / API Management) so participants never get raw model keys.
3. **Codespaces path:** preconfigure repository or Codespaces secrets for the session.

Rotate or revoke workshop credentials immediately after the session.

## 4) Where participants should paste credentials

Participants should create `.env` from `.env.example` and paste values there:

```env
FOUNDRY_ENDPOINT=<paste endpoint>
FOUNDRY_API_KEY=<paste api key>
FOUNDRY_MODEL_DEPLOYMENT=<paste deployment name>
FOUNDRY_PROJECT_ENDPOINT=<paste project endpoint>
FOUNDRY_OPENAI_ENDPOINT=<optional; use if provided directly>
```

## 5) Participant sanity-check command

Ask participants to run this first:

`uv run eh health`

Then:

- `uv run eh baseline`
- `uv run eh reviewed`
- `uv run eh evals`

## 6) Demo flow suggestion (50 min)

1. 0-10 min: setup + health check
2. 10-20 min: baseline run + bias findings discussion
3. 20-35 min: participant edits (agent prompts/skills/evals)
4. 35-45 min: rerun reviewed flow + compare scores
5. 45-50 min: share learnings + next steps

## 7) Troubleshooting quick list

- If import errors appear: run `uv sync` again.
- If credentials errors appear: verify `.env` endpoint/deployment/API key values.
- If score changes are unclear: run `uv run eh evals` to compare LLM judge outputs.
