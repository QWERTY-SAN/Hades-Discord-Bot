from hades_bot.ai.fanservice import (
    fanservice_categories,
    fanservice_category,
    fanservice_guidance,
    fanservice_intensity,
    is_fanservice_message,
)


def test_step_on_me_is_fanservice():
    assert fanservice_category("please step on me, Hades") == "fan_command"


def test_old_hades_fanservice_variants_are_preserved():
    assert fanservice_category("sit on me") == "fan_command"
    assert fanservice_category("make me ask properly") == "fan_command"
    assert fanservice_category("make me behave") == "fan_command"
    assert fanservice_category("mommy Hades") == "playful_fandom"
    assert fanservice_category("my queen") == "playful_fandom"
    assert fanservice_category("make me your puppet") == "playful_fandom"
    assert fanservice_category("somewhere private, away from prying eyes") == "flirtation"
    assert fanservice_category("you're a temptation") == "flirtation"
    assert fanservice_category("you're making this too easy") == "flirtation"
    assert fanservice_category("you're asking for trouble") == "flirtation"
    assert fanservice_category("don't look at me like that") == "flirtation"
    assert fanservice_category(
        "I ain't backing down to someone who's like a fine looking wine"
    ) == "flirtation"


def test_dominant_fan_command_variants():
    assert fanservice_category("Hades, put me in my place") == "fan_command"
    assert fanservice_category("boss me around") == "fan_command"


def test_hug_is_fanservice():
    assert "affection" in fanservice_categories("Hades, give me a hug")


def test_puppet_request_is_fanservice():
    assert "puppet_fantasy" in fanservice_categories("Make me your puppet, Lady Hades")


def test_attention_request_is_fanservice():
    assert is_fanservice_message("please notice me")


def test_new_categories_are_detected():
    assert fanservice_category("tell me I'm good") == "praise"
    assert fanservice_category("stop making me blush") == "flustered"
    assert fanservice_category("prove it") == "teasing_challenge"

    assert fanservice_category("Want to go on a date?") == "romantic"
    assert fanservice_category("Can I take you out to dinner?") == "romantic"
    assert fanservice_category("May I take a whiff of your scent?") == "scent_and_proximity"
    assert fanservice_category("Can I sniff behind your ears?") == "scent_and_proximity"
    assert fanservice_category("why are you so hard to get?") == "teasing_challenge"

    assert fanservice_category("You've got me under your spell.") == "captivated"
    assert fanservice_category("You're living rent-free in my head.") == "captivated"
    assert fanservice_category("I'm your devoted little lamb.") == "devotion"
    assert fanservice_category("I'd worship you, Lady Hades.") == "devotion"
    assert fanservice_category("Am I your favorite?") == "playful_jealousy"
    assert fanservice_category("Don't make me jealous.") == "playful_jealousy"
    assert fanservice_category("I could listen to your voice all day.") == "admiration"
    assert fanservice_category("You make it hard to focus.") == "admiration"


def test_multiple_categories_survive():
    categories = fanservice_categories("You're gorgeous. Step on me.")
    assert "admiration" in categories
    assert "fan_command" in categories


def test_intensity_is_calibrated():
    assert fanservice_intensity("you're gorgeous") == "warm"
    assert fanservice_intensity("don't tempt me like that") == "flirty"
    assert fanservice_intensity("step on me") == "bold"
    assert fanservice_intensity("may I take a whiff of your scent?") == "warm"

    assert fanservice_intensity("you've got me under your spell") == "flirty"
    assert fanservice_intensity("I'd worship you") == "flirty"
    assert fanservice_intensity("am I your favorite?") == "flirty"


def test_guidance_is_not_a_response_template():
    guidance = fanservice_guidance("step on me")
    assert "fresh response" in guidance
    assert "fixed response list" in guidance


def test_guidance_prioritizes_specific_hades_reactions():
    guidance = fanservice_guidance("you make it hard to focus")
    assert "React to the exact social move" in guidance
    assert "three beats" in guidance
    assert "Hades-specific social texture" in guidance
    assert "generic pickup lines" in guidance
    assert "ending with a question" in guidance


def test_normal_game_question_is_not_fanservice():
    assert not is_fanservice_message("What team works well with Hades?")


def test_expanded_classic_and_indirect_cues():
    assert fanservice_category("you're the one for me") == "romantic"
    assert fanservice_category("one for me") == "romantic"
    assert fanservice_category("you're trouble") == "flirtation"
    assert fanservice_category("what are you doing to me?") == "flirtation"
    assert fanservice_category("you've got me speechless") == "flustered"
    assert fanservice_category("how are you this pretty?") == "admiration"
    assert fanservice_category("Eh I mean ur the one who drew my attention to u :v") == "admiration"
    assert fanservice_category("you keep catching my eye") == "admiration"
    assert fanservice_category("you've got me looking at you") == "admiration"
    assert fanservice_category("I was drawn to you") == "admiration"
    assert fanservice_category("I can't look away from you") == "admiration"
