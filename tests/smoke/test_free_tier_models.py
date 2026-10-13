from types import SimpleNamespace

import pytest

import hades_bot.config as config


def test_free_tier_allowlist_is_lite_only():
    assert config.FREE_TIER_ELIGIBLE_GEMINI_MODELS == {
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
    }


def test_default_fallback_is_on_the_free_tier_allowlist():
    assert set(config.SETTINGS.gemini_fallback_models).issubset(
        config.FREE_TIER_ELIGIBLE_GEMINI_MODELS
    )


def test_validator_rejects_unapproved_primary_model(monkeypatch):
    monkeypatch.setattr(
        config,
        "SETTINGS",
        SimpleNamespace(
            discord_token="test-token",
            gemini_api_key="test-api-key",
            gemini_model="gemini-3.8-flash",
            gemini_thinking_level="minimal",
        ),
    )

    with pytest.raises(RuntimeError, match="approved Free Tier Lite models"):
        config.validate_settings()
