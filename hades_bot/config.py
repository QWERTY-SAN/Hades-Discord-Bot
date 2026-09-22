import os
from dotenv import load_dotenv

load_dotenv()


def _int_env(name: str, default: int, minimum: int = 0) -> int:
    try:
        return max(minimum, int(os.getenv(name, str(default))))
    except (TypeError, ValueError):
        return default


def _float_env(name: str, default: float, minimum: float = 0.0) -> float:
    try:
        return max(minimum, float(os.getenv(name, str(default))))
    except (TypeError, ValueError):
        return default


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

BOT_PREFIX = os.getenv("BOT_PREFIX", "h!")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

MAX_HISTORY = _int_env("MAX_HISTORY", 16, 2)
MAX_OUTPUT_TOKENS = _int_env("MAX_OUTPUT_TOKENS", 768, 128)
USER_COOLDOWN = _float_env("USER_COOLDOWN", 2.0, 0.0)
MAX_CONCURRENT_REQUESTS = _int_env("MAX_CONCURRENT_REQUESTS", 3, 1)
REQUEST_TIMEOUT = _float_env("REQUEST_TIMEOUT", 45.0, 5.0)
MEMORY_TTL_SECONDS = _int_env("MEMORY_TTL_SECONDS", 21600, 300)
MAX_CONVERSATIONS = _int_env("MAX_CONVERSATIONS", 500, 10)

DISCORD_MESSAGE_LIMIT = 2000


def validate() -> None:
    missing = []

    if not DISCORD_TOKEN:
        missing.append("DISCORD_TOKEN")

    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")

    if missing:
        raise RuntimeError(
            "Missing required environment variable(s): "
            + ", ".join(missing)
        )
