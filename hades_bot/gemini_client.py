import asyncio
import logging

from google import genai
from google.genai import errors, types

from .config import SETTINGS
from .lore import build_aether_context
from .persona import HADES_SYSTEM_PROMPT
from .utils import clean_model_output

logger = logging.getLogger("hades-bot.gemini")


class AIServiceError(RuntimeError):
    def __init__(self, user_message: str, status_code: int | None = None):
        super().__init__(user_message)
        self.user_message = user_message
        self.status_code = status_code


class GeminiService:
    def __init__(self) -> None:
        retry_options = types.HttpRetryOptions(
            attempts=SETTINGS.max_retries + 1,
            initial_delay=1.0,
            max_delay=8.0,
            exp_base=2.0,
            jitter=1.0,
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
    def build_contents(history: list[dict[str, str]]) -> list[types.Content]:
        contents = []
        for message in history:
            role = "model" if message["role"] in {"assistant", "model"} else "user"
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=message["content"])],
            ))
        return contents

    async def generate(self, history: list[dict[str, str]]) -> str:
        latest = next((m["content"] for m in reversed(history) if m.get("role") == "user"), "")
        context = build_aether_context(latest)
        config = types.GenerateContentConfig(
            system_instruction=f"{HADES_SYSTEM_PROMPT}\n\n{context}",
            max_output_tokens=SETTINGS.max_output_tokens,
            thinking_config=types.ThinkingConfig(thinking_level=SETTINGS.gemini_thinking_level),
        )
        try:
            response = await self.client.aio.models.generate_content(
                model=SETTINGS.gemini_model,
                contents=self.build_contents(history),
                config=config,
            )
        except errors.ClientError as exc:
            status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
            if status == 429:
                message = "Gemini is rate-limiting the bot. Try again shortly."
            elif status in (401, 403):
                message = "The Gemini API key is not working right now."
            elif status == 404:
                message = "That Gemini model is not available right now."
            else:
                message = "Gemini rejected the request. Try again shortly."
            raise AIServiceError(message, status if isinstance(status, int) else None) from exc
        except errors.ServerError as exc:
            logger.warning("Gemini server error: %s", exc)
            raise AIServiceError("Gemini is having trouble right now. Try again shortly.") from exc
        except (TimeoutError, asyncio.TimeoutError) as exc:
            raise AIServiceError("That response took too long. Try again in a moment.") from exc
        except Exception as exc:
            logger.exception("Unexpected Gemini error")
            raise AIServiceError("Something went wrong with the AI service.") from exc

        text = clean_model_output(response.text or "")
        if not text:
            raise AIServiceError("Gemini returned an empty response. Try again.")
        return text

    async def close(self) -> None:
        await self.client.aio.aclose()
