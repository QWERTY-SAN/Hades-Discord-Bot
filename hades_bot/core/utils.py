from __future__ import annotations

import re
import time
from dataclasses import dataclass

from ..config import SETTINGS


DISCORD_MESSAGE_LIMIT = 2000
_GIF_URL_RE = re.compile(r"https?://[^\s<>]+?\.gif(?:\?[^\s<>]*)?", re.I)
_RAW_DISCORD_MENTION_RE = re.compile(r"<@!?\d+>|<@&\d+>|<#\d+>")


def split_message(text: str, limit: int = DISCORD_MESSAGE_LIMIT) -> list[str]:
    text = text.strip()
    if not text:
        return [""]
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        split_at = remaining.rfind("\n", 0, limit + 1)
        if split_at < max(1, limit // 2):
            split_at = remaining.rfind(" ", 0, limit + 1)
        if split_at <= 0:
            split_at = limit
        chunk = remaining[:split_at].rstrip()
        if chunk:
            chunks.append(chunk)
        remaining = remaining[split_at:].lstrip()
    if remaining:
        chunks.append(remaining)
    return chunks


def strip_bot_mentions(content: str, bot_id: int) -> str:
    if not bot_id:
        return content.strip()
    content = content.replace(f"<@{bot_id}>", "")
    content = content.replace(f"<@!{bot_id}>", "")
    return content.strip()


def sanitize_model_output(text: str) -> str:
    text = text.replace("\x00", "").strip()
    text = re.sub(r"^(?:Hades\s*:\s*)+", "", text, flags=re.I)
    text = re.sub(r"\bAs an AI(?: language model)?[,:]", "", text, flags=re.I)
    text = _GIF_URL_RE.sub("", text)
    text = _RAW_DISCORD_MENTION_RE.sub("", text)
    text = re.sub(r"\n{4,}", "\n\n", text)
    return text.strip()


@dataclass(slots=True)
class _Cooldown:
    touched_at: float


class CooldownManager:
    def __init__(self, cooldown_seconds: float) -> None:
        self.cooldown_seconds = max(0.0, cooldown_seconds)
        self._last: dict[str, _Cooldown] = {}

    async def try_acquire(self, key: str) -> float:
        now = time.monotonic()
        previous = self._last.get(key)
        if previous is not None:
            remaining = self.cooldown_seconds - (now - previous.touched_at)
            if remaining > 0:
                return remaining
        self._last[key] = _Cooldown(now)
        return 0.0

    async def release(self, key: str) -> None:
        self._last.pop(key, None)

    async def prune(self, ttl_seconds: float = 3600.0) -> int:
        now = time.monotonic()
        removed = 0
        for key, state in list(self._last.items()):
            if now - state.touched_at > ttl_seconds:
                self._last.pop(key, None)
                removed += 1
        return removed
