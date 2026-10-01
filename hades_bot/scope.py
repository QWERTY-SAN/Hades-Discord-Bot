import re
from random import choice

from .config import STRICT_AETHER_TOPIC


# Aether Gazer topics that should be allowed through to Gemini.
# Keep this broad enough for lore, characters, gameplay, modes, and casual discussion.
AETHER_GAZER_TERMS = (
    "aether gazer",
    "aethergazer",
    "hades",
    "mintha",
    "leuce",
    "society of muses",
    "olympus gen-zone",
    "gen-zone",
    "modifier",
    "modifiers",
    "visbane",
    "visbanes",
    "gaea",
    "thoth",
    "apollo",
    "selene",
    "artemis",
    "hermes",
    "osiris",
    "zeus",
    "athena",
    "ares",
    "hephaestus",
    "odin",
    "skadi",
    "tsukuyomi",
    "buzenbo",
    "zhu rong",
    "lingguang",
    "jin-ei",
    "shinri",
    "vastness",
    "oneiroi",
    "metis",
    "thoth ai",
    "sigil",
    "access key",
    "functor",
    "modification level",
    "recurring dream",
    "hazard zone",
    "dimensional variable",
    "md variable",
    "causality survey",
    "casualty survey",
    "past grudges",
    "iterative testing",
    "hypothetical deduction",
    "battle sweep",
    "flaneuring",
    "warp skill",
    "access key synergy",
    "chip expansion",
    "mimir",
)

# Strong non-Aether requests should always be blocked even if an Aether term is present.
STRONG_UNRELATED_REQUEST_CUES = (
    r"\bwrite\s+(?:me\s+)?(?:some\s+)?(?:code|python|javascript|java|c\+\+|c#|lua|rust|sql|html|css)\b",
    r"\b(?:python|javascript|java|c\+\+|c#|lua|rust|sql|html|css)\s+(?:code|script|program|function|class|bot)\b",
    r"\b(?:debug|refactor|program|programming|coding|code)\b",
    r"\b(?:pc|computer|cpu|gpu|ram|ssd|hdd|windows|linux|macos|router|wifi|internet)\b",
    r"\b(?:school|homework|assignment|exam|thesis|college|university|coursework)\b",
    r"\b(?:math|mathematics|algebra|calculus|physics|chemistry|biology)\b",
    r"\b(?:politics|politician|president|election|government|law|legislation)\b",
    r"\b(?:weather|forecast|news|stock|stocks|crypto|bitcoin|forex)\b",
    r"\b(?:recipe|cooking|diet|workout|gym)\b",
    r"\b(?:buy|shopping|price|product recommendation|recommend a laptop|recommend a phone)\b",
)

# Generic assistant wording is only considered off-topic when there is no Aether Gazer
# signal. This fixes legitimate questions such as "how do I clear Recurring Dream?".
GENERAL_ASSISTANT_CUES = (
    r"\b(?:what is|how do i|how can i|can you explain|teach me|help me with)\b",
)

CASUAL_PATTERNS = (
    r"^(?:hi|hello|hey|yo|hiya|sup|what's up|whats up)[!.? ]*$",
    r"\bhow are you\b",
    r"\bhow have you been\b",
    r"\bwhat are you doing\b",
    r"\bhow was your day\b",
    r"\bhow(?:s| is) your day\b",
    r"\byou there\b",
    r"\bmiss(?:ed)? you\b",
    r"\bi (?:like|love|hate) you\b",
    r"\byou(?:'re| are) (?:cute|pretty|funny|mean)\b",
    r"^(?:lol|lmao|haha|hehe|nice|cool|based|bruh|damn)[!.? ]*$",
    r"\bthank(?:s| you)\b",
    r"\bgood (?:morning|afternoon|evening|night)\b",
    r"\bwhat do you think of me\b",
    r"\bdo you like me\b",
    r"\bdo you remember me\b",
    r"\bhey,? little lamb\b",
    r"\btell me about yourself\b",
)

# Mythology-specific uses of "Hades" should not accidentally count as Aether Gazer.
MYTHOLOGY_CUES = (
    "greek mythology",
    "greek god",
    "underworld god",
    "underworld",
    "zeus and hades",
    "poseidon and hades",
    "pluto",
    "mythological hades",
)

REDIRECT_RESPONSES = (
    "You're pulling on the wrong strings, Administrator. I won't turn my stage into a guidebook for that. Ask me about Aether Gazer.",
    "Mm. That's outside my little stage, Administrator. Bring me something from Aether Gazer and I'll pay attention.",
    "No, little lamb. I have no interest in becoming a general-purpose answer machine. Ask me about Aether Gazer instead.",
    "That subject has nothing to do with my stage. Try again with Aether Gazer, the Society of Muses, or something properly interesting.",
    "You're wandering off the script. I handle Aether Gazer here. Come back with a Modifier, a mission, some lore, or a little gossip.",
    "Those strings aren't mine to pull. Keep the conversation in Aether Gazer territory, Administrator.",
    "Tempting. Still no. This stage is for Aether Gazer, not every problem you've managed to collect.",
)

SUMMON_RESPONSES = (
    "You summoned me, little lamb. Speak.",
    "Administrator? You have my attention. Go on.",
    "Mm? Was that my name I heard, or are you simply testing the strings?",
    "I'm here. Now, what did you want?",
)


def _normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def _matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def _contains_term(text: str, term: str) -> bool:
    if " " in term:
        return term in text
    return re.search(rf"\b{re.escape(term)}\b", text) is not None


def is_aether_gazer_related(text: str) -> bool:
    normalized = _normalized(text)
    if any(cue in normalized for cue in MYTHOLOGY_CUES):
        return False
    return any(_contains_term(normalized, term) for term in AETHER_GAZER_TERMS)


def is_casual_conversation(text: str) -> bool:
    normalized = _normalized(text)
    if not normalized:
        return True
    return _matches_any(normalized, CASUAL_PATTERNS)


def is_explicitly_unrelated_request(text: str) -> bool:
    normalized = _normalized(text)
    if _matches_any(normalized, STRONG_UNRELATED_REQUEST_CUES):
        return True
    if is_aether_gazer_related(normalized):
        return False
    return _matches_any(normalized, GENERAL_ASSISTANT_CUES)


def is_hades_scope_allowed(text: str) -> bool:
    """Return True for Aether Gazer discussion or ordinary social conversation."""
    if not STRICT_AETHER_TOPIC:
        return True
    if is_explicitly_unrelated_request(text):
        return False
    if is_casual_conversation(text):
        return True
    return is_aether_gazer_related(text)


def off_topic_response() -> str:
    return choice(REDIRECT_RESPONSES)


def summon_response() -> str:
    return choice(SUMMON_RESPONSES)
