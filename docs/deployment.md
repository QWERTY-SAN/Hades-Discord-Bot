# Deployment

## Render

This repository deploys as a Render Web Service because the bot also exposes lightweight HTTP health endpoints.

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
python main.py
```

Health check:

```text
/health
```

Readiness check:

```text
/ready
```

The Blueprint uses:

```yaml
autoDeployTrigger: checksPass
```

That means Render can deploy the commit after the GitHub Actions checks pass. The existing Render service must be attached to/synced with this Blueprint for changes in `render.yaml` to take effect.

## Required Render variables

Store these as Render environment secrets:

```text
DISCORD_TOKEN
GEMINI_API_KEY
```

The recommended runtime configuration is:

```text
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_THINKING_LEVEL=minimal
BOT_PREFIX=h!
STRICT_AETHER_TOPIC=true
EMOJIS_ENABLED=true
LIVE_SOURCE_REFRESH=true
LIVE_SOURCE_MAX_URLS=3
MAX_HISTORY=16
MAX_OUTPUT_TOKENS=768
MAX_INPUT_CHARS=6000
KNOWLEDGE_CONTEXT_MAX_CHARS=9000
USER_COOLDOWN=2.0
MAX_CONCURRENT_REQUESTS=3
MAX_QUEUE_WAIT=20
REQUEST_TIMEOUT=45
MAX_RETRIES=3
MEMORY_TTL_SECONDS=21600
MAX_CONVERSATIONS=500
MEMORY_PRUNE_INTERVAL=900
COOLDOWN_PRUNE_INTERVAL=3600
```

Do not put real tokens or API keys in GitHub. `.env.example` contains placeholders only.

## Discord configuration

Enable **Message Content Intent** for the Discord application. Without it, prefix commands and message text processing will not work reliably.

The bot responds through:
- `h!hades <message>`
- `h!ask <message>`
- direct mentions
- DMs
- replies to Hades messages

## Troubleshooting

### Render builds successfully but exits immediately

Check the start command first:

```text
python main.py
```

`main.py` validates secrets, starts the HTTP server, and then starts Discord.

### Render health check fails

Open:

```text
/health
```

A successful liveness response should return HTTP 200.

`/ready` is intentionally stricter: it returns HTTP 503 until Discord has connected. Use it for diagnostics rather than the Render health check.

### Bot is online but does not read messages

Verify:
1. Message Content Intent is enabled in the Discord Developer Portal.
2. `DISCORD_TOKEN` is the current bot token.
3. The command prefix remains `h!`.
4. The bot has permission to View Channel, Send Messages, Embed Links, and Read Message History.

### Gemini requests fail

Verify:
1. `GEMINI_API_KEY` is valid.
2. `GEMINI_MODEL` matches a model available to that API key/project.
3. The service is not being rate-limited.
4. The Render logs do not show 401/403/404/429 errors.

Current/live questions can use Gemini URL Context when `LIVE_SOURCE_REFRESH=true`. If URL Context is rejected, the bot falls back to a normal Gemini request instead of crashing.

## Local run

Install:

```text
python -m pip install -r requirements.txt pytest
```

Set `DISCORD_TOKEN` and `GEMINI_API_KEY`, then:

```text
python main.py
```

Local default HTTP port is 10000 unless `PORT` is set.
