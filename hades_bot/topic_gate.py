from __future__ import annotations

import re


# Strong Aether Gazer signals. These are deliberately broad enough to catch
# character/lore discussion without requiring the exact phrase "Aether Gazer".
AETHER_TERMS = (
    "aether gazer",
    "aethergazer",
    "hades",
    "blade",
    "thoth",
    "anubis",
    "sekhem",
    "sekmet",
    "jinwu",
    "julius",
    "lingguang",
    "gengchen",
    "buzenbo",
    "kuramitsuha",
    "tsukuyomi",
    "skuld",
    "verthandi",
    "wafers",
    "puppeteer",
    "olympus",
    "society of muses",
    "modifier",
    "modifiers",
    "visbanes",
    "mintha",
    "leuce",
    "administrator",
    "little lamb",
    "gen-zone",
    "genzone",
    "skuld",
    "verthandi",
    "thor",
    "tsukuyomi",
    "buzenbo",
    "corgh",
    "osiris",
    "poseidon",
    "lingguang",
    "selene",
    "waden",
    "apollo",
    "hera",
    "hera",
    "artemis",
    "shu",
    "tian luo",
    "zenki",
    "nile",
    "shinou",
    "astrolabe",
    "past grudge",
    "visbanes",
    "source layer",
    "sephirah",
    "administrator",
)

# Explicitly non-Aether contexts that can otherwise collide with the name Hades.
EXPLICIT_NON_AETHER = (
    "greek mythology",
    "greek god",
    "mythological hades",
    "hades game",
    "supergiant games",
    "underworld mythology",
    "disney hades",
    "blade runner",
)

# Requests that clearly seek general-purpose information rather than casual
# conversation with Hades.
REQUEST_PREFIXES = (
    "what is ",
    "what are ",
    "what's ",
    "who is ",
    "who are ",
    "where is ",
    "where are ",
    "when is ",
    "when was ",
    "why is ",
    "why are ",
    "how does ",
    "how do ",
    "how can i ",
    "how can you ",
    "how to ",
    "explain ",
    "tell me about ",
    "tell me how ",
    "give me ",
    "show me ",
    "write ",
    "generate ",
    "create ",
    "make ",
    "fix ",
    "debug ",
    "calculate ",
    "compare ",
    "recommend ",
    "teach me ",
)

# Obvious technical/programming/off-domain requests. These are blocked even if
# the wording is not phrased as a question.
HARD_OFF_TOPIC = (
    "programming",
    "programmer",
    "python",
    "javascript",
    "typescript",
    "java code",
    "c++",
    "c#",
    "rust code",
    "golang",
    "html",
    "css",
    "sql",
    "regex",
    "source code",
    "discord bot code",
    "write code",
    "fix my code",
    "debug this code",
    "homework",
    "math problem",
    "solve this equation",
    "pc build",
    "graphics card",
    "cpu",
    "gpu",
    "router",
    "networking",
    "stock price",
    "crypto price",
    "bitcoin",
    "weather today",
    "politics",
    "president",
    "election",
    "genshin impact",
    "honkai star rail",
    "minecraft",
    "league of legends",
    "valorant",
)

SOCIAL_PATTERNS = (
    r"^(hi|hello|hey|yo|hiya|sup|good morning|good afternoon|good evening)[!.?\s]*$",
    r"^(lol|lmao|lmfao|haha|hehe|bruh|damn|wow|what|huh|okay|ok|alright)[!.?\s]*$",
    r"^(how are you|how are you doing|what are you doing|are you okay)[!?.,\s]*$",
    r"^(i miss you|i like you|i love you|i'm bored|im bored)[!.?\s]*$",
)


def _contains_term(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def is_social_message(text: str) -> bool:
    compact = " ".join(text.lower().split())
    return any(re.match(pattern, compact) for pattern in SOCIAL_PATTERNS)


def is_aether_gazer_related(text: str) -> bool:
    """Return True when content is clearly in Hades/Aether Gazer scope.

    Casual/social messages are allowed because the bot is still having a
    conversation with the user, but substantive off-topic information requests
    should not reach Gemini.
    """
    normalized = " ".join(text.lower().split())

    if not normalized:
        return True

    if is_social_message(normalized):
        return True

    if "```" in normalized:
        return False

    if _contains_term(normalized, EXPLICIT_NON_AETHER):
        return False

    if _contains_term(normalized, HARD_OFF_TOPIC):
        return False

    if _contains_term(normalized, AETHER_TERMS):
        return True

    # Personal conversation addressed to Hades can remain conversational,
    # but do not treat arbitrary factual questions as in-domain.
    personal_patterns = (
        r"\b(do you|are you|did you|would you|could you|can you|have you)\b.*\b(you|your|hades)\b",
        r"\b(what do you think|how do you feel|do you like|do you hate|are you afraid)\b",
        r"\b(administrator|little lamb)\b",
    )

    if any(re.search(pattern, normalized) for pattern in personal_patterns):
        return True

    # A clear informational request without an Aether signal is off-topic.
    if normalized.endswith("?") or normalized.startswith(REQUEST_PREFIXES):
        return False

    # Statements, jokes, reactions, and ordinary conversation can continue in
    # character; they are not treated as requests for general information.
    return True


OFF_TOPIC_RESPONSES = (
    "You're wandering rather far from my world, Administrator.",
    "That's hardly a subject for Hades, little lamb.",
    "You've brought me quite an unrelated question.",
    "Why are you asking me about that?",
    "That's not really my concern.",
    "You summoned Hades for that? How curious.",
    "If you want my attention, choose a more fitting subject.",
    "You've strayed rather far from Olympus.",
)
