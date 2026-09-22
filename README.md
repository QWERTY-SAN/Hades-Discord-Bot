# Hades Discord AI Bot

<<<<<<< HEAD
A modular Discord AI chatbot that roleplays as **Hades from Aether Gazer** using the Gemini API.
<<<<<<< HEAD
=======

The bot is designed to run on **Render Web Service** and supports Discord mentions, DMs, prefix commands, conversation memory, automatic retries, and basic request protection.
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505
=======
A modular Discord AI chatbot that roleplays as **Hades from Aether Gazer** using the **Groq API**.
>>>>>>> parent of 39d2903 (revert back to gemini 3.5-lite)

## Features

- Python + `discord.py`
- Groq API via the official `groq` Python SDK
- Fast chat completions
- Default model: `openai/gpt-oss-20b`
- `h!` command prefix
<<<<<<< HEAD
- Mention, DM, and reply-to-Hades chat support
- Per-user, per-channel conversation memory
- Automatic memory expiration and bounded memory usage
- Per-user cooldown
- Global Groq concurrency limit and queue timeout
- Groq request timeout and retry handling
- Discord-safe message splitting
- Discord mention suppression for bot replies
- `/health` endpoint for Render
- `/ready` endpoint for readiness checks
- Automatic deployment on commits to `main` when the GitHub-connected Render service uses the Blueprint
=======
- Hades roleplay personality based on *Aether Gazer*
- Automatic replies when Hades is mentioned
- Direct-message support
- Reply-to-Hades support
- Per-user, per-channel conversation memory
- Automatic cleanup of inactive conversations
- Bounded memory usage
- Per-user cooldown
- Global Gemini request limit
- Gemini request timeout and retry handling
- Discord 2,000-character response splitting
- Protection against accidental Discord mentions such as `@everyone` and `@here`
- `/health` HTTP endpoint for Render
- `h!reset`
- `h!forget`
- `h!memory`
- `h!status`
- `h!ping`
- `h!hadeshelp`
- Environment-variable based secret management
- Automatic Render deployment from GitHub
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505

## Commands

```text
<<<<<<< HEAD
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

You can also mention Hades directly:

```text
@Hades hello
```

Or reply directly to one of Hades' messages.

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
    ├── groq_client.py
    ├── memory.py
    ├── persona.py
    ├── utils.py
    └── web.py
```

## Environment Variables

Create `.env` locally and keep it out of GitHub:

```env
DISCORD_TOKEN=your_discord_bot_token
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
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

For Render, add the same variables under **Environment Variables**.

## Local Setup

```bash
git clone https://github.com/QWERTY-SAN/Hades-Discord-Bot.git
cd Hades-Discord-Bot
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python main.py
```

## Discord Setup

Enable **Message Content Intent** in the Discord Developer Portal.

Required permissions:

- View Channels
- Send Messages
- Read Message History

Administrator permission is not required.

## Groq Setup

Create a Groq API key in the Groq Console and store it as `GROQ_API_KEY`.

The official Groq Python SDK supports both synchronous and asynchronous clients; this bot uses `AsyncGroq` for non-blocking Discord operation.

Default model:

```text
openai/gpt-oss-20b
```

Groq's current production model list includes `openai/gpt-oss-20b`. Check the current model list in Groq Console before changing models.

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

Add these secrets in Render:

```text
DISCORD_TOKEN
GROQ_API_KEY
```

Never put real credentials in the repository.

### Health endpoints

```text
/health
```

Returns HTTP 200 while the web server is alive.

```text
/ready
```

Returns HTTP 200 when the Discord bot is connected and ready, otherwise HTTP 503.

## Automatic Deployment

With the Render service connected directly to GitHub and Auto-Deploy set to **On Commit**:

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

If a Discord token or Groq API key is exposed, rotate it immediately and replace it in Render.

## Memory

Conversation memory is stored in RAM and separated by:

```text
Server + Channel + User
```

Memory automatically expires after the configured TTL and is capped by the maximum conversation count.

A Render restart or redeploy clears in-memory conversations.

## License

<<<<<<< HEAD
Fan-made project. Not affiliated with or endorsed by **Aether Gazer**, Yongshi, or the relevant rights holders.
=======
h!hades <message>
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505
=======
Fan-made project. Not affiliated with or endorsed by **Aether Gazer**, Yongshi, Groq, or the relevant rights holders.
>>>>>>> parent of 39d2903 (revert back to gemini 3.5-lite)
