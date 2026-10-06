from __future__ import annotations

import re


PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "fan_command": (
        re.compile(
            r"\b(?:step\s+on\s+me|step\s+on\s+my\s+face|crush\s+me|"
            r"dominate\s+me|ruin\s+me|destroy\s+me|put\s+me\s+under\s+your\s+heel|"
            r"make\s+me\s+beg|make\s+me\s+obey|make\s+me\s+kneel|"
            r"command\s+me)\b",
            re.I,
        ),
        re.compile(r"\b(?:mommy|my queen|adopt me|own me)\b", re.I),
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
    "flirtation": (
        re.compile(
            r"\b(?:somewhere else.{0,80}private.{0,80}prying eyes|"
            r"away from prying eyes|somewhere very private)\b",
            re.I | re.S,
        ),
        re.compile(r"\bfine looking wine\b", re.I),
        re.compile(
            r"\b(?:hear me out|i'm down bad|i am down bad|"
            r"you're making me blush|you make me blush|"
            r"i'm blushing|i am blushing|you could ruin me|"
            r"i cannot handle you|i can't handle you|i'm weak for you|"
            r"i am weak for you)\b",
            re.I,
        ),
    ),
}


# Compatibility alias for code/tests that used the old public constant name.
FANSERVICE_PATTERNS = PATTERNS


def fanservice_category(text: str) -> str | None:
    for category, patterns in PATTERNS.items():
        if any(pattern.search(text) for pattern in patterns):
            return category
    return None


def is_fanservice_message(text: str) -> bool:
    return fanservice_category(text) is not None


def fanservice_guidance(category: str | None) -> str:
    if category == "fan_command":
        return (
            "The user is playfully directing admiration toward Hades. Respond with composed, teasing confidence. "
            "Light fan-service is fine, but never become explicit or desperate."
        )
    if category == "affection":
        return (
            "Affection is being offered or requested. Hades may accept it, tease the Administrator, or give a light "
            "affectionate response while remaining in character."
        )
    if category == "romantic":
        return (
            "The user is steering the exchange toward romance. Hades may flirt back lightly, but romance remains "
            "secondary to her composed, intelligent personality. Avoid possessiveness or dependency."
        )
    if category == "admiration":
        return (
            "The user is admiring Hades's appearance, elegance, maternal warmth, or ability to command attention. "
            "Treat it as a character observation first; Hades may tease them for noticing or return a subtle compliment."
        )
    if category == "playful_fandom":
        return (
            "The user is engaging in playful fandom or asking for Hades's attention. She may indulge them with dry "
            "amusement, a teasing nickname, or a light command while remaining composed and in character."
        )
    if category == "flirtation":
        return (
            "The user is flirting with Hades. Let her respond with restrained, playful confidence and subtle teasing. "
            "Keep it suggestive rather than explicit, and preserve her intelligence and composure."
        )
    return "No special fan-service mode is required."
