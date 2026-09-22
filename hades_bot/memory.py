import time
from collections import OrderedDict, deque
from dataclasses import dataclass


@dataclass(slots=True)
class MessageTurn:
    role: str
    text: str


@dataclass(slots=True)
class Conversation:
    turns: deque[MessageTurn]
    touched_at: float


class ConversationMemory:
    def __init__(
        self,
        max_messages: int,
        ttl_seconds: int,
        max_conversations: int,
    ) -> None:
        self.max_messages = max_messages
        self.ttl_seconds = ttl_seconds
        self.max_conversations = max_conversations
        self._conversations: OrderedDict[str, Conversation] = OrderedDict()

    def _expired(self, conversation: Conversation, now: float) -> bool:
        return now - conversation.touched_at >= self.ttl_seconds

    def _prune(self, now: float | None = None) -> None:
        now = time.monotonic() if now is None else now

        expired = [
            key
            for key, conversation in self._conversations.items()
            if self._expired(conversation, now)
        ]

        for key in expired:
            self._conversations.pop(key, None)

        while len(self._conversations) > self.max_conversations:
            self._conversations.popitem(last=False)

    def get(self, key: str) -> deque[MessageTurn]:
        now = time.monotonic()
        self._prune(now)

        conversation = self._conversations.get(key)

        if conversation is None or self._expired(conversation, now):
            conversation = Conversation(
                turns=deque(maxlen=self.max_messages),
                touched_at=now,
            )
            self._conversations[key] = conversation
        else:
            conversation.touched_at = now
            self._conversations.move_to_end(key)

        return conversation.turns

    def add(self, key: str, role: str, text: str) -> None:
        turns = self.get(key)
        turns.append(MessageTurn(role=role, text=text))
        self._conversations[key].touched_at = time.monotonic()
        self._conversations.move_to_end(key)

    def reset(self, key: str) -> None:
        self._conversations.pop(key, None)

    def clear_all(self) -> None:
        self._conversations.clear()

    def conversation_count(self) -> int:
        self._prune()
        return len(self._conversations)

    def message_count(self, key: str) -> int:
        return len(self.get(key))
