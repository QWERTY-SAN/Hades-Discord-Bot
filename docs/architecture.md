# Architecture

## Repository layout

```text
Hades-Discord-Bot/
├── .github/workflows/ci.yml   # compile, smoke checks, and pytest
├── data/aether_gazer/         # versioned lore and gameplay snapshots
├── docs/                      # architecture, deployment, and behavior guides
├── hades_bot/
│   ├── ai/                    # provider calls, chat orchestration, persona
│   ├── core/                  # conversation modes, scope, memory, utilities
│   ├── knowledge/             # lore retrieval and live-source selection
│   ├── media/                 # GIF/image catalogs and sending logic
│   ├── bot.py                 # Discord commands and message event routing
│   ├── config.py              # typed environment settings and validation
│   ├── web.py                 # Render health/readiness endpoints
│   └── version.py             # runtime/build metadata
├── tests/
│   ├── smoke/                 # executable contract and startup checks
│   └── unit/                  # pytest unit and regression tests
├── main.py                    # process entry point
├── render.yaml                # Render Web Service blueprint
├── requirements.txt           # runtime dependencies
├── .env.example               # safe environment template (no real secrets)
├── README.md                  # user setup and command guide
└── CHANGELOG.md               # release history
```

## Module responsibilities

| Area | Responsibility |
|---|---|
| `hades_bot/bot.py` | Discord lifecycle, command dispatch, message/mention routing, output delivery |
| `hades_bot/config.py` | Reads environment values once and validates required secrets/settings |
| `hades_bot/ai/chat.py` | Coordinates conversation context and response generation |
| `hades_bot/ai/gemini_client.py` | Calls AI providers and handles provider failover |
| `hades_bot/ai/persona.py` | Hades system prompt and character contract |
| `hades_bot/ai/fanservice.py` | Classifies social/fan-service cues and prompt guidance |
| `hades_bot/core/` | Message scope, conversational signals, memory, shared helpers |
| `hades_bot/knowledge/` | Selects local lore context and optional current-source URLs |
| `hades_bot/media/` | Validates media URLs, selects media, tracks cooldown/history |
| `data/aether_gazer/` | Source-controlled lore/gameplay data, separate from runtime logic |
| `tests/smoke/` | Fast executable checks for key integration contracts |
| `tests/unit/` | Focused pytest tests for classifiers, memory, prompts, and failover |

Keep provider/network code in `ai/`, Discord framework code in `bot.py`, reusable message logic in `core/`, and facts in `data/`. Avoid duplicating knowledge facts inside prompts or command handlers.

## Request flow

1. Discord receives a command, mention, DM, or reply to Hades.
2. Commands are processed before the regular AI message handler.
3. Message scope is checked; unrelated specialist requests and hard-off-topic subjects are rejected early.
4. Conversation memory is keyed by guild/channel/user or DM-channel/user and guarded by an async lock.
5. Local Aether Gazer context is retrieved from the versioned knowledge snapshot.
6. Current/source-sensitive questions may use Gemini URL Context with a small set of selected source URLs.
7. AI generation uses the Hades persona contract, recent dialogue, fan-service category, and conversation mode.
8. The response is sanitized and checked before it is committed to memory.
9. Discord output is split at the 2,000-character limit; eligible replies may include a single GIF or image.
10. Memory, cooldown, and recent-media state are pruned periodically.

## AI provider order

The configured chain is **Gemini 3.5 Flash Lite → Gemini 3.1 Flash Lite → Groq**. Groq is required and is attempted when the Gemini model hierarchy cannot produce a response. The API keys belong in local `.env` or Render secret environment settings, never in source files.

## Knowledge and media

The knowledge layer separates stable character identity from dated gameplay/event/meta snapshots. `game_knowledge.json` stores broad structured references; `hades_reference.json` stores Hades-specific identity and gameplay snapshots. The bot treats this local data as a snapshot, not live truth.

Automatic media sends at most one GIF or one image per eligible trigger, uses shared cooldown/history state, and records state only after Discord accepts the response. Manual `h!gif` and `h!image` commands use their own configured cooldowns.

## Runtime health

`main.py` validates settings, starts the HTTP health server on Render's `PORT`, and starts Discord.

- `/health` — process liveness
- `/ready` — Discord readiness
- `/status` — bot diagnostics for authorized managers

The health server runs independently of Discord's event loop so Render can reach its endpoint while Discord is reconnecting.

## Testing layout

- `tests/smoke/` contains standalone Python checks executed directly by CI.
- `tests/unit/` contains `test_*.py` files executed by pytest.
- GitHub Actions compiles Python, runs the smoke scripts, then runs the pytest suite.
- CI supplies placeholder API keys; it does not make live AI calls.

Keep new regression tests in `tests/unit/` and keep fast, script-style deployment checks in `tests/smoke/`.
