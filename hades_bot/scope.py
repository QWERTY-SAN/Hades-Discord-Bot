from __future__ import annotations

import random
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

SPECIALIST_REQUESTS = (
    re.compile(r"\b(?:write|build|code|debug|fix|program)\b.*\b(?:python|javascript|typescript|java|c\+\+|rust|sql|api|bot)\b", re.I),
    re.compile(r"\b(?:calculate|solve)\b.*\b(?:equation|integral|derivative|matrix|physics|chemistry)\b", re.I),
)


def is_hades_scope_allowed(text: str) -> bool:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    if any(term in normalized for term in HADES_TERMS):
        return True
    # Ordinary conversation is intentionally allowed. Only clearly explicit
    # specialist-assistant requests can be filtered when strict mode is enabled.
    return not any(pattern.search(normalized) for pattern in SPECIALIST_REQUESTS)


def off_topic_response() -> str:
    return random.choice((
        "You're asking me to perform as a specialist now? How ambitious. I can still talk with you, Administrator, but don't mistake me for a dedicated technical service.",
        "That is rather outside my usual stage. Ask me as Hades, not as a substitute for an entire engineering department.",
        "I can discuss it, little lamb, but I won't pretend to be an all-purpose specialist merely because you asked nicely.",
    ))
