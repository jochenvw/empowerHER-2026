from __future__ import annotations

import warnings

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

from .config import Settings, get_settings

warnings.filterwarnings(
    "ignore",
    message=".*experimental.*",
    module="agent_framework.*",
)

from agent_framework.openai import OpenAIChatClient


def generate_text(prompt: str) -> str:
    settings = get_settings()
    return _call_foundry_model(prompt, settings)


def _call_foundry_model(prompt: str, settings: Settings) -> str:
    deployment = settings.foundry_model_deployment or ""
    if not deployment:
        raise RuntimeError("FOUNDRY_MODEL_DEPLOYMENT is required.")

    base_url = _resolve_openai_base_url(settings)
    client = OpenAI(base_url=base_url, api_key=_resolve_api_key(settings))

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are a concise, professional writing assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_completion_tokens=900,
    )

    if not response.choices:
        raise RuntimeError("Model response did not contain any choices.")
    message = response.choices[0].message
    content = message.content
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            text = getattr(item, "text", None)
            if isinstance(text, str):
                parts.append(text)
        if parts:
            return "\n".join(parts).strip()
    raise RuntimeError("Model response did not contain text content.")


def create_framework_chat_client() -> OpenAIChatClient:
    settings = get_settings()
    deployment = settings.foundry_model_deployment or ""
    if not deployment:
        raise RuntimeError("FOUNDRY_MODEL_DEPLOYMENT is required.")
    return OpenAIChatClient(
        model=deployment,
        base_url=_resolve_openai_base_url(settings),
        api_key=_resolve_api_key(settings),
    )


def _resolve_api_key(settings: Settings):
    if settings.foundry_api_key:
        return settings.foundry_api_key
    return get_bearer_token_provider(
        DefaultAzureCredential(), "https://ai.azure.com/.default"
    )


def _resolve_openai_base_url(settings: Settings) -> str:
    if settings.foundry_openai_endpoint:
        return settings.foundry_openai_endpoint.rstrip("/")

    configured_endpoint = (
        settings.foundry_project_endpoint or settings.foundry_endpoint or ""
    ).rstrip("/")
    if not configured_endpoint:
        raise RuntimeError(
            "FOUNDRY_PROJECT_ENDPOINT, FOUNDRY_ENDPOINT, or FOUNDRY_OPENAI_ENDPOINT is required."
        )

    marker = "/api/projects/"
    if marker in configured_endpoint:
        host_root = configured_endpoint.split(marker, 1)[0]
    else:
        host_root = configured_endpoint
    return f"{host_root}/openai/v1"
