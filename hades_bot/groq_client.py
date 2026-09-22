import asyncio
import logging

from groq import AsyncGroq

from .config import MAX_INPUT_CHARS, REQUEST_TIMEOUT
from .persona import HADES_SYSTEM_PROMPT


logger = logging.getLogger("hades-bot.groq")


class GroqService:
    def __init__(
        self,
        api_key: str,
        model: str,
        max_output_tokens: int,
    ) -> None:
        self.client = AsyncGroq(api_key=api_key)
        self.model = model
        self.max_output_tokens = max_output_tokens

    @staticmethod
    def _normalize_user_message(text: str) -> str:
        text = text.strip()
        if len(text) <= MAX_INPUT_CHARS:
            return text

        cutoff = max(0, MAX_INPUT_CHARS - 80)
        return (
            text[:cutoff].rstrip()
            + "\n\n[Message truncated to keep the conversation manageable.]"
        )

    @classmethod
    def build_messages(cls, history, user_message: str) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": HADES_SYSTEM_PROMPT,
            }
        ]

        for turn in history:
            role = "assistant" if turn.role == "model" else turn.role
            messages.append(
                {
                    "role": role,
                    "content": turn.text,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": cls._normalize_user_message(user_message),
            }
        )

        return messages

    async def generate(self, history, user_message: str) -> str:
        response = await asyncio.wait_for(
            self.client.chat.completions.create(
                model=self.model,
                messages=self.build_messages(history, user_message),
                temperature=0.8,
                max_completion_tokens=self.max_output_tokens,
                stream=False,
            ),
            timeout=REQUEST_TIMEOUT,
        )

        if not response.choices:
            raise RuntimeError("Groq returned no choices.")

        text = (response.choices[0].message.content or "").strip()

        if not text:
            raise RuntimeError("Groq returned an empty response.")

        return text

    @staticmethod
    def _looks_transient(exc: Exception) -> bool:
        message = str(exc).lower()
        transient_terms = (
            "429",
            "rate limit",
            "too many requests",
            "503",
            "502",
            "500",
            "service unavailable",
            "temporarily unavailable",
            "timeout",
            "timed out",
            "connection reset",
            "connection aborted",
            "server disconnected",
        )
        return isinstance(exc, (TimeoutError, asyncio.TimeoutError)) or any(
            term in message for term in transient_terms
        )

    async def generate_with_retry(
        self,
        history,
        user_message: str,
        attempts: int = 3,
    ) -> str:
        last_error: Exception | None = None

        for attempt in range(1, attempts + 1):
            try:
                return await self.generate(history, user_message)
            except Exception as exc:
                last_error = exc

                logger.warning(
                    "Groq request failed (%d/%d): %s",
                    attempt,
                    attempts,
                    exc,
                )

                if attempt >= attempts or not self._looks_transient(exc):
                    break

                await asyncio.sleep(1.5 * (2 ** (attempt - 1)))

        raise RuntimeError("Groq request failed.") from last_error
