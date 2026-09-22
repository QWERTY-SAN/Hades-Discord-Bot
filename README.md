# Hades Discord AI Bot

A modular Discord AI chatbot that roleplays as **Hades from Aether Gazer** using the Gemini API.

## Features

- Python + `discord.py`
- Gemini API via `google-genai`
- Gemini 3.5 Flash-Lite
- `h!` command prefix
- Mention, DM, and reply-to-Hades chat support
- Per-user, per-channel conversation memory
- Automatic memory expiration and bounded memory usage
- Per-user cooldown
- Global Gemini concurrency limit and queue timeout
- Gemini request timeout and retry handling
- Discord-safe message splitting
- Discord mention suppression for bot replies
- `/health` endpoint for Render
- `/ready` endpoint for readiness checks
- Automatic deployment on commits to `main` when the GitHub-connected Render service uses the Blueprint

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

You can also:

```text
@Hades hello
```

or reply directly to one of Hades' messages.

## Project Structure

```text
Hades-Discord-Bot/
├── main.py
├── requirements.txt
├── render.yaml
├── .env.example
├── .gitignore
├── .python-version
├── README.md
└── hades_bot/
    ├── __init__.py
    ├── bot.py
    ├── chat.py
    ├── config.py
    ├── gemini_client.py
    ├── memory.py
    ├── persona.py
    ├── utils.py
    └── web.py
```

## Environment Variables

Create `.env` locally and keep it out of GitHub:

```env
DISCORD_TOKEN=your_new_discord_bot_token
GEMINI_API_KEY=your_new_gemini_api_key
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

For Render, use the same values as Environment Variables. Never put real credentials in the repository.

## Local Setup

```bash
git clone https://github.com/QWERTY-SAN/Hades-Discord-Bot.git
cd Hades-Discord-Bot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Discord Setup

Enable **Message Content Intent** in the Discord Developer Portal.

Required permissions:

- View Channels
- Send Messages
- Read Message History

Administrator permission is not required.

## Render

Use a **Web Service**.

```text
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

The Blueprint configures:

- Branch: `main`
- Auto deploy: every commit
- Health check: `/health`

Real secrets belong in Render Environment Variables:

```text
DISCORD_TOKEN
GEMINI_API_KEY
```

Other configuration variables can also be set there.

### Health endpoints

```text
/health
```

Returns HTTP 200 while the HTTP server is alive.

```text
/ready
```

Returns HTTP 200 when the Discord bot is connected and ready, otherwise HTTP 503.

Use `/health` for simple uptime monitoring. Use `/ready` when you specifically want Discord readiness.

## Automatic Deployment

With the Render service connected directly to GitHub and Auto-Deploy set to **On Commit**, normal updates are:

```bash
git add .
git commit -m "Update Hades bot"
git push origin main
```

Render then builds and deploys the new commit automatically.

## Security

Never commit:

```text
.env
```

Keep only `.env.example` in GitHub.

If a Discord token or Gemini API key is exposed, rotate it immediately and replace the secret in Render.

## Memory

Conversation memory is stored in RAM and separated by:

```text
Server + Channel + User
```

Memory automatically expires after the configured TTL and is capped by the maximum conversation count.

A Render restart or redeploy clears in-memory conversations.

## License

Fan-made project. Not affiliated with or endorsed by **Aether Gazer**, Yongshi, or the relevant rights holders.
