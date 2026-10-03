"""Conversation scope for Hades.

Aether Gazer/Hades topics and ordinary conversation are allowed. Programming,
unrelated specialist work, and generic content-production requests are declined
before Gemini is called so Hades cannot accidentally turn into a general-purpose
assistant.
"""
from __future__ import annotations

import random
import re
import unicodedata

from .lore import SCOPE_TERMS

HADES_TERMS = {
    "aether gazer", "aethergazer", "hades", "administrator", "society of muses",
    "puppet master", "mintha", "leuce", "skuld", "verthandi", "tsukuyomi",
    "buzenbo", "lingguang", "jinwu", "gesh", "apollo", "poseidon", "osiris",
    "shera", "thor", "artemis", "leviathan", "selene", "ausar", "tyr", "hel",
    "anubis", "sobek", "hera", "oceanus", "modaeus", "sigil", "functor",
    "modifier", "gen-zone", "gen zone", "access key", "modifier sync",
    "modification factor", "divine grace", "chthonic mark",
}
HADES_TERMS.update(SCOPE_TERMS)

# These are intentionally hard-blocked regardless of STRICT_AETHER_TOPIC.
SPECIALIST_TERMS = {
    "python", "javascript", "typescript", "java", "c++", "c#", "rust", "golang",
    "ruby", "php", "sql", "html", "css", "programming", "coding", "code", "script",
    "regex", "api", "github", "git", "docker", "linux", "windows", "powershell",
    "terminal", "command line", "cpu", "gpu", "ram", "ssd", "nvme", "motherboard",
    "processor", "graphics card", "power supply", "psu", "driver", "bios", "uefi",
    "router", "ethernet", "wifi", "hardware", "overclock", "fl studio", "vst",
    "mathematics", "math", "calculus", "algebra", "physics", "chemistry", "biology",
    "statistics", "homework", "thesis", "assignment", "essay", "debugging", "debug",
}
CONTENT_CREATION_PATTERNS = (
    re.compile(r"\b(?:write|write me|create|generate|make|build|implement|program|code)\b"),
    re.compile(r"\b(?:translate|summarize|proofread|rewrite|draft|compose)\b"),
    re.compile(r"\b(?:tutorial|guide|instructions|step[- ]by[- ]step)\b"),
    re.compile(r"\b(?:solve|calculate|derive|fix|debug|optimize)\b"),
)
INFORMATIONAL_PATTERN = re.compile(
    r"\b(?:what|who|when|where|why|how|explain|compare|which|best|worst|recommend|teach me|help me with)\b"
)
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
    "That's not a performance I'm interested in conducting, little lamb. 🌙",
    "No. I won't turn myself into a technical assistant. 🎭 Talk to me as Hades instead.",
    "You're asking the wrong woman for that sort of work. 😏 Stay with me, Administrator.",
    "I have no desire to become your programmer, tutor, or clerk. 🕯️ Ask me something more fitting.",
)
_rng = random.SystemRandom()


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    value = re.sub(r"[\u200b-\u200d\ufeff]", "", value)
    value = re.sub(r"[^\w+#'.!?-]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _contains_term(text: str, terms: set[str] | frozenset[str]) -> bool:
    for term in terms:
        if " " in term:
            if term in text:
                return True
        elif re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text):
            return True
    return False


def _matches(patterns: tuple[re.Pattern[str], ...], text: str) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def is_hades_scope_allowed(content: str) -> bool:
    text = _normalize(content)
    if not text:
        return True
    if _contains_term(text, HADES_TERMS):
        return True
    if _matches(CASUAL_PATTERNS, text):
        return True
    if _contains_term(text, SPECIALIST_TERMS):
        return False
    if _matches(CONTENT_CREATION_PATTERNS, text):
        return False
    if _matches((INFORMATIONAL_PATTERN,), text):
        return False
    return True


def off_topic_response() -> str:
    return _rng.choice(OFF_TOPIC_RESPONSES)


def summon_response() -> str:
    return _rng.choice((
        "Yes, Administrator? 🌙 You have my attention.",
        "Go on, little lamb. ✨ I'm listening.",
        "You called. 🎭 What is it?",
        "I'm listening, Administrator. 🕯️",
    ))
