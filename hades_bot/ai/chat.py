from __future__ import annotations

import asyncio
import logging

from .gemini_client import GeminiService, UnsafeModelOutputError
from ..config import SETTINGS
from ..core.memory import ConversationMemory

logger = logging.getLogger("hades-bot")


class HadesChat:
    def __init__(self, gemini: GeminiService, memory: ConversationMemory, max_concurrent_requests: int = 3) -> None:
        self.gemini = gemini
        self.memory = memory
        self._max_concurrent_requests = max(1, max_concurrent_requests)
        self._semaphore = asyncio.Semaphore(self._max_concurrent_requests)
        self.active_requests = 0
        self.total_requests = 0

    @property
    def max_concurrent_requests(self) -> int:
        return self._max_concurrent_requests

    async def ask(self, key: str, user_message: str) -> str:
        try:
            await asyncio.wait_for(self._semaphore.acquire(), timeout=SETTINGS.max_queue_wait)
        except asyncio.TimeoutError as exc:
            raise RuntimeError("The response queue is full.") from exc

        self.active_requests += 1
        self.total_requests += 1
        try:
            async with self.memory.session(key) as session:
                history = session.history
                reply = await self.gemini.generate(history, user_message)
                from .scope_validator import validate_generated_reply

                validate_generated_reply(reply, history, user_message)
                session.commit(user_message, reply)
                return reply
        finally:
            self._semaphore.release()
            self.active_requests = max(0, self.active_requests - 1)

    async def scope_refusal(self, reason: str | None) -> str:
        reason_text = reason or "a subject outside Hades's interests"
        fallback = {
            "programming or software development": "Programming? Mm. Not my stage, Administrator. Bring me something from Aether Gazer instead.",
            "sports": "Sports hold little interest for me. Choose a subject closer to my world, little lamb.",
            "Formula One or motorsports": "The racetrack can keep its drama. Ask me about Aether Gazer instead.",
            "other games": "Another game's stage? No. If it concerns Aether Gazer, however, you have my attention.",
            "politics": "Politics is a tedious stage. Ask me something more worthy of my attention.",
            "finance": "Markets are hardly my favorite performance. Bring me something within my world instead.",
            "a specialist technical subject": "That technical maze is outside my realm. Ask me about Aether Gazer, the Society of Muses, or something more personal.",
            "an unrelated factual subject": "Mm. My interests lie closer to home. Ask me about something within my world, Administrator.",
        }
        return fallback.get(reason_text, "That lies outside my stage, little lamb. Bring me something closer to my world.")

    async def reset(self, key: str) -> None:
        await self.memory.reset(key)

    async def prune_memory(self) -> int:
        return await self.memory.prune()

    async def close(self) -> None:
        await self.gemini.close()
