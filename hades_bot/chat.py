import asyncio

from .config import MAX_CONCURRENT_REQUESTS
from .gemini_client import GeminiService
from .memory import ConversationMemory


class HadesChat:
    def __init__(
        self,
        gemini: GeminiService,
        memory: ConversationMemory,
    ) -> None:
        self.gemini = gemini
        self.memory = memory
        self._locks: dict[str, asyncio.Lock] = {}
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    def _get_lock(self, key: str) -> asyncio.Lock:
        lock = self._locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[key] = lock
        return lock

    async def ask(self, key: str, message: str) -> str:
        async with self._semaphore:
            async with self._get_lock(key):
                history = self.memory.get(key)

                reply = await self.gemini.generate_with_retry(
                    history=history,
                    user_message=message,
                )

                self.memory.add(key, "user", message)
                self.memory.add(key, "model", reply)

                return reply

    def reset(self, key: str) -> None:
        self.memory.reset(key)
        self._locks.pop(key, None)

    def reset_all(self) -> None:
        self.memory.clear_all()
        self._locks.clear()
