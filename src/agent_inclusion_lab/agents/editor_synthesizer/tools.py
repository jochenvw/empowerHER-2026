from __future__ import annotations

from typing import Any


def has_actionable_feedback(review_panel: list[dict[str, Any]]) -> bool:
    return any(item.get("suggestions") for item in review_panel)
