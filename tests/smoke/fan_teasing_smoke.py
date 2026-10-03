from hades_bot.core.scope import is_hades_scope_allowed


def test_fan_teasing_scope() -> None:
    allowed = (
        "can you step on me",
        "step on me",
        "Hades, you're gorgeous",
        "Hades, I adore you",
    )
    blocked = (
        "Hades, what is Formula One?",
        "Hades, write Python for me",
    )
    for message in allowed:
        assert is_hades_scope_allowed(message), message
    for message in blocked:
        assert not is_hades_scope_allowed(message), message
