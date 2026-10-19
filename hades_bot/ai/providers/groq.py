from __future__ import annotations

import asyncio
from typing import Any

from groq import AsyncGroq

from ...config import SETTINGS


class GroqProvider:
    """Groq's OpenAI-compatible API adapter; returns plain response text."""

    def __init__(self) -> None:
        self.client = AsyncGroq(
            api_key=SETTINGS.groq_api_key,
            timeout=SETTINGS.request_timeout,
            max_retries=1,
        )

    @staticmethod
    def to_messages(
        *,
        contents: list[Any],
        system_instruction: str | None,
    ) -> list[dict[str, str]]:
        messages = [{"role": "system", "content": system_instruction or ""}]
        for item in contents:
            role = "assistant" if getattr(item, "role", "user") == "model" else "user"
            body = "\n".join(
                part.text
                for part in (getattr(item, "parts", None) or [])
                if getattr(part, "text", None)
            ).strip()
            if body:
                messages.append({"role": role, "content": body})
        return messages

    async def generate(
        self,
        *,
        model: str,
        contents: list[Any],
        system_instruction: str | None,
        max_tokens: int,
        timeout_seconds: float,
    ) -> str:
        """Call one Groq model and fail explicitly if it returns no usable text."""
        response = await asyncio.wait_for(
            self.client.chat.completions.create(
                model=model,
                messages=self.to_messages(
                    contents=contents,
                    system_instruction=system_instruction,
                ),
                max_tokens=max_tokens,
                temperature=0.8,
            ),
            timeout=timeout_seconds,
        )
        text = (
            response.choices[0].message.content
            if response.choices
            else None
        )
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError(f"Groq model {model} returned an empty response.")
        return text.strip()

    async def close(self) -> None:
        await self.client.close()
