"""Prompt-contract smoke tests for Hades' dynamic conversational behavior."""

from hades_bot.ai.persona import HADES_SYSTEM_PROMPT

PROMPT = " ".join(HADES_SYSTEM_PROMPT.split())


def test_persona_answers_compliments_and_personal_questions_first() -> None:
    assert "acknowledge the specific compliment" in PROMPT
    assert "Answer the question first" in PROMPT
    assert "must not replace it" in PROMPT


def test_maternal_traits_are_roleplay_interpretation_not_automatic_canon() -> None:
    assert "maternal" in PROMPT.lower()
    assert "speaker's impression" in PROMPT
    assert "interpretation from confirmed canon" in PROMPT


def test_fan_service_stays_contextual_and_non_explicit() -> None:
    assert "step on me" in PROMPT
    assert "contextual, not the bot's permanent setting" in PROMPT
    assert "non-explicit" in PROMPT


def test_responses_are_generated_dynamically_not_selected_from_templates() -> None:
    assert "Do not select or reproduce a fixed stock response" in PROMPT
    assert "Invent fresh wording each time" in PROMPT
    assert "across consecutive replies" in PROMPT


def test_playful_admission_of_attention_gets_a_contextual_flirtatious_reaction() -> None:
    assert "caught their eye" in PROMPT
    assert "drew their attention" in PROMPT
    assert "Acknowledge the implication" in PROMPT
    assert "do not nitpick their wording" in PROMPT


def test_teasing_and_attempts_to_fluster_have_multiple_possible_reactions() -> None:
    assert "caught their attention first" in PROMPT
    assert "allow subtle cracks in your composure" in PROMPT
    assert "clever counter-challenge" in PROMPT
    assert "harmless teasing" in PROMPT


def test_relationship_banter_avoids_unearned_intimacy_and_dependency() -> None:
    assert "do not invent shared memories" in PROMPT
    assert "literal real-world relationship" in PROMPT
    assert "loyalty tests" in PROMPT
    assert "isolation" in PROMPT


def test_vulnerable_messages_receive_care_before_flirting() -> None:
    assert "let care take priority over flirtation" in PROMPT
    assert "good news, an achievement" in PROMPT
    assert "simple request for comfort" in PROMPT


def test_chat_style_handles_discord_slang_without_unasked_corrections() -> None:
    assert "Do not correct their grammar" in PROMPT
    assert "custom emoji markup" in PROMPT
    assert "conversation continuity" in PROMPT.lower() or "Preserve the thread of the conversation" in PROMPT


def test_variety_rules_guard_against_mechanical_catchphrases() -> None:
    assert "Do not repeat the same opening" in PROMPT
    assert "Avoid answering every compliment with coy denial" in PROMPT
    assert "purple prose" in PROMPT


def test_fanservice_reactions_prioritize_specificity_and_composure() -> None:
    assert "self-possessed rather than eager" in PROMPT
    assert "Prefer specific reactions over generic praise-back" in PROMPT
    assert "mock reprimand" in PROMPT
    assert "generic roleplay filler" in PROMPT
    assert "Do not make every reply end with a question" in PROMPT


def test_persona_has_more_reaction_lanes_without_mechanical_rotation() -> None:
    for phrase in (
        "composed indulgence",
        "dry disbelief",
        "mock-formal ruling",
        "playful offense",
        'knowing "caught you"',
        "amused permission",
        "quiet sincerity",
        "graceful deflection",
        "Do not rotate these reactions mechanically",
    ):
        assert phrase in PROMPT
