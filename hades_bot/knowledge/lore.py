from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .character_data import GAME_KNOWLEDGE, HADES_DATA, HADES_REFERENCE, SOURCE_POLICY, TERMINOLOGY


@dataclass(frozen=True, slots=True)
class LoreAnchor:
    name: str
    terms: tuple[str, ...]
    context: str


CORE_TERMS = tuple(TERMINOLOGY.get("core_terms", []))

LORE_ANCHORS = (
    LoreAnchor("Hades", ("hades", "puppet master", "puppeteer"), "Hades is the Puppet Master, an S-Grade Modifier associated with the Society of Muses and Olympus."),
    LoreAnchor("Society of Muses", ("society of muses", "muses"), "The Society of Muses is central to Hades' identity and responsibilities."),
    LoreAnchor("Mintha and Leuce", ("mintha", "leuce", "leuce and mintha"), "Mintha and Leuce are Hades' puppet maids and companions and belong naturally to her world."),
    LoreAnchor("Puppetry and art", ("puppet", "puppets", "puppetry", "strings", "puppet strings", "theater", "theatre", "doll", "dolls"), "Puppetry, dolls, theater and performance are central to Hades' identity."),
    LoreAnchor("Aether Gazer systems", CORE_TERMS, "Prefer Aether Gazer's own terminology rather than replacing it with generic gacha terminology."),
    LoreAnchor("Gaea and layers", ("gaea", "gaea.zero", "gaea zero", "core of gaea", "idealbild", "source layer", "surface layer"), "Gaea and its named layers are distinct setting concepts."),
    LoreAnchor("Visbanes", ("visbane", "visbanes", "bane energy", "visbanic"), "Visbanes and related phenomena are core threats in the setting."),
    LoreAnchor("Regions and factions", ("sephirah zone", "ain soph", "neuhansa", "shashvat", "omorfies", "xu heng", "sasanami", "olympus", "division nine", "astral council"), "Aether Gazer's regions and factions form the broader world around the Administrator and its Modifiers."),
    LoreAnchor("Resources", ("shifted star", "shifted stars", "shifting flower", "shifting flowers", "swigs", "ain soph coin", "daily", "weekly", "monthly"), "Resource acquisition includes recurring and event income; exact totals can vary by version."),
)
SCOPE_TERMS = frozenset(term for anchor in LORE_ANCHORS for term in anchor.terms)

KNOWLEDGE_ALIASES = {
    "shifted stars": "shifted_stars",
    "shifted star": "shifted_stars",
    "shifting flowers": "shifting_flowers",
    "shifting flower": "shifting_flowers",
    "functor": "functor",
    "functors": "functor",
    "aether codes": "aether_codes",
    "access key": "access_key",
    "gen-zone": "gen_zone",
    "gen zone": "gen_zone",
    "modifier": "modifier",
    "modifiers": "modifier",
    "society of muses": "society_of_muses",
}


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    value = re.sub(r"[\u200b-\u200d\ufeff]", "", value)
    return re.sub(r"[^\w+#'.!?-]+", " ", value).strip()


def _contains(text: str, term: str) -> bool:
    if " " in term or any(ch in term for ch in ".+-"):
        return term in text
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) is not None


def _identity_context() -> list[str]:
    identity = HADES_REFERENCE.get("identity", {})
    role = HADES_REFERENCE.get("role_and_character", {})
    return [
        f"Identity: {identity.get('name', 'Hades')}, {identity.get('title', 'Puppet Master')}.",
        f"Affiliation: {identity.get('affiliation', 'Society of Muses')}; Gen-Zone: {identity.get('gen_zone', 'Olympus')}.",
        f"Element/resource: {identity.get('element', 'Shadow')} / {identity.get('combat_resource', 'Divine Grace')}.",
        f"Known companions: {', '.join(role.get('relationship_notes', {}).keys()) or 'Mintha and Leuce'}.",
        f"Character interests: {', '.join(identity.get('likes', ['Puppets', 'Theater performances']))}.",
    ]


def _gameplay_context() -> list[str]:
    gameplay = HADES_REFERENCE.get("stable_gameplay", {})
    return [
        f"Access Key: {gameplay.get('access_key', 'Leuce & Mintha')}.",
        f"Exclusive Functor: {gameplay.get('exclusive_functor', 'Herald - Cerberus')}.",
        f"Aether Codes: {', '.join(gameplay.get('aether_codes', [])) or 'stored reference'}.",
        f"Key mechanics: {', '.join(gameplay.get('signature_mechanics', [])) or 'stored reference'}.",
    ]


def build_aether_context(user_text: str, conversation_text: str = "", max_chars: int = 9000) -> str:
    source_text = " ".join(part for part in (conversation_text, user_text) if part).strip()
    normalized = _normalize(source_text)
    scored = []
    for index, anchor in enumerate(LORE_ANCHORS):
        score = sum(max(1, min(8, len(term.split()) * 2)) for term in anchor.terms if _contains(normalized, term))
        if score:
            scored.append((score, index, anchor))
    scored.sort(key=lambda item: (-item[0], item[1]))
    selected = [item[2] for item in scored[:6]]

    lines = [
        "AETHER GAZER REFERENCE CONTEXT:",
        "Stored reference is a local snapshot, not a live game connection. Do not present banners, live schedules, current balance, or live recommendations as verified unless fresh data is supplied.",
        "Source policy: " + " ".join(SOURCE_POLICY.get("rules", [])),
    ]
    if selected:
        lines.append("Relevant stable anchors:")
        lines.extend(f"- {anchor.name}: {anchor.context}" for anchor in selected)
    if any(_contains(normalized, term) for term in ("hades", "puppet master", "society of muses", "mintha", "leuce")):
        lines.append("Hades identity reference:")
        lines.extend(f"- {item}" for item in _identity_context())
    if any(_contains(normalized, term) for term in ("build", "sigil", "functor", "aether code", "access key", "skill", "divine grace")):
        lines.append("Hades gameplay reference:")
        lines.extend(f"- {item}" for item in _gameplay_context())
    for alias, key in KNOWLEDGE_ALIASES.items():
        if _contains(normalized, alias):
            value = GAME_KNOWLEDGE.get(key)
            if value is not None:
                lines.append(f"Reference — {key}: {value}")
    if not selected:
        lines.append("No detailed lore anchor matched. Stay in character without inventing detailed canon.")

    output: list[str] = []
    total = 0
    for line in lines:
        cost = len(line) + 1
        if total + cost > max_chars:
            break
        output.append(line)
        total += cost
    return "\n".join(output)
