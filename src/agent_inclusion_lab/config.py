from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    dry_run: bool
    foundry_endpoint: str | None
    foundry_api_key: str | None
    foundry_model_deployment: str | None
    foundry_project_endpoint: str | None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings(
        dry_run=_to_bool(os.getenv("DRY_RUN"), default=False),
        foundry_endpoint=os.getenv("FOUNDRY_ENDPOINT"),
        foundry_api_key=os.getenv("FOUNDRY_API_KEY"),
        foundry_model_deployment=os.getenv("FOUNDRY_MODEL_DEPLOYMENT"),
        foundry_project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
    )
    if not settings.dry_run:
        missing = [
            name
            for name, value in {
                "FOUNDRY_ENDPOINT": settings.foundry_endpoint,
                "FOUNDRY_API_KEY": settings.foundry_api_key,
                "FOUNDRY_MODEL_DEPLOYMENT": settings.foundry_model_deployment,
                "FOUNDRY_PROJECT_ENDPOINT": settings.foundry_project_endpoint,
            }.items()
            if not value
        ]
        if missing:
            joined = ", ".join(missing)
            raise RuntimeError(
                "Missing required Foundry configuration: "
                f"{joined}. Set DRY_RUN=true to run without credentials."
            )
    return settings

