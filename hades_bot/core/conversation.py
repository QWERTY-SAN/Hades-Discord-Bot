from __future__ import annotations

import re

from ..ai.fanservice import fanservice_category
from .scope import (
    is_personal_life_request,
    is_social_message,
    is_subjective_question,
)


EMOTIONAL_PATTERNS = (
    re.compile(
        r"\b(?:i(?:'m|\s+am)|i\s+feel)\s+(?:so\s+)?(?:sad|happy|angry|mad|annoyed|pissed|upset|"
        r"tired|exhausted|lonely|bored|excited|nervous|anxious|embarrassed|overwhelmed|proud|"
        r"disappointed|confused|stressed|frustrated|drained|sleepy|restless|hurt)\b", re.I
    ),
    re.compile(
        r"\b(?:rough\s+day|bad\s+day|good\s+day|long\s+day|i\s+need\s+to\s+vent|"
        r"i\s+need\s+someone\s+to\s+talk\s+to|i\s+feel\s+like\s+crap|i\s+feel\s+awful|"
        r"i\s+feel\s+great|i\s+can't\s+sleep|i\s+cannot\s+sleep)\b", re.I
    ),
)

STORY_PATTERNS = (
    re.compile(
        r"^(?:so\s+today|today\s+i|earlier\s+i|yesterday\s+i|last\s+night\s+i|"
        r"guess\s+what|you\s+won'?t\s+believe|you\s+know\s+what\s+happened|"
        r"i\s+just\s+(?:got|came|saw|watched|met|bought|found|heard|did|finished|"
        r"received|started|ended)|i\s+have\s+to\s+tell\s+you|i\s+need\s+to\s+tell\s+you)\b", re.I
    ),
)

BANter_PATTERNS = (
    re.compile(
        r"^(?:lol|lmao|haha|hehe|rofl|bruh|oof|welp|yikes|wow|damn|nice|cool|cute|"
        r"seriously\??|really\??|no\s+way|you'?re\s+funny|that'?s\s+(?:wild|crazy|funny|rough|cute|sweet|interesting|weird)|"
        r"that\s+was\s+(?:wild|crazy|funny|rough|cute|sweet|interesting|weird))\b", re.I
    ),
    re.compile(r"\b(?:you\s+know\s+me|look\s+at\s+you|there\s+you\s+go|oh\s+really|is\s+that\s+so)\??$", re.I),
)


def conversation_mode(text: str) -> str:
    """Return a lightweight mode hint for the generation prompt."""
    if fanservice_category(text) is not None:
        return "flirtation"
    if is_personal_life_request(text):
        return "advice"
    if is_subjective_question(text):
        return "personal_question"
    if any(pattern.search(text) for pattern in EMOTIONAL_PATTERNS):
        return "emotional"
    if any(pattern.search(text) for pattern in STORY_PATTERNS):
        return "storytelling"
    if any(pattern.search(text) for pattern in BANter_PATTERNS):
        return "banter"
    if is_social_message(text):
        return "casual"
    return "general"
