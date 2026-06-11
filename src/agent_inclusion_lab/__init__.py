"""agent_inclusion_lab package."""

import warnings

# Agent Framework emits FutureWarning-based "experimental" notices at import
# time (e.g. SkillResource, MemoryStore). They fire before pytest/CLI can apply
# filters, so suppress them by message here, before any submodule imports
# agent_framework. Keeps workshop output clean for beginners.
warnings.filterwarnings("ignore", message=r".*is experimental.*")

from .workflow import WorkflowResult, run_inclusion_workflow

__all__ = ["WorkflowResult", "run_inclusion_workflow"]

