from __future__ import annotations

import re
import unicodedata

from ..knowledge.lore import SCOPE_TERMS

HADES_TERMS = {
    "aether gazer", "aethergazer", "hades", "administrator", "modifier",
    "society of muses", "olympus", "gen-zone", "gen zone", "sigil", "functor",
    "mintha", "leuce", "puppet master", "aether code", "access key",
    "modification factor", "modifier sync", "divine grace", "chthonic mark",
    "shifted star", "shifted stars", "shifting flower", "shifting flowers", "swigs",
    "ain soph coin", "zero time", "modified mode", "warp skill", "warp skills",
    "support module", "support modules", "odin", "heimdall", "shu", "poseidon",
    "tsukuyomi", "skuld", "gengchen", "lingguang", "izanami", "hera",
    "recurring dream", "hazard zone", "dimensional variable", "iterative testing",
    "past grudges", "causality survey", "ancient shadow", "crisis analysis",
    "m.e.o.w.", "meow", "mijir", "micoco", "mitir", "me-yow", "mininja",
    "opponent intel", "risk level i", "risk level ii", "risk level iii",
    "sigil enchant", "sigil enchants", "transcendence", "transcend", "ultimate skillchain",
    "gacha", "f2p", "free-to-play", "free to play", "low spender", "dolphin", "whale", "spender", "spending",
    "battle sweep", "flaneuring", "music dossier", "heart link", "access key synergy",
    "gaea", "gaea.zero", "gaea zero", "idealbild", "source layer", "surface layer",
    "visbane", "visbanes", "bane energy", "corrosion", "quakes", "ain soph",
    "neuhansa", "shashvat", "omorfies", "xu heng", "sasanami", "division nine",
    "corg supreme directorate", "olympia express", "spealght industries", "children of iron",
    "akkadian guild", "stellaris academy", "astral council", "knights of convallaria",
    "izuru family", "miyahebi family", "karasugo family", "meruism", "tian lu traders", "quad",
}
HADES_TERMS.update(SCOPE_TERMS)

HARD_OFF_TOPIC_PATTERNS = (
    ("F1 or motorsport", re.compile(
        r"\b(?:f1|formula\s*(?:1|one)|motogp|nascar|indycar|motorsport|grand\s*prix)\b", re.I)),
    ("other sports", re.compile(
        r"\b(?:sports?|football|soccer|basketball|baseball|tennis|golf|hockey|nfl|nba|mlb|nhl|ufc)\b", re.I)),
    ("other games", re.compile(
        r"\b(?:genshin|honkai|star\s*rail|nikke|valorant|league\s+of\s+legends|minecraft|fortnite|elden\s+ring|dark\s+souls|destiny|warframe|wuthering\s+waves|zenless\s+zone\s+zero|zzz)\b", re.I)),
    ("programming or technology", re.compile(
        r"\b(?:python|javascript|typescript|java|c\+\+|c#|rust|golang|ruby|php|sql|regex|html|css|discord\.py|programming|linux|windows|router|server|database|driver|cpu|gpu|ram|pc|computer|network|debugging|software|hardware)\b", re.I)),
    ("politics, news, or finance", re.compile(
        r"\b(?:politics?|politician|president|prime\s+minister|election|elections|senate|congress|government|political|breaking\s+news|stock|stocks|share\s+price|crypto|cryptocurrency|bitcoin|ethereum|forex|investment|trading|finance|financial)\b", re.I)),
)

CONTEXTUAL_OFF_TOPIC_PATTERNS = (
    ("unrelated entertainment or media", re.compile(
        r"\b(?:movie|movies|film|films|tv|television|series|anime|manga|celebrity|actor|actress|singer|song|songs|band|concert|netflix|youtube|twitch|streamer|influencer|music)\b", re.I)),
    ("unrelated racing", re.compile(r"\b(?:racing|race)\b", re.I)),
)

SPECIALIST_REQUESTS = (
    re.compile(
        r"\b(?:write|build|make|create|code|debug|fix|program|implement|develop|generate|show|give|provide)\b"
        r".{0,100}\b(?:code|script|program|bot|api|regex|source\s+code|discord\s+bot)\b", re.I | re.S),
    re.compile(
        r"\b(?:write|build|make|create|code|debug|fix|program|implement|develop|generate|show|give|provide)\b"
        r".{0,100}\b(?:python|javascript|typescript|java|c\+\+|c#|rust|golang|ruby|php|sql|regex|html|css|api|script|source\s+code|code\s+snippet|discord\.py|programming)\b", re.I | re.S),
    re.compile(
        r"\b(?:write|do|finish|solve|answer|complete|help\s+with|help\s+me\s+with)\b.{0,80}\b(?:my|this|the)\b.{0,50}\b(?:homework|assignment|essay|thesis|report|worksheet|exam|test)\b", re.I | re.S),
    re.compile(
        r"\b(?:fix|troubleshoot|configure|set\s+up|diagnose|repair)\b.{0,80}\b(?:windows|linux|router|printer|network|pc|computer|server|database|driver)\b", re.I | re.S),
)

GENERAL_FACTUAL_QUESTION = re.compile(
    r"^(?:who|what|when|where|why|how|which|tell\s+me\s+about|explain|define|is|are|can|could|do|does|did|should|would|will|have|has|may|might)\b",
    re.I,
)

# Ordinary conversation is intentionally broad, but is still bounded by the
# hard off-topic filters above. These patterns cover greetings, feelings,
# preferences, day-to-day chat, playful banter, and conversational requests.
SOCIAL_PATTERNS = (
    re.compile(r"^(?:hi|hello|hey|hiya|yo|sup|good\s+(?:morning|afternoon|evening|night))[!. ]*$", re.I),
    re.compile(
        r"^(?:how\s+are\s+you|how're\s+you|how\s+do\s+you\s+feel|are\s+you\s+okay|are\s+you\s+tired|"
        r"what(?:'s|\s+is)\s+up|what\s+are\s+you\s+doing|how\s+was\s+your\s+day|did\s+you\s+sleep|"
        r"can\s+we\s+(?:talk|chat)|talk\s+to\s+me|stay\s+with\s+me|tell\s+me\s+about\s+yourself|"
        r"what\s+do\s+you\s+think\s+of\s+me|do\s+you\s+(?:like|trust|remember)\s+me|"
        r"what(?:'s|\s+is)\s+your\s+(?:favorite|favourite)|what\s+do\s+you\s+(?:like|enjoy|prefer)|"
        r"do\s+you\s+(?:like|enjoy|prefer)|would\s+you\s+rather|want\s+to\s+(?:talk|chat)|"
        r"are\s+you\s+(?:bored|busy|lonely|happy|sad|curious|sleepy)|"
        r"what\s+have\s+you\s+been\s+doing)[?.! ]*$", re.I),
    re.compile(
        r"^(?:guess\s+what|look\s+at\s+this|listen|you\s+know\s+what|i\s+have\s+something\s+to\s+tell\s+you|"
        r"want\s+to\s+hear\s+something|let's\s+(?:talk|chat)|let\s+us\s+(?:talk|chat)|"
        r"tell\s+me\s+something|say\s+something|make\s+me\s+smile|cheer\s+me\s+up|"
        r"i'?m\s+(?:bored|tired|sad|happy|lonely|excited|upset|fine|okay|back)|"
        r"i\s+(?:miss|like|love|hate|need|want|feel|think|guess|remember)\b).{0,500}$", re.I | re.S),
    re.compile(r"^(?:lol|lmao|haha|hehe|nice|cool|cute|damn|wow|ugh|hmm+|oh+|seriously\??)[!. ]*$", re.I),
    re.compile(r"^(?:i|i'm|im|i've|ive|my|today\s+i|tonight\s+i|this\s+is|that\s+was)\b.{0,500}$", re.I | re.S),
)

SUBJECTIVE_QUESTION = re.compile(
    r"^(?:what\s+do\s+you\s+(?:think|like|prefer|want|feel)|what(?:'s|\s+is)\s+your\s+(?:favorite|favourite)|"
    r"do\s+you\s+(?:like|enjoy|prefer|want|remember|mind|care|agree)|would\s+you\s+rather|"
    r"how\s+do\s+you\s+feel|are\s+you\s+(?:okay|tired|happy|sad|bored|busy|lonely))\b", re.I)


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    value = re.sub(r"[\u200b-\u200d\ufeff]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def _contains_term(normalized: str, term: str) -> bool:
    if " " in term or any(ch in term for ch in ".+-"):
        return term in normalized
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", normalized) is not None


def has_aether_context(text: str) -> bool:
    normalized = _normalize(text)
    meaningful = HADES_TERMS - {"hades", "administrator"}
    return any(_contains_term(normalized, term) for term in meaningful)


def forbidden_topic_category(text: str) -> str | None:
    normalized = _normalize(text)
    if not normalized:
        return None
    for category, pattern in HARD_OFF_TOPIC_PATTERNS:
        if pattern.search(normalized):
            return category
    aether_context = has_aether_context(normalized)
    if not aether_context:
        for category, pattern in CONTEXTUAL_OFF_TOPIC_PATTERNS:
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


def is_subjective_question(text: str) -> bool:
    normalized = _normalize(text)
    return bool(SUBJECTIVE_QUESTION.search(normalized))


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
    if is_social_message(normalized) or is_subjective_question(normalized):
        return True
    return False


def scope_block_reason(text: str) -> str:
    category = forbidden_topic_category(text)
    if category:
        return category
    if is_specialist_request(text):
        return "programming or specialist work"
    if GENERAL_FACTUAL_QUESTION.search(_normalize(text)):
        return "unrelated factual information"
    return "an unrelated topic"
