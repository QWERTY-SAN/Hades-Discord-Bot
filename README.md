# Hades Discord AI Bot

A modular Discord AI bot that roleplays as Hades from *Aether Gazer* using Gemini.

## What is fixed in this version

- `EMOJIS_ENABLED` is defined consistently in the settings, `.env.example`, `render.yaml`, and Gemini service.
- Programming, coding, homework/assignment, and other explicit specialist-work requests are blocked before Gemini is called.
- `STRICT_AETHER_TOPIC=false` keeps ordinary conversation allowed while the specialist guard stays active.
- Hades keeps her character instead of turning into a generic programming or technical assistant.
- Emojis are sparse and optional rather than spammy.
- GIFs use one plain `HADES_GIF_URLS` list in `hades_bot/gifs.py`.
- There is no GIF mood/category system.
- GIFs are never downloaded or re-uploaded as Discord attachments.
- GIF previews use the original external URL in a Discord image embed.
- No `HADES_GIF_URLS` environment variable is required.
- Discord mentions from model output are sanitized and `AllowedMentions.none()` is used.
- Render health/readiness endpoints remain `/health` and `/ready`.

## Commands

```text
h!hades <message>
h!ask <message>
h!reset
h!forget
h!clear
h!memory
h!gif
h!hadesgif
h!ping
h!status
h!hadeshelp
h!help
```

You can also mention Hades, DM her, or reply to one of her messages.

## GIFs

Edit:

```text
hades_bot/gifs.py
```

Example:

```python
HADES_GIF_URLS = [
    "https://example.com/hades1.gif",
    "https://example.com/hades2.gif",
]
```

Use direct, publicly reachable GIF URLs. The bot sends the original URL and does not create a Discord attachment.

## Render

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

Enable Discord **Message Content Intent** for prefix commands.

## Environment

Copy `.env.example` for local development. In Render, add the same variables through Environment.
Keep the actual `DISCORD_TOKEN` and `GEMINI_API_KEY` out of Git.
