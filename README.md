# Hades Discord AI Bot

A modular Discord AI bot that roleplays as **Hades from Aether Gazer**, powered by Google's Gemini API.

The bot is designed around three priorities:

- **Hades first:** responses should sound like Hades rather than a generic AI assistant.
- **Aether Gazer focused:** lore, characters, factions, gameplay, abilities, and related conversation are the bot's main subject.
- **Natural conversation:** casual conversation is allowed, while clearly unrelated requests are redirected without turning every message into a hard refusal.

> **Current scope:** This repository is a character-focused Hades bot, not a general-purpose Discord assistant.

---

## Features

### Hades persona

Hades is represented as a composed, refined, observant, confident, mischievous, and authoritative character. Her tone can become warmer, teasing, serious, or protective depending on the conversation while avoiding forced catchphrases and repetitive puppetry metaphors.

### Balanced topic scope

The bot uses an application-level scope check before sending a request to Gemini.

- Aether Gazer questions are allowed.
- Casual conversation is allowed, even when it is not about Aether Gazer.
- Ambiguous messages are allowed through instead of being blocked by generic question words.
- Clearly unrelated information or task requests can be redirected before they reach Gemini.
- Aether Gazer context takes priority when unrelated words are mentioned incidentally.
- Greek-mythology references to Hades are separated from the Aether Gazer character where possible.

The scope system is intentionally **balanced**. It should not treat words such as `what is`, `how do I`, or `explain` as off-topic by themselves.

### Conversation memory

The bot keeps short-term conversation memory per conversation context. Memory is stored in memory while the process is running and is subject to the configured TTL and conversation limit.

### Discord interaction

You can talk to Hades using commands, mentions, DMs, or replies to her messages.

### Reliability controls

The bot includes:

- Per-conversation cooldown handling
- Concurrent Gemini request limits
- Request timeouts
- Queue wait limits
- Retry handling in the Gemini client
- Discord message splitting for responses over Discord's message limit
- Output sanitization and disabled automatic mentions
- Periodic memory and cooldown cleanup
- A small Flask health endpoint for hosting platforms such as Render

---

## Commands

Default prefix: `h!`

| Command | Description |
|---|---|
| `h!hades <message>` | Talk to Hades |
| `h!ask <message>` | Alias for `h!hades` |
| `h!reset` | Clear the current conversation |
| `h!forget` | Alias for `h!reset` |
| `h!clear` | Alias for `h!reset` |
| `h!memory` | Show the current conversation's memory count and expiry |
| `h!ping` | Show Discord gateway latency |
| `h!status` | Show bot status information; server administrators only |
| `h!hadeshelp` | Show the command list |
| `h!help` | Alias for `h!hadeshelp` |

You can also:

- Mention Hades directly.
- Reply to one of Hades' messages.
- DM the bot.

### Examples

```text
h!hades Tell me about the Society of Muses.
h!hades What do you think of Mintha?
h!ask Explain Hades' role in Olympus.
```

---

## Requirements

- Python 3.10+ recommended
- A Discord application and bot token
- A Google Gemini API key
- Discord **Message Content Intent** enabled

The current repository pins these main dependencies:

- `discord.py 2.7.1`
- `google-genai 2.23.0`
- `python-dotenv 1.1.1`
- `Flask 3.1.3`

See `requirements.txt` for the exact versions.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/QWERTY-SAN/Hades-Discord-Bot.git
cd Hades-Discord-Bot
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` for local development:

```text
DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
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

`DISCORD_TOKEN` and `GEMINI_API_KEY` are required. The remaining values have defaults in `hades_bot/config.py`.

**Never commit real API keys or bot tokens to Git.**

### 4. Enable Message Content Intent

In the Discord Developer Portal:

1. Open your application.
2. Go to **Bot**.
3. Enable **Message Content Intent**.
4. Save the changes.

The bot enables the intent in code, but Discord must also allow it for the application.

### 5. Start locally

```bash
python main.py
```

The process starts the health server and then connects the Discord bot.

---

## Render deployment

This repository includes `render.yaml` for Render deployment.

### Build command

```text
pip install -r requirements.txt
```

### Start command

```text
python main.py
```

### Health check

```text
/health
```

The included Render configuration uses a **Web Service**, listens through the small Flask server, and is configured for automatic deployment on commits to `main`.

Add these required secrets in Render:

```text
DISCORD_TOKEN
GEMINI_API_KEY
```

The other environment variables are already provided with defaults by `render.yaml`.

### Important

The Discord bot itself is not an HTTP application. The web server exists primarily so a hosting platform such as Render can check that the process is alive.

---

## Configuration

| Variable | Default | Purpose |
|---|---:|---|
| `DISCORD_TOKEN` | — | Discord bot token **(required)** |
| `GEMINI_API_KEY` | — | Gemini API key **(required)** |
| `GEMINI_MODEL` | `gemini-3.5-flash-lite` | Gemini model name |
| `BOT_PREFIX` | `h!` | Prefix for commands |
| `MAX_HISTORY` | `16` | Maximum messages retained per conversation |
| `MAX_OUTPUT_TOKENS` | `768` | Maximum generated output tokens |
| `MAX_INPUT_CHARS` | `6000` | Maximum user prompt length |
| `USER_COOLDOWN` | `2.0` | Cooldown in seconds |
| `MAX_CONCURRENT_REQUESTS` | `3` | Maximum Gemini requests processed at once |
| `MAX_QUEUE_WAIT` | `20` | Maximum queue wait before a request fails |
| `REQUEST_TIMEOUT` | `45` | Gemini request timeout in seconds |
| `MEMORY_TTL_SECONDS` | `21600` | Conversation memory lifetime (6 hours) |
| `MAX_CONVERSATIONS` | `500` | Maximum stored conversations |
| `MEMORY_PRUNE_INTERVAL` | `900` | Memory cleanup interval (15 minutes) |
| `COOLDOWN_PRUNE_INTERVAL` | `3600` | Cooldown cleanup interval (1 hour) |

---

## Project structure

```text
Hades-Discord-Bot/
├── hades_bot/
│   ├── __init__.py
│   ├── bot.py
│   ├── chat.py
│   ├── config.py
│   ├── gemini_client.py
│   ├── memory.py
│   ├── persona.py
│   ├── scope.py
│   ├── utils.py
│   └── web.py
├── .env.example
├── .gitignore
├── main.py
├── render.yaml
├── requirements.txt
└── README.md
```

### What each module does

| File | Role |
|---|---|
| `main.py` | Application entry point; starts the web server and bot |
| `hades_bot/bot.py` | Discord events, commands, message routing, and cooldowns |
| `hades_bot/persona.py` | Hades system prompt and character behavior |
| `hades_bot/scope.py` | Balanced Aether Gazer / off-topic detection |
| `hades_bot/chat.py` | Conversation orchestration and Gemini request flow |
| `hades_bot/gemini_client.py` | Gemini API integration, retries, timeout handling |
| `hades_bot/memory.py` | Per-conversation short-term memory |
| `hades_bot/config.py` | Environment variables and configuration defaults |
| `hades_bot/utils.py` | Message splitting, sanitization, cooldown helpers, and utilities |
| `hades_bot/web.py` | Health/readiness web endpoints for hosting |

---

## Memory behavior

Conversation memory is scoped by user and channel.

In a server conversation, the key is based on:

```text
guild → channel → user
```

DM conversations are scoped to the user.

Memory is temporary and is automatically removed after the configured TTL or when the conversation limit requires pruning.

Use:

```text
h!memory
```

to see the current conversation's stored message count and expiry period.

Use:

```text
h!reset
```

to clear the current conversation immediately.

---

## Scope behavior

The scope system is **not** meant to be a complete content classifier. It is a lightweight guard around the character bot.

### Allowed

```text
"Tell me about Hades in Aether Gazer."
"How does the Society of Muses work?"
"What do you think of Mintha?"
"Hey Hades, how are you?"
"I'm tired today."
```

### Redirected

```text
"How do I write a Python Discord bot?"
"Which GPU should I buy?"
"Explain calculus."
"What's the weather today?"
```

### Important distinction

Mentioning an unrelated word does not automatically make a message off-topic.

For example, a conversation such as:

```text
"I was playing Aether Gazer on my PC and I'm having trouble with Hades' build."
```

still has clear Aether Gazer context and should remain a normal Hades conversation.

Likewise, generic question phrasing such as `what is`, `how do I`, or `explain` is not considered off-topic by itself.

---

## Character design

The bot's character instructions are intentionally separate from its Discord and API code.

`persona.py` controls things such as:

- Hades' voice and temperament
- Her relationship with the Administrator
- Teasing and affection boundaries
- Puppetry imagery
- Mintha and Leuce
- Society of Muses and Olympus context
- Canon discipline
- Serious and emotional situations
- Conversational pacing and response length

The goal is to keep **character behavior** separate from the technical bot implementation.

---

## Security and privacy

- Never commit `.env` or real credentials.
- Gemini credentials should stay in environment variables or your hosting provider's secret store.
- Discord mentions are disabled for generated output to reduce accidental pings.
- User conversation memory is held in process memory and is not designed as permanent storage.
- `h!status` is restricted to server administrators because it exposes operational information.

---

## Troubleshooting

### Bot starts but does not respond

Check:

1. `DISCORD_TOKEN` is correct.
2. `GEMINI_API_KEY` is correct.
3. **Message Content Intent** is enabled in the Discord Developer Portal.
4. Hades has permission to read and send messages in the channel.
5. The user is actually mentioning Hades, replying to Hades, using a DM, or using a command.

### Prefix commands do not work

Make sure:

```text
BOT_PREFIX=h!
```

and **Message Content Intent** is enabled.

### Render reports an unhealthy service

Check the Render health path:

```text
/health
```

The web server is started by `main.py` before the Discord bot connects.

### Gemini requests fail

Check the Render logs or local console output for API errors. Confirm the model name and Gemini API key are valid.

### Hades feels too restrictive

The first place to check is:

```text
hades_bot/scope.py
```

The second is:

```text
hades_bot/persona.py
```

Avoid turning the scope file into a huge keyword blacklist. The intended behavior is balanced: clear off-topic tasks are redirected, while normal conversation and ambiguous messages are allowed through.

---

## Development notes

The bot is intentionally modular so persona changes do not require rewriting the Discord event system.

A typical change should be limited to:

- `persona.py` for characterization
- `scope.py` for topic boundaries
- `bot.py` for Discord behavior and commands
- `chat.py` / `gemini_client.py` for AI request handling
- `memory.py` for conversation storage behavior

Keep secrets out of source control and test locally before deploying to Render.

---

## License

No license is currently declared in this repository. Unless a license is added, do not assume the code is available for unrestricted reuse.

---

## Repository

**GitHub:** https://github.com/QWERTY-SAN/Hades-Discord-Bot

Built as a Hades from **Aether Gazer** character bot using Discord.py and Gemini.
