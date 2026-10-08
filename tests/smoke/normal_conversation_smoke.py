from hades_bot.core.scope import (
    is_hades_scope_allowed,
    is_personal_life_request,
    is_social_message,
)


def test_common_small_talk_is_allowed() -> None:
    allowed = [
        "thanks",
        "same",
        "fair enough",
        "you too",
        "for real",
        "no way",
        "welcome back",
        "what about you?",
        "and you?",
        "what's up?",
        "I'm back.",
        "I just got home.",
        "I'm tired tonight.",
        "I missed you.",
        "tell me something",
        "stay with me",
        "that's wild",
        "woof woof!",
        "meow :3",
        "rawr",
        "Ayooo",
        "Ayooo!",
        "Ayooo:DuduLevi:",
        "Woahhh :Pepeuwu:",
        "💀",
        "😭😭",
        "owo",
        "Eh like what???",
        "like what?",
        "what else?",
        "Ok as u say so I'll get out of the shadows",
        "Eh ur so hot",
        "Want to go on a date?",
        "Can I take you out to dinner?",
        "May I take a whiff of your scent?",
        "Can I sniff behind your ears?",
        "why are you so hard to get?",
        "How did you know?",

        "Mind if I have a small allegiance here?",
        "What do u mean?",
        "wdym?",
        "nahhh",
        "ikr",
        "idk",
        "lmaooo",
        "bro",
        "No, I meant the other one.",
        "actually, never mind",
        "what u mean?",
        "What do u mean?",
        "Woahhh :Pepeuwu:",
        "Ayooo:DuduLevi:",
        "woof woof!",
        "Mommy 😭",
        "If I beg for you to embrace me.....will you?",
        "Mind if I have a small allegiance here?",

    ]

    for message in allowed:
        assert is_social_message(message), message
        assert is_hades_scope_allowed(message), message


def test_personal_choice_requests_are_allowed() -> None:
    allowed = [
        "what should I do tonight?",
        "what can I do?",
        "give me something to do",
        "pick something for me",
        "I have nothing to do",
        "should I stay home or go out?",
        "what would you do?",
    ]

    for message in allowed:
        assert is_personal_life_request(message), message
        assert is_hades_scope_allowed(message), message


def test_hard_boundaries_still_block_unrelated_topics() -> None:
    blocked = [
        "What do you think about Formula One?",
        "Who won the basketball game?",
        "Write me a Python script.",
        "What is Bitcoin?",
        "Explain how a CPU works.",
        "Can you write Python for me?",
    ]

    for message in blocked:
        assert not is_hades_scope_allowed(message), message


if __name__ == "__main__":
    test_common_small_talk_is_allowed()
    test_personal_choice_requests_are_allowed()
    test_hard_boundaries_still_block_unrelated_topics()
    print("normal_conversation_smoke: OK")
