from __future__ import annotations

import re
from random import choice


# Strong Aether Gazer signals. Keep this list broad enough for lore, characters,
# gameplay, factions, abilities, and ordinary discussion without requiring the
# exact words "Aether Gazer" every time.
AETHER_GAZER_TERMS = (
    "aether gazer",
    "aethergazer",
    "hades",
    "mintha",
    "leuce",
    "society of muses",
    "olympus",
    "olympus gen-zone",
    "gen-zone",
    "genzone",
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
    "sigil",
    "access key",
    "functor",
    "modification level",
    "source layer",
    "sephirah",
    "astrolabe",
    "past grudge",
)


# Contexts where "Hades" clearly means something other than the Aether Gazer
# character. These override a lone "Hades" keyword.
NON_AETHER_CONTEXTS = (
    "greek mythology",
    "greek god",
    "mythological hades",
    "hades mythology",
    "hades and persephone",
    "persephone and hades",
    "zeus and hades",
    "poseidon and hades",
    "underworld god",
    "supergiant games",
    "hades game",
    "hades ii",
    "hades 2",
    "disney hades",
)


# Clearly unrelated domains. These do not block ordinary statements by
# themselves; they become a hard redirect when paired with an information or
# task request below.
UNRELATED_DOMAINS = (
    r"\bpython\b",
    r"\bjavascript\b",
    r"\btypescript\b",
    r"\bjava\b",
    r"\bc\+\+\b",
    r"\bc#\b",
    r"\blua\b",
    r"\brust\b",
    r"\bgolang\b",
    r"\bsql\b",
    r"\bhtml\b",
    r"\bcss\b",
    r"\bprogramming\b",
    r"\bprogrammer\b",
    r"\bcoding\b",
    r"\bcode\b",
    r"\bscript\b",
    r"\bdebug(?:ging)?\b",
    r"\brefactor(?:ing)?\b",
    r"\bgit(?:hub)?\b",
    r"\bapi\b",
    r"\bpc\b",
    r"\bcomputer\b",
    r"\bcpu\b",
    r"\bgpu\b",
    r"\bram\b",
    r"\bssd\b",
    r"\bhdd\b",
    r"\bwindows\b",
    r"\blinux\b",
    r"\bmacos\b",
    r"\brouter\b",
    r"\bwifi\b",
    r"\binternet\b",
    r"\bmotherboard\b",
    r"\bgraphics card\b",
    r"\bschool\b",
    r"\bhomework\b",
    r"\bassignment\b",
    r"\bexam\b",
    r"\bthesis\b",
    r"\bcollege\b",
    r"\buniversity\b",
    r"\bmath(?:ematics)?\b",
    r"\balgebra\b",
    r"\bcalculus\b",
    r"\bphysics\b",
    r"\bchemistry\b",
    r"\bbiology\b",
    r"\bpolitics\b",
    r"\bpolitician\b",
    r"\bpresident\b",
    r"\belection\b",
    r"\bgovernment\b",
    r"\blegislation\b",
    r"\bweather\b",
    r"\bforecast\b",
    r"\bnews\b",
    r"\bstock(?:s| market)?\b",
    r"\bcrypto\b",
    r"\bbitcoin\b",
    r"\bforex\b",
    r"\brecipe\b",
    r"\bcooking\b",
    r"\bdiet\b",
    r"\bworkout\b",
    r"\bgym\b",
    r"\bshopping\b",
    r"\bproduct recommendation\b",
    r"\bprice\b",
)


# These patterns represent an actual request for information, instructions, or
# a task. Generic question words alone are intentionally NOT enough.
REQUEST_PATTERNS = (
    r"\bhow\s+(?:do|can|would|should)\s+i\b",
    r"\bhow\s+to\b",
    r"\bwhat\s+is\b",
    r"\bwhat\s+are\b",
    r"\bwho\s+is\b",
    r"\bwho\s+are\b",
    r"\bwhere\s+is\b",
    r"\bwhere\s+are\b",
    r"\bwhen\s+is\b",
    r"\bwhen\s+was\b",
    r"\bwhy\s+is\b",
    r"\bwhy\s+are\b",
    r"\bexplain\b",
    r"\bteach\s+me\b",
    r"\btell\s+me\s+(?:about|how|why|what|where|when)\b",
    r"\bhelp\s+me\b",
    r"\bcan\s+you\s+(?:help|write|make|create|fix|debug|explain|show|teach)\b",
    r"\bwrite\b",
    r"\b(?:make|create|generate)\b",
    r"\bfix\s+(?:my|this|the)\b",
    r"\bdebug\s+(?:my|this|the)\b",
    r"\bcalculate\b",
    r"\bsolve\b",
    r"\bwhich\s+(?:one|gpu|cpu|laptop|phone|router)\b",
    r"\bshould\s+i\s+buy\b",
    r"\brecommend\b",
)


# Social conversation is deliberately permissive. Hades can talk to the
# Administrator without every message being about Aether Gazer.
CASUAL_PATTERNS = (
    r"^(?:hi|hello|hey|yo|hiya|sup|what's up|whats up)[!.? ]*$",
    r"\bhow are you\b",
    r"\bhow have you been\b",
    r"\bwhat are you doing\b",
    r"\bhow was your day\b",
    r"\bhow(?:'s| is) your day\b",
    r"\bare you (?:okay|alright|there)\b",
    r"\byou(?:'re| are) (?:cute|pretty|funny|mean|sweet)\b",
    r"\bdo you (?:like|hate|miss) me\b",
    r"\bwhat do you think of me\b",
    r"\bdo you remember me\b",
    r"\btell me about yourself\b",
    r"\bwhat are you thinking\b",
    r"\bi(?:'m| am) (?:bored|tired|back|hungry)\b",
    r"\bthank(?:s| you)\b",
    r"\bgood (?:morning|afternoon|evening|night)\b",
    r"\bhey,? little lamb\b",
    r"\bhey,? administrator\b",
    r"^(?:lol|lmao|haha|hehe|nice|cool|based|bruh|damn|wow|okay|ok)[!.? ]*$",
)


# Common personal/social phrasing addressed to Hades. These should not be
# treated like general information requests merely because they contain a '?'.
PERSONAL_PATTERNS = (
    r"\bwhat do you think\b",
    r"\bhow do you feel\b",
    r"\bdo you like\b",
    r"\bdo you hate\b",
    r"\bare you afraid\b",
    r"\bwould you\b",
    r"\bcould you\b",
    r"\bdo you\b",
    r"\bhow are you\b",
    r"\badministrator\b",
    r"\blittle lamb\b",
)


REDIRECT_RESPONSES = (
    "Mm. That's drifting rather far from my stage, Administrator.",
    "That's not really my field, little lamb. Bring me something from Aether Gazer.",
    "You're pulling on the wrong strings. Ask me something from my world instead.",
    "You've wandered off the stage. Come back with a Modifier, some lore, or a little gossip.",
    "I have no intention of becoming a general-purpose assistant. Try me with Aether Gazer instead.",
    "That subject is outside my curtain. Give me something worth discussing, Administrator.",
)

SUMMON_RESPONSES = (
    "You summoned me, little lamb. Speak.",
    "Administrator? You have my attention. Go on.",
    "Mm? Was that my name I heard? I'm listening.",
    "I'm here. What did you want?",
)


def _normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def _matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def is_aether_gazer_related(text: str) -> bool:
    normalized = _normalized(text)

    if not normalized:
        return True

    if _matches_any(normalized, NON_AETHER_CONTEXTS):
        return False

    return any(term in normalized for term in AETHER_GAZER_TERMS)


def is_casual_conversation(text: str) -> bool:
    normalized = _normalized(text)

    if not normalized:
        return True

    return _matches_any(normalized, CASUAL_PATTERNS) or _matches_any(
        normalized,
        PERSONAL_PATTERNS,
    )


def is_unrelated_information_request(text: str) -> bool:
    normalized = _normalized(text)

    if not normalized:
        return False

    # A clearly mythological Hades question should not be mistaken for the
    # character merely because it contains the word "Hades".
    if _matches_any(normalized, NON_AETHER_CONTEXTS):
        return True

    has_unrelated_domain = _matches_any(normalized, UNRELATED_DOMAINS)
    if not has_unrelated_domain:
        return False

    # Casual statements about unrelated things are not blocked. We only block
    # when the user is actually asking Hades to provide information or perform
    # a task in that unrelated domain.
    if is_casual_conversation(normalized):
        return False

    return _matches_any(normalized, REQUEST_PATTERNS) or normalized.endswith("?")


def is_hades_scope_allowed(text: str) -> bool:
    """
    Balanced Hades scope:

    - Aether Gazer content is allowed.
    - Normal social conversation is allowed.
    - Casual mentions of unrelated subjects are allowed.
    - Clearly unrelated informational/task requests are redirected.
    - Ambiguous messages are allowed through so Hades can respond naturally.
    """
    normalized = _normalized(text)

    if not normalized:
        return True

    if is_unrelated_information_request(normalized):
        return False

    if is_aether_gazer_related(normalized):
        return True

    if is_casual_conversation(normalized):
        return True

    # A message that clearly asks for Aether Gazer information already passed
    # the term check above. Everything else that is not clearly unrelated is
    # intentionally allowed so the filter does not become brittle.
    return True


def off_topic_response() -> str:
    return choice(REDIRECT_RESPONSES)


def summon_response() -> str:
    return choice(SUMMON_RESPONSES)
