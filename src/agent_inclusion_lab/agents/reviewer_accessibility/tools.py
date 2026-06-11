"""Helper tools for the accessibility-review agent.

Follows the same pattern as ``rewrite_agent_llm/tools.py``:

1. ``FoundryChatClient`` adapts ``generate_text`` into the ``af.BaseChatClient``
   interface expected by ``af.Agent``.
2. ``review_with_agent`` builds the agent, runs it, and parses structured JSON
   findings from the response.  Falls back gracefully when the model returns
   non-JSON text rather than raising an exception.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable, Coroutine, Mapping, Sequence
from threading import Thread
from typing import Any

import agent_framework as af

from agent_inclusion_lab import model_client


class FoundryChatClient(af.BaseChatClient):
    """Minimal Agent Framework chat client backed by ``generate_text``.

    Flattens the conversation into a single prompt and returns the model reply
    as an assistant ``Message``.
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
    # The coroutine must be created inside the event loop that runs it to avoid
    # an Agent Framework telemetry context-var error.
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


def review_with_agent(instructions: str, job_posting: str) -> dict[str, Any]:
    """Run the accessibility-review LLM agent and return structured findings.

    Returns a dict with ``summary`` (str), ``suggestions`` (list[str]), and
    ``evidence_spans`` (list[str]).  When the model returns non-JSON text the
    response is used as the summary and the lists are left empty.
    """
    agent = af.Agent(FoundryChatClient(), instructions, name="reviewer.accessibility")
    response = _run_sync(lambda: agent.run(job_posting))
    raw = response.text.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "summary": raw or "Accessibility review completed.",
            "suggestions": [],
            "evidence_spans": [],
        }
    return {
        "summary": str(data.get("summary", "Accessibility review completed.")),
        "suggestions": [str(s) for s in data.get("suggestions", [])],
        "evidence_spans": [str(e) for e in data.get("evidence_spans", [])],
    }
