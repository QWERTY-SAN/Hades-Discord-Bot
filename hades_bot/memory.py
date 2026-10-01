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
    """Per-conversation memory with TTL, LRU-style capping, and async locking."""

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
        expired = [
            key
            for key, conversation in self._conversations.items()
            if self._expired(conversation, now)
        ]
        for key in expired:
            if self._conversations.pop(key, None) is not None:
                removed += 1

        while len(self._conversations) > self.max_conversations:
            removable_key = next(
                (
                    key
                    for key, conversation in self._conversations.items()
                    if key != exclude_key and not conversation.lock.locked()
                ),
                None,
            )
            if removable_key is None:
                break
            self._conversations.pop(removable_key, None)
            removed += 1
        return removed

    async def _get_or_create(self, key: str) -> Conversation:
        async with self._index_lock:
            now = time.monotonic()
            self._prune_locked(now)
            conversation = self._conversations.get(key)
            if conversation is None:
                conversation = Conversation(turns=deque(maxlen=self.max_history))
                self._conversations[key] = conversation
            else:
                conversation.touched_at = now
                self._conversations.move_to_end(key)
            self._prune_locked(now, exclude_key=key)
            return conversation

    @asynccontextmanager
    async def session(self, key: str) -> AsyncIterator["ConversationSession"]:
        conversation = await self._get_or_create(key)
        async with conversation.lock:
            conversation.touched_at = time.monotonic()
            async with self._index_lock:
                if self._conversations.get(key) is conversation:
                    self._conversations.move_to_end(key)
            yield ConversationSession(conversation)

    async def reset(self, key: str) -> None:
        async with self._index_lock:
            conversation = self._conversations.get(key)
        if conversation is None:
            return
        async with conversation.lock:
            async with self._index_lock:
                if self._conversations.get(key) is conversation:
                    self._conversations.pop(key, None)

    async def clear_all(self) -> None:
        async with self._index_lock:
            self._conversations.clear()

    async def prune(self, now: float | None = None) -> int:
        now = time.monotonic() if now is None else now
        async with self._index_lock:
            return self._prune_locked(now)

    async def conversation_count(self) -> int:
        await self.prune()
        async with self._index_lock:
            return len(self._conversations)

    async def message_count(self, key: str) -> int:
        conversation = await self._get_or_create_if_existing(key)
        if conversation is None:
            return 0
        async with conversation.lock:
            if self._expired(conversation, time.monotonic()):
                return 0
            return len(conversation.turns)

    async def _get_or_create_if_existing(self, key: str) -> Conversation | None:
        async with self._index_lock:
            now = time.monotonic()
            self._prune_locked(now)
            conversation = self._conversations.get(key)
            if conversation is None:
                return None
            conversation.touched_at = now
            self._conversations.move_to_end(key)
            return conversation


@dataclass(slots=True)
class ConversationSession:
    conversation: Conversation

    @property
    def history(self) -> list[dict[str, str]]:
        return [
            {"role": turn.role, "content": turn.text}
            for turn in self.conversation.turns
        ]

    def commit(self, user_content: str, assistant_content: str) -> None:
        self.conversation.turns.append(MessageTurn(role="user", text=user_content))
        self.conversation.turns.append(MessageTurn(role="model", text=assistant_content))
        self.conversation.touched_at = time.monotonic()
