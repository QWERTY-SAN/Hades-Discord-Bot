import os

from dotenv import load_dotenv

load_dotenv()


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

BOT_PREFIX = os.getenv("BOT_PREFIX", "h!")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

MAX_HISTORY = max(2, int(os.getenv("MAX_HISTORY", "24")))
MAX_OUTPUT_TOKENS = max(128, int(os.getenv("MAX_OUTPUT_TOKENS", "1024")))
USER_COOLDOWN = max(0.0, float(os.getenv("USER_COOLDOWN", "2.0")))

DISCORD_MESSAGE_LIMIT = 2000


def validate() -> None:
    missing = []

    if not DISCORD_TOKEN:
        missing.append("DISCORD_TOKEN")

    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")

    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            f"Missing required environment variable(s): {joined}"
        )
