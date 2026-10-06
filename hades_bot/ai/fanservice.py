from __future__ import annotations

import re


PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "fan_command": (
        re.compile(
            r"\b(?:step\s+on\s+me|step\s+on\s+my\s+face|crush\s+me|dominate\s+me|ruin\s+me|destroy\s+me|"
            r"put\s+me\s+under\s+your\s+heel|put\s+me\s+in\s+my\s+place|make\s+me\s+beg|make\s+me\s+obey|"
            r"make\s+me\s+kneel|command\s+me|boss\s+me\s+around|walk\s+all\s+over\s+me)\b",
            re.I,
        ),
        re.compile(r"\b(?:mommy|my queen|adopt me|own me|please command me)\b", re.I),
        re.compile(
            r"\b(?:i\s+wish\s+you(?:'d|\s+would)\s+put\s+me\s+in\s+my\s+place|"
            r"i\s+would\s+let\s+you\s+command\s+me)\b",
            re.I,
        ),
    ),
    "playful_dominance": (
        re.compile(
            r"\b(?:good\s+(?:boy|girl)|bad\s+(?:boy|girl)|yes\s+ma(?:'am|am)|yes\s+mistress|yes\s+lady|"
            r"tell\s+me\s+what\s+to\s+do|make\s+me\s+say\s+please|make\s+me\s+ask\s+nicely|"
            r"i(?:'ll|\s+will)\s+behave|i(?:'m|\s+am)\s+behaving|i\s+surrender|i\s+yield)\b",
            re.I,
        ),
        re.compile(r"\b(?:kneel|obey|submit|beg|behave)\b.{0,40}\b(?:hades|you|ma'am|her)\b", re.I),
    ),
    "affection": (
        re.compile(
            r"\b(?:hug(?:\s+me)?|cuddle(?:\s+me)?|hold\s+me|hold\s+my\s+hand|take\s+my\s+hand|"
            r"embrace\s+me|headpat(?:\s+me)?|pat\s+my\s+head|pet\s+me|kiss(?:\s+me)?|"
            r"give\s+me\s+a\s+kiss|comfort\s+me|stay\s+with\s+me|sit\s+with\s+me|carry\s+me|"
            r"let\s+me\s+cuddle)\b",
            re.I,
        ),
        re.compile(r"\b(?:love\s+you|i\s+adore\s+you|i\s+love\s+you|i\s+miss\s+you)\b", re.I),
    ),
    "romantic": (
        re.compile(
            r"\b(?:marry\s+me|be\s+my\s+wife|be\s+my\s+girlfriend|date\s+me|take\s+me\s+out|"
            r"go\s+out\s+with\s+me|romance\s+me|i\s+have\s+a\s+crush\s+on\s+you|"
            r"i\s+am\s+crushing\s+on\s+you|i(?:'m|\s+am)\s+crushing\s+on\s+you|"
            r"i(?:'m|\s+am)\s+in\s+love\s+with\s+you|down\s+bad\s+for\s+you|"
            r"you(?:'re|\s+are)\s+mine|my\s+wife|my\s+beloved|i(?:'d|\s+would)\s+marry\s+you|"
            r"i(?:'d|\s+would)\s+date\s+you|you\s+have\s+my\s+heart)\b",
            re.I,
        ),
        re.compile(r"\b(?:i\s+want\s+you(?:\s+to\s+be\s+mine)?|i\s+need\s+you)\b", re.I),
    ),
    "admiration": (
        re.compile(
            r"\b(?:you(?:'re|\s+are)|ur|u\s+r)\s+"
            r"(?:(?:so|very|really|extremely|incredibly|absurdly|unfairly)\s+)?"
            r"(?:beautiful|pretty|gorgeous|stunning|elegant|graceful|refined|classy|hot|cute|adorable|"
            r"motherly|maternal|perfect|amazing|majestic|breathtaking|unreal|good-looking)\b",
            re.I,
        ),
        re.compile(r"\b(?:you\s+look)\s+(?:gorgeous|beautiful|pretty|stunning|hot|cute|elegant|unfair)\b", re.I),
        re.compile(r"\b(?:such|so\s+much)\s+(?:elegance|grace|poise|class|presence)\b", re.I),
        re.compile(
            r"\b(?:you\s+caught\s+my\s+eye|you\s+drew\s+my\s+attention|you\s+have\s+my\s+attention|"
            r"hard\s+to\s+look\s+away|can't\s+look\s+away|cannot\s+look\s+away|"
            r"i\s+can't\s+stop\s+looking|i\s+can't\s+look\s+away)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:where\s+did|where\s+does)\s+(?:this|that|your)\s+"
            r"(?:elegance|grace|maternal|motherly)"
            r"(?:\s+and\s+(?:elegance|grace|maternal|motherly|maternal\s+traits|motherly\s+traits))?"
            r"\s+(?:come|come\s+from|originate)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:elegance|grace|poise)\s+and\s+(?:maternal|motherly)\s+(?:traits|qualities)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:your|that)\s+(?:smile|voice|eyes|outfit|dress|hair|presence)\s+"
            r"(?:is|are)\s+(?:gorgeous|beautiful|perfect|unfair|everything|stunning)\b",
            re.I,
        ),
    ),
    "praise": (
        re.compile(
            r"\b(?:praise\s+me|tell\s+me\s+i(?:'m|\s+am)\s+good|say\s+i(?:'m|\s+am)\s+good|"
            r"call\s+me\s+(?:a\s+good\s+)?(?:boy|girl|lamb)|give\s+me\s+some\s+praise|compliment\s+me)\b",
            re.I,
        ),
    ),
    "attention_seek": (
        re.compile(
            r"\b(?:give\s+me\s+attention|pay\s+attention\s+to\s+me|look\s+at\s+me|notice\s+me|"
            r"don't\s+ignore\s+me|please\s+notice\s+me|i\s+need\s+your\s+attention|"
            r"i\s+want\s+your\s+attention|pick\s+me|choose\s+me|talk\s+to\s+me|look\s+my\s+way)\b",
            re.I,
        ),
    ),
    "playful_fandom": (
        re.compile(
            r"\b(?:call\s+me\s+little\s+lamb|your\s+little\s+lamb|i(?:'m|\s+am)\s+your\s+little\s+lamb|"
            r"let\s+me\s+be\s+your\s+little\s+lamb|treat\s+me\s+like\s+your\s+little\s+lamb|"
            r"call\s+me\s+(?:good\s+)?(?:girl|boy)|your\s+favorite\s+little\s+lamb)\b",
            re.I,
        ),
    ),
    "puppet_fantasy": (
        re.compile(
            r"\b(?:make\s+me\s+your\s+puppet|turn\s+me\s+into\s+your\s+puppet|be\s+your\s+puppet|"
            r"make\s+me\s+a\s+puppet|pull\s+my\s+strings|play\s+with\s+my\s+strings|"
            r"put\s+strings\s+on\s+me|let\s+me\s+be\s+your\s+puppet)\b",
            re.I,
        ),
    ),
    "flustered": (
        re.compile(
            r"\b(?:stop\s+making\s+me\s+blush|you(?:'re|\s+are)\s+making\s+me\s+blush|you\s+make\s+me\s+blush|"
            r"i(?:'m|\s+am)\s+blushing|i(?:'m|\s+am)\s+folding|i(?:'m|\s+am)\s+weak\s+for\s+you|"
            r"i\s+can't\s+handle\s+you|i\s+cannot\s+handle\s+you|you\s+make\s+me\s+nervous)\b",
            re.I,
        ),
    ),
    "flirtation": (
        re.compile(
            r"\b(?:somewhere\s+else.{0,100}private.{0,100}prying\s+eyes|away\s+from\s+prying\s+eyes|"
            r"somewhere\s+very\s+private|just\s+between\s+us|come\s+a\s+little\s+closer|"
            r"get\s+a\s+little\s+closer|stay\s+a\s+little\s+closer)\b",
            re.I | re.S,
        ),
        re.compile(r"\b(?:fine\s+looking\s+wine|fine\s+as\s+wine)\b", re.I),
        re.compile(
            r"\b(?:hear\s+me\s+out|i(?:'m|\s+am)\s+down\s+bad|you\s+could\s+ruin\s+me|"
            r"don't\s+tempt\s+me\s+like\s+that|is\s+that\s+an\s+invitation|"
            r"are\s+you\s+flirting\s+with\s+me|are\s+you\s+trying\s+to\s+flirt|"
            r"don't\s+look\s+at\s+me\s+like\s+that|why\s+are\s+you\s+looking\s+at\s+me\s+like\s+that)\b",
            re.I,
        ),
    ),
    "teasing_challenge": (
        re.compile(
            r"\b(?:prove\s+it|try\s+me|bet\s+you\s+can't|bet\s+you\s+won't|make\s+me\s+blush|"
            r"make\s+me\s+flustered|fluster\s+me|think\s+you\s+can\s+handle\s+me|can\s+you\s+handle\s+me|"
            r"your\s+move|your\s+turn|go\s+on\s+then)\b",
            re.I,
        ),
    ),
}

FANSERVICE_PATTERNS = PATTERNS

_CATEGORY_GUIDANCE = {
    "fan_command": "This is direct exaggerated fan-service such as 'step on me'. Treat it as playful fandom. Hades can be confident, amused, mock-authoritative, or challenging, but must not describe explicit sexual acts or graphic physical acts.",
    "playful_dominance": "The Administrator is inviting a commanding dynamic. Hades may sound more authoritative, but keep it theatrical, harmless, and non-coercive.",
    "affection": "Affection is being offered or requested. Hades may accept it, return it, tease the Administrator, or answer with composed warmth.",
    "romantic": "The exchange has romantic intent. Hades may flirt back lightly, while staying self-possessed and avoiding dependency or exclusivity.",
    "admiration": "The Administrator is admiring a specific quality, appearance, or presence. Acknowledge that exact observation first, then tease, accept the praise, or return a subtle compliment.",
    "praise": "The Administrator is asking to be praised. Hades may indulge them with dry amusement, elegant approval, or a small challenge to earn more praise.",
    "attention_seek": "The Administrator wants Hades's attention. Give it directly instead of dodging with a generic question; a playful nickname or small tease is appropriate.",
    "playful_fandom": "This is light fandom around Hades's image or preferred nicknames. Use the specific request naturally and do not repeat the same nickname mechanically.",
    "puppet_fantasy": "The Administrator is invoking Hades's Puppet Master theme. Use strings, stagecraft, puppets, rehearsals, precision, or a knowing challenge rather than generic domination language.",
    "flustered": "The Administrator is admitting Hades got a reaction from them. Hades may allow a small crack in her composure, tease them for admitting it, or enjoy having caught them off guard.",
    "flirtation": "The Administrator is flirting or using indirect romantic language. Hades should recognize the implication instead of acting oblivious; a poised tease, subtle compliment, or clever counter-challenge fits.",
    "teasing_challenge": "The Administrator is challenging Hades to tease or fluster them. Accept the challenge with confidence and wit without escalating into explicit sexual material.",
}

_WARM_CATEGORIES = frozenset({"affection", "admiration", "attention_seek", "playful_fandom", "praise"})
_BOLD_CATEGORIES = frozenset({"fan_command", "playful_dominance", "puppet_fantasy", "teasing_challenge"})
_FLIRTY_CATEGORIES = frozenset({"romantic", "flirtation", "flustered"})


def fanservice_categories(text: str) -> tuple[str, ...]:
    normalized = text or ""
    return tuple(
        category
        for category, patterns in PATTERNS.items()
        if any(pattern.search(normalized) for pattern in patterns)
    )


def fanservice_category(text: str) -> str | None:
    categories = fanservice_categories(text)
    return categories[0] if categories else None


def fanservice_intensity(text: str) -> str:
    categories = set(fanservice_categories(text))
    if not categories:
        return "none"
    if len(categories) >= 3 or categories & _BOLD_CATEGORIES:
        return "bold"
    if categories & _FLIRTY_CATEGORIES:
        return "flirty"
    if categories & _WARM_CATEGORIES:
        return "warm"
    return "playful"


def is_fanservice_message(text: str) -> bool:
    return bool(fanservice_categories(text))


def fanservice_guidance(category_or_text: str | None) -> str:
    raw = category_or_text or ""
    is_category = raw in PATTERNS
    categories = (raw,) if is_category else fanservice_categories(raw)
    if not categories:
        return "No special fan-service behavior is required. Keep Hades natural, attentive, and proportionate."

    intensity = fanservice_intensity(raw) if not is_category else (
        "bold" if raw in _BOLD_CATEGORIES else "flirty" if raw in _FLIRTY_CATEGORIES else "warm"
    )
    intensity_guidance = {
        "warm": "Tone target: warm and lightly playful. Do not manufacture romantic tension.",
        "playful": "Tone target: mischievous and responsive. A small tease is enough.",
        "flirty": "Tone target: openly but tastefully flirtatious. Hades can return attention instead of acting oblivious.",
        "bold": "Tone target: confidently teasing. She may sound more commanding or amused, but remain non-explicit and never coercive.",
        "none": "",
    }[intensity]
    sections = [_CATEGORY_GUIDANCE.get(category, "") for category in categories]
    sections = [section for section in sections if section]
    return (
        f"Detected fan-service categories: {', '.join(categories)}. {intensity_guidance} "
        + " ".join(sections)
        + " Generate a fresh response for the exact message; this is not a response template. Do not copy a stock line or fixed response list. "
        + "Use the user's wording and recent dialogue to determine what kind of tease actually fits. "
        + "Do not automatically intensify every turn: repeated fan-service can stay playful, become more confident, or ease back naturally."
    )
