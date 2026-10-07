from hades_bot.ai.fanservice import (
    fanservice_categories,
    fanservice_category,
    fanservice_guidance,
    fanservice_intensity,
    is_fanservice_message,
)
from hades_bot.core.scope import is_hades_scope_allowed


def test_fan_teasing_scope() -> None:
    allowed = (
        "can you step on me",
        "step on me",
        "Hades, walk all over me",
        "Hades, you're gorgeous",
        "Hades, I adore you",
        "Hades, marry me",
        "kiss me, Hades",
        "Hades, give me a hug",
        "Hades, give me attention",
        "Hades, you're stunning",
        "Eh ur so hot",
        "ur so hot",
        "u look pretty",
        "u r so hot",
        "ur sooo pretty",
        "ur seriously gorgeous",
        "Hades, you're making me blush.",
        "Hades, you look dangerous.",
        "Hades, absolute beauty.",
        "I have a crush on you",
        "I need you, Hades",
        "call me little lamb",
        "Hades, tell me I'm good",
        "Hades, make me your puppet",
        "Hades, stop making me blush",
        "Hades, don't look at me like that",
        "Prove it, Hades.",
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
    assert fanservice_category("kneel and obey Hades") == "playful_dominance"
    assert fanservice_category("marry me") == "romantic"
    assert fanservice_category("kiss me") == "affection"
    assert fanservice_category("you're gorgeous") == "admiration"
    assert fanservice_category("Eh ur so hot") == "admiration"
    assert fanservice_category("ur so hot") == "admiration"
    assert fanservice_category("u look pretty") == "admiration"
    assert fanservice_category("u r so hot") == "admiration"
    assert fanservice_category("ur sooo pretty") == "admiration"
    assert fanservice_category("ur seriously gorgeous") == "admiration"
    assert fanservice_category("Hades, you're making me blush.") == "flustered"
    assert fanservice_category("Hades, you look dangerous.") == "admiration"
    assert fanservice_category("Hades, absolute beauty.") == "admiration"
    assert fanservice_category("tell me I'm good") == "praise"
    assert fanservice_category("please notice me") == "attention_seek"
    assert fanservice_category("call me little lamb") == "playful_fandom"
    assert fanservice_category("make me your puppet") == "puppet_fantasy"
    assert fanservice_category("stop making me blush") == "flustered"
    assert fanservice_category("don't tempt me like that") == "flirtation"
    assert fanservice_category("prove it") == "teasing_challenge"
    assert fanservice_category("How abt somewhere else very private away from prying eyes") == "flirtation"
    assert fanservice_category("It's either do it or not, but I ain't backing down to someone who's like a fine looking wine") == "flirtation"


def test_combined_fanservice_keeps_multiple_signals() -> None:
    text = "You're gorgeous, step on me and make me blush."
    categories = fanservice_categories(text)
    assert "fan_command" in categories
    assert "admiration" in categories
    assert "flustered" in categories
    assert fanservice_intensity(text) == "bold"


def test_guidance_is_dynamic_and_not_a_stock_reply() -> None:
    guidance = fanservice_guidance("Hades, you're gorgeous, step on me.")
    assert "fan_command" in guidance
    assert "admiration" in guidance
    assert "fresh response" in guidance
    assert "fixed response list" in guidance
    assert "one dominant reaction style" in guidance
