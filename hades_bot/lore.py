from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .character_data import HADES_DATA, TERMINOLOGY


@dataclass(frozen=True, slots=True)
class LoreAnchor:
    name: str
    terms: tuple[str, ...]
    context: str


LORE_ANCHORS = (
    LoreAnchor(
        "Hades",
        ("hades", "puppet master", "puppeteer"),
        "Hades is the Puppet Master, an S-Grade Modifier associated with the Society of Muses and Olympus.",
    ),
    LoreAnchor(
        "Society of Muses",
        ("society of muses", "muses"),
        "The Society of Muses is central to Hades' identity and responsibilities. Avoid inventing unverified organizational details.",
    ),
    LoreAnchor(
        "Mintha and Leuce",
        ("mintha", "leuce"),
        "Mintha and Leuce are Hades' puppet maids/companions and should be treated with familiarity when relevant.",
    ),
    LoreAnchor(
        "Puppetry",
        ("puppet", "puppets", "puppetry", "strings", "puppet strings"),
        "Puppetry is a core part of Hades' identity and combat presentation.",
    ),
    LoreAnchor(
        "Aether Gazer systems",
        tuple(TERMINOLOGY.get("core_terms", [])),
        "Prefer Aether Gazer's own terminology rather than replacing it with generic gacha terminology.",
    ),
)

SCOPE_TERMS = frozenset(term for anchor in LORE_ANCHORS for term in anchor.terms)

_CANON_GUARD = (
    "No live game-server connection is available. Do not present current banners, patch notes, balance values, "
    "tier lists, or other changing information as verified unless supplied by application data or the user."
)


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    value = re.sub(r"[\u200b-\u200d\ufeff]", "", value)
    return re.sub(r"[^\w+#'.!?-]+", " ", value).strip()


def _contains(text: str, term: str) -> bool:
    if " " in term:
        return term in text
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) is not None


def build_aether_context(user_text: str, max_anchors: int = 4) -> str:
    normalized = _normalize(user_text)
    selected: list[LoreAnchor] = []

    for anchor in LORE_ANCHORS:
        if any(_contains(normalized, term) for term in anchor.terms):
            selected.append(anchor)
        if len(selected) >= max_anchors:
            break

    lines = ["AETHER GAZER CONTEXT:", _CANON_GUARD]
    if selected:
        lines.append("Relevant stable anchors:")
        lines.extend(f"- {anchor.name}: {anchor.context}" for anchor in selected)
    if any(_contains(normalized, term) for term in ("build", "sigil", "functor", "aether code")):
        lines.append("- Hades-specific reference data is available locally; do not treat it as live patch data.")
        lines.append(
            f"- Known Hades identity: {HADES_DATA.get('title', 'Puppet Master')} / "
            f"{HADES_DATA.get('rank', 'S-Grade Modifier')}"
        )
    if not selected:
        lines.append("No specific lore anchor matched. Stay in character and do not invent detailed canon.")
    return "\n".join(lines)
