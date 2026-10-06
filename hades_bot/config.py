from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    discord_token: str
    gemini_api_key: str
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_thinking_level: str = "minimal"
    bot_prefix: str = "h!"
    strict_aether_topic: bool = True
    emojis_enabled: bool = True
    max_history: int = 16
    max_output_tokens: int = 768
    max_input_chars: int = 6000
    knowledge_context_max_chars: int = 9000
    user_cooldown: float = 2.0
    max_concurrent_requests: int = 3
    max_queue_wait: float = 20.0
    request_timeout: float = 45.0
    max_retries: int = 3
    memory_ttl_seconds: int = 21600
    max_conversations: int = 500
    memory_prune_interval: float = 180.0
    cooldown_prune_interval: float = 300.0
    web_host: str = "0.0.0.0"
    web_port: int = 10000


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

SETTINGS = Settings(
    discord_token=DISCORD_TOKEN,
    gemini_api_key=GEMINI_API_KEY,
    gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip(),
    gemini_thinking_level=os.getenv("GEMINI_THINKING_LEVEL", "minimal").strip(),
    bot_prefix=os.getenv("BOT_PREFIX", "h!").strip() or "h!",
    strict_aether_topic=_bool("STRICT_AETHER_TOPIC", True),
    emojis_enabled=_bool("EMOJIS_ENABLED", True),
    max_history=max(4, _int("MAX_HISTORY", 16)),
    max_output_tokens=max(128, _int("MAX_OUTPUT_TOKENS", 768)),
    max_input_chars=max(1000, _int("MAX_INPUT_CHARS", 6000)),
    knowledge_context_max_chars=max(2000, _int("KNOWLEDGE_CONTEXT_MAX_CHARS", 9000)),
    user_cooldown=max(0.0, _float("USER_COOLDOWN", 2.0)),
    max_concurrent_requests=max(1, _int("MAX_CONCURRENT_REQUESTS", 3)),
    max_queue_wait=max(1.0, _float("MAX_QUEUE_WAIT", 20.0)),
    request_timeout=max(5.0, _float("REQUEST_TIMEOUT", 45.0)),
    max_retries=max(0, _int("MAX_RETRIES", 3)),
    memory_ttl_seconds=max(60, _int("MEMORY_TTL_SECONDS", 21600)),
    max_conversations=max(10, _int("MAX_CONVERSATIONS", 500)),
    memory_prune_interval=max(30.0, _float("MEMORY_PRUNE_INTERVAL", 180.0)),
    cooldown_prune_interval=max(30.0, _float("COOLDOWN_PRUNE_INTERVAL", 300.0)),
    web_host=os.getenv("WEB_HOST", "0.0.0.0"),
    web_port=max(1, _int("PORT", _int("WEB_PORT", 10000))),
)


def validate_settings() -> None:
    if not SETTINGS.discord_token:
        raise RuntimeError("Missing DISCORD_TOKEN environment variable.")
    if not SETTINGS.gemini_api_key:
        raise RuntimeError("Missing GEMINI_API_KEY environment variable.")
