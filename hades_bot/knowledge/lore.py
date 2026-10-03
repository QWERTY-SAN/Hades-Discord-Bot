from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable

from .character_data import GAME_KNOWLEDGE, HADES_DATA, HADES_REFERENCE, SOURCE_POLICY, TERMINOLOGY


@dataclass(frozen=True, slots=True)
class LoreAnchor:
    name: str
    terms: tuple[str, ...]
    context: str


LORE_ANCHORS = (
    LoreAnchor("Hades", ("hades", "puppet master", "puppeteer"), "Hades is the Puppet Master, an S-Grade Modifier associated with the Society of Muses and Olympus."),
    LoreAnchor("Society of Muses", ("society of muses", "muses"), "The Society of Muses is central to Hades' identity and responsibilities."),
    LoreAnchor("Mintha and Leuce", ("mintha", "leuce", "leuce and mintha"), "Mintha and Leuce are Hades' puppet maids/companions and serve the Society of Muses."),
    LoreAnchor("Hades character life", ("youthful witch", "puppet shop", "puppet store", "gift from hades", "nighttime iris", "lantern of lethe", "lazy vacation"), "Hades' reference profile includes her puppet-making life, Heart Link story material, and named outfits."),
    LoreAnchor("Hades Ultimate Skillchains", ("fantoccini fancy", "dream luminous", "grand finale", "ultimate skillchain"), "Hades has named Ultimate Skillchains tied to Oneiroi and her Shadow-focused playstyle. Exact effects are version-sensitive and should come from the stored current profile when available."),
    LoreAnchor("Puppetry and art", ("puppet", "puppets", "puppetry", "strings", "puppet strings", "theater", "theatre", "doll", "dolls"), "Puppetry, dolls, theater and performance are central to Hades' identity."),
    LoreAnchor("Aether Gazer systems", tuple(TERMINOLOGY.get("core_terms", [])), "Prefer Aether Gazer's own terminology rather than replacing it with generic gacha terminology."),
    LoreAnchor("Gaea and layers", ("gaea", "gaea.zero", "gaea zero", "core of gaea", "idealbild", "source layer", "surface layer"), "Gaea, Gaea.Zero, Core of Gaea, Idealbild, Source Layer and Surface Layer are distinct named concepts in the setting."),
    LoreAnchor("Visbanes and Bane Energy", ("visbane", "visbanes", "bane energy", "visbanic agi mecha", "corrosion", "quakes"), "Visbanes and related phenomena are core threats and setting concepts."),
    LoreAnchor("Regions and factions", ("sephirah zone", "ain soph", "neuhansa", "shashvat", "omorfies", "xu heng", "sasanami", "olympus", "division nine", "astral council", "quad"), "Aether Gazer's regions and factions form the broader world around the Administrator and its Modifiers."),
    LoreAnchor("Endgame systems", ("recurring dream", "hazard zone", "dimensional variable", "iterative testing", "past grudges", "causality survey", "ancient shadow", "crisis analysis"), "Aether Gazer's late game combines recurring challenge modes with versional event challenges; exact schedules and reward tables are version-sensitive."),
    LoreAnchor("Resources and farming", ("shifted star", "shifted stars", "shifting flower", "shifting flowers", "swigs", "ain soph coin", "daily", "weekly", "monthly"), "Resource farming includes recurring, one-time, event and achievement income; exact totals vary by version and server."),
    LoreAnchor("Auxiliary systems", ("m.e.o.w.", "meow", "support module", "support modules", "opponent intel", "sigil enchants", "battle sweep", "flaneuring", "music dossier"), "Auxiliary systems support account progression and collection; exact unlocks and effects are version-sensitive."),
)
SCOPE_TERMS = frozenset(term for anchor in LORE_ANCHORS for term in anchor.terms)

KNOWLEDGE_ALIASES = {
    "shifted stars": "shifted_star", "shifted star": "shifted_star",
    "shifting flowers": "shifting_flower", "shifting flower": "shifting_flower",
    "swigs": "swigs", "ain soph coin": "ain_soph_coin", "coolant": "coolant",
    "divine factor": "divine_factor", "sigil material": "sigil_materials",
    "daily missions": "shifted_star_routine", "weekly missions": "shifted_star_routine",
    "monthly": "shifted_star_routine", "daily": "shifted_star_routine", "weekly": "shifted_star_routine",
    "modifier sync": "modifier_sync", "modified mode": "modified_mode", "zero time": "zero_time",
    "warp skills": "warp", "support modules": "support_modules", "sigil enchants": "sigil_enchants",
    "functor": "functor", "functors": "functor", "aether codes": "aether_code", "access key": "access_key",
    "transcendence": "transcend", "modifier": "modifier", "gen-zone": "gen_zone", "gen zone": "gen_zone",
    "ancient shadow": "ancient_shadow", "nightmare shadows": "ancient_shadow",
    "crisis analysis": "crisis_analysis", "recurring dream": "recurring_dream",
    "hazard zone": "hazard_zone", "dimensional variable": "dimensional_variable",
    "iterative testing": "iterative_testing", "past grudges": "past_grudges",
    "causality survey": "causality_survey", "battle sweep": "battle_sweep",
    "m.e.o.w.": "meow", "meow chips": "meow", "opponent intel": "opponent_intel",
    "risk level": "opponent_intel", "flaneuring": "flaneuring", "music dossier": "music_dossier",
    "achievement": "achievements", "achievements": "achievements",
    "service lifecycle": "service_lifecycle", "eos": "service_lifecycle", "eou": "service_lifecycle",
    "end of service": "service_lifecycle", "end of updates": "service_lifecycle",
    "end of content": "service_lifecycle", "companion server": "service_lifecycle",
    "v5.2": "service_lifecycle", "version 5.2": "service_lifecycle", "2031": "service_lifecycle",
    "event": "events_and_event_endgame", "events": "events_and_event_endgame",
    "event shop": "events_and_event_endgame", "anniversary": "events_and_event_endgame",
    "f2p": "player_spending_terms", "free-to-play": "player_spending_terms", "free to play": "player_spending_terms",
    "low spender": "player_spending_terms", "dolphin": "player_spending_terms", "whale": "player_spending_terms",
    "spender": "player_spending_terms", "spending": "player_spending_terms", "scan planning": "scan_economy_conversation",
    "gacha": "scans_and_gacha", "gacha economy": "scan_economy_conversation",
    "limited time": "events_and_event_endgame", "endgame event": "events_and_event_endgame",
    "team": "current_team_snapshot", "team comp": "current_team_snapshot",
    "team composition": "current_team_snapshot", "teammates": "current_team_snapshot",
}

ENTITY_ALIASES = {
    name: name
    for name in (
        "odin", "heimdall", "shu", "poseidon", "tsukuyomi", "skuld",
        "gengchen", "lingguang", "izanami", "hera", "mintha", "leuce",
    )
}


def _dynamic_entity_aliases() -> dict[str, tuple[str, str]]:
    """Build searchable aliases from the structured knowledge database."""
    aliases: dict[str, tuple[str, str]] = {}
    sources = (
        ("Character / organization", GAME_KNOWLEDGE.get("organizations_and_people", {})),
        ("Location / zone", GAME_KNOWLEDGE.get("locations_and_zones", {})),
        ("Organization", GAME_KNOWLEDGE.get("organizations_catalog", {})),
        ("Named entity", GAME_KNOWLEDGE.get("notable_people_and_entities_index", {})),
        ("World concept", GAME_KNOWLEDGE.get("world_concepts_and_history", {})),
    )
    for label, mapping in sources:
        if not isinstance(mapping, dict):
            continue
        for raw_key in mapping:
            alias = str(raw_key).replace("_", " ").strip().casefold()
            if len(alias) < 4 or alias in {"the general", "the singer", "the monk"}:
                continue
            aliases.setdefault(alias, (label, raw_key))
    return aliases


def _structured_scope_terms() -> frozenset[str]:
    """Make the scope gate aware of names and systems already present in the data layer."""
    terms = set(SCOPE_TERMS)
    sections = (
        "world_and_setting", "game_systems", "currencies_and_resources",
        "organizations_and_people", "endgame_and_late_game", "locations_and_zones",
        "organizations_catalog", "notable_people_and_entities_index",
        "world_concepts_and_history", "combat_and_progression_reference",
        "support_and_auxiliary_systems", "content_catalog",
    )
    for section_name in sections:
        mapping = GAME_KNOWLEDGE.get(section_name, {})
        if isinstance(mapping, dict):
            for raw_key in mapping:
                alias = str(raw_key).replace("_", " ").strip().casefold()
                if len(alias) >= 4 and alias not in {"overview", "purpose", "rules", "accuracy rule", "source note"}:
                    terms.add(alias)
    terms.update(_dynamic_entity_aliases().keys())
    terms.update(ENTITY_ALIASES.keys())
    return frozenset(terms)


# Exported after the helpers exist so scope.py gets the full structured vocabulary.
SCOPE_TERMS = _structured_scope_terms()
_CANON_GUARD = "Reference data is a stored snapshot, not a live game connection. Do not present current banners, patch notes, balance values, tier lists, or live recommendations as verified unless fresh application data is supplied."
_SOURCE_POLICY = " ".join(SOURCE_POLICY.get("rules", []))


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
    profile = HADES_REFERENCE.get("profile_snapshot", {})
    return [
        f"Identity: {identity.get('name', 'Hades')}, {identity.get('title', 'Puppet Master')}.",
        f"Affiliation: {identity.get('affiliation', 'Society of Muses')}; Gen-Zone: {identity.get('gen_zone', 'Olympus')}.",
        f"Element/resource: {identity.get('element', 'Shadow')} / {identity.get('combat_resource', 'Divine Grace')}.",
        f"Known companions: {', '.join(role.get('relationship_notes', {}).keys()) or 'Mintha and Leuce'}.",
        f"Character interests: {', '.join(identity.get('likes', ['Puppets', 'Theater performances']))}.",
        f"Profile snapshot: {profile.get('last_update', 'unknown')}.",
    ]


def _gameplay_context() -> list[str]:
    gameplay = HADES_REFERENCE.get("stable_gameplay", {})
    profile = HADES_REFERENCE.get("profile_snapshot", {})
    codes = ", ".join(gameplay.get("aether_codes", []))
    mechanics = ", ".join(gameplay.get("signature_mechanics", []))
    return [
        f"Access Key: {gameplay.get('access_key', 'Leuce & Mintha')}.",
        f"Exclusive Functor: {gameplay.get('exclusive_functor', 'Herald - Cerberus')}.",
        f"Aether Codes: {codes}.",
        f"Key mechanics: {mechanics}.",
        f"Current profile named outfits: {', '.join(profile.get('outfits', [])) or 'not stored'}.",
        f"Heart Link event: {profile.get('heart_link_event', 'not stored')}.",
        f"Access Key synergy: {profile.get('access_key_synergy', 'not stored')}.",
        f"Hades chips: {', '.join(profile.get('chips', [])) or 'not stored'}.",
    ]


def _dated_guide_context() -> list[str]:
    guide = HADES_REFERENCE.get("dated_build_reference", {})
    source_date = guide.get("source_last_update", "unknown")
    sigils = guide.get("standard_dps_sigils", {})
    codes = guide.get("aether_code_guidance", {})
    slot135 = sigils.get("slots_1_3_5", "Mooncrown")
    slot246 = sigils.get("slots_2_4_6", "Acheron's Obol")
    return [
        f"DATED GUIDE SNAPSHOT ({source_date}): Standard DPS Sigils are {slot135} in slots 1/3/5 and {slot246} in slots 2/4/6.",
        f"DATED GUIDE SNAPSHOT ({source_date}): Aether Code guidance lists Red={codes.get('red', 'Deliberation Unspoken')}, Blue={codes.get('blue', 'Boundary Unseen')}, Yellow={codes.get('yellow', 'Hoax Unheard')}.",
        "These dated recommendations must be described as dated reference material, not as the current live meta.",
    ]


def _append_value(lines: list[str], key: str, value: object) -> None:
    if isinstance(value, dict):
        role = value.get("role", "")
        lore = value.get("lore_note", "")
        farming = value.get("farming_note", "")
        knowledge = value.get("knowledge", "")
        advice = value.get("advice", "")
        current = value.get("current", "")
        text = " ".join(part for part in (role, lore, farming, knowledge, advice, current) if part)
        lines.append(f"{key}: {text}" if text else f"{key}: {value}")
    else:
        lines.append(f"{key}: {value}")


def _knowledge_context(normalized: str) -> list[str]:
    lines: list[str] = []
    systems = GAME_KNOWLEDGE.get("game_systems", {})
    resources = GAME_KNOWLEDGE.get("currencies_and_resources", {})
    world = GAME_KNOWLEDGE.get("world_and_setting", {})
    people = GAME_KNOWLEDGE.get("organizations_and_people", {})
    endgame = GAME_KNOWLEDGE.get("endgame_and_late_game", {})
    support = GAME_KNOWLEDGE.get("support_and_auxiliary_systems", {})

    for alias, key in KNOWLEDGE_ALIASES.items():
        if not _contains(normalized, alias):
            continue
        if key == "shifted_star_routine":
            routine = GAME_KNOWLEDGE.get("shifted_star_routine", {})
            lines.append("Shifted Star routine reference:")
            for cadence in ("daily", "weekly", "monthly"):
                items = "; ".join(routine.get(cadence, []))
                lines.append(f"- {cadence.title()}: {items}")
            lines.append(f"- Accuracy rule: {routine.get('accuracy_rule', '')}")
        elif key == "current_team_snapshot":
            snapshot = HADES_REFERENCE.get("current_team_snapshot", {})
            if snapshot:
                lines.append(f"DATED CURRENT TEAM SNAPSHOT ({snapshot.get('source_last_update', 'unknown')}): {', '.join(snapshot.get('team', []))}.")
                lines.append(snapshot.get("snapshot_note", ""))
        elif key == "service_lifecycle":
            lifecycle = GAME_KNOWLEDGE.get("service_lifecycle", {})
            global_info = lifecycle.get("global", {})
            china_info = lifecycle.get("china", {})
            lines.append(f"SERVICE LIFECYCLE SNAPSHOT ({lifecycle.get('current_snapshot_date', 'unknown')}):")
            lines.append(f"- Global: {global_info.get('status_as_of_snapshot', '')}")
            lines.append(f"- Global final content update: {global_info.get('final_content_update', '')} on {global_info.get('final_content_update_date', '')}.")
            lines.append(f"- Global after V5.2: {global_info.get('after_v5_2', '')}")
            lines.append(f"- CN: final content update {china_info.get('final_content_update', '')} on {china_info.get('final_content_update_date', '')}; Companion Server started {china_info.get('companion_server_start', '')}.")
            lines.append("Future options must be described as possibilities, not guarantees.")
        elif key in resources:
            _append_value(lines, key, resources[key])
        elif key in systems:
            _append_value(lines, key, systems[key])
        elif key in world:
            _append_value(lines, key, world[key])
        elif key in endgame:
            _append_value(lines, key, endgame[key])
        elif key == "player_spending_terms":
            spending = GAME_KNOWLEDGE.get("scans_and_gacha", {}).get("player_spending_terms", {})
            lines.append(f"Player spending terminology: {spending.get('overview', '')}")
            for field in ("f2p", "low_spender", "dolphin", "whale", "spender", "terminology_rule", "gameplay_rule"):
                if spending.get(field):
                    lines.append(f"- {field.replace('_', ' ').title()}: {spending[field]}")
        elif key == "scan_economy_conversation":
            lines.append(GAME_KNOWLEDGE.get("scans_and_gacha", {}).get("scan_economy_conversation", ""))
        elif key == "events_and_event_endgame":
            events = GAME_KNOWLEDGE.get("events_and_event_endgame", {})
            lines.append(f"Event-system reference: {events.get('overview', '')}")
            lines.append(f"Version event structure: {events.get('version_event_structure', '')}")
            lines.append(f"Endgame event types: {'; '.join(events.get('endgame_event_types', []))}")
            lines.append(f"Known 2026 examples: {'; '.join(events.get('known_2026_examples', []))}")
            lines.append(f"Accuracy rule: {events.get('companion_server_rule', '')}")
        elif key == "support_modules":
            _append_value(lines, key, support.get("support_modules", {}))
        elif key in GAME_KNOWLEDGE.get("combat_and_progression_reference", {}):
            _append_value(lines, key, GAME_KNOWLEDGE["combat_and_progression_reference"][key])
        elif key in support:
            _append_value(lines, key, support[key])

    # Explicit and dynamically indexed named entities. This means follow-up
    # questions can retrieve more than the small hand-written character list.
    dynamic_entities = _dynamic_entity_aliases()
    seen_entities: set[str] = set()
    for alias, key in ENTITY_ALIASES.items():
        if _contains(normalized, alias) and key in people:
            lines.append(f"Character reference — {alias.title()}: {people[key]}")
            seen_entities.add(alias)
    for alias, (label, raw_key) in dynamic_entities.items():
        if alias in seen_entities or not _contains(normalized, alias):
            continue
        section_map = {
            "Character / organization": people,
            "Location / zone": GAME_KNOWLEDGE.get("locations_and_zones", {}),
            "Organization": GAME_KNOWLEDGE.get("organizations_catalog", {}),
            "Named entity": GAME_KNOWLEDGE.get("notable_people_and_entities_index", {}),
            "World concept": GAME_KNOWLEDGE.get("world_concepts_and_history", {}),
        }
        value = section_map[label].get(raw_key)
        if value is not None:
            rendered: list[str] = []
            _append_value(rendered, raw_key.replace("_", " "), value)
            lines.append(f"{label} reference: {rendered[0]}")
            seen_entities.add(alias)

    return lines


def _anchor_score(normalized: str, anchor: LoreAnchor) -> int:
    score = 0
    for term in anchor.terms:
        if _contains(normalized, term):
            score += max(1, min(8, len(term.split()) * 2))
    return score


def build_aether_context(user_text: str, conversation_text: str = "", max_chars: int = 9000) -> str:
    source_text = " ".join(part for part in (conversation_text, user_text) if part).strip()
    normalized = _normalize(source_text)
    scored = [(score, index, anchor) for index, anchor in enumerate(LORE_ANCHORS) if (score := _anchor_score(normalized, anchor)) > 0]
    scored.sort(key=lambda item: (-item[0], item[1]))
    selected = [item[2] for item in scored[:7]]

    lines = ["AETHER GAZER REFERENCE CONTEXT:", _CANON_GUARD, f"Source policy: {_SOURCE_POLICY}"]
    if selected:
        lines.append("Relevant stable anchors:")
        lines.extend(f"- {anchor.name}: {anchor.context}" for anchor in selected)

    if any(_contains(normalized, term) for term in ("hades", "puppet master", "society of muses", "mintha", "leuce", "hades'")):
        lines.append("Hades identity reference:")
        lines.extend(f"- {item}" for item in _identity_context())

    if any(_contains(normalized, term) for term in ("build", "sigil", "functor", "aether code", "access key", "skill", "divine grace", "chthonic mark", "dance duo", "dance partner", "outfit", "chip")):
        lines.append("Hades gameplay reference:")
        lines.extend(f"- {item}" for item in _gameplay_context())
        lines.extend(f"- {item}" for item in _dated_guide_context())

    knowledge_lines = _knowledge_context(normalized)
    if knowledge_lines:
        lines.append("Additional Aether Gazer knowledge:")
        lines.extend(f"- {item}" for item in knowledge_lines)

    if any(_contains(normalized, term) for term in ("latest", "current", "currently", "today", "this week", "now")):
        lines.append("Freshness warning: this local knowledge is a dated snapshot; do not imply live access to banners, rotations, event schedules, rewards, or balance changes.")

    if not selected and not knowledge_lines:
        lines.append("No detailed lore anchor matched. Stay in character without inventing detailed canon.")

    # Bound context so the model receives useful information rather than a giant dump.
    output: list[str] = []
    total = 0
    for line in lines:
        cost = len(line) + 1
        if total + cost > max_chars:
            break
        output.append(line)
        total += cost
    return "\n".join(output)
