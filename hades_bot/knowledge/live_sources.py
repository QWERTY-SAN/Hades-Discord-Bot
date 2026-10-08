from __future__ import annotations

import re

from ..config import SETTINGS

# Source pages supplied/validated for this bot. Specific pages are preferred over
# broad homepages whenever the question clearly points at them.
MIMIR_HADES_PROFILE = "https://mimir.cat/puppet-master/profile"
MIMIR_HADES_BUILD = "https://mimir.cat/puppet-master/"
MIMIR_HADES_GUIDE = "https://mimir.cat/puppet-master/guides"
MIMIR_HADES_VOICE = "https://mimir.cat/puppet-master/voice"
MIMIR_TEAMS = "https://mimir.cat/teams/"
MIMIR_WORLDVIEW = "https://mimir.cat/worldview/"
MIRAHEZE_HOME = "https://aethergazer.miraheze.org/wiki/Main_Page"
FANDOM_HOME = "https://aether-gazer.fandom.com/wiki/Aether_Gazer_Wiki"
OFFICIAL_NEWS = "https://www.aethergazer.com/main/news/"

_CURRENT_PATTERNS = (
    re.compile(r"\b(?:latest|current|currently|today|tonight|now|recent|recently|up[- ]to[- ]date)\b", re.I),
    re.compile(r"\b(?:this|the)\s+(?:patch|version|update|banner|meta|season)\b", re.I),
    re.compile(r"\b(?:live|real[- ]time)\s+(?:meta|data|information|info)\b", re.I),
    re.compile(r"\bwhat(?:'s| is)\s+(?:new|changed)\b", re.I),
    re.compile(r"\b(?:who|what|which)\s+(?:should|is best|are best)\b", re.I),
    re.compile(r"\b(?:pull|summon|roll)\b.*\b(?:or|vs\.?|versus|instead|skip|save)\b", re.I),
)

_EXPLICIT_SOURCE_PATTERNS = (
    re.compile(r"\b(?:source|sources|cite|citation|according to|verify|verified|check the wiki|check mimir|check fandom|check miraheze)\b", re.I),
    re.compile(r"\b(?:mimir|miraheze|fandom)\b", re.I),
)

_BUILD_TERMS = re.compile(
    r"\b(?:build|team|teams|tier|tier list|sigil|sigils|functor|warp|aether code|enchant|meta|dps|support|teammate|synergy|rotation)\b",
    re.I,
)
_VOICE_TERMS = re.compile(
    r"\b(?:voice|voice line|voiceline|quote|quotes|speak|speaking|personality|mannerisms|how does she talk)\b",
    re.I,
)
_LORE_TERMS = re.compile(
    r"\b(?:lore|story|relationship|society of muses|astral council|omorfies|mintha|leuce|oneiroi|puppet|puppets|art|theater|theatre)\b",
    re.I,
)


def wants_live_source_refresh(text: str) -> bool:
    if not SETTINGS.live_source_refresh:
        return False
    if any(pattern.search(text) for pattern in _EXPLICIT_SOURCE_PATTERNS):
        return True
    return any(pattern.search(text) for pattern in _CURRENT_PATTERNS)


def select_live_sources(text: str) -> tuple[str, ...]:
    """Choose a compact source set to limit URL-context work and noise."""
    selected: list[str] = []

    def add(*urls: str) -> None:
        for url in urls:
            if url not in selected:
                selected.append(url)

    if _BUILD_TERMS.search(text):
        add(MIMIR_TEAMS, MIMIR_HADES_BUILD, MIMIR_HADES_GUIDE)
        if re.search(r"\b(?:latest|current|currently|today|now|meta|tier)\b", text, re.I):
            add(OFFICIAL_NEWS)
    elif _VOICE_TERMS.search(text):
        add(MIMIR_HADES_VOICE, MIMIR_HADES_PROFILE)
    elif _LORE_TERMS.search(text):
        add(MIMIR_HADES_PROFILE, MIMIR_WORLDVIEW, MIRAHEZE_HOME, FANDOM_HOME)
    else:
        add(MIMIR_HADES_PROFILE, MIMIR_TEAMS, MIRAHEZE_HOME, FANDOM_HOME, OFFICIAL_NEWS)

    return tuple(selected[: SETTINGS.live_source_max_urls])


def build_live_source_instruction(text: str) -> str | None:
    if not wants_live_source_refresh(text):
        return None

    urls = select_live_sources(text)
    sources = "\n".join(f"- {url}" for url in urls)
    return (
        "FRESH SOURCE CHECK: This request may depend on information that can change. "
        "Use the URL Context tool to inspect the source pages below before answering. "
        "Prefer the freshest relevant page over the local snapshot. Keep stable canon separate from dated guide/meta data. "
        "If the sources disagree or a page is stale, say that naturally instead of guessing. "
        "Do not claim live game-server access. Do not dump URLs into the reply unless the Administrator asks for sources.\n"
        f"SOURCE PAGES:\n{sources}"
    )
