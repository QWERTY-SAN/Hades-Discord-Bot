from hades_bot.ai.persona import HADES_SYSTEM_PROMPT


def test_character_terms_are_preserved():
    prompt = HADES_SYSTEM_PROMPT
    for term in ("Administrator", "little lamb", "Mintha", "Leuce", "Society of Muses"):
        assert term in prompt


def test_flirting_is_contextual_not_canned():
    assert "Do not turn every compliment into flirting" in HADES_SYSTEM_PROMPT
    assert "Generate a fresh reply rather than selecting from a canned list." in HADES_SYSTEM_PROMPT
