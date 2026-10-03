import asyncio

from .config import SETTINGS
from .gemini_client import GeminiService
from .memory import ConversationMemory


class HadesChat:
    def __init__(self, gemini: GeminiService, memory: ConversationMemory) -> None:
        self.gemini = gemini
        self.memory = memory
        self._semaphore = asyncio.Semaphore(SETTINGS.max_concurrent_requests)
        self._active_requests = 0
        self._total_requests = 0

    async def ask(self, key: str, message: str) -> str:
        try:
            await asyncio.wait_for(self._semaphore.acquire(), timeout=SETTINGS.max_queue_wait)
        except asyncio.TimeoutError as exc:
            raise RuntimeError("The response queue is currently full.") from exc

        try:
            async with self.memory.session(key) as session:
                trial_history = [*session.history, {"role": "user", "content": message}]
                self._active_requests += 1
                self._total_requests += 1
                try:
                    reply = await self.gemini.generate(trial_history)
                finally:
                    self._active_requests -= 1
                session.commit(message, reply)
                return reply
        finally:
            self._semaphore.release()

    async def reset(self, key: str) -> None:
        await self.memory.reset(key)

    async def reset_all(self) -> None:
        await self.memory.clear_all()

    async def prune_memory(self) -> int:
        return await self.memory.prune()

    async def close(self) -> None:
        await self.gemini.close()

    @property
    def active_requests(self) -> int:
        return self._active_requests

    @property
    def total_requests(self) -> int:
        return self._total_requests
