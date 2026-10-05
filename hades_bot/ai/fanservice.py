from __future__ import annotations

import re


FANSERVICE_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "fan_command": (
        re.compile(
            r"\b(?:step\s+on\s+me|dominate\s+me|sit\s+on\s+me|pin\s+me\s+down|"
            r"make\s+me\s+beg|make\s+me\s+ask\s+properly|tell\s+me\s+what\s+to\s+do|"
            r"order\s+me\s+around|boss\s+me\s+around|make\s+me\s+behave)\b",
            re.I,
        ),
    ),
    "romantic": (
        re.compile(
            r"\b(?:marry\s+me|be\s+my\s+wife|be\s+my\s+girlfriend|date\s+me|"
            r"go\s+out\s+with\s+me|i\s+(?:have\s+a\s+crush|am\s+crushing)\s+on\s+you|"
            r"i(?:'m|\s+am)\s+(?:in\s+love|down\s+bad|smitten|head\s+over\s+heels)\s+for\s+you|"
            r"you(?:'re|\s+are)\s+my\s+wife|you(?:'re|\s+are)\s+the\s+one\s+for\s+me)\b",
            re.I,
        ),
    ),
    "affection": (
        re.compile(
            r"\b(?:kiss\s+me|give\s+me\s+a\s+kiss|hug\s+me|cuddle\s+me|hold\s+me|"
            r"hold\s+my\s+hand|pat\s+my\s+head|headpats?|give\s+me\s+attention|"
            r"pay\s+attention\s+to\s+me|look\s+at\s+me|notice\s+me|stay\s+close\s+to\s+me|"
            r"come\s+closer|sit\s+next\s+to\s+me|let\s+me\s+hold\s+you)\b",
            re.I,
        ),
    ),
    "admiration": (
        re.compile(
            r"\b(?:you(?:'re|\s+are)\s+(?:gorgeous|beautiful|pretty|stunning|hot|cute|"
            r"elegant|perfect|amazing|dangerously\s+attractive|ridiculously\s+pretty)|"
            r"you\s+look\s+(?:gorgeous|beautiful|pretty|stunning|hot|cute|amazing)|"
            r"you\s+(?:look|are)\s+like\s+a\s+(?:dream|temptation|snack)|"
            r"i\s+(?:adore|love|worship)\s+you|i(?:'m|\s+am)\s+obsessed\s+with\s+you|"
            r"wife\s+material|my\s+queen|my\s+favorite\s+woman|my\s+gorgeous\s+woman)\b",
            re.I,
        ),
    ),
    "playful_fandom": (
        re.compile(
            r"\b(?:mommy|step\s+on\s+me|please\s+notice\s+me|i\s+need\s+you|"
            r"i\s+want\s+your\s+attention|call\s+me\s+little\s+lamb|"
            r"call\s+me\s+your\s+favorite|let\s+me\s+serve\s+you|make\s+me\s+your\s+puppet|"
            r"keep\s+me\s+with\s+you|make\s+me\s+one\s+of\s+your\s+favorites)\b",
            re.I,
        ),
    ),
    "flirtation": (
        re.compile(
            r"\b(?:somewhere\s+(?:else\s+)?(?:very\s+)?private|"
            r"somewhere\s+private|somewhere\s+quiet|somewhere\s+secluded|"
            r"away\s+from\s+(?:prying|watching)\s+eyes|"
            r"where\s+(?:no\s+one|nobody)\s+can\s+(?:see|hear)\s+us|"
            r"just\s+the\s+two\s+of\s+us|just\s+us|"
            r"behind\s+closed\s+doors|keep\s+this\s+between\s+us|"
            r"no\s+one\s+has\s+to\s+know|out\s+of\s+(?:sight|earshot)|"
            r"when\s+we'?re\s+alone|when\s+no\s+one'?s\s+around|"
            r"after\s+dark|when\s+the\s+others\s+are\s+gone|"
            r"meet\s+me\s+somewhere|come\s+find\s+me|come\s+closer\s+and\s+see|"
            r"closer\s+than\s+that)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:fine|good|gorgeous|beautiful|pretty|stunning|handsome|"
            r"good[- ]looking|fine[- ]looking|dangerously\s+attractive)\s+"
            r"(?:like\s+)?(?:a\s+)?(?:fine\s+)?(?:wine|vintage|dream|snack|temptation)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:aged\s+like\s+(?:fine\s+)?wine|like\s+fine\s+wine|"
            r"fine\s+wine|good\s+enough\s+to\s+tempt\s+me|"
            r"you'?re\s+(?:a\s+)?temptation|you\s+look\s+dangerous|"
            r"you'?re\s+dangerous\s+(?:and\s+)?pretty)\b",
            re.I,
        ),
        re.compile(
            r"(?:not|ain't|am\s+not|i\s+am\s+not)\s+(?:backing|gonna\s+back|going\s+to\s+back)\s+down"
            r".{0,120}\b(?:fine|good|gorgeous|beautiful|pretty|stunning|handsome|"
            r"good[- ]looking|fine[- ]looking|tempting|dangerously\s+attractive)\b",
            re.I | re.S,
        ),
        re.compile(
            r"\b(?:you'?re|you\s+are|ur)\s+(?:fine|good[- ]looking|fine[- ]looking|"
            r"a\s+fine\s+wine|a\s+whole\s+glass\s+of\s+fine\s+wine|"
            r"dangerously\s+attractive|too\s+pretty\s+for\s+my\s+own\s+good)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:don'?t\s+tempt\s+me|are\s+you\s+tempting\s+me|you\s+know\s+what\s+you'?re\s+doing|"
            r"you\s+know\s+exactly\s+what\s+you'?re\s+doing|is\s+that\s+an\s+invitation|"
            r"should\s+i\s+take\s+that\s+as\s+an\s+invitation|are\s+you\s+inviting\s+me|"
            r"you\s+sure\s+you\s+can\s+handle\s+me|can\s+you\s+handle\s+me|"
            r"don'?t\s+look\s+at\s+me\s+like\s+that|stop\s+looking\s+at\s+me\s+like\s+that|"
            r"you'?re\s+making\s+this\s+too\s+easy|you'?re\s+asking\s+for\s+trouble|"
            r"such\s+a\s+tease|quit\s+teasing\s+me)\b",
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
            "Hades may tease their boldness, play coy, challenge them to ask properly, or turn the joke back on them."
        ),
        "romantic": (
            "Treat the user's romantic declaration as light fictional affection. Hades may flirt back, tease them, "
            "or playfully question how serious they are without promising a real-world relationship."
        ),
        "affection": (
            "Treat the user's request for affection as playful in-character fan interaction. "
            "Hades can answer with warmth, a teasing verbal equivalent, a playful challenge, or a coy gesture."
        ),
        "admiration": (
            "The user is admiring Hades. She may accept the compliment with confidence, tease them for being smitten, "
            "or return a light compliment without overreacting."
        ),
        "playful_fandom": (
            "Treat this as exaggerated fan admiration or playful devotion. Hades may indulge the bit with elegant teasing, "
            "a coy challenge, or a playful request that the user behave properly."
        ),
        "flirtation": (
            "The user is being subtly flirtatious, suggestive, or confidently romantic without necessarily stating it directly. "
            "Recognize the implication instead of pretending not to understand it. Hades may tease their intentions, "
            "accept a compliment, challenge their nerve, or reply with restrained flirtation. Private/secret meeting language, "
            "metaphorical compliments, innuendo, invitations, and confident romantic banter count when the wording supports it."
        ),
    }

    return (
        f"Fan-service mode: {category_rules[category]} "
        "Keep it flirtatious, playful, elegant, and non-explicit. Do not describe sexual acts, nudity, anatomy, "
        "or pornography. Do not become a constant flirt outside this kind of message. Vary the wording and stay recognizably Hades."
    )
