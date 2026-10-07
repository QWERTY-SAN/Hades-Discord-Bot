from hades_bot.core.scope import is_hades_scope_allowed, scope_block_reason


def test_hard_off_topic_stays_blocked():
    assert not is_hades_scope_allowed("Can you explain Python decorators?")
    assert scope_block_reason("Can you explain Python decorators?")


def test_short_followup_requires_history():
    assert not is_hades_scope_allowed("why?", has_history=False)
    assert not is_hades_scope_allowed("huh?", has_history=False)
    assert is_hades_scope_allowed("same", has_history=False)
    assert is_hades_scope_allowed("fair enough", has_history=False)
    assert is_hades_scope_allowed("go ahead", has_history=False)
    assert is_hades_scope_allowed("you too", has_history=False)
    assert is_hades_scope_allowed("no way", has_history=False)
    assert is_hades_scope_allowed("why?", has_history=True)
    assert is_hades_scope_allowed("What do u mean?", has_history=False)
    assert is_hades_scope_allowed("wdym?", has_history=False)


def test_hades_social_and_admiration_scope():
    assert is_hades_scope_allowed("Tell me about Mintha.")
    assert is_hades_scope_allowed("Hey Hades, how are you?")
    assert is_hades_scope_allowed("You're very elegant.")
    assert is_hades_scope_allowed("Eh I mean ur the one who drew my attention to u :v")
    assert is_hades_scope_allowed("you keep catching my eye")
    assert is_hades_scope_allowed("you're hilarious")
    assert is_hades_scope_allowed("huh?", has_history=True)
    assert is_hades_scope_allowed("wait what", has_history=True)
    assert is_hades_scope_allowed("go ahead", has_history=True)
    assert is_hades_scope_allowed("I wanted to see you")
    assert is_hades_scope_allowed("I've been thinking about you")
    assert not is_hades_scope_allowed("huh?", has_history=False)
    assert not is_hades_scope_allowed("Tell me the capital of France.")
