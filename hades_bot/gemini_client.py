import asyncio
import logging

from google import genai
from google.genai import types

from .config import REQUEST_TIMEOUT
from .persona import HADES_SYSTEM_PROMPT


logger = logging.getLogger("hades-bot.gemini")


class GeminiService:
    def __init__(
        self,
        api_key: str,
        model: str,
        max_output_tokens: int,
    ) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.max_output_tokens = max_output_tokens

    @staticmethod
    def build_contents(history, user_message: str) -> list[types.Content]:
        contents: list[types.Content] = []

        for turn in history:
            contents.append(
                types.Content(
                    role=turn.role,
                    parts=[types.Part.from_text(text=turn.text)],
                )
            )

        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)],
            )
        )

        return contents

    async def generate(self, history, user_message: str) -> str:
        response = await asyncio.wait_for(
            self.client.aio.models.generate_content(
                model=self.model,
                contents=self.build_contents(history, user_message),
                config=types.GenerateContentConfig(
                    system_instruction=HADES_SYSTEM_PROMPT,
                    max_output_tokens=self.max_output_tokens,
                    thinking_config=types.ThinkingConfig(
                        thinking_level="minimal"
                    ),
                ),
            ),
            timeout=REQUEST_TIMEOUT,
        )

        text = (response.text or "").strip()

        if not text:
            raise RuntimeError("Gemini returned an empty response.")

        return text

    @staticmethod
    def _looks_transient(exc: Exception) -> bool:
        message = str(exc).lower()
        transient_terms = (
            "429",
            "rate limit",
            "resource exhausted",
            "temporarily unavailable",
            "timeout",
            "timed out",
            "503",
            "500",
            "connection reset",
        )
        return isinstance(exc, TimeoutError) or any(
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
                    "Gemini request failed (%d/%d): %s",
                    attempt,
                    attempts,
                    exc,
                )

                if attempt >= attempts or not self._looks_transient(exc):
                    break

                await asyncio.sleep(1.5 * (2 ** (attempt - 1)))

        raise RuntimeError("Gemini request failed.") from last_error
