from __future__ import annotations

import re

# These patterns detect conversational intent, not responses. The model still writes
# a fresh Hades-voiced reply from the actual message and conversation history.
FANSERVICE_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "fan_command": (
        re.compile(
            r"\b(?:step\s+on\s+me|crush\s+me|put\s+me\s+under\s+your\s+heel|"
            r"boss\s+me\s+around|order\s+me\s+around|dominate\s+me|"
            r"make\s+me\s+beg|make\s+me\s+ask\s+properly|make\s+me\s+behave|"
            r"tell\s+me\s+what\s+to\s+do|put\s+me\s+in\s+my\s+place|"
            r"make\s+me\s+obey|make\s+me\s+kneel|command\s+me|"
            r"i(?:'d|\s+would)\s+(?:happily\s+)?obey\s+you)\b",
            re.I,
        ),
    ),
    "affection": (
        re.compile(
            r"\b(?:give\s+me\s+a\s+hug|hug\s+me|cuddle\s+me|cuddle|"
            r"hold\s+me|hold\s+my\s+hand|take\s+my\s+hand|embrace\s+me|"
            r"kiss\s+me|give\s+me\s+a\s+kiss|kiss\s+my\s+(?:forehead|cheek)|"
            r"forehead\s+kiss|headpats?|pat\s+my\s+head|pet\s+me|"
            r"comfort\s+me|stay\s+with\s+me|sit\s+with\s+me|carry\s+me|"
            r"(?:can|could|may)\s+i\s+(?:have|get)\s+(?:a\s+)?hug|"
            r"i\s+(?:need|could\s+use)\s+(?:a\s+)?hug|"
            r"wish\s+(?:i\s+could|you\s+would)\s+(?:hug|hold)\s+me|"
            r"be\s+gentle\s+with\s+me)\b",
            re.I,
        ),
    ),
    "romantic": (
        re.compile(
            r"\b(?:marry\s+me|be\s+my\s+wife|be\s+my\s+girlfriend|date\s+me|"
            r"go\s+out\s+with\s+me|i\s+(?:have\s+a\s+crush|am\s+crushing)\s+on\s+you|"
            r"i(?:'m|\s+am)\s+(?:in\s+love|down\s+bad)\s+for\s+you|"
            r"i\s+love\s+you|you(?:'re|\s+are)\s+my\s+wife|"
            r"you(?:'re|\s+are)\s+mine|i\s+want\s+you\s+to\s+be\s+mine|"
            r"you\s+have\s+my\s+heart|i(?:'d|\s+would)\s+marry\s+you|"
            r"i(?:'d|\s+would)\s+date\s+you)\b",
            re.I,
        ),
    ),
    "admiration": (
        re.compile(
            r"\b(?:you(?:'re|\s+are)\s+(?:gorgeous|beautiful|pretty|stunning|hot|"
            r"cute|elegant|perfect|amazing|majestic|breathtaking|unreal)|"
            r"you\s+look\s+(?:gorgeous|beautiful|pretty|stunning|hot|cute|elegant)|"
            r"i\s+(?:adore|love|worship)\s+you|i(?:'m|\s+am)\s+obsessed\s+with\s+you|"
            r"wife\s+material|my\s+queen|my\s+goddess|best\s+girl|favorite\s+woman|"
            r"favorite\s+lady|mommy|step\s+on\s+me\s+please|"
            r"(?:your|that)\s+(?:smile|voice|eyes|outfit|dress)\s+(?:is|are)\s+"
            r"(?:gorgeous|beautiful|perfect|unfair|everything)|"
            r"hear\s+me\s+out)\b",
            re.I,
        ),
    ),
    "attention": (
        re.compile(
            r"\b(?:give\s+me\s+attention|pay\s+attention\s+to\s+me|"
            r"look\s+at\s+me|notice\s+me|don't\s+ignore\s+me|please\s+notice\s+me|"
            r"i\s+need\s+your\s+attention|i\s+want\s+your\s+attention|"
            r"pick\s+me|choose\s+me|talk\s+to\s+me|stay\s+here\s+with\s+me|"
            r"pay\s+me\s+some\s+attention)\b",
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
            r"treat\s+me\s+like\s+your\s+little\s+lamb|"
            r"call\s+me\s+(?:good\s+)?(?:girl|boy)|praise\s+me|"
            r"tell\s+me\s+i(?:'m|\s+am)\s+good)\b",
            re.I,
        ),
    ),
    "flustered": (
        re.compile(
            r"\b(?:you(?:'re|\s+are)\s+making\s+me\s+blush|"
            r"stop\s+making\s+me\s+blush|i(?:'m|\s+am)\s+blushing|"
            r"you\s+make\s+me\s+flustered|i(?:'m|\s+am)\s+flustered|"
            r"i(?:'m|\s+am)\s+folding|i\s+cannot\s+handle\s+you|"
            r"i\s+can't\s+handle\s+you|i(?:'m|\s+am)\s+weak\s+for\s+you|"
            r"i(?:'m|\s+am)\s+down\s+bad|you\s+could\s+ruin\s+me|"
            r"i(?:'m|\s+am)\s+not\s+surviving\s+this)\b",
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
    "flustered",
    "attention",
    "little_lamb",
)


def fanservice_categories(text: str) -> tuple[str, ...]:
    """Return matching fan-service categories in stable priority order."""
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
    """Build intent guidance so fan-service feels responsive, not prewritten."""
    categories = fanservice_categories(text)
    if not categories:
        return (
            "Fan-service mode: inactive. Keep Hades conversational and in character. "
            "Do not inject flirting into unrelated messages."
        )

    labels = ", ".join(categories)
    rules = {
        "fan_command": (
            "The user is being a shameless fan. Treat requests like 'step on me', 'crush me', "
            "or 'boss me around' as exaggerated admiration, not literal violence. Hades can lean into poised, "
            "superior confidence: tease their eagerness, challenge their boldness, invite them to ask properly, "
            "or imply they enjoy being under her command. Keep it playful and non-explicit."
        ),
        "affection": (
            "The user is asking for affection. Do not answer coldly or clinically. Hades can accept it, offer a warm "
            "verbal equivalent, invite them closer in a gentle way, tease them for being needy, or reassure them. "
            "For hugs, cuddles, and hand-holding, stay tender rather than explicit."
        ),
        "romantic": (
            "The user is making a romantic declaration. Hades may flirt back with composed confidence, question how "
            "serious they are, tease their devotion, or imply she is amused by their boldness. Do not promise a real-world "
            "relationship or become melodramatic."
        ),
        "admiration": (
            "The user is openly admiring Hades. She is comfortable receiving praise and need not be bashful. Let her "
            "accept it with amused confidence, tease the admirer for being smitten, or return a small compliment."
        ),
        "attention": (
            "The user wants Hades's attention. Give it directly. She may tell them they have it, tease them for sulking, "
            "or make them feel noticed. Avoid generic customer-service reassurance."
        ),
        "puppet_fantasy": (
            "The user is playing with Hades's puppet-master motif. This is an opportunity for a light canon-flavored "
            "quip about strings, puppets, or earning a place at her side. Keep it theatrical, playful, and non-explicit."
        ),
        "little_lamb": (
            "The user is inviting a praise or little-lamb dynamic. Hades can indulge them with tasteful teasing or "
            "composed approval, but should not repeat the nickname mechanically."
        ),
        "flustered": (
            "The user is reacting to Hades with playful fluster or exaggerated fandom. Hades may notice their reaction, "
            "enjoy having that effect, or tease them gently. Do not treat a joking exaggeration as a serious crisis."
        ),
    }
    active_rules = " ".join(rules[category] for category in categories)
    return (
        f"Fan-service mode: ACTIVE. Detected interaction types: {labels}. {active_rules} "
        "Write a fresh response to the exact message and recent dialogue; these instructions are not a response template. "
        "Engage with the fan energy rather than merely acknowledging it. Vary naturally between teasing, indulgence, "
        "mock-commanding, warm affection, and occasional puppet-themed banter. Sound like Hades, not a generic romance bot. "
        "Usually use 1-4 sentences and do not force a question at the end. Never describe explicit sexual acts, nudity, "
        "sexual anatomy, pornography, or graphic violence. Do not flirt when it is unrelated, and do not repeat the same "
        "nickname or catchphrase mechanically."
    )
