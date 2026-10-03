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


LORE_ANCHORS = (
    LoreAnchor(
        "Hades",
        ("hades", "puppet master", "puppeteer"),
        "Hades is the Puppet Master, an S-Grade Modifier of the Society of Muses in Olympus.",
    ),
    LoreAnchor(
        "Society of Muses",
        ("society of muses", "muses"),
        "Hades manages the Society of Muses and is described in the reference data as the person actually in charge of its Modifier activities.",
    ),
    LoreAnchor(
        "Astral Council and Omorfies",
        ("astral council", "omorfies"),
        "Hades has established ties to the Astral Council and Omorfies in the supplied character reference material.",
    ),
    LoreAnchor(
        "Mintha and Leuce",
        ("mintha", "leuce", "leuce & mintha"),
        "Mintha and Leuce are Hades' puppet maids and companions. They also serve the Society of Muses and become her weapons in combat.",
    ),
    LoreAnchor(
        "Oneiroi",
        ("oneiroi", "drowsie", "dream luminous"),
        "Oneiroi is connected to Hades through the Society of Muses and Hades' story/skillchain material.",
    ),
    LoreAnchor(
        "Puppetry and art",
        ("puppet", "puppets", "puppetry", "strings", "puppet strings", "theater", "art"),
        "Puppetry, theater and art are recurring parts of Hades' character presentation and dialogue.",
    ),
    LoreAnchor(
        "Aether Gazer world",
        tuple(TERMINOLOGY.get("core_terms", [])),
        "Prefer Aether Gazer's own terminology: Modifiers, Gen-Zones, Access Keys, Sigils, Functors, Aether Codes, Source Layer, Idealbild, Gaea and Visbanes.",
    ),
    LoreAnchor(
        "Hades gameplay",
        tuple(TERMINOLOGY.get("hades_terms", [])),
        "Hades gameplay reference includes Divine Grace, Chthonic Marks, Dance Partner, Dance Duo, Aether Codes and her Leuce & Mintha Access Key.",
    ),
)

SCOPE_TERMS = frozenset(term for anchor in LORE_ANCHORS for term in anchor.terms)


KNOWLEDGE_ALIASES = {
    "shifted stars": "shifted_star",
    "shifted star": "shifted_star",
    "shifting flowers": "shifting_flower",
    "shifting flower": "shifting_flower",
    "swigs": "swigs",
    "ain soph coin": "ain_soph_coin",
    "daily missions": "shifted_star_routine",
    "weekly missions": "shifted_star_routine",
    "monthly": "shifted_star_routine",
    "daily": "shifted_star_routine",
    "weekly": "shifted_star_routine",
    "modifier sync": "modifier_sync",
    "modified mode": "modified_mode",
    "zero time": "zero_time",
    "warp skills": "warp",
    "support modules": "support_modules",
    "eos": "service_lifecycle",
    "eou": "service_lifecycle",
    "end of service": "service_lifecycle",
    "end of updates": "service_lifecycle",
    "end of content": "service_lifecycle",
    "companion server": "service_lifecycle",
    "v5.2": "service_lifecycle",
    "version 5.2": "service_lifecycle",
    "2031": "service_lifecycle",
    "team": "current_team_snapshot",
    "team comp": "current_team_snapshot",
    "team composition": "current_team_snapshot",
    "teammates": "current_team_snapshot",
}

ENTITY_ALIASES = {
    "odin": "odin",
    "heimdall": "heimdall",
    "shu": "shu",
    "poseidon": "poseidon",
    "tsukuyomi": "tsukuyomi",
    "skuld": "skuld",
    "gengchen": "gengchen",
    "lingguang": "lingguang",
    "izanami": "izanami",
    "hera": "hera",
}

_CANON_GUARD = (
    "Reference data is a stored snapshot, not a live game connection. Do not present current banners, patch notes, balance values, tier lists, or live recommendations as verified unless fresh application data is supplied."
)

_SOURCE_POLICY = " ".join(SOURCE_POLICY.get("rules", []))


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    value = re.sub(r"[\u200b-\u200d\ufeff]", "", value)
    return re.sub(r"[^\w+#'.!?-]+", " ", value).strip()


def _contains(text: str, term: str) -> bool:
    if " " in term:
        return term in text
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) is not None


def _identity_context() -> list[str]:
    identity = HADES_REFERENCE.get("identity", {})
    role = HADES_REFERENCE.get("role_and_character", {})
    companions = role.get("relationship_notes", {})
    return [
        f"Identity: {identity.get('name', HADES_DATA.get('name', 'Hades'))}, {identity.get('title', HADES_DATA.get('title', 'Puppet Master'))}.",
        f"Affiliation: {identity.get('affiliation', HADES_DATA.get('affiliation', 'Society of Muses'))}; Gen-Zone: {identity.get('gen_zone', HADES_DATA.get('gen_zone', 'Olympus'))}.",
        f"Element/resource: {identity.get('element', HADES_DATA.get('element', 'Shadow'))} / {identity.get('combat_resource', HADES_DATA.get('combat_resource', 'Divine Grace'))}.",
        f"Known companions: {', '.join(companions.keys()) or 'Mintha and Leuce'}.",
        f"Character interests: {', '.join(identity.get('likes', ['Puppets', 'Theater performances']))}.",
    ]


def _gameplay_context() -> list[str]:
    gameplay = HADES_REFERENCE.get("stable_gameplay", {})
    codes = ", ".join(gameplay.get("aether_codes", []))
    mechanics = ", ".join(gameplay.get("signature_mechanics", []))
    return [
        f"Access Key: {gameplay.get('access_key', 'Leuce & Mintha')}.",
        f"Exclusive Functor: {gameplay.get('exclusive_functor', 'Herald - Cerberus')}.",
        f"Aether Codes: {codes}.",
        f"Key mechanics: {mechanics}.",
    ]


def _dated_guide_context() -> list[str]:
    guide = HADES_REFERENCE.get("dated_build_reference", {})
    source_date = guide.get("source_last_update", "unknown")
    sigils = guide.get("standard_dps_sigils", {})
    codes = guide.get("aether_code_guidance", {})
    sigil_135 = sigils.get('slots_1_3_5', 'Mooncrown')
    sigil_246 = sigils.get('slots_2_4_6', "Acheron's Obol")
    return [
        f"DATED GUIDE SNAPSHOT ({source_date}): Standard DPS Sigils are {sigil_135} in slots 1/3/5 and {sigil_246} in slots 2/4/6.",
        f"DATED GUIDE SNAPSHOT ({source_date}): Aether Code guidance lists Red={codes.get('red', 'Deliberation Unspoken')}, Blue={codes.get('blue', 'Boundary Unseen')}, Yellow={codes.get('yellow', 'Hoax Unheard')}.",
        "These dated recommendations must be described as dated reference material, not as the current live meta.",
    ]


def _knowledge_context(normalized: str) -> list[str]:
    lines: list[str] = []
    systems = GAME_KNOWLEDGE.get("game_systems", {})
    resources = GAME_KNOWLEDGE.get("currencies_and_resources", {})
    world = GAME_KNOWLEDGE.get("world_and_setting", {})
    people = GAME_KNOWLEDGE.get("organizations_and_people", {})

    for alias, key in KNOWLEDGE_ALIASES.items():
        if _contains(normalized, alias):
            if key == "shifted_star_routine":
                routine = GAME_KNOWLEDGE.get("shifted_star_routine", {})
                lines.append("Shifted Star routine reference:")
                for cadence in ("daily", "weekly", "monthly"):
                    items = "; ".join(routine.get(cadence, []))
                    lines.append(f"- {cadence.title()}: {items}")
                lines.append(f"- Accuracy rule: {routine.get('accuracy_rule', '')}")
            elif key in resources:
                value = resources[key]
                if isinstance(value, dict):
                    lines.append(f"{key}: {value.get('role', '')} {value.get('lore_note', '')} {value.get('farming_note', '')}".strip())
                else:
                    lines.append(f"{key}: {value}")
            elif key == "current_team_snapshot":
                snapshot = HADES_REFERENCE.get("current_team_snapshot", {})
                if snapshot:
                    lines.append(f"DATED CURRENT TEAM SNAPSHOT ({snapshot.get('source_last_update', 'unknown')}): {', '.join(snapshot.get('team', []))}.")
                    lines.append(snapshot.get("snapshot_note", ""))
            elif key == "service_lifecycle":
                lifecycle = GAME_KNOWLEDGE.get("service_lifecycle", {})
                global_info = lifecycle.get("global", {})
                china_info = lifecycle.get("china", {})
                lines.append("SERVICE LIFECYCLE SNAPSHOT (checked 2026-10-04):")
                lines.append(f"- EoU/EOS distinction: {lifecycle.get('terminology', {}).get('eou', '')}")
                lines.append(f"- Global: {global_info.get('status_as_of_snapshot', '')}")
                lines.append(f"- Global final content update: {global_info.get('final_content_update', '')} on {global_info.get('final_content_update_date', '')}.")
                lines.append(f"- Global after V5.2: {global_info.get('after_v5_2', '')}")
                lines.append(f"- Global Companion Server: {global_info.get('companion_server', '')} Planned horizon: {global_info.get('planned_service_period_end', '')}.")
                lines.append(f"- Global reassessment: {global_info.get('reassessment', '')}")
                lines.append(f"- CN: final content update {china_info.get('final_content_update', '')} on {china_info.get('final_content_update_date', '')}; Companion Server started {china_info.get('companion_server_start', '')}.")
                lines.append("- Future options must be described as possibilities, not guarantees: extension, preservation/offline client, or other arrangements.")
            elif key in systems:
                lines.append(f"{key}: {systems[key]}")
            elif key in world:
                lines.append(f"{key}: {world[key]}")

    for alias, key in ENTITY_ALIASES.items():
        if _contains(normalized, alias) and key in people:
            lines.append(f"Character reference — {alias.title()}: {people[key]}")

    return lines


def build_aether_context(user_text: str, max_anchors: int = 5) -> str:
    normalized = _normalize(user_text)
    selected: list[LoreAnchor] = []

    for anchor in LORE_ANCHORS:
        if any(_contains(normalized, term) for term in anchor.terms):
            selected.append(anchor)
        if len(selected) >= max_anchors:
            break

    lines = [
        "AETHER GAZER REFERENCE CONTEXT:",
        _CANON_GUARD,
        f"Source policy: {_SOURCE_POLICY}",
    ]

    if selected:
        lines.append("Relevant stable anchors:")
        lines.extend(f"- {anchor.name}: {anchor.context}" for anchor in selected)

    if any(
        _contains(normalized, term)
        for term in (
            "hades",
            "puppet master",
            "society of muses",
            "astral council",
            "omorfies",
            "mintha",
            "leuce",
        )
    ):
        lines.append("Hades identity reference:")
        lines.extend(f"- {item}" for item in _identity_context())

    if any(
        _contains(normalized, term)
        for term in (
            "build",
            "sigil",
            "functor",
            "aether code",
            "access key",
            "skill",
            "divine grace",
            "chthonic mark",
            "dance duo",
            "dance partner",
        )
    ):
        lines.append("Hades gameplay reference:")
        lines.extend(f"- {item}" for item in _gameplay_context())
        lines.extend(f"- {item}" for item in _dated_guide_context())

    knowledge_lines = _knowledge_context(normalized)
    if knowledge_lines:
        lines.append("Additional Aether Gazer knowledge:")
        lines.extend(f"- {item}" for item in knowledge_lines[:12])

    if not selected and not knowledge_lines:
        lines.append("No detailed lore anchor matched. Stay in character without inventing detailed canon.")

    return "\n".join(lines)
