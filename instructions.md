Scaffold a minimal Python repository for a 50-minute interactive hackathon.

Project name:
agent-inclusion-lab

Goal:
Create boilerplate code only. Keep the solution intentionally small, readable, and easy for beginners to navigate. Do not build a large framework. Do not over-engineer. The repository should help participants quickly understand how agents, skills/tools, workflows, GitHub issues, PRs, and evals fit together.

Technology assumptions:

* Python
* uv for dependency management
* Microsoft Agent Framework for Python
* Azure AI Foundry / Foundry model endpoint
* GitHub repository
* VS Code-friendly setup

Important:
Do not commit secrets.
Do not put API keys, Foundry keys, tokens, or endpoints directly in source code.
Use environment variables and .env.example.
Make it possible for the workshop owner to provide the endpoint/model/key through:

* local .env file for demos
* GitHub Codespaces secrets
* GitHub Actions secrets
* or a future proxy service

Add a clear warning in README:
Repository/Codespaces secrets are good for workshop speed, but they do not provide perfect secret isolation if participants can run arbitrary code. For stronger isolation, use a server-side proxy, Azure Function, API Management proxy, or managed identity-backed service.

Required repository structure:

agent-inclusion-lab/
README.md
CONTRIBUTING.md
AGENTS.md
pyproject.toml
uv.lock if generated
.env.example
.gitignore

.vscode/
extensions.json
settings.json

.github/
copilot-instructions.md
ISSUE_TEMPLATE/
new-agent.yml
improve-agent.yml
eval-case.yml
workflows/
validate.yml

data/
legacy/
hiring_guidelines_legacy.md
clean/
inclusive_hiring_principles.md

src/
agent_inclusion_lab/
**init**.py
config.py
model_client.py
workflow.py

```
  agents/
    __init__.py
    baseline_agent.py
    inclusion_reviewer.py
    rewrite_agent.py

  skills/
    __init__.py
    document_loader.py
    bias_checks.py

  evals/
    __init__.py
    inclusion_eval.py
```

tests/
test_bias_checks.py
test_eval_baseline.py
test_workflow_smoke.py

scripts/
run_baseline.py
run_reviewed.py
run_evals.py

Core design:

* workflow.py contains the orchestration entry point.
* agents/ contains one file per agent.
* skills/ contains helper functions/tools.
* evals/ contains evaluation logic.
* data/legacy contains old biased source material.
* tests/ contains quick deterministic tests.
* scripts/ contains simple runnable scripts.

Keep all names explicit and beginner-friendly.

Environment variables:
Create .env.example with:

FOUNDRY_ENDPOINT=
FOUNDRY_API_KEY=
FOUNDRY_MODEL_DEPLOYMENT=
FOUNDRY_PROJECT_ENDPOINT=

The code should load config from environment variables. It should fail with a clear error message if required variables are missing.

VS Code:
Add .vscode/extensions.json recommending:

* Python extension
* GitHub Copilot extension
* GitHub Pull Requests extension
* Azure-related extension
* Azure AI Foundry / Foundry Toolkit or AI Toolkit extension if available

Do not invent a specific extension ID if you are not sure. Add a README note that participants should install the Azure AI Foundry Toolkit / AI Toolkit extension from the VS Code marketplace.

README content:
Include:

1. What this repo is
2. What participants will build
3. Setup with uv:

   * uv sync
   * cp .env.example .env
   * fill env vars if running locally
4. Run commands:

   * uv run python scripts/run_baseline.py
   * uv run python scripts/run_reviewed.py
   * uv run python scripts/run_evals.py
   * uv run pytest
5. Contribution paths:

   * local dev
   * GitHub web edit
   * Codespaces
   * create issue and assign to Copilot agent
6. Explain that contributions can be:

   * new agent
   * improved instructions
   * new eval case
   * better rubric
   * better bias check
7. Explain the teaching point:
   The baseline agent is not asked to be biased. It inherits biased assumptions from weak instructions and legacy source material.

Legacy biased source material:
Create data/legacy/hiring_guidelines_legacy.md with fictional but realistic outdated hiring guidance. Keep it subtle and workplace-realistic, not offensive or extreme.

Include examples like:

* defaulting to “he” for senior leaders
* preference for “aggressive” and “dominant” leadership language
* vague “culture fit”
* assumptions that ideal leaders are always available outside working hours
* implicit preference for office visibility over remote participation
* describing collaborative or flexible work patterns as less leadership-oriented
* unnecessary elite-school or degree preference

Example tone:
“An ideal senior engineering manager is a strong, decisive leader. He should be visible in the office, command the room, and show executive presence. Candidates who require flexible schedules may struggle with the demands of senior leadership. The best leaders are aggressive problem-solvers who fit naturally into the existing culture.”

Clean source material:
Create data/clean/inclusive_hiring_principles.md with concise modern guidance:

* use gender-neutral language
* define observable competencies
* avoid vague culture-fit criteria
* distinguish real job requirements from preferences
* avoid assumptions about caregivers, remote workers, age, gender, or background
* prefer evidence-based interview rubrics

Baseline behavior:
baseline_agent.py should produce a job description and interview rubric from the legacy material. It should not be explicitly prompted to be biased. It should simply be weakly instructed, for example:
“Use the available hiring guidance to draft a job description and interview rubric for a Senior Engineering Manager.”

The expected baseline output should likely contain subtle bias because the source material is biased.

Reviewer behavior:
inclusion_reviewer.py should inspect the baseline output and identify risks:

* gendered language
* vague criteria
* unnecessary availability assumptions
* exclusionary language
* culture-fit ambiguity
* overemphasis on aggressive leadership
* unsupported assumptions

Rewrite behavior:
rewrite_agent.py should rewrite the baseline output using the reviewer findings and the clean inclusive principles.

Evaluation:
Implement a very small deterministic eval first. Do not require an LLM judge for the first version.

Create src/agent_inclusion_lab/skills/bias_checks.py with simple checks:

* count gendered pronouns: he, him, his, manpower
* detect phrases: culture fit, aggressive, dominant, command the room, always available, flexible schedules may struggle, visible in the office, young and energetic, native speaker
* detect vague terms: executive presence, rockstar, high potential, natural leader
* produce a score from 0 to 100 where higher is better
* return findings as structured data

Create src/agent_inclusion_lab/evals/inclusion_eval.py:

* function evaluate_text(text: str) -> dict
* returns:

  * score
  * findings
  * flagged_terms
  * recommendation

Tests:
Create tests that assert:

1. The legacy text has a lower inclusion score than the clean text.
2. A deliberately biased sample text fails the inclusion eval.
3. A neutral rewritten sample text passes.
4. run_baseline.py and run_reviewed.py can execute in dry-run mode without Foundry credentials.

Dry-run mode:
Add a DRY_RUN=true option. In dry-run mode, do not call Foundry. Return fixed sample outputs. This allows GitHub Actions and participants without credentials to run the project.

Scripts:
scripts/run_baseline.py:

* loads legacy guidance
* calls baseline agent
* prints output
* prints inclusion score

scripts/run_reviewed.py:

* runs baseline
* runs reviewer
* runs rewrite
* prints before/after scores

scripts/run_evals.py:

* runs deterministic evals against sample cases
* prints compact report

GitHub Actions:
Create .github/workflows/validate.yml:

* checkout
* setup Python
* install uv
* uv sync
* uv run pytest
* uv run python scripts/run_evals.py with DRY_RUN=true

Do not require real Foundry credentials in CI.

GitHub issue templates:
new-agent.yml should ask:

* agent name
* responsibility
* input context
* expected output
* tools/skills needed
* eval cases
* failure modes

improve-agent.yml should ask:

* which agent
* problem observed
* proposed improvement
* how to test it

eval-case.yml should ask:

* input
* bad behavior to detect
* expected safer behavior
* relevant bias/fairness pattern

Copilot instructions:
Create .github/copilot-instructions.md and AGENTS.md with rules for coding agents:

* Keep the repo simple.
* Put each agent in its own file under src/agent_inclusion_lab/agents.
* Put reusable tools/helpers under src/agent_inclusion_lab/skills.
* Put orchestration only in src/agent_inclusion_lab/workflow.py.
* Put eval logic only in src/agent_inclusion_lab/evals.
* Do not put secrets in code.
* Do not add large dependencies unless necessary.
* Prefer idiomatic, typed Python.
* Use small functions.
* Add tests for every new agent or eval behavior.
* Maintain DRY_RUN support.
* Do not “solve” bias by hardcoding only one string replacement.
* Prefer structured findings over vague text.
* Keep outputs understandable for beginners.

Python style:

* Use type hints.
* Use dataclasses or Pydantic only if useful; avoid unnecessary complexity.
* Use pathlib.
* Use clear function names.
* Keep files short.
* Use logging only if helpful.
* Avoid clever abstractions.
* Favor explicit code over magic.

Foundry/model client:
Create model_client.py with a thin abstraction:

* generate_text(prompt: str) -> str
* if DRY_RUN=true, return deterministic sample text
* otherwise call the configured Foundry model deployment

If exact Microsoft Agent Framework APIs are known, use them.
If not, create a clearly marked placeholder adapter with TODO comments and keep the rest of the repo functional in DRY_RUN mode.

Do not build a complete production system.
The goal is a workshop-ready scaffold that can be extended by participants.

Reference implementation branch:
Do not put the full “ideal solution” on main.
Add a README section suggesting that the facilitator can keep a separate branch named:
solution/reference-implementation

That branch can contain:

* improved reviewer
* better rewrite agent
* extra eval cases
* example PRs
* expected before/after output

Acceptance criteria:

* uv sync works
* uv run pytest works
* uv run python scripts/run_evals.py works without credentials using DRY_RUN=true
* repo structure matches the requested layout
* baseline sample scores worse than reviewed sample
* no secrets are committed
* beginner can understand where agents, skills, workflows, and evals live
Scaffold a minimal Python repository for a 50-minute interactive hackathon.

Project name:
agent-inclusion-lab

Goal:
Create boilerplate code only. Keep the solution intentionally small, readable, and easy for beginners to navigate. Do not build a large framework. Do not over-engineer. The repository should help participants quickly understand how agents, skills/tools, workflows, GitHub issues, PRs, and evals fit together.

Technology assumptions:

* Python
* uv for dependency management
* Microsoft Agent Framework for Python
* Azure AI Foundry / Foundry model endpoint
* GitHub repository
* VS Code-friendly setup

Important:
Do not commit secrets.
Do not put API keys, Foundry keys, tokens, or endpoints directly in source code.
Use environment variables and .env.example.
Make it possible for the workshop owner to provide the endpoint/model/key through:

* local .env file for demos
* GitHub Codespaces secrets
* GitHub Actions secrets
* or a future proxy service

Add a clear warning in README:
Repository/Codespaces secrets are good for workshop speed, but they do not provide perfect secret isolation if participants can run arbitrary code. For stronger isolation, use a server-side proxy, Azure Function, API Management proxy, or managed identity-backed service.

Required repository structure:

agent-inclusion-lab/
README.md
CONTRIBUTING.md
AGENTS.md
pyproject.toml
uv.lock if generated
.env.example
.gitignore

.vscode/
extensions.json
settings.json

.github/
copilot-instructions.md
ISSUE_TEMPLATE/
new-agent.yml
improve-agent.yml
eval-case.yml
workflows/
validate.yml

data/
legacy/
hiring_guidelines_legacy.md
clean/
inclusive_hiring_principles.md

src/
agent_inclusion_lab/
**init**.py
config.py
model_client.py
workflow.py

```
  agents/
    __init__.py
    baseline_agent.py
    inclusion_reviewer.py
    rewrite_agent.py

  skills/
    __init__.py
    document_loader.py
    bias_checks.py

  evals/
    __init__.py
    inclusion_eval.py
```

tests/
test_bias_checks.py
test_eval_baseline.py
test_workflow_smoke.py

scripts/
run_baseline.py
run_reviewed.py
run_evals.py

Core design:

* workflow.py contains the orchestration entry point.
* agents/ contains one file per agent.
* skills/ contains helper functions/tools.
* evals/ contains evaluation logic.
* data/legacy contains old biased source material.
* tests/ contains quick deterministic tests.
* scripts/ contains simple runnable scripts.

Keep all names explicit and beginner-friendly.

Environment variables:
Create .env.example with:

FOUNDRY_ENDPOINT=
FOUNDRY_API_KEY=
FOUNDRY_MODEL_DEPLOYMENT=
FOUNDRY_PROJECT_ENDPOINT=

The code should load config from environment variables. It should fail with a clear error message if required variables are missing.

VS Code:
Add .vscode/extensions.json recommending:

* Python extension
* GitHub Copilot extension
* GitHub Pull Requests extension
* Azure-related extension
* Azure AI Foundry / Foundry Toolkit or AI Toolkit extension if available

Do not invent a specific extension ID if you are not sure. Add a README note that participants should install the Azure AI Foundry Toolkit / AI Toolkit extension from the VS Code marketplace.

README content:
Include:

1. What this repo is
2. What participants will build
3. Setup with uv:

   * uv sync
   * cp .env.example .env
   * fill env vars if running locally
4. Run commands:

   * uv run python scripts/run_baseline.py
   * uv run python scripts/run_reviewed.py
   * uv run python scripts/run_evals.py
   * uv run pytest
5. Contribution paths:

   * local dev
   * GitHub web edit
   * Codespaces
   * create issue and assign to Copilot agent
6. Explain that contributions can be:

   * new agent
   * improved instructions
   * new eval case
   * better rubric
   * better bias check
7. Explain the teaching point:
   The baseline agent is not asked to be biased. It inherits biased assumptions from weak instructions and legacy source material.

Legacy biased source material:
Create data/legacy/hiring_guidelines_legacy.md with fictional but realistic outdated hiring guidance. Keep it subtle and workplace-realistic, not offensive or extreme.

Include examples like:

* defaulting to “he” for senior leaders
* preference for “aggressive” and “dominant” leadership language
* vague “culture fit”
* assumptions that ideal leaders are always available outside working hours
* implicit preference for office visibility over remote participation
* describing collaborative or flexible work patterns as less leadership-oriented
* unnecessary elite-school or degree preference

Example tone:
“An ideal senior engineering manager is a strong, decisive leader. He should be visible in the office, command the room, and show executive presence. Candidates who require flexible schedules may struggle with the demands of senior leadership. The best leaders are aggressive problem-solvers who fit naturally into the existing culture.”

Clean source material:
Create data/clean/inclusive_hiring_principles.md with concise modern guidance:

* use gender-neutral language
* define observable competencies
* avoid vague culture-fit criteria
* distinguish real job requirements from preferences
* avoid assumptions about caregivers, remote workers, age, gender, or background
* prefer evidence-based interview rubrics

Baseline behavior:
baseline_agent.py should produce a job description and interview rubric from the legacy material. It should not be explicitly prompted to be biased. It should simply be weakly instructed, for example:
“Use the available hiring guidance to draft a job description and interview rubric for a Senior Engineering Manager.”

The expected baseline output should likely contain subtle bias because the source material is biased.

Reviewer behavior:
inclusion_reviewer.py should inspect the baseline output and identify risks:

* gendered language
* vague criteria
* unnecessary availability assumptions
* exclusionary language
* culture-fit ambiguity
* overemphasis on aggressive leadership
* unsupported assumptions

Rewrite behavior:
rewrite_agent.py should rewrite the baseline output using the reviewer findings and the clean inclusive principles.

Evaluation:
Implement a very small deterministic eval first. Do not require an LLM judge for the first version.

Create src/agent_inclusion_lab/skills/bias_checks.py with simple checks:

* count gendered pronouns: he, him, his, manpower
* detect phrases: culture fit, aggressive, dominant, command the room, always available, flexible schedules may struggle, visible in the office, young and energetic, native speaker
* detect vague terms: executive presence, rockstar, high potential, natural leader
* produce a score from 0 to 100 where higher is better
* return findings as structured data

Create src/agent_inclusion_lab/evals/inclusion_eval.py:

* function evaluate_text(text: str) -> dict
* returns:

  * score
  * findings
  * flagged_terms
  * recommendation

Tests:
Create tests that assert:

1. The legacy text has a lower inclusion score than the clean text.
2. A deliberately biased sample text fails the inclusion eval.
3. A neutral rewritten sample text passes.
4. run_baseline.py and run_reviewed.py can execute in dry-run mode without Foundry credentials.

Dry-run mode:
Add a DRY_RUN=true option. In dry-run mode, do not call Foundry. Return fixed sample outputs. This allows GitHub Actions and participants without credentials to run the project.

Scripts:
scripts/run_baseline.py:

* loads legacy guidance
* calls baseline agent
* prints output
* prints inclusion score

scripts/run_reviewed.py:

* runs baseline
* runs reviewer
* runs rewrite
* prints before/after scores

scripts/run_evals.py:

* runs deterministic evals against sample cases
* prints compact report

GitHub Actions:
Create .github/workflows/validate.yml:

* checkout
* setup Python
* install uv
* uv sync
* uv run pytest
* uv run python scripts/run_evals.py with DRY_RUN=true

Do not require real Foundry credentials in CI.

GitHub issue templates:
new-agent.yml should ask:

* agent name
* responsibility
* input context
* expected output
* tools/skills needed
* eval cases
* failure modes

improve-agent.yml should ask:

* which agent
* problem observed
* proposed improvement
* how to test it

eval-case.yml should ask:

* input
* bad behavior to detect
* expected safer behavior
* relevant bias/fairness pattern

Copilot instructions:
Create .github/copilot-instructions.md and AGENTS.md with rules for coding agents:

* Keep the repo simple.
* Put each agent in its own file under src/agent_inclusion_lab/agents.
* Put reusable tools/helpers under src/agent_inclusion_lab/skills.
* Put orchestration only in src/agent_inclusion_lab/workflow.py.
* Put eval logic only in src/agent_inclusion_lab/evals.
* Do not put secrets in code.
* Do not add large dependencies unless necessary.
* Prefer idiomatic, typed Python.
* Use small functions.
* Add tests for every new agent or eval behavior.
* Maintain DRY_RUN support.
* Do not “solve” bias by hardcoding only one string replacement.
* Prefer structured findings over vague text.
* Keep outputs understandable for beginners.

Python style:

* Use type hints.
* Use dataclasses or Pydantic only if useful; avoid unnecessary complexity.
* Use pathlib.
* Use clear function names.
* Keep files short.
* Use logging only if helpful.
* Avoid clever abstractions.
* Favor explicit code over magic.

Foundry/model client:
Create model_client.py with a thin abstraction:

* generate_text(prompt: str) -> str
* if DRY_RUN=true, return deterministic sample text
* otherwise call the configured Foundry model deployment

If exact Microsoft Agent Framework APIs are known, use them.
If not, create a clearly marked placeholder adapter with TODO comments and keep the rest of the repo functional in DRY_RUN mode.

Do not build a complete production system.
The goal is a workshop-ready scaffold that can be extended by participants.

Reference implementation branch:
Do not put the full “ideal solution” on main.
Add a README section suggesting that the facilitator can keep a separate branch named:
solution/reference-implementation

That branch can contain:

* improved reviewer
* better rewrite agent
* extra eval cases
* example PRs
* expected before/after output

Acceptance criteria:

* uv sync works
* uv run pytest works
* uv run python scripts/run_evals.py works without credentials using DRY_RUN=true
* repo structure matches the requested layout
* baseline sample scores worse than reviewed sample
* no secrets are committed
* beginner can understand where agents, skills, workflows, and evals live
