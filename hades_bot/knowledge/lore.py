from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from dataclasses import dataclass

from .character_data import GAME_KNOWLEDGE, HADES_DATA, HADES_REFERENCE, SOURCE_POLICY, TERMINOLOGY


@dataclass(frozen=True, slots=True)
class LoreAnchor:
    name: str
    terms: tuple[str, ...]
    context: str


CORE_TERMS = tuple(TERMINOLOGY.get("core_terms", []))

LORE_ANCHORS = (
    LoreAnchor("Hades", ("hades", "puppet master", "puppeteer"), "Hades is the Puppet Master, an S-Grade Modifier associated with the Society of Muses and Olympus. She is the seventh member of the Astral Council in the current character reference."),
    LoreAnchor("Hades character", ("youthful witch", "astral council", "seventh member", "puppet shop", "puppet maker", "artist"), "Hades is an accomplished artist associated with puppetry and theater. Her reference profile describes her as the person actually in charge of the Society of Muses' Modifier activities and notes her menacing demeanor during Society meetings."),
    LoreAnchor("Society of Muses", ("society of muses", "muses"), "The Society of Muses is central to Hades' identity and responsibilities. Publicly it presents itself as an appraisal society for unconventional art; operationally it also monitors Source Layer stability and gathers information related to Visbanes in Omorfies."),
    LoreAnchor("Astral Council", ("astral council", "seventh member", "seventh seat"), "The Astral Council is the chief council overseeing Omorfies. Hades holds the seventh seat in the current character reference."),
    LoreAnchor("Oneiroi", ("oneiroi", "dreamshade"), "Hades brought Oneiroi into the Society of Muses, where Mintha and Leuce look after her."),
    LoreAnchor("Mintha and Leuce", ("mintha", "leuce", "leuce and mintha"), "Mintha and Leuce are Hades' puppet maids and companions and belong naturally to her world."),
    LoreAnchor("Puppetry and art", ("puppet", "puppets", "puppetry", "strings", "puppet strings", "theater", "theatre", "doll", "dolls", "art", "artist"), "Puppetry, dolls, theater, art and performance are central to Hades' identity; these are genuine interests, not merely decorative metaphors."),
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
        f"Character traits: {', '.join(role.get('traits', ['calm', 'confident', 'observant', 'mischievous', 'authoritative']))}.",
        f"Established background: {', '.join(role.get('background', ['owner of a puppet shop in Omorfies', 'later joined the Astral Council']))}.",
        f"Artistic profile: {HADES_REFERENCE.get('artistic_profile', {}).get('creative_identity', 'stored reference')}.",
        f"Society context: {HADES_REFERENCE.get('society_context', {}).get('public_role', 'stored reference')}.",
    ]


def _gameplay_context() -> list[str]:
    gameplay = HADES_REFERENCE.get("stable_gameplay", {})
    return [
        f"Access Key: {gameplay.get('access_key', 'Leuce & Mintha')}.",
        f"Exclusive Functor: {gameplay.get('exclusive_functor', 'Herald - Cerberus')}.",
        f"Aether Codes: {', '.join(gameplay.get('aether_codes', [])) or 'stored reference'}.",
        f"Key mechanics: {', '.join(gameplay.get('signature_mechanics', [])) or 'stored reference'}.",
    ]


@lru_cache(maxsize=1)
def _structured_knowledge_entries() -> tuple[tuple[str, str], ...]:
    entries: list[tuple[str, str]] = []

    def visit(value, path: tuple[str, ...]) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                visit(child, path + (str(key),))
            return
        if isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, path + (str(index),))
            return
        if value is None:
            return
        text = str(value).strip()
        if text:
            entries.append((" > ".join(part.replace("_", " ") for part in path), text[:900]))

    visit(GAME_KNOWLEDGE, ("game knowledge",))
    visit(HADES_REFERENCE, ("hades reference",))
    return tuple(entries)


def _structured_knowledge_matches(normalized: str, limit: int = 8) -> list[tuple[int, str, str]]:
    tokens = {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9'-]{2,}", normalized)
        if token not in {"the", "and", "for", "with", "about", "what", "how", "are", "does", "this", "that", "from", "tell"}
    }
    if not tokens:
        return []

    ranked: list[tuple[int, str, str]] = []
    for label, value in _structured_knowledge_entries():
        label_norm = _normalize(label)
        score = 12 if label_norm and label_norm in normalized else 0
        label_tokens = set(re.findall(r"[a-z0-9][a-z0-9'-]{2,}", label_norm))
        score += len(tokens & label_tokens) * 4
        if score:
            ranked.append((score, label, value))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return ranked[:limit]


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
    if any(_contains(normalized, term) for term in ("hades", "puppet master", "society of muses", "mintha", "leuce", "oneiroi", "dreamshade")):
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

    # Some expanded references live under nested knowledge sections rather than
    # at the top level. Keep these explicit so named-term queries receive the
    # actual stored reference instead of only the broad lore anchor.
    resources = GAME_KNOWLEDGE.get("currencies_and_resources", {})
    systems = GAME_KNOWLEDGE.get("game_systems", {})
    people = GAME_KNOWLEDGE.get("organizations_and_people", {})
    if any(_contains(normalized, term) for term in ("shifted star", "shifted stars")):
        shifted = resources.get("shifted_star")
        routine = GAME_KNOWLEDGE.get("shifted_star_routine")
        if shifted is not None:
            lines.append(f"Reference — shifted_star: {shifted}")
        if routine is not None:
            lines.append(f"Reference — shifted_star_routine: {routine}")
    if _contains(normalized, "swigs") and resources.get("swigs") is not None:
        lines.append(f"Reference — swigs: {resources['swigs']}")
    if _contains(normalized, "zero time") and systems.get("zero_time") is not None:
        lines.append(f"Reference — zero_time: {systems['zero_time']}")
    if _contains(normalized, "heimdall") and people.get("heimdall") is not None:
        lines.append(f"Reference — heimdall: {people['heimdall']}")
    if _contains(normalized, "gengchen") and people.get("gengchen") is not None:
        lines.append(f"Reference — gengchen: {people['gengchen']}")
    structured_matches = _structured_knowledge_matches(normalized)
    if structured_matches:
        lines.append("Relevant structured catalog entries:")
        for score, label, value in structured_matches:
            lines.append(f"- {label}: {value}")

    if not selected and not structured_matches:
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
