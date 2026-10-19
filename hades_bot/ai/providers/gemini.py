from __future__ import annotations

import asyncio
import logging
from typing import Any

from google import genai
from google.genai import errors, types

from ...config import SETTINGS


logger = logging.getLogger("hades-bot.ai.providers.gemini")


class GeminiProvider:
    """Google Gemini transport shared by the configured Gemini model IDs."""

    def __init__(self) -> None:
        retry_options = types.HttpRetryOptions(
            attempts=max(1, min(2, SETTINGS.max_retries + 1)),
            initial_delay=0.5,
            max_delay=2.0,
            exp_base=2.0,
            jitter=0.5,
            http_status_codes=[408, 429, 500, 502, 503, 504],
        )
        self.client = genai.Client(
            api_key=SETTINGS.gemini_api_key,
            http_options=types.HttpOptions(
                timeout=int(SETTINGS.request_timeout * 1000),
                retry_options=retry_options,
            ),
        )

    @staticmethod
    def status_code(exc: Exception) -> int | None:
        value = getattr(exc, "status_code", None)
        if value is None:
            value = getattr(exc, "code", None)
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def can_fail_over(cls, exc: Exception) -> bool:
        status = cls.status_code(exc)
        return (
            isinstance(exc, (errors.ServerError, asyncio.TimeoutError, TimeoutError))
            or status in {404, 408, 429, 500, 502, 503, 504}
        )

    async def _generate_once(
        self,
        *,
        model: str,
        contents: list[types.Content],
        config: types.GenerateContentConfig,
    ) -> Any:
        timeout = min(SETTINGS.request_timeout, SETTINGS.gemini_model_timeout_seconds)
        return await asyncio.wait_for(
            self.client.aio.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            ),
            timeout=timeout,
        )

    async def generate(
        self,
        *,
        model: str,
        contents: list[types.Content],
        config: types.GenerateContentConfig,
        fallback_contents: list[types.Content] | None = None,
        fallback_config: types.GenerateContentConfig | None = None,
    ) -> Any:
        """Generate with one specific Gemini model, retrying without URL Context if needed."""
        try:
            return await self._generate_once(
                model=model,
                contents=contents,
                config=config,
            )
        except errors.ClientError as exc:
            if (
                self.status_code(exc) == 400
                and fallback_contents is not None
                and fallback_config is not None
            ):
                logger.warning(
                    "Gemini rejected URL Context on model %s; retrying that model without tools.",
                    model,
                )
                return await self._generate_once(
                    model=model,
                    contents=fallback_contents,
                    config=fallback_config,
                )
            raise

    async def close(self) -> None:
        await self.client.aio.aclose()
