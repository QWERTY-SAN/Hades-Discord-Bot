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

### Emojis
`EMOJIS_ENABLED=true` enables sparse Hades-style emoji use. Usually 0-2 emojis are used; many responses use none.

### GIFs
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

GIF URLs are not stored in `.env` and are not uploaded back to Discord. The bot uses the original external URL as an embed image, so the raw URL is not posted as message content.

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
h!status
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

The repository contains lightweight smoke tests for scope enforcement and the source-grounded Hades reference layer.

## Endgame knowledge

The knowledge layer includes recurring and late-game systems: Recurring Dream, Hazard Zone, Dimensional Variable, Iterative Testing, Past Grudges, Causality Survey, Sigil Collection, Battle Sweep, Support Modules, and M.E.O.W. progression. Exact schedules, reward totals, difficulty thresholds, and meta recommendations are treated as version-sensitive rather than hard-coded.

## Service lifecycle knowledge

The bot has a dated Aether Gazer service-lifecycle snapshot. It distinguishes EoU (end of updates/content) from immediate EOS and treats future dates/options as plans unless an official notice changes them.

As of 2026-10-04, CN has already ended new content after V5.2 (2026-07-23) and entered its Companion Server phase. Global is still scheduled to receive content through V5.2 on 2026-12-01, after which it is planned to continue through a Companion Server with a planned horizon of 2031-09 and a reassessment around 2031-03.

