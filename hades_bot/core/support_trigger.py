"""Channel-specific support triggers for Hades."""

from __future__ import annotations

import re

MENTAL_BREAKDOWN_CHANNEL_ID = 1537979704714334238
MENTAL_BREAKDOWN_PATTERN = re.compile(r"\bmental[\s-]+breakdown\b", re.IGNORECASE)


def is_mental_breakdown_trigger(channel_id: int | None, content: str) -> bool:
    """Match mental-breakdown wording only in the configured Discord channel."""
    if channel_id != MENTAL_BREAKDOWN_CHANNEL_ID or not content:
        return False
    return MENTAL_BREAKDOWN_PATTERN.search(content) is not None
