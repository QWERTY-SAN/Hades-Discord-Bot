from hades_bot.core.conversation import conversation_mode, conversation_signals, is_short_followup


def test_short_followups_are_contextual():
    assert is_short_followup("what about her?")
    assert is_short_followup("and you?")
    assert is_short_followup("really?")


def test_signals():
    assert "continuation" in conversation_signals("why?")
    assert "turn_back" in conversation_signals("and you?")
    assert "correction" in conversation_signals("Actually, I meant the other one.")


def test_flirtation_mode():
    assert conversation_mode("You drew my attention.") == "flirtation"


def test_elegance_maternal_question_is_fanservice():
    from hades_bot.ai.fanservice import fanservice_category
    text = "Tell me, where did this elegance and maternal traits come from?"
    assert fanservice_category(text) == "admiration"
