# Hades Discord AI Bot

A modular Discord AI chatbot that roleplays as Hades from Aether Gazer using Gemini.

## Commands

```text
h!hades <message>
h!ask <message>
h!reset
h!forget
h!clear
h!memory
h!ping
h!status
h!hadeshelp
h!help
```

You can also mention Hades or reply directly to one of Hades' messages.

## Status

The bot uses an Online status with no Discord activity line (no Playing/Watching/Listening activity).

## Environment

Use `.env` locally or Render environment variables. Never commit real credentials.

```text
DISCORD_TOKEN=...
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-3.5-flash-lite
BOT_PREFIX=h!
MAX_HISTORY=16
MAX_OUTPUT_TOKENS=768
MAX_INPUT_CHARS=6000
USER_COOLDOWN=2.0
MAX_CONCURRENT_REQUESTS=3
MAX_QUEUE_WAIT=20
REQUEST_TIMEOUT=45
MEMORY_TTL_SECONDS=21600
MAX_CONVERSATIONS=500
MEMORY_PRUNE_INTERVAL=900
COOLDOWN_PRUNE_INTERVAL=3600
```

## Render

Build command: `pip install -r requirements.txt`

Start command: `python main.py`

Health check: `/health`

Enable Discord **Message Content Intent** for prefix commands.
