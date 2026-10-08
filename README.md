# Hades Discord Bot

A modular Discord AI bot that roleplays as Hades from *Aether Gazer* using Gemini.

## What is improved in this version

### Hades character grounding
- Expanded Hades reference data with identity, affiliation, Gen-Zone, element, Divine Grace, interests, companions, Access Key, Aether Codes, and other stable character details.
- Added source-aware knowledge handling so stable character facts are separated from dated gameplay recommendations.
- Added Hades-specific terminology including Astral Council, Omorfies, Oneiroi, Dance Partner, Dance Duo, and related concepts.
- Updated the persona to align with Hades' documented interests in puppetry, theater, art, and her relationship with Mintha and Leuce.
- Hades remains Hades instead of becoming a generic assistant.

### Reference sources
The bot stores reference metadata for:
- Aether Gazer Wiki (Miraheze): https://aethergazer.miraheze.org/wiki/Main_Page
- Aether Gazer Wiki (Fandom): https://aether-gazer.fandom.com/wiki/Aether_Gazer_Wiki
- Mimir.cat: https://mimir.cat/
- Hades profile: https://mimir.cat/puppet-master/profile
- Hades guide: https://mimir.cat/puppet-master/guides
- Hades voice reference: https://mimir.cat/puppet-master/voice

Mimir's profile and reference pages are treated as structured game data. Dated guide recommendations are explicitly labeled as dated rather than being presented as a live meta.

### Expanded Aether Gazer knowledge
The bot now includes a local, source-aware reference layer for:
- Gaea, Idealbild, Source Layer, Sephirah Zones, Visbanes, Division Nine and key organizations.
- Modifiers, Gen-Zones, Access Keys, Functors, Sigils, Aether Codes, Modified Mode, Zero Time, Modifier Sync, Warp Skills, and Support Modules.
- Shifted Stars, Shifting Flowers, Swigs, Ain Soph Coins and other resource vocabulary.
- Daily, weekly and monthly Shifted Star farming concepts without pretending a fixed live income total is permanent.
- Key characters including Odin, Heimdall, Shu, Poseidon, Tsukuyomi, Skuld, Gengchen, Lingguang, Izanami, and Hera.

Gameplay totals, banner advice, tier lists and balance recommendations remain version-sensitive. The knowledge layer tells Hades to treat those as dated unless fresh source data is available.

### Normal conversation improvements
Normal conversation is treated as a first-class use case while keeping the bot's Aether Gazer scope intact.
- Common short replies such as "thanks", "same", "fair enough", "you too", "really?", and "no way" are recognized as conversation instead of unrelated questions.
- Everyday personal statements such as being tired, getting home, waking up, missing someone, or having nothing to do can continue the conversation naturally.
- Simple personal-choice prompts such as "what should I do tonight?" are allowed without turning Hades into a general-purpose assistant.
- Casual turns no longer receive a large lore-retrieval block unless the current message actually calls for Aether Gazer knowledge.
- Hades is instructed to react to the user's actual message, avoid automatic lectures/advice, keep simple replies short, and avoid ending every message with a question.

### Scope
The bot is intentionally narrow.

Allowed:
- Aether Gazer
- Hades and her lore
- Aether Gazer characters, organizations, terminology and gameplay
- Direct personal/social conversation with the Administrator
- Puppetry, theater, art, and Hades' own interests

Blocked:
- F1 / Formula One / motorsports and sports
- Other video games
- Programming, coding, computing and technical work
- Politics, news and finance
- General entertainment/media
- Homework and other specialist work
- Unrelated factual questions

Scope decisions are deterministic, but refusal wording is generated dynamically in Hades' persona and the blocked subject is not discussed in the refusal.


### Fan-service behavior

The bot includes a narrow, dynamic fan-service layer for playful admiration and affectionate banter. Examples include compliments, exaggerated requests such as "step on me," light romance, hugs/kisses/headpats, and requests for attention. Responses are generated in Hades' persona rather than selected from fixed replies. The behavior is intentionally non-explicit and does not turn unrelated conversation into flirting.

### Emojis
`EMOJIS_ENABLED=true` enables sparse Hades-style emoji use. Usually 0-2 emojis are used; many responses use none.

### Expanded social interaction

Hades' strict topic scope now recognizes more Hades-directed social cues without turning her into a general-purpose assistant. This includes date invitations, shared meals, scent/perfume/whiff requests, close-proximity affection, playful "hard to get" banter, and contextual follow-ups such as "how did you know?". These cues remain dynamic Gemini-generated interactions; they are not predefined responses.

### Expanded fan-service

Fan-service now covers more than direct compliments or "step on me" prompts. Detection includes captivated/mesmerized language, theatrical devotion, playful jealousy, additional affection cues, voice/presence compliments, and attention-focused flirting. These are classification cues for Gemini—not a fixed response bank—and Hades is instructed to vary between teasing, graceful acceptance, mock authority, warmth, challenge, and restrained flirtation.


### Hades images

Standalone Hades images are configured separately from GIFs in `hades_bot/media/images.py`:

```python
HADES_IMAGE_URLS = [
    "https://i.imgur.com/uNBcXQg.jpeg",
    "https://i.imgur.com/gQN3GNb.jpeg",
]
```

### GIFs
Edit:

```text
hades_bot/media/gifs.py
```

Example:

```python
HADES_GIF_URLS = [
    "https://example.com/hades1.gif",
    "https://example.com/hades2.gif",
]
```

GIF URLs are not stored in `.env` and are not uploaded back to Discord. The bot uses the original external URL as an embed image, so the raw URL is not posted as message content. Image URLs are handled separately in `hades_bot/media/images.py`. Automatic media is attached to Hades' normal response embed rather than sent as a second message. Media state is pruned periodically so long-running Render instances do not accumulate stale per-user/channel entries. When both media types are configured, automatic selection chooses the type evenly before choosing a recent-URL-safe item.

### Endgame, events, and service lifecycle knowledge
The local knowledge layer also covers:
- Recurring Dream, Hazard Zone, Dimensional Variable, Iterative Testing, Past Grudges, and Causality Survey.
- M.E.O.W., M.E.O.W. Chips, Support Modules, Sigil Collection, Battle Sweep, and other late-game progression.
- Temporary version events, anniversary/seasonal events, minigames, reward campaigns, reruns, and event shops.
- Daily/weekly/monthly Shifted Star farming concepts, with version-sensitive totals kept separate from stable terminology.
- EoU vs EOS terminology, the Global V5.2 final-content plan, the planned Companion Server, and future-preservation uncertainty.

Lifecycle and event data is stored as a dated snapshot. Hades is instructed not to present old event schedules, reward totals, team tiers, or service plans as timeless facts.

### Current reference snapshots
- Mimir Hades profile: last update September 1, 2026.
- Mimir Global Teams: last update September 28, 2026.
- Knowledge snapshot: October 4, 2026.

### Commands

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
h!about
h!version
h!privacy
h!status
h!diagnose
h!hadeshelp
h!help
```

You can also mention Hades, DM her, or reply directly to one of her messages.

### Environment
Copy `.env.example` for local development. Render should contain the same configuration values, with the actual `DISCORD_TOKEN` and `GEMINI_API_KEY` stored as secrets.

```env
DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_THINKING_LEVEL=minimal
BOT_PREFIX=h!
STRICT_AETHER_TOPIC=true
EMOJIS_ENABLED=true
LIVE_SOURCE_REFRESH=true
LIVE_SOURCE_MAX_URLS=3
MAX_HISTORY=16
MEMORY_TTL_SECONDS=21600
MAX_CONVERSATIONS=500
MAX_OUTPUT_TOKENS=768
MAX_INPUT_CHARS=6000
USER_COOLDOWN=2.0
MAX_CONCURRENT_REQUESTS=3
MAX_QUEUE_WAIT=20
REQUEST_TIMEOUT=45
MAX_RETRIES=3
MEMORY_PRUNE_INTERVAL=900
COOLDOWN_PRUNE_INTERVAL=3600
```

### Render

The Blueprint uses Render's After CI Checks Pass deployment mode (`checksPass`), so a commit is deployed only after the GitHub Actions checks succeed. Render retains an existing service's auto-deploy setting until the Blueprint is synced, so sync the Blueprint once after changing `render.yaml`.

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

### Tests

CI runs the complete smoke suite plus pytest-style regression tests for conversation behavior, fan-service detection, memory, persona contracts, scope boundaries, compilation, media, and Render startup configuration.

## Endgame knowledge

The knowledge layer includes recurring and late-game systems: Recurring Dream, Hazard Zone, Dimensional Variable, Iterative Testing, Past Grudges, Causality Survey, Sigil Collection, Battle Sweep, Support Modules, and M.E.O.W. progression. Exact schedules, reward totals, difficulty thresholds, and meta recommendations are treated as version-sensitive rather than hard-coded.

## Service lifecycle knowledge

The bot has a dated Aether Gazer service-lifecycle snapshot. It distinguishes EoU (end of updates/content) from immediate EOS and treats future dates/options as plans unless an official notice changes them.

As of 2026-10-04, CN has already ended new content after V5.2 (2026-07-23) and entered its Companion Server phase. Global is still scheduled to receive content through V5.2 on 2026-12-01, after which it is planned to continue through a Companion Server with a planned horizon of 2031-09 and a reassessment around 2031-03.


## Aether Gazer knowledge layer

The bot includes structured reference data covering Hades, world/lore, regions and organizations, named historical events, combat resources and systems, endgame modes, version events, Shifted Star routines, Support Modules, M.E.O.W., Opponent Intel, Achievements, scans/economy, side content, and the service lifecycle.

The knowledge layer distinguishes stable lore from dated gameplay data. It does not claim live access to banners, rotations, rewards, or current meta.

## Additional improvements

- Knowledge retrieval now scores multiple relevant Aether Gazer anchors instead of taking only the first few exact matches.
- Follow-up questions can reuse the most recent user turns when selecting lore/gameplay context.
- Scope matching distinguishes hard unrelated topics from generic words that can legitimately appear in Aether Gazer lore (for example, a character liking horse racing or the game's Music Dossier).
- GIF cooldown/history state is periodically pruned.
- Forbidden model output releases the user's cooldown instead of consuming it.
- Hades' current profile snapshot includes her named outfits, Heart Link reference, Access Key synergy and current chips.
- Ancient Shadow and Crisis Analysis are represented as version-sensitive event/challenge content.


## Repository structure

The repository is split by responsibility so knowledge updates and runtime changes stay isolated:

```text
Hades-Discord-Bot/
├── hades_bot/
│   ├── bot.py
│   ├── config.py
│   ├── core/       # memory, scope, shared utilities
│   ├── ai/         # Gemini, chat orchestration, persona
│   ├── knowledge/  # local knowledge loading and retrieval
│   └── media/      # external GIF list and media handling
├── data/aether_gazer/
│   ├── game_knowledge.json
│   ├── terminology.json
│   ├── source_policy.json
│   ├── sources.json
│   └── characters/
├── docs/
└── tests/smoke/
```

The Scan/Gacha material is knowledge-only. It explains Aether Gazer's acquisition systems, vouchers, pity/guarantee concepts, and version-sensitive rules; it does not add a gacha command.

## Release
Version 1.5.0 consolidates the latest Hades persona, strict scope, dynamic refusals, confidence-aware fan-service, canonical Hades reference loading, safer memory commits, Aether Gazer knowledge, Scan/Gacha knowledge, F2P/spender terminology, endgame/event/lifecycle data, emoji handling, external GIF embedding, and improved normal conversation behavior.


### Automatic media

When Hades is mentioned, the bot randomly chooses **one** automatic media type: a GIF **or** an image. It never sends both from the same automatic trigger. The GIF and image libraries remain separate, and the automatic media trigger uses one 5-minute per-user/channel cooldown. The selected media is placed inside the same embed as Hades' response, so no second media message is sent. The manual `h!gif` and `h!image` commands remain separate as well.
