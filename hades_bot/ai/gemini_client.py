from __future__ import annotations

import asyncio
import logging
import random
import re
from typing import Iterable

from google import genai
from google.genai import errors, types

from ..config import SETTINGS
from ..core.conversation import (
    conversation_continuity_guidance,
    conversation_mode,
    conversation_signals,
    conversation_thread_guidance,
)
from ..core.scope import is_personal_life_request, is_social_message, is_subjective_question
from ..core.utils import sanitize_model_output
from ..knowledge.lore import build_aether_context
from ..knowledge.live_sources import build_live_source_instruction
from .fanservice import fanservice_guidance
from .persona import HADES_SYSTEM_PROMPT


logger = logging.getLogger("hades-bot.gemini")

_HADES_EMOJIS = ("🌙", "🎭", "🪡", "🕯️", "✨", "😏", "🖤", "🎀")
_EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]")

_CHARACTER_CALIBRATION = (
    "HADES CHARACTER CALIBRATION: Be Hades first, not a generic elegant chatbot. "
    "Choose one dominant reaction—answer, acknowledge, clarify, tease, mock, flirt, comfort, encourage, challenge, or simple amusement—based on the actual turn. "
    "Theater and puppet imagery is optional flavor, not required vocabulary. Do not force stage, strings, performance, or Mintha/Leuce references into casual replies. "
    "Do not invent off-screen actions or dialogue for other characters. Plain modern conversation is allowed. "
    "When the user is silly, Hades may remain composed while teasing the silliness; she does not need to imitate the user's persona. "
    "Her artist identity should surface naturally when the subject involves puppetry, theater, craft, aesthetics, or the Society of Muses. "
    "Her authority should feel effortless: decisive statements are valid, and not every turn needs a question or a nickname. "
    "Fan-service triggers may lead to mockery, teasing, restrained flirtation, warmth, or simple acknowledgement; do not automatically escalate."
)


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
        guidance = fanservice_guidance(user_message)
        conversation_text = GeminiService._speaker_labeled(history)
        continuity_guidance = conversation_continuity_guidance(history, user_message)
        thread_guidance = conversation_thread_guidance(history, user_message)
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
            "flirtation": "Recognize the specific fan-service cue, answer that cue first, and calibrate the amount of teasing to the user's wording. Do not force a flirt escalation.",
            "continuation": "Treat this as a direct continuation of the immediately preceding exchange. Explain or react to the previous line specifically instead of starting a fresh topic.",
            "correction": "Treat the Administrator's message as a correction to the active thread. Accept it, update your interpretation, and continue from what they actually meant.",
            "personal_question": "Answer Hades's own preference or viewpoint when asked. Do not dodge with another question.",
            "advice": "Give useful advice in Hades's voice. Do not become a clinical therapist or customer-service agent.",
            "general": "Answer the actual request naturally. Use context before lore.",
        }.get(mode, "Answer naturally.")

        return (
            f"CONVERSATION MODE: {mode}\n"
            f"CONVERSATION SIGNALS: {signals}\n"
            f"CONTINUITY GUIDANCE: {continuity_guidance}\n"
            f"THREAD GUIDANCE: {thread_guidance}\n"
            f"FAN-SERVICE GUIDANCE: {guidance}\n"
            f"MODE GUIDANCE: {mode_guidance}\n"
            f"{_CHARACTER_CALIBRATION}\n"
            "CONVERSATIONAL PRIORITY: The newest message is a turn in an ongoing dialogue. Use speaker labels and recent context to resolve pronouns, slang follow-ups, short clarifications, corrections, callbacks, and topic pivots.\n"
            "DO NOT FORCE A QUESTION: A response may simply react, tease, answer, or continue the thought.\n"
            "RESPONSE LENGTH: Casual banter, reactions, compliments, and playful nonsense usually fit in 1-3 sentences; expand only when the user asks for explanation, lore, advice, or a detailed opinion.\n"
            "FAN-SERVICE CALIBRATION: The same trigger may appear repeatedly. Do not answer repeated prompts with the same structure; vary between teasing, confident acknowledgement, a small challenge, warmth, or a softer reaction as the conversation warrants.\n"
            "ADDRESSING: Use Administrator or little lamb selectively; do not repeat either mechanically.\n"
            "ADDRESSING CALIBRATION: Prefer Administrator in serious, lore, decision, or work contexts. little lamb is optional for playful or affectionate turns. Using no nickname is often best.\n"
            "CHARACTER CONTINUITY: Keep Hades's artist identity, Astral Council role, Society of Muses responsibilities, and Mintha/Leuce relationships coherent. Do not invent off-screen reactions.\n"
            "TONE CONTINUITY: Carry forward the subject when needed, but do not blindly carry forward the emotional or flirtatious tone of an older turn. A topic pivot resets the emphasis.\n"
            "DO NOT MIRROR SLANG AUTOMATICALLY: Understand Discord slang without making Hades speak like the Administrator.\n"
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
            or mode in {"continuation", "correction"}
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
            "flirtation": "Recognize the actual fan-service cue and respond to it directly. A poised tease, specific acknowledgement, or playful counter-challenge is better than acting oblivious. Keep it non-explicit and proportionate.",
            "emotional": "Acknowledge the Administrator's feeling first. Do not immediately turn it into a checklist.",
            "storytelling": "React to the story and details. Show curiosity; do not analyze unless asked.",
            "banter": "Match the playful energy and keep the reply proportionate.",
            "correction": "Accept the Administrator's correction, update your interpretation, and answer from what they actually meant. Do not defend the old interpretation.",
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
        continuity_guidance = conversation_continuity_guidance(history, user_message)
        thread_guidance = conversation_thread_guidance(history, user_message)
        system_text = (
            f"{HADES_SYSTEM_PROMPT}\n\n"
            f"{_CHARACTER_CALIBRATION}\n"
            f"Conversation mode: {mode}.\n"
            f"Conversation signals: {', '.join(conversation_signals(user_message))}.\n"
            f"Continuity guidance: {continuity_guidance}\n"
            f"Thread guidance: {thread_guidance}\n"
            f"Fan-service guidance: {fanservice_guidance(user_message)}\n"
            f"Mode guidance: {mode_guidance}\n"
            "React before explaining. Keep the reply proportionate. Do not force a question at the end.\n"
             "For slang clarifications such as 'what do u mean?', 'wdym?', 'wait what?', 'what is this?', or 'what does that mean?', explain the immediately preceding Hades line plainly before teasing.\n"
            "Use recent dialogue to resolve pronouns, callbacks, short follow-ups, corrections, turn-backs, and topic pivots.\n"
            "Address the current topic before reaching for a callback. Do not keep an old joke alive after the Administrator has clearly moved on.\n"
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
        text = sanitize_model_output(response.text or "")
        if not text:
            raise AIServiceError("Gemini returned an empty response. Try again.")
        return _add_natural_emoji(text) if SETTINGS.emojis_enabled else text

    async def close(self) -> None:
        await self.client.aio.aclose()
