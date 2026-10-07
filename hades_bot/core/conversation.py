from __future__ import annotations

import re
import unicodedata

from ..ai.fanservice import fanservice_categories, fanservice_intensity
from .scope import is_personal_life_request, is_reaction_message, is_social_message, is_subjective_question

EMOTIONAL_PATTERNS = (
    re.compile(r"\b(?:i(?:'m| am)|i feel)\s+(?:so\s+)?(?:sad|happy|angry|mad|annoyed|pissed|upset|tired|exhausted|lonely|bored|excited|nervous|anxious|embarrassed|overwhelmed|proud|disappointed|confused|stressed|frustrated|drained|sleepy|restless|hurt)\b", re.I),
    re.compile(r"\b(?:rough day|bad day|good day|long day|i need to vent|i need someone to talk to|i feel like crap|i feel awful|i feel great|i can't sleep|i cannot sleep)\b", re.I),
)
STORY_PATTERNS = (
    re.compile(r"^(?:so today|today i|earlier i|yesterday i|last night i|guess what|you won't believe|you know what happened|i just (?:got|came|saw|watched|met|bought|found|heard|did|finished|received|started|ended)|i have to tell you|i need to tell you)\b", re.I),
)
BANTER_PATTERNS = (
    re.compile(r"^(?:lol|lmao|haha|hehe|rofl|bruh|oof|welp|yikes|wow|damn|nice|cool|ayoo+|owo|uwu|whoa+|woah+|seriously\??|really\??|no way|you're funny|that's (?:wild|crazy|funny|rough|cute|sweet|interesting|weird))\b", re.I),
    re.compile(r"\b(?:look at you|there you go|oh really|is that so)\??$", re.I),
    re.compile(r"^(?:(?:woof|arf|awoo|meow|mew|nya|rawr)(?:[\s.!?]*(?:woof|arf|awoo|meow|mew|nya|rawr)){0,5})[\s.!?]*$", re.I),
)
SHORT_FOLLOWUPS = frozenset({
    "why", "why?", "really", "really?", "how so", "how so?", "go on", "go on.",
    "and then", "and then?", "what about her", "what about her?", "what about him", "what about him?",
    "what about that", "what about that?", "and you", "and you?", "you too", "you too?", "same",
    "same.", "fair enough", "fair enough.", "no way", "no way!", "tell me more", "continue",
    "continue?", "what do you mean", "what do you mean?", "how come", "how come?", "your turn",
    "your turn?", "really then", "prove it", "prove it?", "what then", "what then?",
    "wait, what", "wait what", "huh", "huh?", "seriously", "seriously?",
    "like what", "like what?", "what else", "what else?", "what now", "what now?",
    "and", "and?", "so what", "so what?",
    "for real", "for real?", "okay then", "okay then?", "go ahead", "go ahead?",
    "what do u mean", "what do u mean?", "what u mean", "what u mean?", "wdym", "wdym?",
    "wait what do u mean", "wait what do u mean?", "what did you mean", "what did you mean?",
})
CORRECTION_PREFIXES = re.compile(r"^(?:no[, ]|nah[, ]|wait[, ]|not exactly[, ]|that's not what i meant[, ]|i meant[, ]|actually[, ]|correction[, ]|wrong[, ])", re.I)
TURN_BACK_PATTERNS = (
    re.compile(r"\b(?:and you|what about you|how about you|your take|your opinion|your thoughts|what do you like|do you like)\b", re.I),
)
TOPIC_PIVOT_PATTERNS = (
    re.compile(r"^(?:anyway|anyways|speaking of that|on another note|by the way|btw|unrelated|changing the subject)\b", re.I),
)


def conversation_mode(text: str) -> str:
    if fanservice_categories(text):
        return "flirtation"
    if is_short_followup(text):
        return "continuation"
    if is_personal_life_request(text):
        return "advice"
    if is_subjective_question(text):
        return "personal_question"
    if any(pattern.search(text) for pattern in EMOTIONAL_PATTERNS):
        return "emotional"
    if any(pattern.search(text) for pattern in STORY_PATTERNS):
        return "storytelling"
    if is_reaction_message(text):
        return "banter"
    if any(pattern.search(text) for pattern in BANTER_PATTERNS):
        return "banter"
    if is_social_message(text):
        return "casual"
    return "general"


def is_short_followup(text: str) -> bool:
    normalized = unicodedata.normalize("NFKC", text or "").casefold()
    normalized = re.sub(r"[\u200b-\u200d\ufeff]", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized.strip())
    return normalized in SHORT_FOLLOWUPS


def conversation_continuity_guidance(history: list[dict[str, str]], user_message: str) -> str:
    """Explain how a short follow-up should inherit the active conversational thread."""
    if not history or not is_short_followup(user_message):
        return "No special continuity handoff is needed."

    previous_user = next((item.get("content", "").strip() for item in reversed(history) if item.get("role") == "user" and item.get("content")), "")
    previous_hades = next((item.get("content", "").strip() for item in reversed(history) if item.get("role") in {"assistant", "model"} and item.get("content")), "")

    parts = [
        "CURRENT TURN IS A FOLLOW-UP: interpret the current short message as part of the immediately preceding exchange, not as a new standalone topic."
    ]
    if previous_user:
        parts.append(f"Previous Administrator message: {previous_user[:500]}")
        categories = fanservice_categories(previous_user)
        if categories:
            parts.append(f"The active social/fan-service thread was: {', '.join(categories)}.")
    if previous_hades:
        parts.append(f"Previous Hades reply: {previous_hades[:700]}")
    if re.match(r"^(?:what do|what did|what u|wdym|wait what|huh)\b", user_message.strip(), re.I):
        parts.append("CLARIFICATION RULE: explain what Hades meant in the immediately preceding reply before adding any tease. Do not repeat the old line verbatim.")
    return " ".join(parts)


def conversation_signals(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.strip())
    signals: list[str] = []
    categories = fanservice_categories(normalized)
    if categories:
        signals.append("fanservice:" + ",".join(categories[:4]))
        signals.append("fanservice_intensity:" + fanservice_intensity(normalized))
    if is_short_followup(normalized):
        signals.append("continuation")
    if CORRECTION_PREFIXES.search(normalized):
        signals.append("correction")
    if any(pattern.search(normalized) for pattern in TURN_BACK_PATTERNS):
        signals.append("turn_back")
    if any(pattern.search(normalized) for pattern in TOPIC_PIVOT_PATTERNS):
        signals.append("topic_pivot")
    if re.search(r"\b(?:finally|i did it|we did it|got it|got them|got her|got him|pulled|won|cleared|finished|completed)\b", normalized, re.I):
        signals.append("achievement")
    if re.search(r"\b(?:rough day|bad day|i feel awful|i feel like crap|i need comfort|comfort me|reassure me|i'm overwhelmed|i am overwhelmed)\b", normalized, re.I):
        signals.append("needs_comfort")
    if re.search(r"[?？！]\s*$", normalized):
        signals.append("question")
    if re.search(r"!!+$|\b(?:lmao|lol|haha|hehe)\b", normalized, re.I):
        signals.append("high_energy")
    if re.search(r"\b(?:thanks|thank you|ty|thx)\b", normalized, re.I):
        signals.append("gratitude")
    if re.search(r"\b(?:sorry|my bad|apologies)\b", normalized, re.I):
        signals.append("apology")
    if re.search(r"(?:\.\.\.|…)$", normalized):
        signals.append("hesitation")
    return signals or ["none"]
