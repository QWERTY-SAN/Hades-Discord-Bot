from hades_bot.ai.fanservice import fanservice_categories, fanservice_category, is_fanservice_message


def test_step_on_me_is_fanservice():
    assert fanservice_category("please step on me, Hades") == "fan_command"


def test_hug_is_fanservice():
    assert "affection" in fanservice_categories("Hades, give me a hug")


def test_puppet_request_is_fanservice():
    assert "puppet_fantasy" in fanservice_categories("Make me your puppet, Lady Hades")


def test_attention_request_is_fanservice():
    assert is_fanservice_message("please notice me")


def test_normal_game_question_is_not_fanservice():
    assert not is_fanservice_message("What team works well with Hades?")
