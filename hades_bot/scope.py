from __future__ import annotations

import re
import unicodedata

from .lore import SCOPE_TERMS

HADES_TERMS = {
    "aether gazer",
    "aethergazer",
    "hades",
    "administrator",
    "modifier",
    "society of muses",
    "olympus",
    "gen-zone",
    "gen zone",
    "sigil",
    "functor",
    "mintha",
    "leuce",
    "puppet master",
    "aether code",
    "access key",
    "modification factor",
    "modifier sync",
    "divine grace",
    "chthonic mark",
    "shifted star",
    "shifted stars",
    "shifting flower",
    "shifting flowers",
    "swigs",
    "ain soph coin",
    "zero time",
    "modified mode",
    "modifier sync",
    "warp skill",
    "warp skills",
    "support module",
    "support modules",
    "odin",
    "heimdall",
    "shu",
    "poseidon",
    "tsukuyomi",
    "skuld",
    "gengchen",
    "lingguang",
    "izanami",
    "hera",
}
HADES_TERMS.update(SCOPE_TERMS)

# These are topics Hades must not engage with, even when the user mentions her name.
# The scope gate checks these BEFORE Aether Gazer terms so messages like
# "Hades, what do you think about F1?" are rejected.
OFF_TOPIC_PATTERNS = (
    # F1 / motorsport / sports
    ("sports or motorsport", re.compile(
        r"\b(?:f1|formula\s*(?:1|one)|grand\s*prix|motogp|nascar|indycar|motorsport|racing|"
        r"sports?|football|soccer|basketball|baseball|tennis|golf|hockey|nfl|nba|mlb|nhl|ufc)\b",
        re.I,
    )),
    # Other games / game franchises
    ("other games", re.compile(
        r"\b(?:genshin|honkai|star\s*rail|nikke|valorant|league\s+of\s+legends|minecraft|fortnite|"
        r"elden\s+ring|dark\s+souls|destiny|warframe|wuthering\s+waves|zenless\s+zone\s+zero|zzz)\b",
        re.I,
    )),
    # Programming / computing / IT
    ("programming or technology", re.compile(
        r"\b(?:python|javascript|typescript|java|c\+\+|c#|rust|golang|ruby|php|sql|regex|html|css|"
        r"discord\.py|programming|linux|windows|router|server|database|driver|cpu|gpu|ram|pc|computer|"
        r"network|debugging|software|hardware)\b",
        re.I,
    )),
    # Politics / current events / finance
    ("politics, news, or finance", re.compile(
        r"\b(?:politics?|politician|president|prime\s+minister|election|elections|senate|congress|"
        r"government|political|news|breaking\s+news|stock|stocks|share\s+price|crypto|cryptocurrency|"
        r"bitcoin|ethereum|forex|investment|trading|finance|financial)\b",
        re.I,
    )),
    # Entertainment / celebrities / other media
    ("entertainment or media", re.compile(
        r"\b(?:movie|movies|film|films|tv|television|series|anime|manga|celebrity|actor|actress|"
        r"singer|song|songs|music|band|concert|netflix|youtube|twitch|streamer|influencer)\b",
        re.I,
    )),
    # Generic school / specialist requests
    ("academic or specialist work", re.compile(
        r"\b(?:homework|assignment|thesis|essay|worksheet|exam|test|research\s+paper|resume|cv|cover\s+letter)\b",
        re.I,
    )),
)

SPECIALIST_REQUESTS = (
    re.compile(
        r"\b(?:write|build|make|create|code|debug|fix|program|implement|develop|generate|show|give|provide)\b"
        r".{0,100}\b(?:code|script|program|bot|api|regex|source\s+code|discord\s+bot)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:write|build|make|create|code|debug|fix|program|implement|develop|generate|show|give|provide)\b"
        r".{0,100}\b(?:python|javascript|typescript|java|c\+\+|c#|rust|golang|ruby|php|sql|regex|html|css|"
        r"api|script|source\s+code|code\s+snippet|discord\.py|programming)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:write|do|finish|solve|answer|complete|help\s+with|help\s+me\s+with)\b.{0,80}\b"
        r"(?:my|this|the)\b.{0,50}\b(?:homework|assignment|essay|thesis|report|worksheet|exam|test)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:fix|troubleshoot|configure|set\s+up|diagnose|repair)\b.{0,80}\b"
        r"(?:windows|linux|router|printer|network|pc|computer|server|database|driver)\b",
        re.I | re.S,
    ),
)

# Questions asking for general factual information are not Hades' role.
GENERAL_FACTUAL_QUESTION = re.compile(
    r"^(?:who|what|when|where|why|how|which|tell\s+me\s+about|explain|define|is|are|can|could|do|does|did|should|would|will|have|has|may|might)\b",
    re.I,
)

SOCIAL_PATTERNS = (
    re.compile(r"^(?:hi|hello|hey|hiya|yo|good\s+(?:morning|afternoon|evening|night))[!. ]*$", re.I),
    re.compile(
        r"^(?:how\s+are\s+you|how're\s+you|how\s+do\s+you\s+feel|are\s+you\s+okay|are\s+you\s+tired|"
        r"what(?:'s|\s+is)\s+up|what\s+are\s+you\s+doing|how\s+was\s+your\s+day|did\s+you\s+sleep|"
        r"can\s+we\s+(?:talk|chat)|talk\s+to\s+me|stay\s+with\s+me|tell\s+me\s+about\s+yourself|"
        r"what\s+do\s+you\s+think\s+of\s+me|do\s+you\s+(?:like|trust|remember)\s+me)[?.! ]*$",
        re.I,
    ),
    re.compile(r"^(?:i|i'm|im|i've|ive|my|today\s+i|tonight\s+i)\b.{0,260}$", re.I | re.S),
)


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    value = re.sub(r"[\u200b-\u200d\ufeff]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def forbidden_topic_category(text: str) -> str | None:
    normalized = _normalize(text)
    if not normalized:
        return None
    for category, pattern in OFF_TOPIC_PATTERNS:
        if pattern.search(normalized):
            return category
    return None


def contains_forbidden_topic(text: str) -> bool:
    return forbidden_topic_category(text) is not None


def is_specialist_request(text: str) -> bool:
    normalized = _normalize(text)
    return any(pattern.search(normalized) for pattern in SPECIALIST_REQUESTS)


def is_social_message(text: str) -> bool:
    normalized = _normalize(text)
    return any(pattern.search(normalized) for pattern in SOCIAL_PATTERNS)


def _contains_term(normalized: str, term: str) -> bool:
    if " " in term:
        return term in normalized
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", normalized) is not None


def is_hades_scope_allowed(text: str) -> bool:
    normalized = _normalize(text)
    if not normalized:
        return False
    if forbidden_topic_category(normalized) is not None:
        return False
    if is_specialist_request(normalized):
        return False
    if any(_contains_term(normalized, term) for term in HADES_TERMS):
        return True
    if is_social_message(normalized):
        return True
    if GENERAL_FACTUAL_QUESTION.search(normalized):
        return False
    # Unknown non-social topics are still outside Hades' role.
    return False


def scope_block_reason(text: str) -> str:
    """Return a short internal label used to steer Hades's generated refusal."""
    category = forbidden_topic_category(text)
    if category:
        return category
    if is_specialist_request(text):
        return "programming or specialist work"
    if GENERAL_FACTUAL_QUESTION.search(_normalize(text)):
        return "unrelated factual information"
    return "an unrelated topic"
