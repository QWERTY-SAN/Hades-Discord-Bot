from __future__ import annotations

import re

FANSERVICE_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "fan_command": (
        re.compile(
            r"\b(?:step\s+on\s+me|dominate\s+me|sit\s+on\s+me|pin\s+me\s+down|"
            r"make\s+me\s+beg|make\s+me\s+ask\s+properly|make\s+me\s+your\s+puppet|"
            r"turn\s+me\s+into\s+your\s+puppet|pull\s+my\s+strings|make\s+me\s+kneel|"
            r"have\s+me\s+kneel)\b",
            re.I,
        ),
    ),
    "romantic": (
        re.compile(
            r"\b(?:marry\s+me|be\s+my\s+wife|be\s+my\s+girlfriend|date\s+me|"
            r"go\s+out\s+with\s+me|i\s+(?:have\s+a\s+crush|am\s+crushing)\s+on\s+you|"
            r"i(?:'m|\s+am)\s+(?:in\s+love|down\s+bad)\s+for\s+you|you(?:'re|\s+are)\s+my\s+wife)\b",
            re.I,
        ),
    ),
    "affection": (
        re.compile(
            r"\b(?:kiss\s+me|give\s+me\s+a\s+kiss|hug\s+me|cuddle\s+me|hold\s+me|"
            r"hold\s+my\s+hand|pat\s+my\s+head|headpats?|give\s+me\s+attention|"
            r"pay\s+attention\s+to\s+me|look\s+at\s+me|notice\s+me)\b",
            re.I,
        ),
    ),
    "admiration": (
        re.compile(
            r"\b(?:you(?:'re|\s+are)\s+(?:gorgeous|beautiful|pretty|stunning|hot|cute|"
            r"elegant|perfect|amazing)|you\s+look\s+(?:gorgeous|beautiful|pretty|stunning|hot|cute)|"
            r"i\s+(?:adore|love|worship)\s+you|i(?:'m|\s+am)\s+obsessed\s+with\s+you|"
            r"wife\s+material|my\s+queen|my\s+favorite\s+woman)\b",
            re.I,
        ),
    ),
    "playful_fandom": (
        re.compile(
            r"\b(?:mommy|step\s+on\s+me|crush\s+me|please\s+notice\s+me|i\s+need\s+you|"
            r"i\s+want\s+your\s+attention|call\s+me\s+little\s+lamb|"
            r"call\s+me\s+your\s+favorite|let\s+me\s+serve\s+you|i(?:'m|\s+am)\s+your\s+puppet|"
            r"i(?:'ll|\s+will)\s+be\s+your\s+puppet|make\s+me\s+your\s+puppet|"
            r"your\s+little\s+lamb|your\s+puppet)\b",
            re.I,
        ),
    ),
}


def fanservice_category(text: str) -> str | None:
    value = text.casefold()
    for category, patterns in FANSERVICE_PATTERNS.items():
        if any(pattern.search(value) for pattern in patterns):
            return category
    return None


def is_fanservice_message(text: str) -> bool:
    return fanservice_category(text) is not None


def fanservice_guidance(text: str) -> str:
    category = fanservice_category(text)
    if category is None:
        return "No special fan-service behavior is required. Keep Hades conversational and in character."

    category_rules = {
        "fan_command": (
            "Treat the user's exaggerated request as playful fan teasing rather than a literal command. "
            "Hades may tease their boldness, call them a little lamb, challenge them to ask properly, "
            "or playfully frame them as a prospective puppet."
        ),
        "romantic": (
            "Treat the user's romantic declaration as light fandom affection. Hades may flirt back, tease them, "
            "or playfully question how serious they are without making promises of a real-world relationship."
        ),
        "affection": (
            "Treat the user's request for affection as playful in-character fan interaction. "
            "Hades can answer with a teasing verbal equivalent, a playful challenge, or warm banter."
        ),
        "admiration": (
            "The user is admiring Hades. She may accept the compliment with confidence, tease them for being smitten, "
            "or return a light compliment."
        ),
        "playful_fandom": (
            "Treat this as exaggerated fan admiration or playful devotion. Hades may indulge the bit with elegant teasing, "
            "a coy challenge, a playful reminder that she makes the strings, or a request that the user behave properly."
        ),
    }

    return (
        f"Fan-service mode: {category_rules[category]} "
        "Keep it flirtatious, playful, and non-explicit. Do not describe sexual acts, nudity, anatomy, or pornography. "
        "Do not become a constant flirt outside this kind of message. Vary the wording and stay recognizably Hades."
    )
