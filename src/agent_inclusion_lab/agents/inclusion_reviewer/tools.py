from __future__ import annotations

from typing import Any


def build_noop_review() -> dict[str, Any]:
    return {
        "reviewer": "reviewer.accept_all",
        "summary": "No improvements suggested.",
        "suggestions": [],
    }
