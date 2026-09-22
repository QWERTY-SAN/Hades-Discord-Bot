# Hades Discord AI Bot

A modular Discord AI chatbot that roleplays as Hades from Aether Gazer and uses the Gemini API.

## Features

- Python + discord.py
- Gemini API via `google-genai`
- `h!` command prefix
- Automatic replies when Hades is mentioned
- DM support
- Per-user, per-channel conversation memory
- `h!reset`
- `h!ping`
- `h!hadeshelp`
- Discord 2000-character response splitting
- Basic per-user cooldown
- Retry handling for Gemini failures
- Render Background Worker configuration
- Secrets kept in environment variables

## Commands

```text
h!hades hello
h!reset
h!ping
h!hadeshelp
```

You can also mention the bot:

```text
@Hades hello
```

## Local setup

Create a local `.env` file. Do not commit it.

```env
DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash
BOT_PREFIX=h!
MAX_HISTORY=24
MAX_OUTPUT_TOKENS=1024
USER_COOLDOWN=2.0
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python main.py
```

## Discord setup

Enable the **Message Content Intent** for the bot in the Discord Developer Portal.

The bot needs permission to:

- View Channels
- Send Messages
- Read Message History

## Render

Use a **Background Worker**.

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
python main.py
```

Add `DISCORD_TOKEN` and `GEMINI_API_KEY` as Render environment variables.

## Security

Never put real Discord or Gemini credentials in this repository.

The real values belong in Render's environment variables or in a local `.env` file that is ignored by Git.

If a credential has already been exposed publicly, rotate it before deploying.
