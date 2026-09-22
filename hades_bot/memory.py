from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque


@dataclass
class MessageTurn:
    role: str
    text: str


class ConversationMemory:
    def __init__(self, max_messages: int) -> None:
        self.max_messages = max_messages
        self._histories: dict[str, Deque[MessageTurn]] = defaultdict(
            lambda: deque(maxlen=self.max_messages)
        )

    def get(self, key: str) -> Deque[MessageTurn]:
        return self._histories[key]

    def add(self, key: str, role: str, text: str) -> None:
        self._histories[key].append(
            MessageTurn(role=role, text=text)
        )

    def reset(self, key: str) -> None:
        self._histories.pop(key, None)

    def clear_all(self) -> None:
        self._histories.clear()
