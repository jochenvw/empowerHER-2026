from __future__ import annotations

from typing import Any


def has_rewrite_suggestions(reviewer_feedback: list[dict[str, Any]]) -> bool:
    return any(item.get("suggestions") for item in reviewer_feedback)
