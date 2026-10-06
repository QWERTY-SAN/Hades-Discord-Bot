from __future__ import annotations

import re


PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "fan_command": (
        re.compile(
            r"\b(?:step\s+on\s+me|step\s+on\s+my\s+face|crush\s+me|"
            r"dominate\s+me|ruin\s+me|destroy\s+me|put\s+me\s+under\s+your\s+heel|"
            r"make\s+me\s+beg|make\s+me\s+obey|make\s+me\s+kneel|"
            r"command\s+me|put\s+me\s+in\s+my\s+place)\b",
            re.I,
        ),
        re.compile(r"\b(?:mommy|my queen|adopt me|own me)\b", re.I),
        re.compile(r"\b(?:i\s+wish\s+you(?:'d|\s+would)\s+put\s+me\s+in\s+my\s+place)\b", re.I),
    ),
    "affection": (
        re.compile(
            r"\b(?:hug(?: me)?|cuddle(?: me)?|hold me|hold my hand|take my hand|"
            r"embrace me|headpat(?: me)?|pat my head|pet me|kiss(?: me)?|"
            r"give me a kiss|comfort me|stay with me|sit with me|carry me)\b",
            re.I,
        ),
        re.compile(r"\b(?:love you|i adore you|i love you)\b", re.I),
    ),
    "romantic": (
        re.compile(
            r"\b(?:marry me|be my wife|be my girlfriend|date me|take me out|"
            r"go out with me|romance me|i have a crush on you|i am crushing on you|"
            r"i'm crushing on you|i'm in love with you|i am in love with you|"
            r"down bad for you|you're mine|you are mine|my wife|my beloved|"
            r"i'd marry you|i would marry you|i'd date you|i would date you|"
            r"you have my heart)\b",
            re.I,
        ),
        re.compile(r"\b(?:i want you(?:\s+to\s+be\s+mine)?|i need you)\b", re.I),
    ),
    "admiration": (
        re.compile(
            r"\b(?:you're|you are|ur|u r)\s+"
            r"(?:(?:so|very|really|extremely|incredibly)\s+)?"
            r"(?:beautiful|pretty|gorgeous|stunning|elegant|graceful|refined|"
            r"classy|hot|cute|adorable|motherly|maternal|perfect|amazing|majestic|"
            r"breathtaking|unreal)\b",
            re.I,
        ),
        re.compile(r"\b(?:you look)\s+(?:gorgeous|beautiful|pretty|stunning|hot|cute|elegant)\b", re.I),
        re.compile(r"\b(?:such|so much)\s+(?:elegance|grace|poise|class)\b", re.I),
        re.compile(
            r"\b(?:you caught my eye|you drew my attention|you have my attention|"
            r"hard to look away|can't look away|cannot look away)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:where did|where does)\s+(?:this|that|your)\s+"
            r"(?:elegance|grace|maternal|motherly)"
            r"(?:\s+and\s+(?:elegance|grace|maternal|motherly|maternal\s+traits|motherly\s+traits))?"
            r"\s+(?:come|come\s+from|originate)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:elegance|grace|poise)\s+and\s+"
            r"(?:maternal|motherly)\s+(?:traits|qualities)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:your|that)\s+(?:smile|voice|eyes|outfit|dress)\s+"
            r"(?:is|are)\s+(?:gorgeous|beautiful|perfect|unfair|everything)\b",
            re.I,
        ),
    ),
    "playful_fandom": (
        re.compile(
            r"\b(?:call me little lamb|your little lamb|i'm your little lamb|"
            r"i am your little lamb|let me be your little lamb|"
            r"treat me like your little lamb|call me (?:good )?(?:girl|boy)|"
            r"praise me|tell me i'm good|tell me i am good)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:give me attention|pay attention to me|look at me|notice me|"
            r"don't ignore me|please notice me|i need your attention|"
            r"i want your attention|pick me|choose me|talk to me)\b",
            re.I,
        ),
    ),
    "puppet_fantasy": (
        re.compile(
            r"\b(?:make me your puppet|turn me into your puppet|be your puppet|"
            r"make me a puppet|pull my strings|play with my strings)\b",
            re.I,
        ),
    ),
    "flustered": (
        re.compile(
            r"\b(?:stop making me blush|you(?:'re| are) making me blush|"
            r"you make me blush|i'm blushing|i am blushing|i'm folding|"
            r"i am folding|i'm weak for you|i am weak for you)\b",
            re.I,
        ),
    ),
    "flirtation": (
        re.compile(
            r"\b(?:somewhere else.{0,80}private.{0,80}prying eyes|"
            r"away from prying eyes|somewhere very private)\b",
            re.I | re.S,
        ),
        re.compile(r"\bfine looking wine\b", re.I),
        re.compile(
            r"\b(?:hear me out|i'm down bad|i am down bad|"
            r"you could ruin me|i cannot handle you|i can't handle you|"
            r"don't tempt me like that|is that an invitation)\b",
            re.I,
        ),
    ),
}

FANSERVICE_PATTERNS = PATTERNS


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


def is_fanservice_message(text: str) -> bool:
    return bool(fanservice_categories(text))


def fanservice_guidance(category_or_text: str | None) -> str:
    category = category_or_text if category_or_text in PATTERNS else fanservice_category(category_or_text or "")
    guidance = {
        "fan_command": (
            "The user is playfully directing admiration toward Hades. Respond with composed, teasing confidence. "
            "Light fan-service is fine, but never become explicit or desperate."
        ),
        "affection": (
            "Affection is being offered or requested. Hades may accept it, tease the Administrator, or give a light "
            "affectionate response while remaining in character."
        ),
        "romantic": (
            "The user is steering the exchange toward romance. Hades may flirt back lightly, but romance remains "
            "secondary to her composed, intelligent personality. Avoid possessiveness or dependency."
        ),
        "admiration": (
            "The user is admiring Hades's appearance, elegance, maternal warmth, or ability to command attention. "
            "Treat it as a character observation first; Hades may tease them for noticing or return a subtle compliment."
        ),
        "playful_fandom": (
            "The user is engaging in playful fandom or asking for Hades's attention. She may indulge them with dry "
            "amusement, a teasing nickname, or a light command while remaining composed and in character."
        ),
        "puppet_fantasy": (
            "The user is playing with Hades's puppet-master imagery. Keep it theatrical and playful; do not turn the "
            "metaphor into explicit sexual content or dependency."
        ),
        "flustered": (
            "The user is admitting that Hades caught them off guard or made them blush. Hades may allow a subtle crack "
            "in her composure, tease them for revealing it, or calmly acknowledge the implication."
        ),
        "flirtation": (
            "The user is flirting with Hades. Let her respond with restrained, playful confidence and subtle teasing. "
            "Keep it suggestive rather than explicit, and preserve her intelligence and composure."
        ),
    }.get(category, "No special fan-service mode is required.")
    return (
        f"{guidance} Generate a fresh response from Hades rather than a predefined reply; this guidance is not a response template. "
        "Vary the wording naturally across consecutive replies."
    )
