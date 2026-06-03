# Coding agent rules

- Keep the repository simple and workshop-oriented.
- Put each agent in its own file under `src/agent_inclusion_lab/agents`.
- Put reusable tools/helpers under `src/agent_inclusion_lab/skills`.
- Put orchestration logic only in `src/agent_inclusion_lab/workflow.py`.
- Put eval logic only in `src/agent_inclusion_lab/evals`.
- Do not put secrets in code.
- Do not add large dependencies unless necessary.
- Prefer idiomatic, typed Python with small functions.
- Add tests for each new agent or eval behavior.
- Maintain `DRY_RUN` support.
- Do not "fix bias" with only one hardcoded string replacement.
- Prefer structured findings over vague prose.
- Keep outputs understandable for beginners.
- For new agent variants, add a new file in `src/agent_inclusion_lab/agents` that exports `AGENT_PLUGIN`; avoid editing shared workflow logic unless required.
