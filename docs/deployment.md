# Deployment and local development

## Render deployment

This project runs as a Render Web Service because it serves a read-only web dashboard and health endpoints while maintaining the Discord gateway connection.

Open the service root URL (`/`) to view the dashboard. It shows runtime metrics, Discord readiness, the configured Gemini → Groq fallback chain, diagnostics, and common command references. The dashboard uses a Server-Sent Events connection at `/api/events` for live runtime snapshots and new log entries. `/api/status` remains available for manual refresh and `/api/logs` returns the bounded log buffer. No extra packages or frontend build step are required. It has no control actions and never displays API keys. The in-memory log panel keeps up to 300 curated operational events, filters by level/text, can pause the display, and exports the visible entries as JSON. For complete tracebacks and durable history, use Render Logs or the local terminal; the dashboard log buffer resets on restart.

| Setting | Value |
|---|---|
| Build command | `pip install -r requirements.txt` |
| Start command | `python main.py` |
| Health check | `/health` |
| Readiness check | `/ready` |
| Deploy policy | `autoDeployTrigger: checksPass` |

The existing Render service must be connected to and synced with this repository's `render.yaml` for Blueprint changes to apply.

## Required secrets

Configure all three as secret environment variables in Render and in a local `.env` file:

- `DISCORD_TOKEN` — Discord bot token.
- `GEMINI_API_KEY` — primary and secondary Gemini model access.
- `GROQ_API_KEY` — required final provider if Gemini 3.5 and Gemini 3.1 fail.

The bot deliberately fails startup if one of these required keys is missing. Do not commit real tokens or API keys. `.env.example` contains placeholders only.

## AI model order

```text
1. gemini-3.5-flash-lite
2. gemini-3.1-flash-lite
3. Groq: llama-3.3-70b-versatile
```

Relevant settings:

```dotenv
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_FALLBACK_MODELS=gemini-3.1-flash-lite
GEMINI_MODEL_TIMEOUT_SECONDS=20
GEMINI_THINKING_LEVEL=minimal
GROQ_MODEL=llama-3.3-70b-versatile
```

The Gemini model allowlist does not determine a Google project's billing tier. Check the project's billing tier and quotas separately.

## Local development (Windows)

From the repository root, open Command Prompt or PowerShell and run:

```bat
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt pytest
copy .env.example .env
```

Edit `.env` and replace the placeholder values for `DISCORD_TOKEN`, `GEMINI_API_KEY`, and `GROQ_API_KEY`. Then launch the bot:

```bat
.venv\Scripts\python.exe main.py
```

To run the checks locally:

```bat
.venv\Scripts\python.exe -m compileall -q .
.venv\Scripts\python.exe tests\smoke\render_startup_smoke.py
.venv\Scripts\python.exe -m pytest -q tests\unit
```

## Discord configuration

Enable **Message Content Intent** in the Discord Developer Portal. The bot responds to `h!hades <message>`, `h!ask <message>`, direct mentions, DMs, and replies to Hades messages.

## Troubleshooting

### The process exits during startup

Check that all three required environment secrets are present and non-empty, and that the Gemini model setting is on the approved model allowlist. A missing `GROQ_API_KEY` now causes a clear startup error because Groq is mandatory as the final fallback.

### The bot is online but does not read messages

Verify Message Content Intent is enabled, `DISCORD_TOKEN` is current, the command prefix remains `h!`, and the bot has View Channel, Send Messages, Embed Links, and Read Message History permissions.

### Gemini requests fail

Check the Gemini API key, model availability, quota/rate limits, and Render logs for 401/403/404/429 responses. The bot attempts the next provider in the configured chain. If Gemini credentials are rejected, it does not waste time repeating the same failed credential with Gemini 3.1; it proceeds to Groq.

### Render health check fails

Open `/health`; it should return HTTP 200. The `/ready` endpoint is stricter and returns HTTP 503 until Discord is connected, so use it for diagnostics rather than as the Render health check.
