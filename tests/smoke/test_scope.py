from hades_bot.core.scope import is_hades_scope_allowed, scope_block_reason


def test_hard_off_topic_stays_blocked():
    assert not is_hades_scope_allowed("Can you explain Python decorators?")
    assert scope_block_reason("Can you explain Python decorators?")


def test_short_followup_requires_history():
    assert not is_hades_scope_allowed("why?", has_history=False)
    assert is_hades_scope_allowed("why?", has_history=True)


def test_hades_social_and_admiration_scope():
    assert is_hades_scope_allowed("Tell me about Mintha.")
    assert is_hades_scope_allowed("Hey Hades, how are you?")
    assert is_hades_scope_allowed("You're very elegant.")
    assert not is_hades_scope_allowed("Tell me the capital of France.")
