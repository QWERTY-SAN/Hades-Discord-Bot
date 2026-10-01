import re
import time

from .config import DISCORD_MESSAGE_LIMIT


class CooldownManager:
    """Cooldowns keyed by conversation instead of globally by user."""

    def __init__(self, cooldown_seconds: float):
        self.cooldown_seconds = cooldown_seconds
        self._last_request: dict[str, float] = {}

    def consume(self, key: str) -> float:
        now = time.monotonic()
        previous = self._last_request.get(key, 0.0)
        remaining = self.cooldown_seconds - (now - previous)
        if remaining > 0:
            return remaining
        self._last_request[key] = now
        return 0.0

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


def split_message(text: str, limit: int = DISCORD_MESSAGE_LIMIT) -> list[str]:
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
    content = re.sub(rf"<@!?{re.escape(str(bot_id))}>", "", content)
    return content.strip()


def sanitize_model_output(text: str) -> str:
    """Remove raw Discord broadcast/mention constructs from model output."""
    text = text.replace("@everyone", "everyone")
    text = text.replace("@here", "here")
    text = re.sub(r"<@&\d+>", "role", text)
    text = re.sub(r"<@!?\d+>", "user", text)
    return text.strip()
