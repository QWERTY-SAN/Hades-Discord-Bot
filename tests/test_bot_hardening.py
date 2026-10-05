from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

os.environ.setdefault("DISCORD_TOKEN", "test-token-not-a-real-secret")
os.environ.setdefault("GEMINI_API_KEY", "test-key-not-a-real-secret")

from hades_bot.bot import bot, status_command  # noqa: E402
from hades_bot.config import SETTINGS  # noqa: E402


class _TypingContext:
    def __init__(self, events: list[str]) -> None:
        self.events = events

    async def __aenter__(self):
        self.events.append("typing")
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> bool:
        return False


class _Channel:
    id = 456

    def __init__(self, events: list[str]) -> None:
        self.events = events

    def typing(self) -> _TypingContext:
        return _TypingContext(self.events)

    async def send(self, *args, **kwargs):
        return None


class _Message:
    def __init__(self, events: list[str]) -> None:
        self.author = SimpleNamespace(id=123, bot=False)
        self.guild = SimpleNamespace(id=789)
        self.channel = _Channel(events)
        self.reply = AsyncMock()
        self.reference = None


class _Cooldowns:
    def __init__(self, events: list[str], remaining: float = 0.0) -> None:
        self.events = events
        self.remaining = remaining
        self.released: list[str] = []

    async def try_acquire(self, key: str) -> float:
        self.events.append("cooldown")
        return self.remaining

    async def release(self, key: str) -> None:
        self.released.append(key)


class _Chat:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.scope_refusal = AsyncMock(side_effect=self._refusal)
        self.ask = AsyncMock(return_value="A harmless answer about Aether Gazer.")

    async def _refusal(self, category: str) -> str:
        self.events.append("scope_refusal")
        return "That is outside my stage, little lamb. Ask about Aether Gazer."


class _Media:
    entries = ()

    def should_auto_send(self, message, trigger: str) -> bool:
        return False

    async def send_gif(self, *args, **kwargs) -> bool:
        return False


class TestBotHardening(unittest.IsolatedAsyncioTestCase):
    async def test_blocked_topic_obeys_cooldown_before_generated_refusal(self) -> None:
        events: list[str] = []
        cooldowns = _Cooldowns(events)
        chat = _Chat(events)
        message = _Message(events)

        with (
            patch.object(bot, "cooldowns", cooldowns),
            patch.object(bot, "hades_chat", chat),
            patch.object(bot, "media", _Media()),
        ):
            await bot.handle_ai_message(message, "What is Formula One?", trigger="mention")

        self.assertLess(events.index("cooldown"), events.index("scope_refusal"))
        chat.scope_refusal.assert_awaited_once()
        message.reply.assert_awaited_once()

    async def test_cooldown_denial_prevents_scope_refusal_api_call(self) -> None:
        events: list[str] = []
        cooldowns = _Cooldowns(events, remaining=1.2)
        chat = _Chat(events)
        message = _Message(events)

        with (
            patch.object(bot, "cooldowns", cooldowns),
            patch.object(bot, "hades_chat", chat),
            patch.object(bot, "media", _Media()),
        ):
            await bot.handle_ai_message(message, "What is Formula One?", trigger="mention")

        chat.scope_refusal.assert_not_awaited()
        message.reply.assert_awaited_once()

    async def test_oversized_input_is_rejected_before_cooldown_or_model_call(self) -> None:
        events: list[str] = []
        cooldowns = _Cooldowns(events)
        chat = _Chat(events)
        message = _Message(events)

        with (
            patch.object(bot, "cooldowns", cooldowns),
            patch.object(bot, "hades_chat", chat),
            patch.object(bot, "media", _Media()),
        ):
            await bot.handle_ai_message(
                message,
                "x" * (SETTINGS.max_input_chars + 1),
                trigger="mention",
            )

        self.assertNotIn("cooldown", events)
        chat.scope_refusal.assert_not_awaited()
        message.reply.assert_awaited_once()

    async def test_non_owner_cannot_view_status_in_dm(self) -> None:
        author = SimpleNamespace(
            id=123,
            guild_permissions=SimpleNamespace(manage_guild=False, administrator=False),
        )
        ctx = SimpleNamespace(author=author, guild=None, reply=AsyncMock())

        with patch.object(bot, "is_owner", new_callable=AsyncMock, return_value=False):
            await status_command.callback(ctx)

        ctx.reply.assert_awaited_once()
        response = ctx.reply.await_args.args[0]
        self.assertIn("managing the stage", response)
