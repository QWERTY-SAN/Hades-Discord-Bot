from hades_bot.ai.fanservice import (
    fanservice_categories,
    fanservice_category,
    fanservice_guidance,
    fanservice_intensity,
    is_fanservice_message,
)


def test_step_on_me_is_fanservice():
    assert fanservice_category("please step on me, Hades") == "fan_command"


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


def test_multiple_categories_survive():
    categories = fanservice_categories("You're gorgeous. Step on me.")
    assert "admiration" in categories
    assert "fan_command" in categories


def test_intensity_is_calibrated():
    assert fanservice_intensity("you're gorgeous") == "warm"
    assert fanservice_intensity("don't tempt me like that") == "flirty"
    assert fanservice_intensity("step on me") == "bold"


def test_guidance_is_not_a_response_template():
    guidance = fanservice_guidance("step on me")
    assert "fresh response" in guidance
    assert "fixed response list" in guidance


def test_normal_game_question_is_not_fanservice():
    assert not is_fanservice_message("What team works well with Hades?")
