from hades_bot.ai.fanservice import fanservice_category, is_fanservice_message
from hades_bot.core.scope import is_hades_scope_allowed


def test_fan_teasing_scope() -> None:
    allowed = (
        "can you step on me",
        "step on me",
        "Hades, you're gorgeous",
        "Hades, I adore you",
        "Hades, marry me",
        "kiss me, Hades",
        "Hades, give me a hug",
        "Hades, give me attention",
        "Hades, you're stunning",
        "I have a crush on you",
        "I need you, Hades",
        "call me little lamb",
        "How abt somewhere else very private away from prying eyes",
        "It's either do it or not, but I ain't backing down to someone who's like a fine looking wine",
    )
    blocked = (
        "Hades, what is Formula One?",
        "Hades, write Python for me",
    )
    for message in allowed:
        assert is_hades_scope_allowed(message), message
        assert is_fanservice_message(message), message
    for message in blocked:
        assert not is_hades_scope_allowed(message), message


def test_fanservice_categories() -> None:
    assert fanservice_category("step on me") == "fan_command"
    assert fanservice_category("marry me") == "romantic"
    assert fanservice_category("kiss me") == "affection"
    assert fanservice_category("you're gorgeous") == "admiration"
    assert fanservice_category("call me little lamb") == "playful_fandom"
    assert fanservice_category("How abt somewhere else very private away from prying eyes") == "flirtation"
    assert fanservice_category("It's either do it or not, but I ain't backing down to someone who's like a fine looking wine") == "flirtation"
