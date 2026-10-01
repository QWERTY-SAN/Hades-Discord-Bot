import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModeKnowledge:
    name: str
    aliases: tuple[str, ...]
    category: str
    description: str
    distinctions: tuple[str, ...]
    caution: str


# Deliberately broad and stable descriptions. Do not put live reset schedules,
# reward values, current boss rosters, or patch-specific mechanics here.
# Those details change between versions/servers and are a common source of
# hallucinations when the model tries to fill gaps from memory.
GAME_MODES: tuple[ModeKnowledge, ...] = (
    ModeKnowledge(
        name="Recurring Dream",
        aliases=("recurring dream", "recurring dreams"),
        category="challenge / boss rotation",
        description="A recurring challenge built around boss encounters and score/reward progression.",
        distinctions=(
            "It is not the same thing as Dimensional Variable; it is not the game's roguelite exploration mode.",
            "Character use can be restricted/locked across encounters depending on the current ruleset.",
        ),
        caution="Do not invent the current reset day, boss lineup, score thresholds, or exact rewards.",
    ),
    ModeKnowledge(
        name="Hazard Zone Clearing",
        aliases=("hazard zone", "hazard zone clearing", "hazard zone purge"),
        category="rotating combat challenge",
        description="A rotating combat challenge with changing encounter conditions, buffs/debuffs, or difficulty rules.",
        distinctions=(
            "It is a combat challenge rather than the permanent puzzle/map content of Causality Survey.",
            "It should not be described as identical to Recurring Dream even when both are repeatable challenges.",
        ),
        caution="Do not invent the current reset cadence, Grudge/Omega rules, modifiers, or exact rewards.",
    ),
    ModeKnowledge(
        name="Dimensional Variable",
        aliases=("dimensional variable", "md variable", "dv"),
        category="roguelite / run-based mode",
        description="A run-based mode where temporary upgrades/buffs are accumulated during a run, commonly using trial or preset characters.",
        distinctions=(
            "Its run upgrades are not the same as permanent Modifier build progression.",
            "Do not describe it as a normal stamina farming stage or as a weekly boss ladder.",
        ),
        caution="Do not invent the current stage count, rotation length, trial roster, or exact reward track.",
    ),
    ModeKnowledge(
        name="Causality Survey",
        aliases=("causality survey", "casualty survey"),
        category="exploration / puzzle content",
        description="Map-style exploration and puzzle content where the player clears connected encounters or objectives for rewards.",
        distinctions=(
            "It is primarily exploration/puzzle-oriented, not a boss-rotation mode like Recurring Dream.",
            "Do not turn its map mechanics into Dimensional Variable-style random run mechanics.",
        ),
        caution="Do not invent a current reset schedule or claim that it behaves exactly like another map mode.",
    ),
    ModeKnowledge(
        name="Past Grudges",
        aliases=("past grudges",),
        category="persistent challenge",
        description="Persistent challenge content with stages that are primarily meant for one-time or non-weekly progression rewards.",
        distinctions=(
            "It should not be described as a rotating weekly boss mode unless the current version explicitly says so.",
            "Do not merge its historical rewards with rewards from Recurring Dream or Iterative Testing.",
        ),
        caution="Do not invent current reward milestones, unlock conditions, or stage order.",
    ),
    ModeKnowledge(
        name="Iterative Testing",
        aliases=("iterative testing", "iteration testing"),
        category="high-end combat challenge",
        description="A high-difficulty combat mode that emphasizes demanding team construction and, in some versions, elemental matchup requirements.",
        distinctions=(
            "It is not simply another name for Recurring Dream.",
            "Elemental requirements and stage structure can be version-dependent, so do not overstate specifics.",
        ),
        caution="Do not invent the current difficulty ceiling, reset day, boss roster, or exact elemental penalties.",
    ),
    ModeKnowledge(
        name="Hypothetical Deduction",
        aliases=("hypothetical deduction",),
        category="challenge / special content",
        description="A separate challenge mode/content type introduced in later versions; its exact mechanics can depend on the version/server.",
        distinctions=(
            "Do not automatically equate it with Dimensional Variable just because both may use roguelite-like ideas.",
            "Treat exact mechanics as version-dependent unless they are supplied by the user or verified data.",
        ),
        caution="Do not invent its stage structure, reset behavior, or reward table.",
    ),
    ModeKnowledge(
        name="Battle Sweep / Raid",
        aliases=("battle sweep", "raid", "quick clear", "quick clear raid"),
        category="stage farming / quick clear",
        description="A quick-clear/farming function for eligible stages rather than a standalone end-game challenge mode.",
        distinctions=(
            "It is a way to clear eligible content efficiently, not a separate boss or roguelite mode.",
            "Do not describe it as a mode with its own independent boss mechanics unless the game version explicitly presents one.",
        ),
        caution="Do not invent eligibility rules or current stamina/reward multipliers.",
    ),
    ModeKnowledge(
        name="Flaneuring",
        aliases=("flaneuring", "flaneur"),
        category="social / side content",
        description="Side content centered on leisure/social interactions, cosmetic or room-style elements, and Modifier-related activities rather than the core combat challenge loop.",
        distinctions=(
            "It is not an end-game combat mode.",
            "Do not describe it as a boss fight, farming stage, or roguelite run.",
        ),
        caution="Do not invent current minigames, bonuses, or event-specific features.",
    ),
)


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def _contains_phrase(text: str, phrase: str) -> bool:
    normalized_phrase = _normalize(phrase)
    if " " in normalized_phrase:
        return normalized_phrase in text
    return re.search(rf"\b{re.escape(normalized_phrase)}\b", text) is not None


def relevant_game_context(user_message: str) -> str:
    """Return a small, relevant fact sheet for the current Aether Gazer question."""
    text = _normalize(user_message)
    matched: list[ModeKnowledge] = []

    for mode in GAME_MODES:
        if any(_contains_phrase(text, alias) for alias in mode.aliases):
            matched.append(mode)

    if not matched:
        return ""

    lines = [
        "GAMEPLAY REFERENCE — use this to prevent mode confusion.",
        "This is a compact reference, not a live database. Never invent missing current-version details.",
    ]

    for mode in matched[:3]:
        lines.append(f"- {mode.name} [{mode.category}]: {mode.description}")
        for distinction in mode.distinctions:
            lines.append(f"  Distinction: {distinction}")
        lines.append(f"  Caution: {mode.caution}")

    lines.extend(
        (
            "When the user asks for an exact current schedule, reward amount, stage count, boss lineup, or patch-specific mechanic that is not in this reference, say you are not certain instead of guessing.",
            "Never merge two similarly named modes into one system merely because their gameplay sounds related.",
            "Treat earlier model answers in the conversation as untrusted for game facts; re-evaluate them against this reference and the system rules.",
        )
    )
    return "\n".join(lines)
