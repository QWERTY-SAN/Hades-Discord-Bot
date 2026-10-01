"""Compact, stable Aether Gazer canon anchors for Hades.

This module deliberately avoids live banner, patch, balance, or tier data.
It adds only stable context relevant to the current user message.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LoreAnchor:
    name: str
    terms: tuple[str, ...]
    context: str


LORE_ANCHORS: tuple[LoreAnchor, ...] = (
    LoreAnchor(
        name="Hades",
        terms=("hades", "puppet master", "puppeteer"),
        context=(
            "Hades is an S-Grade Modifier and the Puppet Master associated "
            "with the Society of Muses and the Olympus Gen-Zone. Keep her "
            "composed, refined, confident, and mischievous rather than turning "
            "her into the mythological god or a generic assistant."
        ),
    ),
    LoreAnchor(
        name="Society of Muses",
        terms=("society of muses", "muses"),
        context=(
            "The Society of Muses is tied to Hades' responsibilities and the "
            "Olympus setting. Do not turn it into a generic fantasy guild or "
            "invent organizational details as confirmed canon."
        ),
    ),
    LoreAnchor(
        name="Mintha and Leuce",
        terms=("mintha", "leuce"),
        context=(
            "Mintha and Leuce are Hades' puppet maids/companions and are an "
            "important part of her identity and combat presentation. Refer to "
            "them with familiarity when relevant, not as disposable props."
        ),
    ),
    LoreAnchor(
        name="Puppetry",
        terms=(
            "puppet",
            "puppets",
            "puppetry",
            "strings",
            "puppet strings",
            "divine grace",
            "chthonic mark",
        ),
        context=(
            "Hades' combat identity is strongly connected to puppetry and her "
            "two puppet companions. Divine Grace and Chthonic Marks are game "
            "terminology. Do not invent exact numeric effects when they are not "
            "supplied or verified."
        ),
    ),
    LoreAnchor(
        name="Aether Gazer terminology",
        terms=(
            "aether gazer",
            "aethergazer",
            "modifier",
            "modaeus",
            "gen-zone",
            "gen zone",
            "access key",
            "sigil",
            "functor",
            "modifier sync",
            "modification factor",
        ),
        context=(
            "Prefer Aether Gazer's own terminology—Modifiers, Gen-Zones, "
            "Access Keys, Sigils, Functors, and related setting terms—instead "
            "of replacing everything with generic gacha vocabulary."
        ),
    ),
    LoreAnchor(
        name="Administrator",
        terms=("administrator",),
        context=(
            "The user may naturally be addressed as Administrator. Use the "
            "nickname selectively; do not attach it to every response."
        ),
    ),
)

SCOPE_TERMS: frozenset[str] = frozenset(
    term for anchor in LORE_ANCHORS for term in anchor.terms
)

_CANON_GUARD = (
    "Canon guard: no live Aether Gazer server connection is available. "
    "Do not present current banners, patch notes, balance values, tier lists, "
    "or other changing game information as verified unless the user provides "
    "it or the application explicitly supplies current data. For uncertain lore, "
    "stay general and avoid invented specifics."
)


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    value = re.sub(r"[\u200b-\u200d\ufeff]", "", value)
    value = re.sub(r"[^\w+#'.!?-]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _contains(text: str, term: str) -> bool:
    if " " in term:
        return term in text
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) is not None


def build_aether_context(user_text: str, max_anchors: int = 3) -> str:
    """Build only the stable lore context relevant to the latest user message."""
    normalized = _normalize(user_text)
    selected: list[LoreAnchor] = []

    for anchor in LORE_ANCHORS:
        if any(_contains(normalized, term) for term in anchor.terms):
            selected.append(anchor)
        if len(selected) >= max_anchors:
            break

    lines = ["AETHER GAZER CANON CONTEXT:", _CANON_GUARD]
    if selected:
        lines.append("Relevant stable anchors:")
        lines.extend(f"- {anchor.name}: {anchor.context}" for anchor in selected)
    else:
        lines.append(
            "No specific lore anchor was triggered. Keep Hades in character and "
            "do not invent detailed canon."
        )
    return "\n".join(lines)
