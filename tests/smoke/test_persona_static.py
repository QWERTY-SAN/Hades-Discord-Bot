from hades_bot.ai.persona import HADES_SYSTEM_PROMPT


def test_character_terms_are_preserved():
    prompt = HADES_SYSTEM_PROMPT
    for term in ("Administrator", "little lamb", "Mintha", "Leuce", "Society of Muses"):
        assert term in prompt


def test_flirting_is_contextual_not_canned():
    assert "Do not turn every compliment into flirting" in HADES_SYSTEM_PROMPT
    assert "Generate a fresh reply rather than selecting from a canned list." in HADES_SYSTEM_PROMPT


def test_persona_has_deeper_conversation_behavior():
    assert "good news deserves genuine congratulations" in HADES_SYSTEM_PROMPT
    assert "let warmth and reassurance take priority over teasing" in HADES_SYSTEM_PROMPT
    assert "actual preference, opinion" in HADES_SYSTEM_PROMPT


def test_persona_handles_informal_social_subtext():
    assert "Read casual Discord language charitably" in HADES_SYSTEM_PROMPT
    assert "you drew my attention" in HADES_SYSTEM_PROMPT
    assert "A clearly Hades-directed social remark should remain conversational and in character" in HADES_SYSTEM_PROMPT
