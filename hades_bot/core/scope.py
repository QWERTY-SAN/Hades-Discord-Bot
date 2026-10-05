from __future__ import annotations

import re
import unicodedata

from ..knowledge.lore import SCOPE_TERMS
from ..ai.fanservice import is_fanservice_message

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
# hard off-topic filters above. These patterns cover greetings, short replies,
# feelings, preferences, day-to-day chat, playful banter, and conversational requests.
SOCIAL_PATTERNS = (
    re.compile(
        r"^(?:so\s+today|today\s+i|earlier\s+i|yesterday\s+i|last\s+night\s+i|"
        r"guess\s+what|you\s+won'?t\s+believe|you\s+know\s+what\s+happened|"
        r"i\s+just\s+(?:got|came|saw|watched|met|bought|found|heard|did|finished|"
        r"received|started|ended)|i\s+have\s+to\s+tell\s+you|i\s+need\s+to\s+tell\s+you)\b", re.I
    ),
    re.compile(
        r"^(?:hi|hello|hey|hiya|yo|sup|morning|evening|night|good\s+(?:morning|afternoon|evening|night)|"
        r"welcome\s+back|good\s+to\s+see\s+you|nice\s+to\s+see\s+you|long\s+time\s+no\s+see)[!. ]*$", re.I),
    re.compile(
        r"^(?:thanks?|thank\s+you|thx|ty|you're\s+welcome|youre\s+welcome|no\s+worries|my\s+bad|sorry|"
        r"good\s+luck|same|same\s+here|me\s+too|me\s+neither|you\s+too|exactly|true|fair|"
        r"fair\s+enough|makes\s+sense|that\s+makes\s+sense|for\s+real|fr|ngl|tbh|right|"
        r"no\s+way|really\??|seriously\??|of\s+course|sure|okay|ok|alright|fine|yep|yes|yeah|yup|"
        r"nope|nah|maybe|perhaps)[!. ]*$", re.I),
    re.compile(
        r"^(?:how\s+are\s+you|how're\s+you|how\s+do\s+you\s+feel|are\s+you\s+(?:okay|good|tired|busy|bored|happy|sad|lonely|curious|sleepy)|"
        r"what(?:'s|\s+is)\s+up|what\s+are\s+you\s+doing|what\s+about\s+you|how\s+about\s+you|and\s+you\??|"
        r"how\s+was\s+your\s+day|did\s+you\s+sleep|did\s+you\s+rest|what\s+have\s+you\s+been\s+doing|"
        r"can\s+we\s+(?:talk|chat)|talk\s+to\s+me|stay\s+with\s+me|keep\s+me\s+company|"
        r"tell\s+me\s+about\s+yourself|tell\s+me\s+something|say\s+something|"
        r"what\s+do\s+you\s+think\s+of\s+me|do\s+you\s+(?:like|trust|remember|miss)\s+me|"
        r"what(?:'s|\s+is)\s+your\s+(?:favorite|favourite)|what\s+do\s+you\s+(?:like|enjoy|prefer)|"
        r"do\s+you\s+(?:like|enjoy|prefer)|would\s+you\s+rather|want\s+to\s+(?:talk|chat))[?.! ]*$", re.I),
    re.compile(
        r"^(?:guess\s+what|look\s+at\s+this|listen|you\s+know\s+what|you\s+know|"
        r"i\s+have\s+something\s+to\s+tell\s+you|want\s+to\s+hear\s+something|"
        r"let's\s+(?:talk|chat)|let\s+us\s+(?:talk|chat)|make\s+me\s+smile|cheer\s+me\s+up|"
        r"i'?m\s+(?:bored|tired|sad|happy|lonely|excited|upset|fine|okay|back|home|sleepy)|"
        r"i\s+(?:just\s+got\s+home|just\s+woke\s+up|just\s+got\s+back|miss|missed|like|love|hate|need|want|"
        r"feel|think|guess|remember)\b).{0,700}$", re.I | re.S),
    re.compile(
        r"^(?:that's|thats|this\s+is|this\s+was|that\s+is|that\s+was|it(?:'s|\s+is)|it\s+was|"
        r"sounds\s+(?:like|good|fun|nice|rough|wild|crazy|interesting)|looks\s+(?:like|good|fun|nice|rough|wild|crazy|interesting)|"
        r"seems\s+(?:like|good|fun|nice|rough|wild|crazy|interesting))\b.{0,700}$", re.I | re.S),
    re.compile(
        r"^(?:lol|lmao|haha|hehe|nice|cool|cute|damn|wow|ugh|oof|welp|bruh|based|real|"
        r"hmm+|oh+|ah+|yikes|whoa+|wow+|phew|that's|thats|this\s+is|that\s+was|"
        r"you'?re\s+funny|you\s+know|oh\s+really|is\s+that\s+so)(?:[!. ]|$).{0,300}$", re.I | re.S),
    # Normal first-person statements are conversation too. Specialist/off-topic
    # checks still run first, so this never overrides a hard block.
    re.compile(
        r"^(?:i|i'm|im|i've|ive|my|mine|today\s+i|tonight\s+i|this\s+is|that\s+was|"
        r"just|currently|honestly|literally)\b.{0,700}$", re.I | re.S),
)

PERSONAL_LIFE_PATTERNS = (
    re.compile(
        r"^(?:what\s+should\s+i\s+do|what\s+can\s+i\s+do|what\s+could\s+i\s+do|"
        r"what\s+else\s+(?:can|should)\s+i\s+do|what\s+should\s+we\s+do|what\s+can\s+we\s+do|"
        r"what\s+do\s+you\s+suggest\s+i\s+do|how\s+should\s+i\s+spend\s+(?:my\s+time|my\s+day|my\s+evening|my\s+night)|"
        r"give\s+me\s+(?:something|an\s+idea)\s+to\s+do|give\s+me\s+an?\s+idea|"
        r"pick\s+something\s+for\s+me|choose\s+something\s+for\s+me|surprise\s+me|"
        r"help\s+me\s+decide\s+(?:what\s+to\s+do|what\s+i\s+should\s+do)|"
        r"i\s+(?:don't|do\s+not)\s+know\s+what\s+to\s+do|i\s+have\s+nothing\s+to\s+do|"
        r"anything\s+else)(?:\s+(?:tonight|today|right\s+now|this\s+(?:morning|afternoon|evening|weekend)|tomorrow|for\s+fun|when\s+i'?m\s+bored))?[?.! ]*$", re.I),
    re.compile(
        r"^(?:should\s+i\s+.+\s+or\s+.+|which\s+one\s+should\s+i\s+(?:pick|choose)|"
        r"do\s+you\s+think\s+i\s+should\s+.+|what\s+would\s+you\s+do)[?.! ]*$", re.I | re.S),
)

SUBJECTIVE_QUESTION = re.compile(
    r"^(?:what\s+do\s+you\s+(?:think|like|prefer|want|feel)|what(?:'s|\s+is)\s+your\s+(?:favorite|favourite)|"
    r"do\s+you\s+(?:like|enjoy|prefer|want|remember|mind|care|agree)|would\s+you\s+rather|"
    r"how(?:'re|\s+are)\s+you(?:\s+doing|\s+holding\s+up)?|how\s+do\s+you\s+feel|"
    r"are\s+you\s+(?:okay|tired|happy|sad|bored|busy|lonely))\b", re.I)


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


def is_personal_life_request(text: str) -> bool:
    normalized = _normalize(text)
    return any(pattern.search(normalized) for pattern in PERSONAL_LIFE_PATTERNS)


def is_social_message(text: str) -> bool:
    normalized = _normalize(text)
    if is_fanservice_message(normalized):
        return True
    if is_personal_life_request(normalized):
        return True
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
    # Personal/social conversation is deliberately checked before the generic
    # factual-question fallback so questions like "what should I do tonight?"
    # remain normal conversation rather than being treated as unrelated QA.
    if is_personal_life_request(normalized) or is_social_message(normalized) or is_subjective_question(normalized):
        return True
    return False


def scope_block_reason(text: str) -> str:
    category = forbidden_topic_category(text)
    if category:
        return category
    if is_specialist_request(text):
        return "programming or specialist work"
    if is_personal_life_request(text) or is_social_message(text) or is_subjective_question(text):
        return ""
    if GENERAL_FACTUAL_QUESTION.search(_normalize(text)):
        return "unrelated factual information"
    return "an unrelated topic"
