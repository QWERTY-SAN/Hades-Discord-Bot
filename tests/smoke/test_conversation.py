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
    assert conversation_mode("wanna go out for an date?") == "flirtation"
    assert conversation_mode("wanna hang out with me?") == "casual"
    assert conversation_mode("Old Hag") == "banter"


def test_elegance_maternal_question_is_fanservice():
    from hades_bot.ai.fanservice import fanservice_category
    text = "Tell me, where did this elegance and maternal traits come from?"
    assert fanservice_category(text) == "admiration"


def test_richer_conversation_signals():
    assert "achievement" in conversation_signals("I finally did it!")
    assert "needs_comfort" in conversation_signals("I had a rough day, comfort me.")
    assert "question" in conversation_signals("What do you think?")
    assert "high_energy" in conversation_signals("No way!!")


def test_more_short_followups_are_contextual():
    assert is_short_followup("wait what")
    assert is_short_followup("okay then?")
    assert is_short_followup("go ahead")


def test_personal_social_intent_modes_are_specific_and_non_flirtatious_by_default():
    assert conversation_mode("Are you fine?") == "check_in"
    assert conversation_mode("Only for u") == "personal_gesture"
    assert conversation_mode(
        "I found an ancient golem. Shall I give it to you as a gift?"
    ) == "gift_offer"
