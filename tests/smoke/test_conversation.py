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


def test_food_related_social_chat_uses_its_own_mode():
    from hades_bot.core.scope import is_hades_scope_allowed

    examples = (
        "I'm hungry",
        "What food do you like?",
        "What's your favorite dessert?",
        "This chicken stew looks delicious.",
        "I'm craving ramen.",
        "What should we eat?",
        "I love adobo",
    )
    for message in examples:
        assert conversation_mode(message) == "food_chat", (message, conversation_mode(message))
        assert is_hades_scope_allowed(message), message


def test_food_chat_does_not_allow_recipes_or_cooking_instructions():
    from hades_bot.core.scope import is_hades_scope_allowed

    blocked = (
        "Give me a recipe for chicken stew",
        "How do I cook chicken stew?",
        "What ingredients do I need for stew?",
        "How long should I cook chicken?",
        "What temperature should I cook chicken at?",
    )
    for message in blocked:
        assert not is_hades_scope_allowed(message), message


def test_expanded_fanservice_detects_short_dates_slang_and_fresh_flirt_cues():
    from hades_bot.ai.fanservice import fanservice_categories

    cases = {
        "a date?": "romantic",
        "Will you be my date?": "romantic",
        "Let's go on a date together": "romantic",
        "I'm so down bad for you": "romantic",
        "You're making it hard to behave": "flirtation",
        "If you keep looking at me like that...": "flirtation",
        "Can I steal a kiss?": "affection",
        "I'm so cooked for you": "flustered",
        "I can't get enough of you": "captivated",
    }
    for message, expected_category in cases.items():
        assert expected_category in fanservice_categories(message), (message, fanservice_categories(message))


def test_short_date_fragment_is_fanservice_mode_not_out_of_scope():
    from hades_bot.core.scope import is_hades_scope_allowed

    assert conversation_mode("a date?") == "flirtation"
    assert is_hades_scope_allowed("a date?")
    assert conversation_mode("Will you be my date?") == "flirtation"
    assert is_hades_scope_allowed("Will you be my date?")



def test_emoji_palette_matches_reply_context():
    from hades_bot.ai.gemini_client import _emoji_candidates

    comfort = _emoji_candidates("You've had a rough day. Take your time.")
    celebration = _emoji_candidates("You did it! I'm proud of you.")
    flirtation = _emoji_candidates("A date, little lamb? How bold.")
    food = _emoji_candidates("Tea and cake sound lovely.")
    artistry = _emoji_candidates("The Society of Muses values puppetry and craft.")

    assert any(item in comfort for item in ("💜", "🫶", "🌷"))
    assert any(item in celebration for item in ("🎉", "✨", "🌟"))
    assert any(item in flirtation for item in ("😏", "💋", "🌹", "👀"))
    assert any(item in food for item in ("🍰", "☕", "🫖", "🍓"))
    assert any(item in artistry for item in ("🎭", "🪡", "🧵", "🪆"))


def test_emoji_postprocessor_does_not_duplicate_or_decorate_code():
    from hades_bot.ai.gemini_client import _add_natural_emoji

    with_emoji = "How bold of you, little lamb. 🌙"
    code = "\\x60\\x60\\x60python\\nprint('hello')\\n\\x60\\x60\\x60"
    long_reply = "a" * 421

    assert _add_natural_emoji(with_emoji) == with_emoji
    assert _add_natural_emoji(code) == code
    assert _add_natural_emoji(long_reply) == long_reply
