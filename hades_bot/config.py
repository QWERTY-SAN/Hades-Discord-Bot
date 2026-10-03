from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _int(name: str, default: int, minimum: int = 0) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer.") from exc
    if value < minimum:
        raise RuntimeError(f"{name} must be >= {minimum}.")
    return value


def _float(name: str, default: float, minimum: float = 0.0) -> float:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = float(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a number.") from exc
    if value < minimum:
        raise RuntimeError(f"{name} must be >= {minimum}.")
    return value


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, str(default)).strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} must be true or false.")


@dataclass(frozen=True, slots=True)
class Settings:
    discord_token: str
    gemini_api_key: str
    bot_prefix: str
    gemini_model: str
    gemini_thinking_level: str
    strict_aether_topic: bool
    emojis_enabled: bool
    max_history: int
    max_output_tokens: int
    max_input_chars: int
    user_cooldown: float
    max_concurrent_requests: int
    max_queue_wait: float
    request_timeout: float
    max_retries: int
    memory_ttl_seconds: int
    max_conversations: int
    memory_prune_interval: int
    cooldown_prune_interval: int
    port: int

    @classmethod
    def load(cls) -> "Settings":
        discord_token = os.getenv("DISCORD_TOKEN", "").strip()
        gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not discord_token:
            raise RuntimeError("DISCORD_TOKEN is not configured.")
        if not gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        thinking = os.getenv("GEMINI_THINKING_LEVEL", "minimal").strip().lower()
        if thinking not in {"minimal", "low", "medium", "high"}:
            raise RuntimeError("GEMINI_THINKING_LEVEL must be minimal, low, medium, or high.")

        return cls(
            discord_token=discord_token,
            gemini_api_key=gemini_api_key,
            bot_prefix=os.getenv("BOT_PREFIX", "h!").strip() or "h!",
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip(),
            gemini_thinking_level=thinking,
            strict_aether_topic=_bool("STRICT_AETHER_TOPIC", True),
            emojis_enabled=_bool("EMOJIS_ENABLED", True),
            max_history=_int("MAX_HISTORY", 16, 2),
            max_output_tokens=_int("MAX_OUTPUT_TOKENS", 768, 128),
            max_input_chars=_int("MAX_INPUT_CHARS", 6000, 100),
            user_cooldown=_float("USER_COOLDOWN", 2.0, 0.0),
            max_concurrent_requests=_int("MAX_CONCURRENT_REQUESTS", 3, 1),
            max_queue_wait=_float("MAX_QUEUE_WAIT", 20.0, 0.0),
            request_timeout=_float("REQUEST_TIMEOUT", 45.0, 5.0),
            max_retries=_int("MAX_RETRIES", 3, 0),
            memory_ttl_seconds=_int("MEMORY_TTL_SECONDS", 21600, 60),
            max_conversations=_int("MAX_CONVERSATIONS", 500, 1),
            memory_prune_interval=_int("MEMORY_PRUNE_INTERVAL", 900, 60),
            cooldown_prune_interval=_int("COOLDOWN_PRUNE_INTERVAL", 3600, 60),
            port=_int("PORT", 10000, 1),
        )


SETTINGS = Settings.load()
DISCORD_MESSAGE_LIMIT = 2000


def validate() -> None:
    _ = SETTINGS
