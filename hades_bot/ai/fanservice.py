from __future__ import annotations

import re

PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "fan_command": (
        re.compile(r"\b(?:step on me|step on my face|crush me|dominate me|ruin me|destroy me)\b", re.I),
        re.compile(r"\b(?:mommy|my queen|my wife|marry me|adopt me|own me)\b", re.I),
    ),
    "affection": (
        re.compile(r"\b(?:hug(?: me)?|cuddle(?: me)?|hold me|headpat(?: me)?|pat my head|kiss(?: me)?|give me a kiss)\b", re.I),
        re.compile(r"\b(?:love you|i adore you|i love you)\b", re.I),
    ),
    "romantic": (
        re.compile(r"\b(?:date me|take me out|be mine|go out with me|romance me)\b", re.I),
        re.compile(r"\b(?:i want you|i need you|you're mine|my beloved)\b", re.I),
    ),
    "admiration": (
        re.compile(r"\b(?:you're|you are|ur|u r)\s+(?:(?:so|very|really|extremely|incredibly)\s+)?(?:beautiful|pretty|gorgeous|stunning|elegant|graceful|refined|classy|hot|cute|adorable|motherly|maternal)\b", re.I),
        re.compile(r"\b(?:such|so much)\s+(?:elegance|grace|poise|class)\b", re.I),
        re.compile(r"\b(?:you caught my eye|you drew my attention|you have my attention|hard to look away|can't look away|cannot look away)\b", re.I),
        re.compile(r"\b(?:where did|where does)\s+(?:that|your)\s+(?:elegance|grace|maternal|motherly)\b", re.I),
        re.compile(r"\b(?:where did|where does)\s+(?:this|that|your)\s+(?:elegance|grace|maternal|motherly)(?:\s+and\s+(?:elegance|grace|maternal|motherly|maternal\s+traits|motherly\s+traits))?\s+(?:come|come\s+from|originate)\b", re.I),
        re.compile(r"\b(?:elegance|grace|poise)\s+and\s+(?:maternal|motherly)\s+(?:traits|qualities)\b", re.I),
    ),
}


def fanservice_category(text: str) -> str | None:
    for category, patterns in PATTERNS.items():
        if any(pattern.search(text) for pattern in patterns):
            return category
    return None


def fanservice_guidance(category: str | None) -> str:
    if category == "fan_command":
        return (
            "The user is playfully directing admiration toward Hades. Respond with composed, teasing confidence. "
            "Light fan-service is fine, but never become explicit or desperate."
        )
    if category == "affection":
        return (
            "Affection is being offered or requested. Hades may accept it, tease the Administrator, or give a light "
            "affectionate response while remaining in character."
        )
    if category == "romantic":
        return (
            "The user is steering the exchange toward romance. Hades may flirt back lightly, but romance remains "
            "secondary to her composed, intelligent personality. Avoid possessiveness or dependency."
        )
    if category == "admiration":
        return (
            "The user is admiring Hades's appearance, elegance, maternal warmth, or ability to command attention. "
            "Treat it as a character observation first; Hades may tease them for noticing or return a subtle compliment."
        )
    return "No special fan-service mode is required."
