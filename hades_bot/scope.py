from __future__ import annotations

import re
import unicodedata

from .lore import SCOPE_TERMS

HADES_TERMS = {
    "aether gazer", "aethergazer", "hades", "administrator", "modifier",
    "society of muses", "olympus", "gen-zone", "sigil", "functor",
    "mintha", "leuce", "puppet master", "aether code", "access key",
    "modification factor", "modifier sync", "divine grace", "chthonic mark",
}
HADES_TERMS.update(SCOPE_TERMS)

# Hades is a character, not a programming/technical/academic assistant.
# These guards are deliberately narrow enough to allow ordinary conversation
# about computers, games, school, math, etc. while stopping explicit requests
# to make her perform specialist work.
SPECIALIST_REQUESTS = (
    re.compile(
        r"\b(?:write|build|make|create|code|debug|fix|program|implement|develop|generate|show|give|provide)\b"
        r".{0,100}\b(?:python|javascript|typescript|java|c\+\+|c#|rust|golang|ruby|php|sql|regex|html|css|api|script|source code|code snippet|discord\.py|programming)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:python|javascript|typescript|java|c\+\+|c#|rust|golang|ruby|php|sql|discord\.py)\b"
        r".{0,100}\b(?:code|script|function|class|program|bot|debug|fix|implement|snippet)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:write|do|finish|solve|answer|complete|help with|help me with)\b.{0,80}\b"
        r"(?:my|this|the)\b.{0,50}\b(?:homework|assignment|essay|thesis|report|worksheet|exam|test)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:write|draft|rewrite|proofread|compose)\b.{0,70}\b"
        r"(?:email|resume|cv|cover letter|application|formal letter)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:calculate|solve|derive|work out)\b.{0,80}\b"
        r"(?:equation|integral|derivative|matrix|physics problem|chemistry problem|calculus problem)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:fix|troubleshoot|configure|set up|diagnose|repair)\b.{0,80}\b"
        r"(?:windows|linux|router|printer|network|pc|computer|server|database|driver)\b",
        re.I | re.S,
    ),
)


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    value = re.sub(r"[\u200b-\u200d\ufeff]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def is_specialist_request(text: str) -> bool:
    normalized = _normalize(text)
    return any(pattern.search(normalized) for pattern in SPECIALIST_REQUESTS)


def is_hades_scope_allowed(text: str) -> bool:
    normalized = _normalize(text)
    if any(term in normalized for term in HADES_TERMS):
        return True
    return not is_specialist_request(normalized)


def off_topic_response() -> str:
    return (
        "You're asking me to perform as a specialist now? How ambitious. "
        "I'm Hades, not an entire engineering department. Ask me something I might actually enjoy discussing."
    )
