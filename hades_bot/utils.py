import asyncio
import re
import time

from .config import DISCORD_MESSAGE_LIMIT


class CooldownManager:
    def __init__(self, cooldown_seconds: float) -> None:
        self.cooldown_seconds = cooldown_seconds
        self._last_request: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def try_acquire(self, key: str) -> float:
        if self.cooldown_seconds <= 0:
            return 0.0
        now = time.monotonic()
        async with self._lock:
            previous = self._last_request.get(key, 0.0)
            remaining = self.cooldown_seconds - (now - previous)
            if remaining > 0:
                return remaining
            self._last_request[key] = now
            return 0.0

    async def release(self, key: str) -> None:
        async with self._lock:
            self._last_request.pop(key, None)

    async def prune(self, older_than_seconds: float = 3600.0) -> int:
        cutoff = time.monotonic() - older_than_seconds
        async with self._lock:
            stale = [key for key, timestamp in self._last_request.items() if timestamp < cutoff]
            for key in stale:
                self._last_request.pop(key, None)
            return len(stale)


def split_message(text: str, limit: int = DISCORD_MESSAGE_LIMIT) -> list[str]:
    text = text.strip()
    if not text:
        return ["…"]
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        split_at = remaining.rfind("\n\n", 0, limit + 1)
        if split_at < 1:
            split_at = remaining.rfind("\n", 0, limit + 1)
        if split_at < 1:
            split_at = remaining.rfind(" ", 0, limit + 1)
        if split_at < 1:
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
        return content
    return re.sub(rf"<@!?{bot_id}>", "", content).strip()


def sanitize_model_output(text: str) -> str:
    text = re.sub(r"<@!?\d+>", "@user", text)
    text = re.sub(r"@(everyone|here)", r"@\1", text, flags=re.I)
    return text.strip()


def clean_model_output(text: str) -> str:
    # Gemini can occasionally return empty whitespace or accidental null chars.
    text = text.replace("\x00", "").strip()
    return sanitize_model_output(text)
