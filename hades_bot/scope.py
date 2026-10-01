"""Conversation scope for Hades.

The scope is intentionally conservative:
- Aether Gazer/Hades-related topics are always allowed.
- Casual conversation is allowed, even when the subject is unrelated.
- Unrelated specialist/informational requests are declined.

This is a lightweight heuristic gate. It should never try to be a general
knowledge classifier; the goal is to keep Hades focused without making her
feel incapable of normal conversation.
"""

from __future__ import annotations

import random
import re
import unicodedata

# Strong Aether Gazer / Hades signals. These are deliberately broad enough to
# cover common spelling variants and conversations about the game's cast.
HADES_TERMS = {
    "aether gazer",
    "aethergazer",
    "moda h",
    "hades",
    "administrator",
    "skuld",
    "verthandi",
    "tsukuyomi",
    "buzenbo",
    "lingguang",
    "jinwu",
    "gesh",
    "apollo",
    "poseidon",
    "osiris",
    "shera",
    "thor",
    "artemis",
    "leviathan",
    "selene",
    "ausar",
    "tyr",
    "hel",
    "anubis",
    "sobek",
    "hera",
    "oceanus",
    "modaeus",
    "sigil",
    "modification factor",
    "gen-zone",
    "modifier sync",
}

# Specialized domains that are especially likely to turn Hades into a
# general-purpose assistant if we let factual/how-to questions through.
SPECIALIST_TERMS = {
    # Programming / software engineering
    "python",
    "javascript",
    "typescript",
    "java",
    "c++",
    "c#",
    "rust",
    "golang",
    "ruby",
    "php",
    "sql",
    "html",
    "css",
    "programming",
    "coding",
    "code",
    "script",
    "regex",
    "api",
    "github",
    "git",
    "docker",
    "linux",
    "windows",

    # PC / hardware / electronics
    "cpu",
    "gpu",
    "ram",
    "ssd",
    "nvme",
    "motherboard",
    "processor",
    "graphics card",
    "power supply",
    "psu",
    "driver",
    "bios",
    "uefi",
    "router",
    "ethernet",
    "wifi",
    "hardware",
    "overclock",
    "fl studio",
    "vst",

    # Sports / racing / other specialist hobbies
    "formula 1",
    "f1",
    "motogp",
    "nascar",
    "indycar",
    "nba",
    "nfl",
    "mlb",
    "ufc",
    "premier league",
    "champions league",

    # Academic / technical subjects
    "mathematics",
    "math",
    "calculus",
    "algebra",
    "physics",
    "chemistry",
    "biology",
    "statistics",
    "programming assignment",
    "homework",
    "essay",
    "thesis",
}

# Requests that are inherently task-oriented or factual. These are evaluated
# after casual-conversation patterns so "Do you like F1?" remains allowed.
INFORMATIONAL_PATTERNS = (
    re.compile(r"\bwhat(?:'s| is| are| was| were)\b"),
    re.compile(r"\bwho(?:'s| is| are| was| were)\b"),
    re.compile(r"\bwhen(?: did| was| were| is| are)?\b"),
    re.compile(r"\bwhere(?: is| are| was| were| can| do| does)?\b"),
    re.compile(r"\bwhy(?: is| are| was| were| does| do| did)?\b"),
    re.compile(r"\bhow(?: does| do| did| can| would| to)?\b"),
    re.compile(r"\bexplain\b"),
    re.compile(r"\bcompare\b"),
    re.compile(r"\bwhich (?:is|was|are|were|one|version|model)\b"),
    re.compile(r"\b(?:best|worst|strongest|weakest|dominant|fastest|slowest)\b"),
    re.compile(r"\b(?:write|make|create|build|code|calculate|solve|fix|debug)\b"),
    re.compile(r"\b(?:guide|tutorial|instructions|steps|recommend|recommendation)\b"),
    re.compile(r"\b(?:tell me about|teach me about|help me with)\b"),
)

# Clear signs that someone is simply talking with Hades rather than requesting
# an external fact. This takes precedence over specialist-domain keywords.
CASUAL_PATTERNS = (
    re.compile(r"\bdo you (?:like|love|hate|watch|play|enjoy|know)\b"),
    re.compile(r"\bwhat do you (?:think|feel|prefer|like)\b"),
    re.compile(r"\bwhat(?:'s| is) your (?:favorite|favourite|opinion|take)\b"),
    re.compile(r"\bare you (?:a fan|into|interested)\b"),
    re.compile(r"\bhow (?:are|were) you\b"),
    re.compile(r"\bhow'?s (?:your|it going)\b"),
    re.compile(r"\b(?:good morning|good afternoon|good evening|good night)\b"),
    re.compile(r"^(?:hello|hey|hi|yo|sup)[!.? ]*$"),
    re.compile(r"^(?:thanks|thank you|good job|nice|lol|lmao|bruh|bro)[!.? ]*$"),
)

OFF_TOPIC_RESPONSES = (
    "That isn't really my area, little lamb. 🌙 Stay with Aether Gazer or simply talk to me instead.",
    "You're wandering outside my domain. 🎭 I can chat with you, but that subject isn't mine to handle.",
    "Tsk. That's outside my specialty. 😏 Ask me about Aether Gazer—or just talk to me.",
    "That's not a thread I follow, Administrator. 🕯️ Bring me back to Aether Gazer or ordinary conversation.",
)

_SUMMON_RESPONSE = "Yes, Administrator? 🌙 You have my attention."
_rng = random.SystemRandom()


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    value = re.sub(r"[\u200b-\u200d\ufeff]", "", value)
    value = re.sub(r"[^\w+#'.!?-]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _contains_term(text: str, terms: set[str]) -> bool:
    return any(
        term in text if " " in term else re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text)
        for term in terms
    )


def _matches(patterns: tuple[re.Pattern[str], ...], text: str) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def is_hades_scope_allowed(content: str) -> bool:
    """Return whether Hades should answer the message normally."""
    text = _normalize(content)
    if not text:
        return True

    # Direct Hades / Aether Gazer discussion is always in scope.
    if _contains_term(text, HADES_TERMS):
        return True

    # Friendly conversation is intentionally broad. Mentioning an unrelated
    # hobby is fine when the user is talking *to Hades* rather than asking her
    # to provide specialized information about that hobby.
    if _matches(CASUAL_PATTERNS, text):
        return True

    specialist_topic = _contains_term(text, SPECIALIST_TERMS)
    informational_request = _matches(INFORMATIONAL_PATTERNS, text)

    # Specialized informational requests are outside Hades's role.
    if specialist_topic and informational_request:
        return False

    # Also reject obvious generic knowledge / task requests even when no
    # specialist keyword gives us a domain to latch onto.
    if informational_request:
        return False

    # Statements, banter, reactions, and ordinary conversation remain open.
    return True


def off_topic_response() -> str:
    return _rng.choice(OFF_TOPIC_RESPONSES)


def summon_response() -> str:
    return _SUMMON_RESPONSE
