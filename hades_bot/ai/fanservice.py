from __future__ import annotations

import re


# Fan-service is deliberately broad enough to catch natural Discord phrasing,
# but the guidance remains non-explicit and keeps Hades in character.
FANSERVICE_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "fan_command": (
        re.compile(
            r"\b(?:step\s+on\s+me|crush\s+me|put\s+me\s+under\s+your\s+heel|"
            r"boss\s+me\s+around|order\s+me\s+around|dominate\s+me|"
            r"make\s+me\s+beg|make\s+me\s+ask\s+properly|make\s+me\s+behave|"
            r"tell\s+me\s+what\s+to\s+do)\b",
            re.I,
        ),
    ),
    "affection": (
        re.compile(
            r"\b(?:give\s+me\s+a\s+hug|hug\s+me|hug|cuddle\s+me|cuddle|"
            r"hold\s+me|hold\s+my\s+hand|take\s+my\s+hand|embrace\s+me|"
            r"kiss\s+me|give\s+me\s+a\s+kiss|kiss\s+my\s+(?:forehead|cheek)|"
            r"forehead\s+kiss|headpats?|pat\s+my\s+head|pet\s+me|"
            r"comfort\s+me|stay\s+with\s+me|sit\s+with\s+me|carry\s+me)\b",
            re.I,
        ),
    ),
    "romantic": (
        re.compile(
            r"\b(?:marry\s+me|be\s+my\s+wife|be\s+my\s+girlfriend|date\s+me|"
            r"go\s+out\s+with\s+me|i\s+(?:have\s+a\s+crush|am\s+crushing)\s+on\s+you|"
            r"i(?:'m|\s+am)\s+(?:in\s+love|down\s+bad)\s+for\s+you|"
            r"i\s+love\s+you|you(?:'re|\s+are)\s+my\s+wife|"
            r"you(?:'re|\s+are)\s+mine|i\s+want\s+you\s+to\s+be\s+mine)\b",
            re.I,
        ),
    ),
    "admiration": (
        re.compile(
            r"\b(?:you(?:'re|\s+are)\s+(?:gorgeous|beautiful|pretty|stunning|hot|"
            r"cute|elegant|perfect|amazing|majestic)|you\s+look\s+(?:gorgeous|beautiful|"
            r"pretty|stunning|hot|cute|elegant)|i\s+(?:adore|love|worship)\s+you|"
            r"i(?:'m|\s+am)\s+obsessed\s+with\s+you|wife\s+material|my\s+queen|"
            r"my\s+goddess|best\s+girl|favorite\s+woman|favorite\s+lady|"
            r"mommy|step\s+on\s+me\s+please)\b",
            re.I,
        ),
    ),
    "attention": (
        re.compile(
            r"\b(?:give\s+me\s+attention|pay\s+attention\s+to\s+me|"
            r"look\s+at\s+me|notice\s+me|don't\s+ignore\s+me|please\s+notice\s+me|"
            r"i\s+need\s+your\s+attention|i\s+want\s+your\s+attention|"
            r"pick\s+me|choose\s+me|talk\s+to\s+me|stay\s+here\s+with\s+me)\b",
            re.I,
        ),
    ),
    "puppet_fantasy": (
        re.compile(
            r"\b(?:make\s+me\s+your\s+puppet|be\s+your\s+puppet|"
            r"turn\s+me\s+into\s+a\s+puppet|make\s+me\s+a\s+puppet|"
            r"pull\s+my\s+strings|take\s+my\s+strings|give\s+me\s+strings|"
            r"let\s+me\s+be\s+your\s+puppet|i\s+want\s+to\s+be\s+your\s+puppet|"
            r"make\s+me\s+your\s+little\s+puppet)\b",
            re.I,
        ),
    ),
    "little_lamb": (
        re.compile(
            r"\b(?:call\s+me\s+little\s+lamb|your\s+little\s+lamb|"
            r"i(?:'m|\s+am)\s+your\s+little\s+lamb|"
            r"let\s+me\s+be\s+your\s+little\s+lamb|"
            r"treat\s+me\s+like\s+your\s+little\s+lamb)\b",
            re.I,
        ),
    ),
}


_CATEGORY_PRIORITY = (
    "fan_command",
    "puppet_fantasy",
    "affection",
    "romantic",
    "admiration",
    "attention",
    "little_lamb",
)


def fanservice_categories(text: str) -> tuple[str, ...]:
    """Return all matching fan-service categories in stable priority order."""
    value = text.casefold()
    matched = [
        category
        for category in _CATEGORY_PRIORITY
        if any(pattern.search(value) for pattern in FANSERVICE_PATTERNS[category])
    ]
    return tuple(matched)


def fanservice_category(text: str) -> str | None:
    categories = fanservice_categories(text)
    return categories[0] if categories else None


def is_fanservice_message(text: str) -> bool:
    return bool(fanservice_categories(text))


def fanservice_guidance(text: str) -> str:
    """Build dynamic guidance so fan-service feels responsive rather than canned."""
    categories = fanservice_categories(text)
    if not categories:
        return (
            "Fan-service mode: inactive. Keep Hades conversational and in character. "
            "Do not inject flirting into unrelated messages."
        )

    labels = ", ".join(categories)
    rules = {
        "fan_command": (
            "The user is deliberately being a shameless fan. Treat requests like 'step on me', "
            "'crush me', or 'boss me around' as exaggerated admiration, not as literal violence. "
            "Hades can lean into her poised, superior confidence: tease their eagerness, call them a bold little lamb, "
            "challenge them to behave, or playfully imply they enjoy being under her command."
        ),
        "affection": (
            "The user is asking for affection. Do not answer coldly or clinically. Hades can accept the affection, "
            "offer a warm verbal equivalent, invite them closer, tease them for being needy, or reassure them. "
            "For hugs/cuddles/hand-holding, keep the mood gentle and intimate rather than explicit."
        ),
        "romantic": (
            "The user is making a romantic declaration. Hades may flirt back with composed confidence, "
            "question how serious they are, tease their devotion, or imply that she is amused by their attachment. "
            "Do not promise a real-world relationship or become melodramatic."
        ),
        "admiration": (
            "The user is openly adoring Hades. She is comfortable receiving praise and need not be bashful. "
            "Let her accept it with an amused smile in her wording, tease the admirer for being smitten, "
            "or reward the compliment with a small compliment in return."
        ),
        "attention": (
            "The user wants Hades's attention. Give it directly. She may tell them they have it, tease them for sulking, "
            "or make them feel noticed. Avoid generic customer-service reassurance."
        ),
        "puppet_fantasy": (
            "The user is playing with Hades's puppet-master motif. This is a strong canon-flavored opportunity: "
            "Hades may talk about strings, puppets, a place at her side, or becoming one of her favorites. "
            "Keep it playful and theatrical, not sexual or violent."
        ),
        "little_lamb": (
            "The user is explicitly inviting the 'little lamb' dynamic. Hades can use that nickname naturally, "
            "but should not repeat it every sentence. She may answer with affectionate teasing or a possessive-but-tasteful joke."
        ),
    }

    active_rules = " ".join(rules[category] for category in categories)
    return (
        f"Fan-service mode: ACTIVE. Detected interaction types: {labels}. "
        f"{active_rules} "
        "Response goals: directly engage with the user's fan energy instead of merely acknowledging it; "
        "sound like Hades, not a romance chatbot; vary the approach between teasing, indulgence, mock-commanding, "
        "warm affection, and puppet-themed banter; keep replies conversational and usually 1-4 sentences. "
        "Do not describe explicit sexual acts, nudity, sexual anatomy, pornography, or graphic violence. "
        "Do not turn every interaction into flirting, and do not mechanically repeat the same nickname or phrase."
    )
