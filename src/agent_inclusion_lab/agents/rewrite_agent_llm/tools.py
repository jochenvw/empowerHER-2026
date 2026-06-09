"""Helper tools for the example LLM-backed rewrite agent.

This module shows the small amount of glue needed to drive a real
``agent_framework.Agent``:

1. ``FoundryChatClient`` adapts the project's existing ``generate_text`` Foundry
   call into the ``af.BaseChatClient`` interface an ``af.Agent`` expects.
2. ``rewrite_with_agent`` builds the agent from a system prompt and runs it.

Keeping this in ``tools.py`` keeps the agent's ``__init__.py`` focused on the
plugin wiring.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine, Mapping, Sequence
from threading import Thread
from typing import Any

import agent_framework as af

from agent_inclusion_lab import model_client


class FoundryChatClient(af.BaseChatClient):
    """Minimal Agent Framework chat client backed by ``generate_text``.

    Subclasses only need to implement ``_inner_get_response``. We flatten the
    conversation into a single prompt and return the model reply as an
    assistant ``Message``.
    """

    async def _inner_get_response(  # type: ignore[override]
        self,
        *,
        messages: Sequence[af.Message],
        stream: bool,
        options: Mapping[str, Any],
        **kwargs: Any,
    ) -> af.ChatResponse:
        if stream:
            raise NotImplementedError("Streaming is not needed for this workshop example.")
        prompt = "\n\n".join(message.text for message in messages if message.text)
        reply = model_client.generate_text(prompt)
        return af.ChatResponse(messages=af.Message("assistant", [reply]))


def _run_sync(make_coro: Callable[[], Coroutine[Any, Any, Any]]) -> Any:
    # Plugin runners are called synchronously, but ``af.Agent.run`` is async.
    # The coroutine must be created inside the event loop that runs it, so we
    # take a factory. Run it directly when no loop is active (CLI), or on a
    # worker thread when one already is (Chainlit).
    async def _main() -> Any:
        return await make_coro()

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_main())

    result: dict[str, Any] = {}
    error: dict[str, BaseException] = {}

    def _target() -> None:
        try:
            result["value"] = asyncio.run(_main())
        except BaseException as exc:  # noqa: BLE001
            error["value"] = exc

    thread = Thread(target=_target, daemon=True)
    thread.start()
    thread.join()
    if "value" in error:
        raise error["value"]
    return result["value"]


def rewrite_with_agent(instructions: str, user_request: str) -> str:
    agent = af.Agent(FoundryChatClient(), instructions, name="rewrite.llm")
    response = _run_sync(lambda: agent.run(user_request))
    return response.text.strip()
