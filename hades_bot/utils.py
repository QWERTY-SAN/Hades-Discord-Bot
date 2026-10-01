import re
import time
from typing import Hashable

from .config import DISCORD_MESSAGE_LIMIT


class CooldownManager:
    def __init__(self, cooldown_seconds: float) -> None:
        self.cooldown_seconds = cooldown_seconds
        self._last_request: dict[Hashable, float] = {}

    def remaining(self, key: Hashable) -> float:
        if self.cooldown_seconds <= 0:
            return 0.0

        now = time.monotonic()
        previous = self._last_request.get(key)

        if previous is None:
            return 0.0

        return max(0.0, self.cooldown_seconds - (now - previous))

    def try_acquire(self, key: Hashable) -> float:
        remaining = self.remaining(key)
        if remaining > 0:
            return remaining

        if self.cooldown_seconds > 0:
            self._last_request[key] = time.monotonic()

        return 0.0

    def release(self, key: Hashable) -> None:
        self._last_request.pop(key, None)

    def prune(self, older_than_seconds: float = 3600.0) -> int:
        cutoff = time.monotonic() - older_than_seconds
        stale = [
            key
            for key, timestamp in self._last_request.items()
            if timestamp < cutoff
        ]

        for key in stale:
            self._last_request.pop(key, None)

        return len(stale)

    def size(self) -> int:
        return len(self._last_request)


def split_message(
    text: str,
    limit: int = DISCORD_MESSAGE_LIMIT,
) -> list[str]:
    text = text.strip()

    if not text:
        return ["..."]

    if len(text) <= limit:
        return [text]

    chunks: list[str] = []

    while len(text) > limit:
        split_at = text.rfind("\n\n", 0, limit)

        if split_at < 1:
            split_at = text.rfind("\n", 0, limit)

        if split_at < 1:
            split_at = text.rfind(" ", 0, limit)

        if split_at < 1:
            split_at = limit

        chunk = text[:split_at].rstrip()

        if chunk:
            chunks.append(chunk)

        text = text[split_at:].lstrip()

    if text:
        chunks.append(text)

    return chunks


def strip_bot_mentions(content: str, bot_id: int) -> str:
    content = re.sub(
        rf"<@!?{re.escape(str(bot_id))}>",
        "",
        content,
    )
    return content.strip()


def clean_model_output(text: str) -> str:
    text = text.strip()

    if not text:
        return ""

    # Do not allow generated text to accidentally turn into Discord-wide pings.
    text = text.replace("@everyone", "@\u200beveryone")
    text = text.replace("@here", "@\u200bhere")

    return text
