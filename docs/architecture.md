# Architecture

```text
Hades-Discord-Bot/
├── main.py
├── render.yaml
├── hades_bot/
│   ├── bot.py
│   ├── config.py
│   ├── web.py
│   ├── ai/
│   │   ├── chat.py
│   │   ├── fanservice.py
│   │   ├── gemini_client.py
│   │   └── persona.py
│   ├── core/
│   │   ├── conversation.py
│   │   ├── memory.py
│   │   ├── scope.py
│   │   └── utils.py
│   ├── knowledge/
│   │   ├── character_data.py
│   │   ├── live_sources.py
│   │   └── lore.py
│   └── media/
│       ├── gifs.py
│       ├── images.py
│       └── media.py
├── data/aether_gazer/
└── tests/smoke/
```

## Request flow

1. Discord receives a command, mention, DM, or reply to Hades.
2. Commands are processed first. Prefix commands do not fall through to the AI message handler.
3. Message scope is checked. Explicit specialist requests and configured hard-off-topic subjects are rejected early.
4. Conversation memory is keyed by guild/channel/user or DM-channel/user and guarded by an async lock.
5. Local Aether Gazer context is selected from the stored knowledge snapshot.
6. Current/live questions can attach Gemini URL Context to a small set of relevant Mimir or official source URLs.
7. Gemini generates the response using the Hades persona contract, recent dialogue, fan-service category, and conversation mode.
8. The generated reply is sanitized and checked for forbidden-topic leakage before it is committed to memory.
9. Discord output is split at the 2,000-character limit and optional GIF/image media is attached to the first message.
10. Memory and cooldown/media state are pruned periodically.

## Scope design

Scope is intentionally deterministic before AI generation.

The bot distinguishes:
- stable Aether Gazer terms
- contextual Aether Gazer references
- ordinary social conversation
- personal-choice/advice conversation
- short follow-ups that require history
- specialist requests
- hard unrelated subjects

Context bridges prevent legitimate Aether Gazer statements such as a character's preference for a racing-related activity from being mistaken for an unrelated sports request.

## Knowledge design

The local knowledge layer separates stable character identity from dated gameplay/event/meta snapshots.

`game_knowledge.json` stores larger structured references. `hades_reference.json` stores Hades-specific identity and gameplay snapshots. `live_sources.py` selects fresh source pages only when the message appears to require current/verified information.

The bot never claims that the local snapshot is live.

## Media design

Automatic media:
- chooses either one GIF or one image per automatic trigger
- attaches the selected media to the same response embed
- uses a per-user/per-channel cooldown
- selects GIF vs image type evenly when both are configured
- keeps recent-media history to reduce repetition
- periodically prunes stale state

Manual `h!gif` and `h!image` remain independent.

## Render runtime

`main.py` starts the HTTP health server on Render's `PORT`, validates required secrets, and starts Discord.

- `/health` = liveness
- `/ready` = Discord readiness
- `/status` = bot status command for authorized guild managers

The health server is deliberately kept independent from Discord's event loop so Render can reach the HTTP endpoint while Discord is reconnecting.

## Testing

GitHub Actions runs:
- compilation
- all executable smoke checks
- the full `tests/smoke/test_*.py` pytest suite
- Render startup/config checks
- persona/fan-service regression checks
- memory and scope regression checks

The workflow uses a short timeout and cancels stale runs for the same branch so rapid commits do not create an unnecessary CI backlog.
