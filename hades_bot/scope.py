from __future__ import annotations

import re
import unicodedata

from .lore import SCOPE_TERMS

# Aether Gazer / Hades terminology that is always in-scope.
HADES_TERMS = {
    "aether gazer", "aethergazer", "hades", "administrator", "modifier",
    "society of muses", "olympus", "gen-zone", "sigil", "functor",
    "mintha", "leuce", "puppet master", "aether code", "access key",
    "modification factor", "modifier sync", "divine grace", "chthonic mark",
}
HADES_TERMS.update(SCOPE_TERMS)

# Topics Hades must not discuss, even when the user mentions Hades in the same message.
# This is intentionally broader than the old specialist-only filter because the bot is
# supposed to stay focused on Aether Gazer/Hades rather than becoming a general assistant.
UNRELATED_TOPICS = {
    # Sports / racing
    "sports", "sport", "formula 1", "formula one", "f1", "motogp", "nascar", "indycar", "motorsport",
    "motor sport", "grand prix", "racing", "football", "soccer", "basketball",
    "baseball", "tennis", "volleyball", "cricket", "golf", "rugby", "hockey",
    "boxing", "mma", "ufc", "wwe", "nfl", "nba", "mlb", "nhl", "fifa",
    "premier league", "champions league", "world cup", "olympics", "super bowl",
    # Programming / technology / schoolwork
    "python", "javascript", "typescript", "java", "c++", "c#", "rust", "golang",
    "ruby", "php", "sql", "html", "css", "regex", "programming", "coding", "code",
    "script", "api", "github", "git", "docker", "linux", "windows", "computer",
    "cpu", "gpu", "ram", "ssd", "nvme", "motherboard", "router", "network",
    "fl studio", "homework", "assignment", "thesis", "essay", "calculus", "algebra",
    "statistics", "physics", "chemistry", "biology",
    # News / politics / finance / practical advice
    "politics", "politician", "election", "president", "government", "news", "headline",
    "weather", "forecast", "stock market", "stocks", "crypto", "bitcoin", "cryptocurrency",
    "investment", "taxes", "mortgage", "insurance", "recipe", "cooking", "restaurant",
    "travel", "flight", "hotel", "shopping", "product recommendation",
    # Other entertainment / unrelated franchises
    "anime", "manga", "genshin", "honkai", "pokemon", "minecraft", "fortnite", "valorant",
    "league of legends", "star wars", "marvel", "dc comics", "netflix", "youtube",
    "movie", "movies", "tv show", "television", "celebrity", "music", "song", "album",
}

SPECIALIST_REQUESTS = (
    re.compile(
        r"\b(?:write|build|make|create|code|debug|fix|program|implement|develop|generate|show|give|provide)\b"
        r".{0,100}\b(?:python|javascript|typescript|java|c\+\+|c#|rust|golang|ruby|php|sql|regex|html|css|api|script|source code|code snippet|discord\.py|programming)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:write|do|finish|solve|answer|complete|help with|help me with)\b.{0,80}\b"
        r"(?:my|this|the)\b.{0,50}\b(?:homework|assignment|essay|thesis|report|worksheet|exam|test)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:fix|troubleshoot|configure|set up|diagnose|repair)\b.{0,80}\b"
        r"(?:windows|linux|router|printer|network|pc|computer|server|database|driver)\b",
        re.I | re.S,
    ),
)

# Explicitly conversational messages that do not need a game keyword.
# Everything else is treated as an out-of-scope topic unless it contains Hades/Aether Gazer terms.
CASUAL_PATTERNS = (
    re.compile(r"^(?:hi|hello|hey|heyy+|yo|sup|greetings)[!.?]*$", re.I),
    re.compile(r"^(?:good morning|good afternoon|good evening|good night)[!.?]*$", re.I),
    re.compile(r"\b(?:how are you|how're you|how do you feel|are you okay|you okay)\b", re.I),
    re.compile(r"\b(?:what are you doing|what're you doing|what is up|what's up|whats up)\b", re.I),
    re.compile(r"\b(?:thank you|thanks|thx|sorry|my bad)\b", re.I),
    re.compile(r"^(?:bye|goodbye|good bye|see you|cya)[!.?]*$", re.I),
    re.compile(r"\b(?:i(?:'m| am) (?:tired|sad|happy|bored|fine|okay|ok|lonely)|miss you|love you|like you)\b", re.I),
    re.compile(r"\b(?:you're cute|you are cute|you're pretty|you are pretty|you're beautiful|you are beautiful)\b", re.I),
    re.compile(r"^(?:lol|lmao|lmfao|hehe|haha+|hahaha+)[!.?]*$", re.I),
    re.compile(r"\b(?:tell me something nice|say something nice|keep me company|talk to me)\b", re.I),
)


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    value = re.sub(r"[\u200b-\u200d\ufeff]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def _contains_any_topic(normalized: str) -> bool:
    return any(term in normalized for term in UNRELATED_TOPICS)


def is_specialist_request(text: str) -> bool:
    normalized = _normalize(text)
    return any(pattern.search(normalized) for pattern in SPECIALIST_REQUESTS)


def is_casual_conversation(text: str) -> bool:
    normalized = _normalize(text)
    return any(pattern.search(normalized) for pattern in CASUAL_PATTERNS)


def is_hades_scope_allowed(text: str) -> bool:
    normalized = _normalize(text)
    if not normalized:
        return True

    # Reject unrelated topics first. This prevents messages such as
    # "Hades, what do you think about F1?" from slipping through the Hades gate.
    if _contains_any_topic(normalized):
        return False

    # Aether Gazer / Hades is the primary subject area.
    if any(term in normalized for term in HADES_TERMS):
        return True

    # Allow only explicit social conversation outside the game.
    if is_casual_conversation(normalized):
        return True

    # Keep the specialist guard as a second layer for disguised requests.
    if is_specialist_request(normalized):
        return False

    # Everything else is outside Hades' intended scope.
    return False


def off_topic_response() -> str:
    return (
        "That's outside my little corner of the world. I'm Hades of the Society of Muses, "
        "not a general-purpose oracle. Ask me about Aether Gazer—or speak to me directly. 🎭"
    )
