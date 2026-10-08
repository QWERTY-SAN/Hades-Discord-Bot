from __future__ import annotations

import asyncio
import logging
import random

from .gemini_client import GeminiService, UnsafeModelOutputError
from ..config import SETTINGS
from ..core.memory import ConversationMemory
from ..core.scope import contains_forbidden_topic

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
                context_text = "\n".join(
                    item.get("content", "")
                    for item in history
                    if item.get("content")
                )
                if contains_forbidden_topic(reply, context=f"{context_text}\n{user_message}"):
                    raise UnsafeModelOutputError
                session.commit(user_message, reply)
                return reply
        finally:
            self._semaphore.release()
            self.active_requests = max(0, self.active_requests - 1)

    async def scope_refusal(self, reason: str | None) -> str:
        reason_text = reason or "a subject outside Hades's interests"
        fallback = {
            "programming or software development": (
                "Programming? Mm. That is a stage I shall leave to others, Administrator. Bring me something from my world instead.",
                "Code and debugging are not performances I intend to direct, little lamb. Ask me about Aether Gazer—or simply talk to me.",
            ),
            "programming or specialist work": (
                "Programming? Mm. That is a stage I shall leave to others, Administrator. Bring me something from my world instead.",
                "That technical stage is not mine to direct. Bring me something closer to Aether Gazer.",
            ),
            "sports": (
                "Sports hold little interest for me. Choose a subject closer to my world, little lamb.",
                "The field can keep its athletes. My attention is better spent elsewhere.",
            ),
            "Formula One or motorsports": (
                "The racetrack can keep its drama. Ask me about Aether Gazer instead.",
                "Motorsports? No. I have other stages to mind.",
            ),
            "other games": (
                "Another game's stage? No. If it concerns Aether Gazer, however, you have my attention.",
                "That belongs to another cast, little lamb. Bring me back to Aether Gazer.",
            ),
            "politics, news, or finance": (
                "Politics and markets are tedious stages. Ask me something more worthy of my attention.",
                "The affairs of markets and politicians can perform without me.",
            ),
            "politics": ("Politics is a tedious stage. Ask me something more worthy of my attention.",),
            "finance": ("Markets are hardly my favorite performance. Bring me something within my world instead.",),
            "a specialist technical subject": (
                "That technical maze is outside my realm. Ask me about Aether Gazer, the Society of Muses, or something more personal.",
                "That is specialist territory, Administrator. My interests lie elsewhere.",
            ),
            "an unrelated factual subject": (
                "Mm. My interests lie closer to home. Ask me about something within my world, Administrator.",
                "That question belongs to a different stage. Ask me something Hades would actually care to answer.",
            ),
            "unrelated entertainment or media": (
                "That performance belongs to another stage. Bring me something from Aether Gazer—or something personal.",
                "Another cast, another show. I shall leave that one to them.",
            ),
            "F1 or motorsport": ("The racetrack can keep its drama. Ask me about Aether Gazer instead.",),
            "unrelated racing": ("Racing is not my chosen spectacle. Bring me something closer to my world.",),
        }
        options = fallback.get(
            reason_text,
            (
                "That lies outside my stage, little lamb. Bring me something closer to my world.",
                "Mm. Not my subject. Bring me something from Aether Gazer—or simply speak with me.",
                "That is not a performance I care to direct. Change the subject, Administrator.",
            ),
        )
        return random.SystemRandom().choice(options)

    async def reset(self, key: str) -> None:
        await self.memory.reset(key)

    async def prune_memory(self) -> int:
        return await self.memory.prune()

    async def close(self) -> None:
        await self.gemini.close()
