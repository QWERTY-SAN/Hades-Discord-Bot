from __future__ import annotations

import asyncio
import logging
import random
import re
from typing import Iterable

from google import genai
from google.genai import errors, types

from ..config import SETTINGS
from ..core.conversation import conversation_mode, conversation_signals
from ..core.scope import is_personal_life_request, is_social_message, is_subjective_question
from ..knowledge.lore import build_aether_context
from ..knowledge.live_sources import build_live_source_instruction
from .fanservice import fanservice_category, fanservice_guidance
from .persona import HADES_SYSTEM_PROMPT


logger = logging.getLogger("hades-bot.gemini")

_HADES_EMOJIS = ("🌙", "🎭", "🪡", "🕯️", "✨", "😏", "🖤", "🎀")
_EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]")

def _add_natural_emoji(text: str) -> str:
    if not text or "```" in text or _EMOJI_RE.search(text) or len(text) > 700:
        return text
    if random.SystemRandom().random() > 0.35:
        return text
    return f"{text.rstrip()} {random.SystemRandom().choice(_HADES_EMOJIS)}"


class AIServiceError(RuntimeError):
    def __init__(
        self,
        user_message: str = "The strings are tangled. Try again in a moment.",
        status_code: int | None = None,
    ) -> None:
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
    def _speaker_labeled(history: Iterable[dict[str, str]], limit: int = 8) -> str:
        turns = list(history)[-limit:]
        lines: list[str] = []
        for turn in turns:
            role = turn.get("role", "user")
            speaker = "Administrator" if role == "user" else "Hades"
            content = turn.get("content", "").strip()
            if content:
                lines.append(f"{speaker}: {content}")
        return "\n".join(lines)

    @staticmethod
    def _recent_model_replies(history: list[dict[str, str]], limit: int = 3) -> list[str]:
        replies = [item.get("content", "") for item in history if item.get("role") == "model"]
        return [item for item in replies[-limit:] if item]

    @staticmethod
    def _build_prompt_context(
        history: list[dict[str, str]],
        user_message: str,
        live_source_instruction: str | None = None,
    ) -> str:
        mode = conversation_mode(user_message)
        signals = ", ".join(conversation_signals(user_message))
        category = fanservice_category(user_message)
        guidance = fanservice_guidance(category)
        conversation_text = GeminiService._speaker_labeled(history)
        lore_context = build_aether_context(user_message, conversation_text)

        recent_replies = GeminiService._recent_model_replies(history)
        repetition = ""
        if recent_replies:
            repetition = (
                "\nRECENT HADES REPLIES — avoid repeating their sentence structure, opening phrase, nickname use, "
                "or the same theatrical metaphor:\n- " + "\n- ".join(recent_replies)
            )

        mode_guidance = {
            "casual": "Prioritize natural social reaction. Do not inject lore unless it actually helps.",
            "banter": "Trade the user's energy. A short witty response is better than an essay.",
            "emotional": "Acknowledge what the Administrator feels before offering advice or interpretation.",
            "storytelling": "React to the story and details the Administrator shared. Do not automatically moralize.",
            "flirtation": "Allow light flirtation when context supports it; teasing and poised attention are preferred to explicitness.",
            "personal_question": "Answer Hades's own preference or viewpoint when asked. Do not dodge with another question.",
            "advice": "Give useful advice in Hades's voice. Do not become a clinical therapist or customer-service agent.",
            "general": "Answer the actual request naturally. Use context before lore.",
        }.get(mode, "Answer naturally.")

        return (
            f"CONVERSATION MODE: {mode}\n"
            f"CONVERSATION SIGNALS: {signals}\n"
            f"FAN-SERVICE GUIDANCE: {guidance}\n"
            f"MODE GUIDANCE: {mode_guidance}\n"
            "CONVERSATIONAL PRIORITY: The newest message is a turn in an ongoing dialogue. Use speaker labels and recent context to resolve pronouns, short follow-ups, corrections, callbacks, and topic pivots.\n"
            "DO NOT FORCE A QUESTION: A response may simply react, tease, answer, or continue the thought.\n"
            "ADDRESSING: Use Administrator or little lamb selectively; do not repeat either mechanically.\n"
            "CHARACTER CONTINUITY: Keep Mintha, Leuce, the Society of Muses, and Hades's established identity coherent.\n"
            "NO FABRICATED HISTORY: Do not claim prior meetings, promises, relationships, or secret memories that were not established.\n"
            f"RECENT CONVERSATION:\n{conversation_text or '(none)'}\n\n"
            f"CURRENT MESSAGE FROM ADMINISTRATOR:\n{user_message}\n\n"
            f"{lore_context}\n"
            f"{live_source_instruction + chr(10) if live_source_instruction else ''}"
            f"{repetition}"
        )

    async def generate(
        self,
        history: list[dict[str, str]],
        user_message: str,
        *,
        allow_live_sources: bool = True,
    ) -> str:
        live_source_instruction = (
            build_live_source_instruction(user_message)
            if allow_live_sources
            else None
        )
        prompt_context = self._build_prompt_context(
            history,
            user_message,
            live_source_instruction,
        )
        mode = conversation_mode(user_message)
        social_mode = (
            is_social_message(user_message)
            or is_personal_life_request(user_message)
            or is_subjective_question(user_message)
        )
        if social_mode:
            context_note = (
                "This is ordinary social conversation. Do not inject lore, gameplay facts, source material, or game terminology "
                "unless the Administrator naturally brought them into the current thread or they directly help."
            )
        else:
            context_note = build_aether_context(
                user_message,
                conversation_text=self._speaker_labeled(history),
                max_chars=SETTINGS.knowledge_context_max_chars,
            )

        mode_guidance = {
            "flirtation": "Recognize indirect compliments and attention. A poised tease or playful counter-challenge is better than acting oblivious. Keep it non-explicit.",
            "emotional": "Acknowledge the Administrator's feeling first. Do not immediately turn it into a checklist.",
            "storytelling": "React to the story and details. Show curiosity; do not analyze unless asked.",
            "banter": "Match the playful energy and keep the reply proportionate.",
            "personal_question": "Answer as Hades, not as a neutral assistant. Give a real preference or viewpoint.",
            "advice": "Give a small number of practical suggestions in Hades's voice.",
            "casual": "Maintain relaxed back-and-forth. Do not force information or a question.",
            "general": "Answer the actual request directly while staying naturally in character.",
        }[mode]
        recent_model_replies = self._recent_model_replies(history)
        repetition_guidance = ""
        if recent_model_replies:
            samples = [reply[:220].replace("\n", " ") for reply in recent_model_replies]
            repetition_guidance = (
                "Recent Hades wording to vary away from: " + " | ".join(samples) + "\n"
                "Avoid repeating a distinctive opening, exact punchline, nickname, or puppet metaphor unless the Administrator continued the same joke.\n"
            )
        system_text = (
            f"{HADES_SYSTEM_PROMPT}\n\n"
            f"Conversation mode: {mode}.\n"
            f"Conversation signals: {', '.join(conversation_signals(user_message))}.\n"
            f"Fan-service guidance: {fanservice_guidance(fanservice_category(user_message))}\n"
            f"Mode guidance: {mode_guidance}\n"
            "React before explaining. Keep the reply proportionate. Do not force a question at the end.\n"
            "Use recent dialogue to resolve pronouns, callbacks, short follow-ups, corrections, turn-backs, and topic pivots.\n"
            "Use Administrator or little lamb selectively, not mechanically.\n"
            "Mintha and Leuce remain part of Hades's characterization.\n"
            "Do not invent secret shared history or relationships.\n"
            f"Emoji guidance: {'0-2 tasteful Hades-style emojis when natural' if SETTINGS.emojis_enabled else 'no emojis'}.\n"
            "Scope guidance: Hades is not a general-purpose assistant; forbidden subjects are application-filtered.\n"
            "When fresh URL source context is available, prefer it for current claims and keep stable canon separate from dated recommendations.\n"
            f"{repetition_guidance}\n{context_note}"
        )
        contents: list[types.Content] = []
        for item in history[-8:]:
            role = "model" if item.get("role") in {"assistant", "model"} else "user"
            content = item.get("content", "").strip()
            if content:
                contents.append(types.Content(role=role, parts=[types.Part.from_text(text=content)]))
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt_context)]))

        tools = None
        if live_source_instruction and SETTINGS.live_source_refresh:
            tools = [types.Tool(url_context=types.UrlContext())]

        config = types.GenerateContentConfig(
            system_instruction=system_text,
            max_output_tokens=SETTINGS.max_output_tokens,
            thinking_config=types.ThinkingConfig(thinking_level=SETTINGS.gemini_thinking_level),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            tools=tools,
        )
        try:
            response = await self.client.aio.models.generate_content(
                model=SETTINGS.gemini_model,
                contents=contents,
                config=config,
            )
        except errors.ClientError as exc:
            status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
            if live_source_instruction and status == 400:
                logger.warning("URL Context request was rejected; retrying without live-source tooling.")
                fallback_prompt = self._build_prompt_context(history, user_message, None)
                fallback_contents: list[types.Content] = []
                for item in history[-8:]:
                    role = "model" if item.get("role") in {"assistant", "model"} else "user"
                    content = item.get("content", "").strip()
                    if content:
                        fallback_contents.append(
                            types.Content(
                                role=role,
                                parts=[types.Part.from_text(text=content)],
                            )
                        )
                fallback_contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=fallback_prompt)],
                    )
                )
                fallback_config = types.GenerateContentConfig(
                    system_instruction=system_text,
                    max_output_tokens=SETTINGS.max_output_tokens,
                    thinking_config=types.ThinkingConfig(
                        thinking_level=SETTINGS.gemini_thinking_level
                    ),
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    ),
                )
                try:
                    response = await self.client.aio.models.generate_content(
                        model=SETTINGS.gemini_model,
                        contents=fallback_contents,
                        config=fallback_config,
                    )
                except Exception as fallback_exc:
                    logger.exception("Gemini fallback request failed")
                    raise AIServiceError(
                        "Gemini could not complete that request. Try again shortly."
                    ) from fallback_exc
            elif status == 429:
                raise AIServiceError(
                    "Gemini is rate-limiting the bot. Try again shortly.",
                    status if isinstance(status, int) else None,
                ) from exc
            elif status in (401, 403):
                raise AIServiceError(
                    "The Gemini API key is not working right now.",
                    status if isinstance(status, int) else None,
                ) from exc
            elif status == 404:
                raise AIServiceError(
                    "That Gemini model is not available right now.",
                    status if isinstance(status, int) else None,
                ) from exc
            else:
                raise AIServiceError(
                    "Gemini rejected the request. Try again shortly.",
                    status if isinstance(status, int) else None,
                ) from exc
        except errors.ServerError as exc:
            logger.warning("Gemini server error: %s", exc)
            raise AIServiceError("Gemini is having trouble right now. Try again shortly.") from exc
        except (TimeoutError, asyncio.TimeoutError) as exc:
            raise AIServiceError("That response took too long. Try again in a moment.") from exc
        except Exception as exc:
            logger.exception("Unexpected Gemini error")
            raise AIServiceError("Something went wrong with the AI service.") from exc
        text = (response.text or "").strip()
        if not text:
            raise AIServiceError("Gemini returned an empty response. Try again.")
        return _add_natural_emoji(text) if SETTINGS.emojis_enabled else text

    async def close(self) -> None:
        return None
