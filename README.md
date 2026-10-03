# Hades Discord AI Bot

A modular Discord AI chatbot styled after **Hades from Aether Gazer**, powered by Google Gemini.

This version keeps the current Hades bot architecture and `h!` prefix, while adding a Kafka-style presentation layer and a small local Aether Gazer reference layer.

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

The bot can also respond to direct mentions, DMs, and direct replies to its messages.

## Main improvements

- Hades-first persona: she stays Hades rather than becoming a generic assistant.
- Natural off-topic conversation by default (`STRICT_AETHER_TOPIC=false`).
- Local Hades character data and Aether Gazer terminology.
- Aether Gazer lore context is only injected when relevant.
- Per-user/per-channel memory with TTL, locking and capacity control.
- Gemini retries, queue limiting, cooldowns and error handling.
- Discord-safe output splitting and mention sanitization.
- Kafka-inspired configurable GIF behavior.
- GIF hash-based recent-item avoidance.
- Optional sparse emoji guidance.
- Render-compatible `/`, `/health`, and `/ready` endpoints.

## GIFs

GIF URLs are stored in `hades_bot/gifs.py`, not in `.env`:

```python
    "https://example.com/hades1.gif",
    "https://example.com/hades2.gif",
]
```


```python
    "https://example.com/hades1.gif",
    "https://example.com/hades2.gif",
    "https://example.com/hades3.gif",
    "https://example.com/hades4.gif",
    "https://example.com/hades5.gif",
]
```

Modes:

```text
off
first_reply
every_mention
every_command
every_response
```

`h!gif` and `h!hadesgif` always force one GIF attempt when at least one URL is configured in `hades_bot/gifs.py`.

The bot uploads the downloaded GIF to Discord rather than relying on an external embed. It also remembers recent SHA-256 hashes per user/channel to reduce repeats.

## Setup

### 1. Install Python

Python 3.11 is the recommended runtime used by the repository.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and set:

```text
DISCORD_TOKEN=...
GEMINI_API_KEY=...
```

Never commit `.env` or real keys.

### 4. Discord Developer Portal

Enable **Message Content Intent** for prefix commands and mentions.

### 5. Run locally

```bash
python main.py
```

## Render

Use a **Web Service** with:

```text
Build Command: pip install -r requirements.txt
Start Command: python main.py
Health Check Path: /health
```

`render.yaml` is already configured for automatic deploys from the `main` branch.

## Important model setting

The default environment keeps the model name used by the current Hades repository:

```text
GEMINI_MODEL=gemini-3.5-flash-lite
```

Change it in Render when your Gemini project exposes a different supported model name.

## Data policy

The local `data/` files contain stable character/reference information only. They are not a live Aether Gazer database and deliberately avoid pretending that current banners, patch notes, balance values or tier lists are verified.

Reference sites:

- https://aethergazer.miraheze.org/wiki/Main_Page
- https://mimir.cat/
- https://mimir.cat/puppet-master/

## GIF system

GIF URLs are code configuration, not Render environment variables. Edit `hades_bot/gifs.py` and commit the change.



```python
    "https://host/hades1.gif",
    "https://host/hades2.gif",
    "https://host/hades3.gif",
    "https://host/hades4.gif",
]
```


Useful settings:

```env
```

