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

# Explicit specialist-task patterns. These apply regardless of STRICT_AETHER_TOPIC.
# The goal is to stop Hades from turning into a programming/assignment assistant
# while still allowing casual conversation about those subjects.
SPECIALIST_REQUESTS = (
    re.compile(
        r"\b(?:write|build|make|create|code|debug|fix|program|implement|develop|generate)\b"
        r".{0,80}\b(?:python|javascript|typescript|java|c\+\+|c#|rust|go|golang|ruby|php|sql|regex|html|css|api|script|bot|discord\.py)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:write|do|finish|solve|answer|complete)\b.{0,60}\b"
        r"(?:my|this|the)\b.{0,30}\b(?:homework|assignment|essay|thesis|report|worksheet|exam|test)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:write|draft|rewrite|proofread)\b.{0,50}\b"
        r"(?:email|resume|cv|cover letter|application|formal letter)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:calculate|solve|derive)\b.{0,60}\b"
        r"(?:equation|integral|derivative|matrix|physics problem|chemistry problem|calculus problem)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:fix|troubleshoot|configure|set up)\b.{0,60}\b"
        r"(?:windows|linux|router|printer|network|pc|computer|server|database)\b",
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
