import re
import time

from .config import DISCORD_MESSAGE_LIMIT


class CooldownManager:
    def __init__(self, cooldown_seconds: float) -> None:
        self.cooldown_seconds = cooldown_seconds
        self._last_request: dict[int, float] = {}

    def consume(self, user_id: int) -> float:
        now = time.monotonic()
        previous = self._last_request.get(user_id, 0.0)
        remaining = self.cooldown_seconds - (now - previous)

        if remaining > 0:
            return remaining

        self._last_request[user_id] = now
        return 0.0

    def cleanup(self, older_than_seconds: float = 3600.0) -> None:
        cutoff = time.monotonic() - older_than_seconds
        stale = [
            user_id
            for user_id, timestamp in self._last_request.items()
            if timestamp < cutoff
        ]
        for user_id in stale:
            self._last_request.pop(user_id, None)


def split_message(text: str, limit: int = DISCORD_MESSAGE_LIMIT) -> list[str]:
    text = text.strip()

    if not text:
        return ["..."]

    if len(text) <= limit:
        return [text]

    chunks: list[str] = []

    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit)

        if split_at < 1:
            split_at = text.rfind(" ", 0, limit)

        if split_at < 1:
            split_at = limit

        chunks.append(text[:split_at].rstrip())
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
