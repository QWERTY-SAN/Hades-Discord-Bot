from __future__ import annotations

import re
import unicodedata

from ..ai.fanservice import fanservice_category
from ..config import SETTINGS
from ..knowledge.lore import SCOPE_TERMS

HADES_TERMS = {
    "aether gazer", "aethergazer", "hades", "administrator", "little lamb", "modifier", "modifiers",
    "society of muses", "olympus", "gen-zone", "gen zone", "sigil", "functor", "mintha", "leuce",
    "puppet master", "puppeteer", "aether code", "access key", "modification factor", "modifier sync",
    "divine grace", "chthonic mark", "shifted star", "shifted stars", "shifting flower", "shifting flowers",
    "swigs", "ain soph coin", "zero time", "modified mode", "warp skill", "warp skills", "support module",
    "support modules", "gaea", "gaea.zero", "gaea zero", "idealbild", "source layer", "surface layer",
    "visbane", "visbanes", "bane energy", "corrosion", "quakes", "ain soph", "neuhansa", "shashvat",
    "omorfies", "xu heng", "sasanami", "division nine", "astral council", "quad", "mimir", "oneiroi",
    "recurring dream", "hazard zone", "dimensional variable", "iterative testing", "past grudges",
    "causality survey", "ancient shadow", "crisis analysis", "meow", "m.e.o.w.", "opponent intel",
    "risk level", "sigil enchant", "sigil enchants", "transcendence", "transcend", "ultimate skillchain",
    "gacha", "f2p", "free-to-play", "free to play", "low spender", "dolphin", "whale", "spender", "spending",
    "battle sweep", "flaneuring", "music dossier", "heart link", "access key synergy", "heimdall",
}
HADES_TERMS.update(SCOPE_TERMS)

HARD_OFF_TOPIC_PATTERNS = (
    ("F1 or motorsport", re.compile(r"\b(?:f1|formula\s*(?:1|one)|motogp|nascar|indycar|motorsport|grand\s*prix)\b", re.I)),
    ("other sports", re.compile(r"\b(?:sports?|football|soccer|basketball|baseball|tennis|golf|hockey|nfl|nba|mlb|nhl|ufc)\b", re.I)),
    ("other games", re.compile(r"\b(?:genshin|honkai|star\s*rail|nikke|valorant|league\s+of\s+legends|minecraft|fortnite|elden\s+ring|dark\s+souls|destiny|warframe|wuthering\s+waves|zenless\s+zone\s+zero|zzz)\b", re.I)),
    ("programming or technology", re.compile(r"\b(?:python|javascript|typescript|java|c\+\+|c#|rust|golang|ruby|php|sql|regex|html|css|discord\.py|programming|linux|windows|router|server|database|driver|cpu|gpu|ram|pc|computer|network|debugging|software|hardware)\b", re.I)),
    ("politics, news, or finance", re.compile(r"\b(?:politics?|politician|president|prime\s+minister|election|elections|senate|congress|government|political|breaking\s+news|stock|stocks|share\s+price|crypto|cryptocurrency|bitcoin|ethereum|forex|investment|trading|finance|financial)\b", re.I)),
)
CONTEXTUAL_OFF_TOPIC_PATTERNS = (
    ("unrelated entertainment or media", re.compile(r"\b(?:movie|movies|film|films|tv|television|series|anime|manga|celebrity|actor|actress|singer|song|songs|band|concert|netflix|youtube|twitch|streamer|influencer)\b", re.I)),
    ("unrelated racing", re.compile(r"\b(?:racing|race)\b", re.I)),
)
CORRECTION_PATTERN = re.compile(
    r"^(?:no[,! ]+|nah[,! ]+|wait[,! ]+|actually[,! ]+|correction[,! ]+|wrong[,! ]+|"
    r"nots+(?:exactly|quite)[,! ]+|that'ss+nots+whats+is+meant[,.! ]*|"
    r"is+meant[,.! ]+).{1,700}$",
    re.I | re.S,
)

SPECIALIST_REQUESTS = (
    re.compile(r"\b(?:write|build|make|create|code|debug|fix|program|implement|develop|generate|show|give|provide)\b.{0,100}\b(?:code|script|program|bot|api|regex|source\s+code|discord\s+bot)\b", re.I | re.S),
    re.compile(r"\b(?:write|build|make|create|code|debug|fix|program|implement|develop|generate|show|give|provide)\b.{0,100}\b(?:python|javascript|typescript|java|c\+\+|c#|rust|golang|ruby|php|sql|regex|html|css|api|script|source\s+code|code\s+snippet|discord\.py|programming)\b", re.I | re.S),
    re.compile(r"\b(?:write|do|finish|solve|answer|complete|help\s+with|help\s+me\s+with)\b.{0,80}\b(?:my|this|the)\b.{0,50}\b(?:homework|assignment|essay|thesis|report|worksheet|exam|test)\b", re.I | re.S),
    re.compile(r"\b(?:fix|troubleshoot|configure|set\s+up|diagnose|repair)\b.{0,80}\b(?:windows|linux|router|printer|network|pc|computer|server|database|driver)\b", re.I | re.S),
)
GENERAL_FACTUAL_QUESTION = re.compile(
    r"^(?:who|what|when|where|why|how|which|tell\s+me\s+about|explain|define|is|are|can|could|do|does|did|should|would|will|have|has|may|might)\b",
    re.I,
)
REACTION_ONLY_PATTERN = re.compile(
    r"^(?:(?:[\U0001F300-\U0001FAFF\u2600-\u27BF]|<a?:[A-Za-z0-9_~+-]+:\d+>|:[A-Za-z0-9_~+-]+:|:3c?|x3|xd)[\s.!?]*)+$",
    re.I,
)

STORYTELLING_PATTERNS = (
    re.compile(
        r"^(?:so\s+today|today\s+i|earlier\s+i|yesterday\s+i|last\s+night\s+i|"
        r"guess\s+what|you\s+won't\s+believe|you\s+know\s+what\s+happened|"
        r"i\s+just\s+(?:got|came|saw|watched|met|bought|found|heard|did|finished|"
        r"received|started|ended))\b.{0,700}$",
        re.I | re.S,
    ),
)

SOCIAL_PATTERNS = (
    re.compile(r"^(?:there\s+you\s+are|glad\s+(?:you'?re|you\s+are)\s+here|i\s+(?:wanted|want)\s+to\s+(?:see|talk\s+to|hear\s+from)\s+you|i(?:'ve|\s+have)\s+been\s+(?:thinking\s+about|looking\s+for)\s+you)[!. ]*$", re.I),
    re.compile(r"^(?:you'?re|you\s+are)\s+(?:funny|hilarious|sweet|kind|nice|charming|amusing|interesting|adorable|lovely|something\s+else)\b.{0,250}$", re.I | re.S),
    re.compile(r"^(?:hi|hello|hey|hiya|yo+|ayo+|sup|morning|evening|night|good\s+(?:morning|afternoon|evening|night)|welcome\s+back|good\s+to\s+see\s+you|nice\s+to\s+see\s+you|long\s+time\s+no\s+see)[!. ]*(?::[A-Za-z0-9_~+-]+:|<a?:[A-Za-z0-9_~+-]+:\d+>)*[!. ]*$", re.I),
    re.compile(r"^(?:thanks?|thank\s+you|thx|ty|you'?re\s+welcome|no\s+worries|my\s+bad|sorry|good\s+luck|same|same\s+here|me\s+too|me\s+neither|you\s+too|exactly|true|fair|fair\s+enough|makes\s+sense|that\s+makes\s+sense|for\s+real|fr|frfr|ikr|ngl|tbh|idk|idc|right|no\s+way|really\??|seriously\??|of\s+course|sure|okay|ok|alright|alrighty|fine|yep+|yes|yeah+|yuh|yup|nope|nah+|maybe|perhaps|bro|bruh+|lmao+|lol+)[!. ]*$", re.I),
    re.compile(r"^(?:how\s+are\s+you|how're\s+you|how\s+do\s+you\s+feel|are\s+you\s+(?:okay|good|tired|busy|bored|happy|sad|lonely|curious|sleepy)|what(?:'s|\s+is)\s+up|what\s+are\s+you\s+doing|what\s+about\s+you|how\s+about\s+you|and\s+you\??|how\s+was\s+your\s+day|did\s+you\s+sleep|did\s+you\s+rest|what\s+have\s+you\s+been\s+doing|can\s+we\s+(?:talk|chat)|talk\s+to\s+me|stay\s+with\s+me|keep\s+me\s+company|tell\s+me\s+about\s+yourself|tell\s+me\s+something|say\s+something|what\s+do\s+you\s+think\s+of\s+me|do\s+you\s+(?:like|trust|remember|miss)\s+me|what(?:'s|\s+is)\s+your\s+(?:favorite|favourite)|what\s+do\s+you\s+(?:like|enjoy|prefer)|do\s+you\s+(?:like|enjoy|prefer)|would\s+you\s+rather|want\s+to\s+(?:talk|chat))[?.! ]*$", re.I),
    re.compile(r"^(?:guess\s+what|look\s+at\s+this|listen|you\s+know\s+what|you\s+know|i\s+have\s+something\s+to\s+tell\s+you|want\s+to\s+hear\s+something|let's\s+(?:talk|chat)|let\s+us\s+(?:talk|chat)|make\s+me\s+smile|cheer\s+me\s+up|i'?m\s+(?:bored|tired|sad|happy|lonely|excited|upset|fine|okay|back|home|sleepy)|i\s+(?:just\s+got\s+home|just\s+woke\s+up|just\s+got\s+back|miss|missed|like|love|hate|need|want|feel|think|guess|remember)\b).{0,700}$", re.I | re.S),
    re.compile(r"^(?:that's|thats|this\s+is|this\s+was|that\s+is|that\s+was|it(?:'s|\s+is)|it\s+was|sounds\s+(?:like|good|fun|nice|rough|wild|crazy|interesting)|looks\s+(?:like|good|fun|nice|rough|wild|crazy|interesting)|seems\s+(?:like|good|fun|nice|rough|wild|crazy|interesting))\b.{0,700}$", re.I | re.S),
    re.compile(r"^(?:lol|lmao|haha|hehe|nice|cool|cute|damn|wow|ugh|oof|welp|bruh|based|real|hmm+|oh+|ah+|yikes|whoa+|woah+|phew|that's|thats|this\s+is|that\s+was|you'?re\s+funny|you\s+know|oh\s+really|is\s+that\s+so|owo|uwu)(?:[!. ]|$).{0,300}$", re.I | re.S),
    re.compile(r"^(?:eh|uh+|umm*|well)[,\s]+(?:like\s+what|and\s+what|what\s+else|what\s+now|so\s+what)[?!., ]*$", re.I),
    re.compile(r"^(?:like\s+what|and\s+what|what\s+else|what\s+now|so\s+what)[?!., ]*$", re.I),
    re.compile(r"^(?:ok|okay|alright|fine)[,\s]+as\s+(?:u|you)\s+say\b.{0,700}$", re.I | re.S),
    re.compile(r"^(?:(?:woof|arf|awoo|meow|mew|nya|rawr)(?:[\s.!?]*(?:woof|arf|awoo|meow|mew|nya|rawr)){0,5})[\s.!?]*(?::3|:3c|x3|X3)?[\s.!?]*$", re.I),
    re.compile(r"^(?:i|i'm|im|i've|ive|my|mine|today\s+i|tonight\s+i|this\s+is|that\s+was|just|currently|honestly|literally)\b.{0,700}$", re.I | re.S),
    re.compile(r"^(?:mind\s+if\s+i|can\s+i|may\s+i|is\s+it\s+(?:okay|alright)\s+if\s+i|would\s+you\s+mind\s+if\s+i)\b.{0,300}$", re.I | re.S),
)
PERSONAL_LIFE_PATTERNS = (
    re.compile(r"^(?:what\s+should\s+i\s+do|what\s+can\s+i\s+do|what\s+could\s+i\s+do|what\s+else\s+(?:can|should)\s+i\s+do|what\s+should\s+we\s+do|what\s+can\s+we\s+do|what\s+do\s+you\s+suggest\s+i\s+do|how\s+should\s+i\s+spend\s+(?:my\s+time|my\s+day|my\s+evening|my\s+night)|give\s+me\s+(?:something|an\s+idea)\s+to\s+do|give\s+me\s+an?\s+idea|pick\s+something\s+for\s+me|choose\s+something\s+for\s+me|surprise\s+me|help\s+me\s+decide\s+(?:what\s+to\s+do|what\s+i\s+should\s+do)|i\s+(?:don't|do\s+not)\s+know\s+what\s+to\s+do|i\s+have\s+nothing\s+to\s+do|anything\s+else)(?:\s+(?:tonight|today|right\s+now|this\s+(?:morning|afternoon|evening|weekend)|tomorrow|for\s+fun|when\s+i'?m\s+bored))?[?.! ]*$", re.I),
    re.compile(r"^(?:should\s+i\s+.+\s+or\s+.+|which\s+one\s+should\s+i\s+(?:pick|choose)|do\s+you\s+think\s+i\s+should\s+.+|what\s+would\s+you\s+do)[?.! ]*$", re.I | re.S),
)
SUBJECTIVE_QUESTION = re.compile(
    r"^(?:what\s+do\s+you\s+(?:think|like|prefer|want|feel)|what(?:'s|\s+is)\s+your\s+(?:favorite|favourite)|do\s+you\s+(?:like|enjoy|prefer|want|remember|mind|care|agree)|would\s+you\s+rather|how(?:'re|\s+are)\s+you(?:\s+doing|\s+holding\s+up)?|how\s+do\s+you\s+feel|are\s+you\s+(?:okay|tired|happy|sad|bored|busy|lonely))\b",
    re.I,
)
SHORT_FOLLOWUPS = frozenset({
    "why", "why?", "really", "really?", "how so", "how so?", "go on", "go on.", "and then", "and then?",
    "what about her", "what about her?", "what about him", "what about him?", "what about that", "what about that?",
    "and you", "and you?", "you too", "you too?", "same", "same.", "fair enough", "fair enough.", "no way", "no way!",
    "tell me more", "continue", "continue?", "what do you mean", "what do you mean?", "how come", "how come?",
    "your turn", "your turn?", "what then", "what then?", "prove it", "prove it?",
    "wait, what", "wait what", "huh", "huh?", "seriously", "seriously?",
    "for real", "for real?", "okay then", "okay then?", "go ahead", "go ahead?",
    "what do u mean", "what do u mean?", "what u mean", "what u mean?", "wdym", "wdym?",
    "wait what do u mean", "wait what do u mean?", "what did you mean", "what did you mean?",
    "what is this", "what is this?", "what's this", "what's this?", "whats this", "whats this?",
    "what is that", "what is that?", "what's that", "what's that?", "whats that", "whats that?",
    "what does this mean", "what does this mean?", "what does that mean", "what does that mean?",
    "what's that mean", "what's that mean?", "whats that mean", "whats that mean?",
})


CONTEXTUAL_FOLLOWUPS = frozenset({
    "why", "why?", "how so", "how so?", "go on", "go on.", "and then", "and then?",
    "what about her", "what about her?", "what about him", "what about him?", "what about that", "what about that?",
    "what about this", "what about this?", "what about it", "what about it?",
    "tell me more", "continue", "continue?", "how come", "how come?",
    "what then", "what then?", "wait, what", "wait what", "huh", "huh?", "seriously", "seriously?",
    "what is this", "what is this?", "what's this", "what's this?", "whats this", "whats this?",
    "what is that", "what is that?", "what's that", "what's that?", "whats that", "whats that?",
    "what does this mean", "what does this mean?", "what does that mean", "what does that mean?",
    "what's that mean", "what's that mean?", "whats that mean", "whats that mean?",
})


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
    meaningful = HADES_TERMS - {"hades", "administrator", "little lamb"}
    return any(_contains_term(normalized, term) for term in meaningful)


TECHNICAL_CONTEXT_WORDS = frozenset({
    "server", "database", "driver", "cpu", "gpu", "ram", "pc", "computer", "network", "software",
    "hardware", "system", "ai", "algorithm",
})
HARD_TECHNICAL_WORDS = re.compile(
    r"\b(?:python|javascript|typescript|java|c\+\+|c#|rust|golang|ruby|php|sql|regex|html|css|"
    r"programming|discord\.py|coding|debugging|program|script|source\s+code)\b",
    re.I,
)


def forbidden_topic_category(text: str, *, context: str = "") -> str | None:
    normalized = _normalize(text)
    surrounding = _normalize(" ".join(part for part in (context, text) if part))
    if not normalized:
        return None

    for category, pattern in HARD_OFF_TOPIC_PATTERNS:
        if not pattern.search(normalized):
            continue

        if category == "programming or technology":
            if HARD_TECHNICAL_WORDS.search(normalized) or is_specialist_request(normalized):
                return category
            # Generic words such as "server" or "AI" can legitimately describe Mimir
            # or Aether Gazer infrastructure when an Aether context is present.
            if has_aether_context(surrounding):
                continue

        return category

    aether_context = has_aether_context(surrounding)
    if not aether_context:
        for category, pattern in CONTEXTUAL_OFF_TOPIC_PATTERNS:
            if pattern.search(normalized):
                return category
    return None


def contains_forbidden_topic(text: str, *, context: str = "") -> bool:
    return forbidden_topic_category(text, context=context) is not None


def is_specialist_request(text: str) -> bool:
    normalized = _normalize(text)
    return any(pattern.search(normalized) for pattern in SPECIALIST_REQUESTS)


def is_reaction_message(text: str) -> bool:
    normalized = _normalize(text)
    return bool(REACTION_ONLY_PATTERN.fullmatch(normalized))


def is_personal_life_request(text: str) -> bool:
    normalized = _normalize(text)
    return any(pattern.search(normalized) for pattern in PERSONAL_LIFE_PATTERNS)


def is_social_message(text: str) -> bool:
    normalized = _normalize(text)
    if fanservice_category(normalized) is not None:
        return True
    if is_reaction_message(normalized):
        return True
    if is_short_followup(normalized):
        return True
    if is_personal_life_request(normalized):
        return True
    if any(pattern.search(normalized) for pattern in STORYTELLING_PATTERNS):
        return True
    if CORRECTION_PATTERN.search(normalized):
        return True
    return any(pattern.search(normalized) for pattern in SOCIAL_PATTERNS)


def is_subjective_question(text: str) -> bool:
    normalized = _normalize(text)
    return bool(SUBJECTIVE_QUESTION.search(normalized))


def is_short_followup(text: str) -> bool:
    return _normalize(text) in SHORT_FOLLOWUPS


def is_hades_scope_allowed(text: str, *, has_history: bool = False) -> bool:
    normalized = _normalize(text)
    if not normalized:
        return False

    # The strict flag controls the narrow-topic gate. Even when disabled, explicit
    # specialist requests remain blocked so the bot does not silently become a
    # general-purpose coding assistant.
    if SETTINGS.strict_aether_topic and forbidden_topic_category(normalized) is not None:
        return False
    if is_specialist_request(normalized):
        return False
    # Short conversational follow-ups only make sense when there is an active
    # Hades conversation to attach them to. They remain socially classified so
    # the normal-conversation layer can recognize them, but scope must reject
    # them when no history exists.
    if normalized in CONTEXTUAL_FOLLOWUPS and not has_history:
        return False
    if not SETTINGS.strict_aether_topic:
        return True
    # This is the deliberate context bridge: generic follow-ups are allowed only
    # after a real Hades conversation already exists for this user/channel.
    if has_history and is_short_followup(normalized):
        return True
    if any(_contains_term(normalized, term) for term in HADES_TERMS):
        return True
    if fanservice_category(normalized) is not None:
        return True
    if is_personal_life_request(normalized) or is_social_message(normalized) or is_subjective_question(normalized):
        return True
    return False


def scope_block_reason(text: str) -> str:
    category = forbidden_topic_category(text)
    if category:
        return category
    if is_specialist_request(text):
        return "programming or specialist work"
    if is_personal_life_request(text) or is_social_message(text) or is_subjective_question(text) or CORRECTION_PATTERN.search(_normalize(text)):
        return ""
    if GENERAL_FACTUAL_QUESTION.search(_normalize(text)):
        return "unrelated factual information"
    return "an unrelated topic"
