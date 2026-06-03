from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    foundry_endpoint: str | None
    foundry_api_key: str | None
    foundry_model_deployment: str | None
    foundry_project_endpoint: str | None
    foundry_openai_endpoint: str | None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings(
        foundry_endpoint=os.getenv("FOUNDRY_ENDPOINT"),
        foundry_api_key=os.getenv("FOUNDRY_API_KEY"),
        foundry_model_deployment=os.getenv("FOUNDRY_MODEL_DEPLOYMENT"),
        foundry_project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        foundry_openai_endpoint=os.getenv("FOUNDRY_OPENAI_ENDPOINT"),
    )
    missing = [
        name
        for name, value in {
            "FOUNDRY_MODEL_DEPLOYMENT": settings.foundry_model_deployment,
            "FOUNDRY_PROJECT_ENDPOINT or FOUNDRY_ENDPOINT or FOUNDRY_OPENAI_ENDPOINT": (
                settings.foundry_project_endpoint
                or settings.foundry_endpoint
                or settings.foundry_openai_endpoint
            ),
        }.items()
        if not value
    ]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing required Foundry configuration: {joined}.")
    return settings
