from __future__ import annotations

import time
from types import SimpleNamespace

from hades_bot.media.media import HadesMedia


def fake_message():
    return SimpleNamespace(
        guild=SimpleNamespace(id=101),
        channel=SimpleNamespace(id=202),
        author=SimpleNamespace(id=303),
    )


def test_auto_media_supports_mentions_and_prefix_commands_not_plain_replies():
    media = HadesMedia()
    media.gifs = ("https://cdn.example/hades.gif",)
    media.images = ()
    message = fake_message()

    assert media.should_auto_send_media(message, "mention")
    assert media.should_auto_send_media(message, "command")
    assert not media.should_auto_send_media(message, "reply")
    assert not media.should_auto_send_media(message, "dm")


def test_auto_media_cooldown_and_history_commit_only_after_successful_send():
    media = HadesMedia()
    media.gifs = ("https://cdn.example/hades.gif",)
    media.images = ()
    message = fake_message()

    assert media.should_auto_send_media(message, "command")
    embed = media.choose_auto_media_embed(message)
    assert embed is not None

    # Merely choosing an embed should not consume the cooldown or mark media as sent.
    assert media.should_auto_send_media(message, "command")
    assert media.cooldown_remaining(message, "auto") == 0.0

    media.record_auto_media_sent(message, embed)
    assert not media.should_auto_send_media(message, "command")
    assert media.cooldown_remaining(message, "auto") > 0
    assert len(media._recent_gif[media._key(message)]) == 1


def test_manual_media_cooldowns_are_reported_per_media_type():
    media = HadesMedia()
    message = fake_message()
    key = media._key(message)
    media._last_gif[key] = time.monotonic()

    assert media.cooldown_remaining(message, "gif") > 0
    assert media.cooldown_remaining(message, "image") == 0.0

    media._last_image[key] = time.monotonic()
    assert media.cooldown_remaining(message, "image") > 0


def test_media_url_validation_discards_duplicates_and_unsafe_or_malformed_urls():
    values = [
        " https://cdn.example/hades.gif ",
        "https://cdn.example/hades.gif",
        "javascript:alert(1)",
        "ftp://cdn.example/hades.gif",
        "https://user:pass@cdn.example/hades.png",
        "https://cdn.example/bad url.gif",
        "https:///missing-host.gif",
    ]
    assert HadesMedia._valid_urls(values) == ["https://cdn.example/hades.gif"]


def test_invalid_media_kind_is_reported_clearly():
    media = HadesMedia()
    try:
        media.cooldown_remaining(fake_message(), "video")
    except ValueError as exc:
        assert "media_kind" in str(exc)
    else:
        raise AssertionError("expected a ValueError for an unsupported media kind")
