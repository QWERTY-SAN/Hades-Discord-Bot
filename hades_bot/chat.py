import asyncio
import weakref

from .config import MAX_CONCURRENT_REQUESTS, MAX_QUEUE_WAIT
from .groq_client import GroqService
from .memory import ConversationMemory


class HadesChat:
    def __init__(
        self,
        groq: GroqService,
        memory: ConversationMemory,
    ) -> None:
        self.groq = groq
        self.memory = memory
        self._locks: weakref.WeakValueDictionary[str, asyncio.Lock] = weakref.WeakValueDictionary()
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        self._active_requests = 0
        self._total_requests = 0

    def _get_lock(self, key: str) -> asyncio.Lock:
        lock = self._locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[key] = lock
        return lock

    async def ask(self, key: str, message: str) -> str:
        try:
            await asyncio.wait_for(
                self._semaphore.acquire(),
                timeout=MAX_QUEUE_WAIT,
            )
        except asyncio.TimeoutError as exc:
            raise RuntimeError("The response queue is currently full.") from exc

        try:
            async with self._get_lock(key):
                self._active_requests += 1
                self._total_requests += 1
                try:
                    history = self.memory.get(key)
                    reply = await self.groq.generate_with_retry(
                        history=history,
                        user_message=message,
                    )

                    self.memory.add(key, "user", message)
                    self.memory.add(key, "model", reply)
                    return reply
                finally:
                    self._active_requests -= 1
        finally:
            self._semaphore.release()

    def reset(self, key: str) -> None:
        self.memory.reset(key)

    def reset_all(self) -> None:
        self.memory.clear_all()

    def prune_memory(self) -> int:
        return self.memory.prune()

    @property
    def active_requests(self) -> int:
        return self._active_requests

    @property
    def total_requests(self) -> int:
        return self._total_requests
