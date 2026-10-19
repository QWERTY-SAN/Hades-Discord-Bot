from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any

from ...config import SETTINGS
from .gemini import GeminiProvider
from .groq import GroqProvider


logger = logging.getLogger("hades-bot.ai.router")


class ProviderChainError(RuntimeError):
    """Raised when all configured AI providers fail to produce a response."""

    def __init__(
        self,
        user_message: str,
        status_code: int | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(user_message)
        self.user_message = user_message
        self.status_code = status_code
        self.cause = cause


class AIProviderRouter:
    """Runs each provider independently in priority order and tracks failover metrics."""

    def __init__(self) -> None:
        self.gemini_provider = GeminiProvider()
        self.groq_provider = GroqProvider()
        self.last_successful_model: str | None = None
        self.fallback_count = 0
        self.groq_fallback_count = 0

    def model_hierarchy(self) -> tuple[str, ...]:
        """Return only the Google model IDs in their configured order."""
        return tuple(dict.fromkeys(
            model.strip()
            for model in (SETTINGS.gemini_model, *SETTINGS.gemini_fallback_models)
            if model and model.strip()
        ))

    def provider_chain(self) -> tuple[str, ...]:
        """Return all configured attempts, including the distinct Groq provider."""
        return (*self.model_hierarchy(), f"groq:{SETTINGS.groq_model}")

    @staticmethod
    def _status_code(exc: Exception) -> int | None:
        return GeminiProvider.status_code(exc)

    async def generate(
        self,
        *,
        contents: list[Any],
        config: Any,
        fallback_contents: list[Any] | None = None,
        fallback_config: Any | None = None,
    ) -> Any:
        models = self.model_hierarchy()
        failures: list[Exception] = []
        failure_statuses: list[int | None] = []

        for index, model in enumerate(models):
            try:
                response = await self.gemini_provider.generate(
                    model=model,
                    contents=contents,
                    config=config,
                    fallback_contents=fallback_contents,
                    fallback_config=fallback_config,
                )
                response_text = getattr(response, "text", None)
                if not isinstance(response_text, str) or not response_text.strip():
                    raise RuntimeError(f"Gemini model {model} returned an empty response.")
            except Exception as exc:
                status = self._status_code(exc)
                failures.append(exc)
                failure_statuses.append(status)

                # Both Gemini models use the same key, so an auth error is not
                # recoverable by repeating the request with Gemini 3.1.
                if status in {401, 403}:
                    logger.warning(
                        "Gemini credentials were rejected (%s); switching directly to Groq.",
                        status,
                    )
                    break

                if GeminiProvider.can_fail_over(exc):
                    error_kind = status or type(exc).__name__
                else:
                    error_kind = f"non-retryable {status or type(exc).__name__}"

                if index + 1 < len(models):
                    logger.warning(
                        "Gemini model %s failed (%s); trying %s.",
                        model,
                        error_kind,
                        models[index + 1],
                    )
                else:
                    logger.warning(
                        "Gemini model %s failed (%s); proceeding to Groq.",
                        model,
                        error_kind,
                    )
            else:
                if model != SETTINGS.gemini_model:
                    self.fallback_count += 1
                    logger.warning(
                        "Gemini fallback succeeded: primary=%s selected=%s",
                        SETTINGS.gemini_model,
                        model,
                    )
                self.last_successful_model = model
                return response

        last_error = failures[-1] if failures else None
        last_status = failure_statuses[-1] if failure_statuses else None
        groq_error: Exception | None = None

        # Gemini URL Context is not available in Groq. If this request had a
        # tool-enabled prompt, use the alternate prompt without the source instruction.
        groq_contents = fallback_contents if fallback_contents is not None else contents
        try:
            response_text = await self.groq_provider.generate(
                model=SETTINGS.groq_model,
                contents=groq_contents,
                system_instruction=getattr(config, "system_instruction", None),
                max_tokens=SETTINGS.max_output_tokens,
                timeout_seconds=min(
                    SETTINGS.request_timeout,
                    SETTINGS.gemini_model_timeout_seconds,
                ),
            )
            self.groq_fallback_count += 1
            self.last_successful_model = f"groq:{SETTINGS.groq_model}"
            logger.warning(
                "Groq fallback succeeded after Gemini failure: model=%s",
                SETTINGS.groq_model,
            )
            return SimpleNamespace(text=response_text)
        except Exception as exc:
            groq_error = exc
            logger.warning("Groq fallback failed: %s", type(exc).__name__)
            groq_status = self._status_code(exc)
            if groq_status is not None:
                last_status = groq_status

        if failure_statuses and all(status == 404 for status in failure_statuses):
            message = (
                "The configured Gemini models were not found and Groq could not respond. "
                "Check the model names, API keys, and provider availability."
            )
        elif 429 in failure_statuses or last_status == 429:
            message = "The configured AI providers are rate-limiting requests. Try again shortly."
        else:
            message = "All configured AI providers are temporarily unavailable. Try again shortly."
        cause = groq_error or last_error
        raise ProviderChainError(message, last_status, cause) from cause

    async def close(self) -> None:
        """Close both SDK clients without leaving one open if the other fails."""
        for name, provider in (
            ("Gemini", self.gemini_provider),
            ("Groq", self.groq_provider),
        ):
            try:
                await provider.close()
            except Exception as exc:
                logger.warning("%s client close failed: %s", name, type(exc).__name__)
