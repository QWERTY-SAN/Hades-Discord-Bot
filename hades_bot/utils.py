import time

from .config import DISCORD_MESSAGE_LIMIT


class CooldownManager:
    def __init__(self, cooldown_seconds: float) -> None:
        self.cooldown_seconds = cooldown_seconds
        self._last_request: dict[int, float] = {}

    def remaining(self, user_id: int) -> float:
        now = time.monotonic()
        previous = self._last_request.get(user_id, 0.0)
        return max(0.0, self.cooldown_seconds - (now - previous))

    def touch(self, user_id: int) -> None:
        self._last_request[user_id] = time.monotonic()

    def consume(self, user_id: int) -> float:
        remaining = self.remaining(user_id)

        if remaining <= 0:
            self.touch(user_id)

        return remaining


def split_message(text: str, limit: int = DISCORD_MESSAGE_LIMIT) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []

    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit)

        if split_at == -1:
            split_at = text.rfind(" ", 0, limit)

        if split_at <= 0:
            split_at = limit

        chunk = text[:split_at].strip()
        if chunk:
            chunks.append(chunk)

        text = text[split_at:].lstrip()

    if text:
        chunks.append(text)

    return chunks


def strip_bot_mentions(content: str, bot_id: int) -> str:
    content = content.replace(f"<@{bot_id}>", "")
    content = content.replace(f"<@!{bot_id}>", "")
    return content.strip()
