from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .character_data import GAME_KNOWLEDGE, HADES_DATA, TERMINOLOGY


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
        "The Society of Muses is central to Hades' identity and responsibilities.",
    ),
    LoreAnchor(
        "Mintha and Leuce",
        ("mintha", "leuce"),
        "Mintha and Leuce are Hades' puppet maids/companions and should be treated with familiarity when relevant.",
    ),
    LoreAnchor(
        "Puppetry",
        ("puppet", "puppets", "puppetry", "strings", "puppet strings", "theater", "theatre"),
        "Puppetry, dolls, theater and performance are central to Hades' identity.",
    ),
    LoreAnchor(
        "Aether Gazer systems",
        tuple(TERMINOLOGY.get("core_terms", [])),
        "Prefer Aether Gazer's own terminology rather than replacing it with generic gacha terminology.",
    ),
    # World/lore vocabulary surfaced in the Mimir Worldview index.
    LoreAnchor("Gaea and Gaea.Zero", ("gaea", "gaea.zero", "gaea zero", "core of gaea"),
               "Gaea is the system behind the Idealbild world; Gaea.Zero and Core of Gaea are distinct named concepts in the worldview reference."),
    LoreAnchor("Idealbild and layers", ("idealbild", "source layer", "surface layer", "world line"),
               "Idealbild is Gaea's calculated world line; Source Layer and Surface Layer are distinct setting concepts."),
    LoreAnchor("Gen-Zones and regions", ("sephirah zone", "ain soph", "neuhansa", "shashvat", "omorfies", "xu heng", "sasanami", "olympus"),
               "Sephirah Zones are major regions of the setting, each with its own culture, organizations and history."),
    LoreAnchor("Visbanes and Bane Energy", ("visbane", "visbanes", "bane energy", "visbanic agi mecha", "corrosion", "quakes"),
               "Visbanes and related phenomena such as Bane Energy, Corrosion, Quakes and Visbanic AGI Mecha are distinct Aether Gazer setting concepts."),
    LoreAnchor("Organizations", ("division nine", "corg supreme directorate", "olympia express", "spealght industries", "children of iron", "akkadian guild", "stellaris academy", "astral council", "knights of convallaria", "izuru family", "miyahebi family", "karasugo family", "meruism", "tian lu traders", "quad"),
               "Aether Gazer's world contains many named organizations and families. Use stored source context and do not invent internal details."),
    LoreAnchor("Important Aether Gazer figures", ("odin", "heimdall", "shu", "poseidon", "tsukuyomi", "skuld", "gengchen", "lingguang", "izanami", "hera"),
               "Important figures include Odin, Heimdall, Shu, Poseidon, Tsukuyomi, Skuld, Gengchen, Lingguang, Izanami and Hera. Each has distinct organizations, personalities and story roles; use stored character/reference data rather than inventing relationships or biographies."),
    LoreAnchor("Historical events", ("star dust calamity", "establishing of gaea", "tranzist revolution", "first agi mecha crisis", "five clans", "mountain ceremony", "klein protocol", "ardisis ceremony"),
               "Named historical events appear in the worldview reference; exact chronology should follow the stored lore source."),
    LoreAnchor("Combat resources and systems", ("rage", "energy", "trace", "divine grace", "harmony", "zero time", "modified mode", "ultimate skillchain", "combat resource"),
               "Aether Gazer uses several combat-resource types—Rage, Energy, Trace, Divine Grace and Harmony—and advanced combat systems such as Zero Time, Modified Mode and Ultimate Skillchains. Exact values and interactions can be Modifier/version specific."),
    LoreAnchor("Endgame", ("recurring dream", "hazard zone", "dimensional variable", "iterative testing", "past grudges", "causality survey", "ancient shadow", "crisis analysis"),
               "Late-game content spans Recurring Dream, Hazard Zone, Dimensional Variable, Iterative Testing, Past Grudges and Causality Survey, while version-limited challenge content can include Ancient Shadow and Crisis Analysis. Exact cycles and rewards are version-sensitive."),
    LoreAnchor("M.E.O.W.", ("m.e.o.w.", "meow", "mijir", "micoco", "mitir", "mimtastic", "mininja", "me-yow", "meow chip", "meow chips"),
               "M.E.O.W. are auxiliary AI/progression units and chips. Unlocks and effects are tied to Admin progression, story and endgame milestones."),
    LoreAnchor("Support Modules", ("support module", "support modules", "rahu", "rāhu", "roaring thunder", "flower of yomi", "tenblaze", "phantasmal dawn", "dimglare"),
               "Support Modules provide Administrator/team effects and have current unlock and effect data that can change between versions."),
    LoreAnchor("Sigil Enchants", ("sigil enchant", "sigil enchants", "fierce assault", "berserk", "enraged", "anti-visbane tactics", "counter-visbane defense", "shinn-ryuu", "charged and ready"),
               "Sigil Enchants modify a Modifier through offensive, auxiliary or defensive effects; exact current values are source/date dependent."),
    LoreAnchor("Opponent Intel", ("opponent intel", "risk level i", "risk level ii", "risk level iii"),
               "Mimir's Opponent Intel organizes enemy references by risk level and is useful for distinguishing enemy types when current data is available."),
    LoreAnchor("Achievements and side content", ("achievement", "achievements", "flaneuring", "idol competition", "music dossier", "furniture"),
               "Aether Gazer has achievement categories plus side/collection content such as Flaneuring, Idol Competition, Music Dossier and furniture."),
    LoreAnchor("Scans and economy", ("modifier scan", "functor scan", "precise scan voucher", "modifier scan voucher", "sigil module", "imprint shop", "shifted star", "shifted stars", "shifting flower", "shifting flowers", "swigs"),
               "The acquisition economy includes Modifier Scan, Functor Scan, Precise Scan Vouchers, Modifier Scan Vouchers, Imprint Shop exchanges, Shifted Stars, Shifting Flowers and Swigs. Shifted Star income can come from daily, weekly, monthly/seasonal, event and one-time sources; exact totals depend on the server version and available content."),
)

SCOPE_TERMS = frozenset(term for anchor in LORE_ANCHORS for term in anchor.terms)

_CANON_GUARD = (
    "No live game-server connection is available. Do not present current banners, patch notes, balance values, "
    "tier lists, or other changing information as verified unless supplied by application data or the user. "
    "Stable lore and named systems may be discussed from the stored reference catalog."
)


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    value = re.sub(r"[\u200b-\u200d\ufeff]", "", value)
    return re.sub(r"[^\w+#'.!?-]+", " ", value).strip()


def _contains(text: str, term: str) -> bool:
    if " " in term or "." in term or "-" in term:
        return term in text
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) is not None


def _dynamic_reference_summary(anchor_name: str) -> str | None:
    # Map a subset of anchors directly to the structured catalog for richer context.
    kg = GAME_KNOWLEDGE
    mapping = {
        "Gaea and Gaea.Zero": ("world_and_setting", "gaea"),
        "Idealbild and layers": ("world_and_setting", "idealbild"),
        "Gen-Zones and regions": ("locations_and_zones", "sephirah_zones"),
        "Visbanes and Bane Energy": ("world_and_setting", "visbanes"),
        "Organizations": ("organizations_catalog", "aether_gazer_division_nine"),
    }
    target = mapping.get(anchor_name)
    if not target:
        return None
    section, key = target
    value = kg.get(section, {}).get(key)
    return value if isinstance(value, str) else None


def build_aether_context(user_text: str, max_anchors: int = 5) -> str:
    normalized = _normalize(user_text)
    selected: list[LoreAnchor] = []
    for anchor in LORE_ANCHORS:
        if any(_contains(normalized, term) for term in anchor.terms):
            selected.append(anchor)
        if len(selected) >= max_anchors:
            break

    lines = ["AETHER GAZER CONTEXT:", _CANON_GUARD]
    if selected:
        lines.append("Relevant stable/context anchors:")
        for anchor in selected:
            context = _dynamic_reference_summary(anchor.name) or anchor.context
            lines.append(f"- {anchor.name}: {context}")

    lower = normalized
    if any(_contains(lower, term) for term in ("build", "sigil", "functor", "aether code", "team", "support module", "meow")):
        lines.append("- Gameplay/build data is dated reference material unless a fresh source snapshot is supplied.")
    if any(_contains(lower, term) for term in ("current", "today", "now", "latest", "active", "this week", "this month")):
        lines.append("- Current/live status cannot be verified from the local catalog alone; use the stored snapshot date and qualify uncertainty.")
    if not selected:
        lines.append("No specific lore anchor matched. Stay in character and do not invent detailed canon.")
    return "\n".join(lines)
