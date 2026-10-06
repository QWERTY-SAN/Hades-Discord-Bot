from __future__ import annotations

import asyncio
import time
from collections import OrderedDict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import AsyncIterator


@dataclass(slots=True)
class MessageTurn:
    role: str
    text: str


@dataclass(slots=True)
class Conversation:
    turns: deque[MessageTurn]
    touched_at: float = field(default_factory=time.monotonic)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class ConversationMemory:
    def __init__(self, max_history: int, ttl_seconds: int, max_conversations: int) -> None:
        self.max_history = max_history
        self.ttl_seconds = ttl_seconds
        self.max_conversations = max_conversations
        self._conversations: OrderedDict[str, Conversation] = OrderedDict()
        self._index_lock = asyncio.Lock()

    def _expired(self, conversation: Conversation, now: float) -> bool:
        return now - conversation.touched_at >= self.ttl_seconds

    def _prune_locked(self, now: float, exclude_key: str | None = None) -> int:
        removed = 0
        for key in list(self._conversations):
            conversation = self._conversations[key]
            if self._expired(conversation, now) and key != exclude_key and not conversation.lock.locked():
                self._conversations.pop(key, None)
                removed += 1
        while len(self._conversations) > self.max_conversations:
            removable = next(
                (
                    key
                    for key, conversation in self._conversations.items()
                    if key != exclude_key and not conversation.lock.locked()
                ),
                None,
            )
            if removable is None:
                break
            self._conversations.pop(removable, None)
            removed += 1
        return removed

    async def _get_or_create(self, key: str) -> Conversation:
        async with self._index_lock:
            now = time.monotonic()
            self._prune_locked(now, exclude_key=key)
            conversation = self._conversations.get(key)
            if conversation is None:
                conversation = Conversation(turns=deque(maxlen=self.max_history))
                self._conversations[key] = conversation
            else:
                conversation.touched_at = now
                self._conversations.move_to_end(key)
            return conversation

    async def has_history(self, key: str) -> bool:
        async with self._index_lock:
            now = time.monotonic()
            self._prune_locked(now)
            conversation = self._conversations.get(key)
            if conversation is None or self._expired(conversation, now):
                return False
            return bool(conversation.turns)

    @asynccontextmanager
    async def session(self, key: str) -> AsyncIterator["MemorySession"]:
        conversation = await self._get_or_create(key)
        async with conversation.lock:
            conversation.touched_at = time.monotonic()
            yield MemorySession(conversation)

    async def reset(self, key: str) -> None:
        async with self._index_lock:
            self._conversations.pop(key, None)

    async def clear_all(self) -> None:
        async with self._index_lock:
            self._conversations.clear()

    async def prune(self) -> int:
        async with self._index_lock:
            return self._prune_locked(time.monotonic())

    async def conversation_count(self) -> int:
        async with self._index_lock:
            self._prune_locked(time.monotonic())
            return len(self._conversations)

    async def message_count(self, key: str) -> int:
        async with self._index_lock:
            conversation = self._conversations.get(key)
            if conversation is None or self._expired(conversation, time.monotonic()):
                return 0
        async with conversation.lock:
            return len(conversation.turns)


class MemorySession:
    def __init__(self, conversation: Conversation) -> None:
        self._conversation = conversation

    @property
    def history(self) -> list[dict[str, str]]:
        return [
            {"role": turn.role, "content": turn.text}
            for turn in self._conversation.turns
        ]

    def commit(self, user_text: str, assistant_text: str) -> None:
        self._conversation.turns.append(MessageTurn("user", user_text))
        self._conversation.turns.append(MessageTurn("model", assistant_text))
        self._conversation.touched_at = time.monotonic()
