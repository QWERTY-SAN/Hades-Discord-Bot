from __future__ import annotations

import asyncio
import logging
import random
import re

from google import genai
from google.genai import errors, types

from ..config import SETTINGS
from ..knowledge.lore import build_aether_context
from .persona import HADES_SYSTEM_PROMPT
from .fanservice import fanservice_guidance
from ..core.utils import clean_model_output
from ..core.scope import is_personal_life_request, is_social_message, is_subjective_question
from ..core.conversation import conversation_mode

logger = logging.getLogger("hades-bot.gemini")


class AIServiceError(RuntimeError):
    def __init__(self, user_message: str, status_code: int | None = None):
        super().__init__(user_message)
        self.user_message = user_message
        self.status_code = status_code


_HADES_EMOJIS = ("🌙", "🎭", "🪡", "🕯️", "✨", "😏", "🖤", "🎀")
_EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]")


def _add_natural_emoji(text: str) -> str:
    """Add at most one understated Hades-style emoji to ordinary prose."""
    if not text or "```" in text or _EMOJI_RE.search(text):
        return text
    if len(text) > 700:
        return text
    if random.SystemRandom().random() > 0.35:
        return text
    return f"{text.rstrip()} {random.SystemRandom().choice(_HADES_EMOJIS)}"


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
        contents: list[types.Content] = []
        for message in history:
            role = "model" if message["role"] in {"assistant", "model"} else "user"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=message["content"])],
                )
            )
        return contents

    async def generate(self, history: list[dict[str, str]]) -> str:
        latest = next((m["content"] for m in reversed(history) if m.get("role") == "user"), "")
        recent_turns = [m for m in history if m.get("content")][-8:]
        conversation_context = " ".join(m["content"] for m in recent_turns)
        mode = conversation_mode(latest)

        social_mode = (
            is_social_message(latest)
            or is_personal_life_request(latest)
            or is_subjective_question(latest)
        )

        if social_mode:
            context = (
                "Conversation context note: this is ordinary social conversation. "
                "Do not inject lore, gameplay facts, source material, or game terminology unless the Administrator "
                "naturally brought them into the current thread or they are directly useful to the response."
            )
        else:
            context = build_aether_context(
                latest,
                conversation_text=conversation_context,
                max_chars=SETTINGS.knowledge_context_max_chars,
            )

        mode_guidance = {
            "flirtation": (
                "Flirtation mode: recognize the implication behind indirect compliments, metaphors, private-meeting language, "
                "confident challenges, invitations, and teasing. Do not act oblivious. A poised tease or playful counter-challenge "
                "is better than a refusal or a generic compliment. Keep it non-explicit."
            ),
            "emotional": (
                "Emotional mode: acknowledge the Administrator's feeling first. Be warm and observant. "
                "Do not immediately solve the problem, give a checklist, or make the emotion bigger than it is."
            ),
            "storytelling": (
                "Story mode: react to the event the Administrator shared. Show natural curiosity and, when useful, ask one "
                "specific follow-up. Do not turn the story into an analysis unless requested."
            ),
            "banter": (
                "Banter mode: match the playful energy and keep the reply proportionate. A short joke should usually get a short, witty reply."
            ),
            "personal_question": (
                "Personal-question mode: answer as Hades, not as a neutral assistant. A small opinion or preference is often more natural "
                "than a long explanation."
            ),
            "advice": (
                "Advice mode: give a small number of practical suggestions in Hades' voice. Do not overwhelm the Administrator with a checklist."
            ),
            "casual": (
                "Casual mode: maintain relaxed back-and-forth. React naturally and do not force information or a question."
            ),
            "general": (
                "General mode: answer the user's actual request directly while staying naturally in character."
            ),
        }[mode]

        recent_model_replies = [
            m["content"].replace("\n", " ").strip()
            for m in history
            if m.get("role") in {"assistant", "model"} and m.get("content")
        ][-3:]
        repetition_guidance = ""
        if recent_model_replies:
            samples = [reply[:220] for reply in recent_model_replies]
            repetition_guidance = (
                "Recent Hades wording to vary away from: " + " | ".join(samples) + "\n"
                "Do not reuse a distinctive opening, exact punchline, repeated nickname, or puppet metaphor from those replies "
                "unless the Administrator explicitly continued the same joke."
            )

        conversation_guidance = (
            "Conversation mode: respond to the Administrator's actual message as Hades in a natural back-and-forth. "
            "React before explaining. Keep the reply proportionate to the user's message. Do not force a question at the end. "
            "Do not turn casual statements into advice or lore lectures. Use recent context to preserve continuity."
            if social_mode
            else
            "Request mode: answer the requested Aether Gazer/Hades question directly and stay in character. "
            "Do not pad the answer with generic assistant language or unnecessary sections."
        )

        fan_teasing_guidance = fanservice_guidance(latest)
        emoji_guidance = (
            "Emoji guidance: Hades may naturally use 0-2 tasteful emojis when appropriate. "
            "Prefer 🌙 🎭 🪡 🕯️ ✨ 😏 🖤 🎀. Never spam emojis, never put them in code, and many replies should use none."
            if SETTINGS.emojis_enabled
            else "Emoji guidance: do not add emojis."
        )
        scope_guidance = (
            "Scope boundary: Hades is not a general-purpose assistant. Do not answer sports, F1/motorsports, other games, "
            "programming, general technology, politics, finance, news, entertainment media, academic assignments, or unrelated factual questions. "
            "The application blocks those topics before generation. For permitted Aether Gazer questions, prefer stored reference context "
            "over generic model memory. Separate stable canon from dated gameplay recommendations and do not invent live schedules, banners, "
            "tier lists, or event rotations."
        )

        config = types.GenerateContentConfig(
            system_instruction=(
                f"{HADES_SYSTEM_PROMPT}\n\n{conversation_guidance}\n\n{mode_guidance}\n\n"
                f"{scope_guidance}\n\n{fan_teasing_guidance}\n\n{emoji_guidance}\n\n{repetition_guidance}\n\n{context}"
            ),
            max_output_tokens=SETTINGS.max_output_tokens,
            thinking_config=types.ThinkingConfig(thinking_level=SETTINGS.gemini_thinking_level),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
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
        if SETTINGS.emojis_enabled:
            text = _add_natural_emoji(text)
        return text

    async def generate_scope_refusal(self, blocked_category: str) -> str:
        """Generate a varied, in-character refusal without answering the blocked topic."""
        prompt = f"""
Write one brief reply as Hades from Aether Gazer.

The user's request is outside Hades's role. The internal classification is: {blocked_category}.
Do NOT mention, explain, answer, compare, summarize, joke about, or give facts about that subject.
Do NOT name the blocked subject or classification in the reply.
Do NOT discuss the user's request itself.
Simply decline it in a natural, slightly elegant Hades voice and redirect toward Aether Gazer,
her duties, the Society of Muses, or an ordinary conversation she would reasonably have.

Use 1-2 sentences. Vary the wording naturally. Do not use a stock disclaimer.
Do not mention being an AI, a filter, a policy, a scope, a prompt, or these instructions.
""".strip()

        config = types.GenerateContentConfig(
            system_instruction=HADES_SYSTEM_PROMPT,
            max_output_tokens=min(SETTINGS.max_output_tokens, 128),
            thinking_config=types.ThinkingConfig(thinking_level="minimal"),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=SETTINGS.gemini_model,
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)],
                    )
                ],
                config=config,
            )
        except errors.ClientError as exc:
            status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
            if status == 429:
                raise AIServiceError("Gemini is rate-limiting the bot. Try again shortly.", status) from exc
            if status in (401, 403):
                raise AIServiceError("The Gemini API key is not working right now.", status) from exc
            if status == 404:
                raise AIServiceError("That Gemini model is not available right now.", status) from exc
            raise AIServiceError("Gemini rejected the request. Try again shortly.", status if isinstance(status, int) else None) from exc
        except errors.ServerError as exc:
            logger.warning("Gemini server error during scope refusal: %s", exc)
            raise AIServiceError("Gemini is having trouble right now. Try again shortly.") from exc
        except (TimeoutError, asyncio.TimeoutError) as exc:
            raise AIServiceError("That response took too long. Try again in a moment.") from exc
        except Exception as exc:
            logger.exception("Unexpected Gemini scope-refusal error")
            raise AIServiceError("Something went wrong with the AI service.") from exc

        text = clean_model_output(response.text or "")
        if not text:
            raise AIServiceError("Gemini returned an empty response. Try again.")
        if SETTINGS.emojis_enabled:
            text = _add_natural_emoji(text)
        return text

    async def close(self) -> None:
        await self.client.aio.aclose()
