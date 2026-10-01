# Hades Discord AI Bot

A modular Discord AI bot that speaks as **Hades from Aether Gazer**, powered by Google's Gemini API.

The bot is designed for Discord servers where you want a Hades-themed conversational assistant that can discuss **Aether Gazer characters, lore, gameplay, builds, and game modes** without pretending to know live or patch-specific information it cannot verify.

## Features

* **Hades persona** — replies in-character while keeping answers useful and readable.
* **Aether Gazer focus** — the topic filter keeps normal conversation and Aether Gazer discussion while redirecting unrelated requests.
* **Game-mode grounding** — a small internal reference helps distinguish modes such as Recurring Dream, Hazard Zone, Dimensional Variable, Causality Survey, Past Grudges, Iterative Testing, Hypothetical Deduction, Battle Sweep/Raid, and Flaneuring.
* **Reduced gameplay hallucinations** — the bot is instructed not to invent exact schedules, rewards, boss rosters, stage counts, or patch-specific mechanics when it does not have reliable information.
* **Conversation memory** — separate memory is maintained per user and channel, with automatic expiration and pruning.
* **Discord-safe output** — responses are sanitized and split to stay within Discord's message length limit.
* **Rate limiting** — per-conversation cooldowns plus a shared Gemini request limit help prevent accidental API spam.
* **Retry handling** — Gemini requests can retry after transient failures.
* **Mentions and DMs** — talk to Hades by mentioning her, replying to her message, or sending a DM.
* **Health endpoint** — includes a small Flask web server for Render health checks.
* **Admin status command** — server administrators can inspect basic runtime statistics.

## Commands

| Command             | Description                                             |
| ------------------- | ------------------------------------------------------- |
| `h!hades <message>` | Talk to Hades                                           |
| `h!ask <message>`   | Alias for `h!hades`                                     |
| `h!reset`           | Clear your current conversation memory                  |
| `h!forget`          | Alias for `h!reset`                                     |
| `h!clear`           | Alias for `h!reset`                                     |
| `h!memory`          | Show the number of stored messages in your conversation |
| `h!ping`            | Check Discord gateway latency                           |
| `h!status`          | Show bot/runtime information; administrators only       |
| `h!hadeshelp`       | Show the command list                                   |
| `h!help`            | Alias for `h!hadeshelp`                                 |

You can also mention Hades, reply directly to one of Hades' messages, or send Hades a DM.

## Requirements

* Python **3.12**
* A Discord bot application
* A Google Gemini API key
* Discord **Message Content Intent**

## Local installation

```bash
git clone https://github.com/QWERTY-SAN/Hades-Discord-Bot.git
cd Hades-Discord-Bot
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your real credentials:

```env
DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

Then run:

```bash
python main.py
```

Never commit real credentials.

## Render

Use a **Web Service**.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
python main.py
```

Health check:

```text
/health
```

The included `render.yaml` is configured to deploy automatically on commits to `main`.

Set these as Render environment variables:

```text
DISCORD_TOKEN
GEMINI_API_KEY
```

## Environment variables

### Gemini

| Variable                |                 Default |
| ----------------------- | ----------------------: |
| `GEMINI_MODEL`          | `gemini-3.5-flash-lite` |
| `GEMINI_THINKING_LEVEL` |               `minimal` |
| `GEMINI_TEMPERATURE`    |                  `0.45` |
| `GEMINI_TOP_P`          |                  `0.90` |

### Bot

| Variable              | Default |
| --------------------- | ------: |
| `BOT_PREFIX`          |    `h!` |
| `STRICT_AETHER_TOPIC` |  `true` |
| `MAX_HISTORY`         |    `16` |
| `MAX_OUTPUT_TOKENS`   |   `768` |
| `MAX_INPUT_CHARS`     |  `6000` |

### Performance

| Variable                  | Default |
| ------------------------- | ------: |
| `USER_COOLDOWN`           |   `2.0` |
| `MAX_CONCURRENT_REQUESTS` |     `3` |
| `MAX_QUEUE_WAIT`          |    `20` |
| `REQUEST_TIMEOUT`         |    `45` |
| `MEMORY_TTL_SECONDS`      | `21600` |
| `MAX_CONVERSATIONS`       |   `500` |

## Project structure

```text
Hades-Discord-Bot/
├── main.py
├── requirements.txt
├── render.yaml
├── .env.example
├── .gitignore
├── hades_bot/
│   ├── bot.py
│   ├── chat.py
│   ├── config.py
│   ├── game_knowledge.py
│   ├── gemini_client.py
│   ├── memory.py
│   ├── persona.py
│   ├── scope.py
│   ├── utils.py
│   └── web.py
└── tests/
    └── smoke_test.py
```

### Module overview

`bot.py` handles Discord events and commands.

`chat.py` handles Gemini requests, request limits, and conversation coordination.

`config.py` loads environment variables.

`game_knowledge.py` contains the stable Aether Gazer gameplay reference.

`gemini_client.py` handles Gemini API calls and retries.

`memory.py` manages conversation history and expiration.

`persona.py` controls Hades' personality and response rules.

`scope.py` handles Aether Gazer topic detection.

`utils.py` contains cooldowns, message splitting, sanitization, and Discord helpers.

`web.py` provides the health endpoint used by Render.

`main.py` starts the web server and Discord bot.

## Gameplay accuracy

The bot does **not** treat `game_knowledge.py` as a live game database.

Its purpose is to prevent Gemini from mixing different Aether Gazer systems together.

For example, it explicitly distinguishes:

* Recurring Dream from Dimensional Variable
* Causality Survey from combat-focused challenges
* Battle Sweep/Raid from standalone end-game modes
* Flaneuring from combat content

For information that can change between versions—such as exact reset times, current rewards, boss rosters, stage counts, or patch-specific mechanics—the bot is instructed to avoid guessing.

This means the bot is intended to be a **knowledge-grounded conversational assistant**, not a live database.

## Conversation memory

Conversation memory is stored in process memory and is separated by user and channel.

Memory expires automatically after the configured TTL. The default is **6 hours**.

Restarting the bot clears the in-memory conversation history.

## Security

Never commit:

```text
DISCORD_TOKEN
GEMINI_API_KEY
.env
```

Real secrets should be stored locally in `.env` or in Render's environment variables.

If a token is accidentally exposed, revoke and replace it immediately.

## Troubleshooting

### Bot is online but does not respond

Check:

1. Discord **Message Content Intent** is enabled.
2. The bot can read and send messages in the channel.
3. `DISCORD_TOKEN` is correct.
4. `GEMINI_API_KEY` is correct.
5. Render logs show a successful Discord gateway connection.

### Hades confuses game modes

Update the relevant entry in:

```text
hades_bot/game_knowledge.py
```

Keep this file focused on stable distinctions instead of rapidly changing reward tables or schedules.

### Gemini requests fail

Check the API key, model name, quotas, timeout, and concurrency settings.

### Render exits with status 1

Check the Render deploy log for the **first Python traceback**. Later errors can simply be consequences of the original failure.

## Testing

Run:

```bash
python tests/smoke_test.py
```

For a syntax check:

```bash
python -m compileall .
```

## Development notes

Keep:

* personality logic in `persona.py`;
* topic handling in `scope.py`;
* gameplay knowledge in `game_knowledge.py`;
* configuration in `config.py`.

This keeps the bot modular and makes future changes easier.

## License

No license is currently specified for this repository. Add a `LICENSE` file if you intend to publish the project for reuse or redistribution.
