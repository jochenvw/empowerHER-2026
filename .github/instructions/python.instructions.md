---
name: Python coding standards
description: Python-specific conventions for this workshop repository
applyTo: "**/*.py"
---
# Python standards

Apply the project-wide rules from `../copilot-instructions.md`, then apply these Python-specific constraints:

- Use type hints for function signatures.
- Use `pathlib` for file paths.
- Keep functions short and names explicit.
- Prefer deterministic behavior in tests and evals.
- Avoid broad exception handling and silent failures.
- Prefer Agent Framework-native abstractions over custom wrappers when available.
- Keep agent-folder modules terse and explicit (`system_prompt.md`, optional `skills.md`, optional `tools.py`, `__init__.py`).
