# Hades Discord Bot

An in-character Discord chatbot for **Hades from Aether Gazer**, powered by the Gemini Developer API. Hades supports Aether Gazer lore/gameplay questions and bounded everyday conversation while retaining her character and topic boundaries.

**Current release: 2.7.3**

## AI provider fallback order

Hades uses this exact provider order:

| Priority | Provider/model | When it is used |
|---|---|---|
| 1 — Primary | `gemini-3.5-flash-lite` | Normal responses |
| 2 — Fallback | `gemini-3.1-flash-lite` | If the primary Gemini model fails with a retryable error, timeout, rate limit, or unavailable-model error |
| 3 — Final fallback | Groq `llama-3.3-70b-versatile` | If both Gemini model attempts fail, or Gemini credentials are rejected |

Groq is required as the final fallback. `GROQ_API_KEY` must be set locally and in Render; startup validation fails clearly if it is missing. Groq is attempted after the Gemini model hierarchy, not before Gemini 3.1. If the Gemini credential itself is rejected, the bot skips repeating the same credential failure and proceeds directly to Groq.

Google lists both Gemini Lite models with **Free Tier** token pricing in its [Gemini API pricing table](https://ai.google.dev/gemini-api/docs/pricing). The bot's configuration allowlist rejects other primary model IDs and filters fallback entries that are not approved. Groq has its own separate model and account limits.

**Model choice does not set the Google project's billing tier.** To keep Gemini API usage at $0, use an API key belonging to a project on Gemini API Free Tier and remain within the project's free quotas. The same model IDs are billed at Paid Tier rates when used through a paid-tier project. Review the current [pricing and free-tier terms](https://ai.google.dev/gemini-api/docs/pricing) in Google AI Studio before using the bot.

The bot uses URL Context for configured live-source lookups; Google currently lists URL Context as free of charge. Model availability, quotas, and tool support can change, so consult Google's current documentation rather than treating free access as guaranteed indefinitely.

### Environment model settings

Keep these values in your local `.env` file or Render environment settings:

```env
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_FALLBACK_MODELS=gemini-3.1-flash-lite
GEMINI_MODEL_TIMEOUT_SECONDS=20
GEMINI_THINKING_LEVEL=minimal
GROQ_MODEL=llama-3.3-70b-versatile
# Required final fallback; set your secret in .env / Render, never commit a real key.
GROQ_API_KEY=your_groq_api_key
```

Do not put `DISCORD_TOKEN` or `GEMINI_API_KEY` in source control. Render should store both as secret environment variables. The approved model names are enforced at startup/configuration; they do not override the billing plan or quota attached to the Google project.

---

## Recent updates

The current release is **2.7.3**. Hades now recognizes playful vocal requests such as "Can u say ara-ara?" and handles clipped gameplay follow-ups such as "Can be pierced though for tanky gears" as continuations rather than reflexively refusing them. Food-choice banter, model failover, and Free Tier billing caveats are also documented. The complete release-by-release history—including earlier conversation, fan-service, memory, media, knowledge, safety, and deployment changes—is preserved in [Full version history](#full-version-history).

## Bot overview

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

Food conversation is recognized specifically. Hades can react to messages such as "I'm hungry", "what food do you like?", "this looks delicious", "I'm craving ramen", or "what should we eat?" as natural social chat. She can express an in-character preference without claiming it is confirmed canon. Recipes, ingredient lists, and cooking instructions remain blocked, so this does not make her a general cooking assistant.
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
- Casual food conversation, hunger/cravings, food preferences, and meal invitations
- Puppetry, theater, art, and Hades' own interests

Blocked:
- F1 / Formula One / motorsports and sports
- Other video games
- Programming, coding, computing and technical work
- Politics, news and finance
- General entertainment/media
- Homework and other specialist work
- Unrelated factual questions
- Recipes, ingredient lists, and cooking instructions

Scope decisions are deterministic, but refusal wording is generated dynamically in Hades' persona and the blocked subject is not discussed in the refusal.


### Fan-service behavior

The bot includes a narrow, dynamic fan-service layer for playful admiration and affectionate banter. Examples include compliments, exaggerated requests such as "step on me," light romance, hugs/kisses/headpats, and requests for attention. Responses are generated in Hades' persona rather than selected from fixed replies. The behavior is intentionally non-explicit and does not turn unrelated conversation into flirting.

### Emojis
`EMOJIS_ENABLED=true` enables contextual Hades-style emoji use. The expanded palette covers puppetry/art (🎭🪡🧵🪆), signature atmosphere (🌙✨🖤🎀), teasing/flirtation (😏👀💜🌹💋), comfort (🫶💜🌷), celebration (🎉🌟🥂), and food/tea (🍰☕🫖). Hades usually uses 0-2 emojis; serious, detailed, code-heavy, or already-emoji replies are not decorated automatically.

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
GEMINI_FALLBACK_MODELS=gemini-3.1-flash-lite
GEMINI_THINKING_LEVEL=minimal
GEMINI_MODEL_TIMEOUT_SECONDS=20
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

### AI provider failover

Hades tries `GEMINI_MODEL` first, then the comma-separated `GEMINI_FALLBACK_MODELS` list. With the defaults, that is Gemini 3.5 Flash-Lite → Gemini 3.1 Flash-Lite → required Groq (`GROQ_MODEL`, default `llama-3.3-70b-versatile`). `GROQ_API_KEY` is required and validated at startup. Groq is attempted after Gemini model failures; if Gemini credentials are rejected, the bot proceeds directly to Groq rather than retrying with the same invalid credentials. If a Gemini request fails, the bot moves to Gemini 3.1 where useful and then to Groq; authentication failures skip another attempt with the same rejected Gemini credential and go directly to Groq. The only approved Gemini IDs are `gemini-3.5-flash-lite` (primary) and `gemini-3.1-flash-lite` (fallback). Both are listed with Free Tier token pricing in [Google's official pricing table](https://ai.google.dev/gemini-api/docs/pricing). The allowlist restricts model selection, but it does **not** set the Google project's billing tier; to keep API usage at $0, use a project on Gemini API Free Tier and stay within its quotas. Google's URL Context tool is currently listed as free of charge, but always check the current pricing and tool availability documentation.

`GEMINI_MODEL_TIMEOUT_SECONDS=20` bounds each model attempt, and SDK retries are capped at one retry before the bot moves to the next model. Invalid credentials or permissions fail fast rather than wasting time on every model. The fallback count and last successful model appear in staff diagnostics.

A Gemini outage and a Discord gateway disconnect are separate failure domains. Model failover helps responses survive Gemini errors; it cannot fix a Discord/network outage. discord.py reconnects the gateway, while repeated heartbeat failures should prompt a check for blocked synchronous work, CPU saturation, or unstable network connectivity.

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

## Automatic media

- Bumped the application release to `2.0.0` so the runtime version, README, and release state stay aligned.
- Hardened Render deployment with an explicit free plan and a build filter so documentation-only changes do not unnecessarily rebuild the bot.
- Kept After CI Checks Pass deployment enabled so failed GitHub Actions checks do not reach Render.
- Removed duplicate disconnect-state handling and improved command-error wording.
- Sanitized generated GIF URLs and raw Discord mention markup so model output cannot accidentally expose media links or mention markup as visible text.
- Kept the Gemini 3.5 Flash-Lite model as the default; it is currently a GA model and remains the low-cost/high-throughput choice for this bot.
- Preserved dynamic fan-service behavior: reaction lanes are generated from the current message and recent context rather than a fixed response bank.

### Automatic media

When Hades is mentioned **or** the Administrator uses `h!hades <message>` / `h!ask <message>`, the bot may randomly attach **one** automatic media type: a GIF **or** an image. It never sends both from the same automatic trigger. Plain replies to Hades stay media-free, keeping short follow-ups less noisy. The GIF and image libraries remain separate, and automatic media uses a shared per-user/channel cooldown. The selected media is placed inside the same embed as Hades' response, so no second media message is sent. The manual `h!gif` and `h!image` commands use their own configured cooldowns. Recent-media history, metrics, and automatic cooldowns are recorded only after a successful Discord send.

---

## Full version history

The entries below preserve the detailed release notes from the project's `CHANGELOG.md`, including versions that were not described in the earlier README. Entries reflect each version as it shipped; newer releases can supersede prior defaults. **For the current model configuration, use the Free Tier Lite setup documented near the top of this README.**

## 2.7.3 — 2026-10-14

### In-character vocal requests and contextual game follow-ups
- Recognized direct requests to say playful phrases such as "ara-ara" and routed them through Hades's voice/fan-service guidance instead of the generic scope refusal.
- Added a narrow continuation detector for unfinished clauses such as "Can be pierced though for tanky gears", allowing Hades to use active conversation context or ask a concise clarification when the missing subject is unknown.
- Improved prompt guidance to answer requested vocal performances directly and continue Aether Gazer gameplay/build discussion without inventing mechanics.
- Preserved hard blocks for unrelated specialist work, sports, other games, politics/news/finance, and unrelated how-to requests.
- Added regression tests for both reported failures.

## 2.7.2 — 2026-10-14: Natural food-choice conversation

- Added detection for concise meal choices such as "steak or pasta?", "pizza or sushi?", and "ramen versus adobo?".
- Routed these messages into Hades's food-chat mode and instructed her to choose one option with a brief, in-character reason.
- Kept recipe/how-to requests and hard unrelated-topic restrictions unchanged.
- Added regression tests for food-choice classification and routing.

## 2.7.1 — 2026-10-14

### Free Tier Lite model restriction
- Restricted the primary/fallback allowlist to Gemini 3.5 Flash-Lite and Gemini 3.1 Flash-Lite, both listed with Free Tier pricing in Google's Gemini API pricing table.
- Replaced the default Gemini 3.6 Flash / Gemini 3.8 Flash fallbacks with Gemini 3.1 Flash-Lite in Render and local environment examples.
- Reject unapproved primary model IDs at startup and filter unapproved fallback IDs.
- Clarified that model selection does not switch a Google project from Paid Tier to Free Tier; the project's API billing tier must remain Free Tier for $0 model usage.

## 2.7.0 — 2026-10-14

### Gemini model failover and request deadlines
- Added a configurable model hierarchy that tries the configured primary first, then Gemini 3.6 Flash and Gemini 3.8 Flash by default.
- Added per-model request deadlines and capped SDK-internal retries so transient 503/504 errors move to the next model sooner.
- Kept failover limited to transient errors, timeouts, rate limits, and unavailable model IDs; invalid API credentials fail fast.
- Preserved the same Hades prompt and context across model fallbacks, including a same-model retry without URL Context when that optional tool is rejected.
- Added logs and diagnostics for the selected model and successful fallback count.
- Clarified that a Discord gateway reconnect is separate from Gemini API availability.

## 2.6.0 — 2026-10-14

### Everyday preference conversation
- Expanded strict-scope social routing for short personal either/or prompts such as "beer or wine?", "tea or coffee?", "cats or dogs?", and similar low-stakes choices.
- Added dedicated conversation guidance so Hades gives a clear in-character preference first instead of refusing or needlessly returning the question.
- Made explicit that preferences not established in Aether Gazer canon are roleplay opinions, not verified lore.
- Preserved hard blocks for unrelated specialist, sports, finance, and other-game questions, with regression tests on both allowed and blocked examples.

## 2.5.0 — 2026-10-11

### Channel-specific mental-distress support
- Added a proactive support trigger for messages containing "mental breakdown" or "mental-breakdown" in Discord channel `1537979704714334238`.
- Routed triggered messages through Hades's emotional conversation mode with explicit guidance to respond calmly, compassionately, and without flirtation or teasing.
- Kept the trigger isolated to the requested channel and added a per-user 30-second repeat guard.
- Added tests for channel isolation, phrase variations, emotional routing, and support guidance.

## 2.4.0 — 2026-10-11

### Contextual emoji expansion
- Expanded Hades's emoji palette with character-signature, puppetry/art, flirtation, comfort, celebration, and food/tea accents.
- Added context-matched emoji selection so short replies use a more relevant flourish instead of a completely random symbol.
- Improved the Gemini persona guidance to treat emojis as optional tone markers, not mandatory message endings.
- Preserved clean factual/serious replies, custom-emoji messages, code blocks, and longer explanations.
- Added regression tests for contextual palette selection and duplicate/code/long-reply handling.

## 2.3.0 — 2026-10-11

### Fan-service and flirtation
- Expanded recognition of short date follow-ups, casual date proposals, new flirtatious phrasing, fandom slang, affectionate requests, and flustered/captivated admissions.
- Improved Hades's response guidance for compliments, bold fan comments, affectionate gestures, romantic invitations, and playful teasing so each cue receives a specific in-character reaction.
- Made direct date invitations require an actual in-character answer or counterproposal instead of a generic off-topic refusal.
- Encouraged occasional measured return-flirting while preserving Hades's composure, boundaries, and non-explicit style.
- Added regression coverage for newly recognized phrases, short date fragments, and allowed social scope.
- Kept responses dynamically generated by Gemini; no canned reply bank was added.

## 2.2.1 — 2026-10-11

### Food-related conversation
- Added a dedicated food-chat mode for hunger, cravings, personal food preferences, favorite dishes, meal reactions, and deciding what to eat.
- Allowed everyday food conversation without weakening the strict Aether Gazer scope.
- Kept recipes, ingredient lists, and cooking instructions outside scope, with wider detection for common cooking-how-to wording.
- Added regression tests for allowed food conversation and blocked recipe/instruction requests.

## 2.2.0 — 2026-10-11

### Conversation and reliability
- Expanded contextual social recognition for check-ins, short personal gestures, and unusual gift offers while retaining strict unrelated-topic boundaries.
- Added category-specific in-character refusal wording for unrelated recipe/how-to requests.
- Fixed automatic GIF/image attachment for `h!hades` and `h!ask` responses; the command path requested auto media but the media gate accepted only mentions.
- Automatic media cooldowns, recent-use history, and metrics are committed after Discord accepts the response.
- Manual `h!gif` and `h!image` commands now honor their configured cooldowns and distinguish cooldown waits from missing media configuration.
- Expired history is dropped when opening an unlocked session so stale context cannot be resurrected.
- Memory/media cleanup and cooldown cleanup now use their separate configured intervals.
- Set the custom Discord status to `h!help @GitHub`.
- Added regression tests for conversation scope, media triggers/cooldowns, and expired memory.

## 2.1.0 — 2026-10-08

### Conversation
- Added a dedicated social-planning mode for together-oriented turns such as "what else can we do?", "let's hang out", and "what do you want to do?"
- Added natural acknowledgement handling so "okay", "sure", and "fair enough" do not become formal rulings by default.
- Added relationship-banter detection for "what are we?", "do I have a chance?", and similar fan-service questions.
- Expanded Hades-adjacent art and craft scope with stagecraft, puppetry, costume/set design, painting, sculpture, illustration, and related terms.
- Added regression coverage for Discord-style shorthand and conversational pivots.

### Runtime hardening
- Protected shared health/metrics state with a thread lock and consistent health snapshots.
- Added small category-specific variation to deterministic scope refusals.
- Kept all normal and fan-service responses dynamically generated by Gemini.

## 2.0.0 — 2026-10-08

### Character and conversation
- Expanded social routing so date invitations, casual hangouts, shared meals, and one-on-one plans are distinguished instead of being treated as one generic flirt cue.
- Added a dedicated rivalry/banter lane for playful insults, battle-of-wits lines, victory boasts, and mock challenges.
- Added regression coverage for casual outing wording such as "wanna go out", "wanna hang out", and "go out and eat something".
- Calibrated Gemini to avoid turning ordinary companionship into automatic romance and to answer rivalry as banter.
- Expanded Hades character calibration and contextual fan-service guidance.
- Improved continuity for short follow-ups, corrections, callbacks, and topic pivots.
- Reduced forced questions, repetitive theatrical phrasing, and automatic flirting escalation.
- Preserved selective use of Administrator and little lamb.

### Scope and safety
- Kept the strict Aether Gazer-focused scope.
- Preserved deterministic blocking for unrelated technical work, sports/F1, other games, politics/news/finance, and unrelated specialist requests.
- Sanitized generated raw Discord mention markup and direct GIF URLs.

### Runtime and deployment
- Added release version 2.0.0.
- Added an explicit Render free plan.
- Added a Render build filter so documentation-only changes do not trigger unnecessary service builds.
- Kept Render deployment behind passing CI checks.
- Removed duplicate Discord disconnect-state updates.
- Improved command-error messaging.

### Gemini
- Kept gemini-3.5-flash-lite as the default model.
- Preserved URL Context fallback behavior for current/source-sensitive questions.
- Preserved bounded concurrency, retries, request timeout, and output limits.

### Media
- GIFs remain external embeds rather than raw URLs in bot messages.
- Automatic media remains limited and cooldown-protected.
- Generated GIF URLs are removed from model text before Discord delivery.

# Changelog

## 1.9.0
- Hardened runtime observability with readiness state and bounded health metrics.
- Made maintenance cleanup resilient so a single failed cleanup pass does not stop the background loop.
- Fixed automatic GIF/image state isolation to use guild/channel/user keys.
- Made media cooldowns configurable through environment and Render settings.
- Fixed deterministic scope blocker labels so refusal wording matches the detected topic category.
- Expanded nested Aether Gazer/Hades knowledge retrieval beyond the top-level alias list.
- Improved current build/meta source selection by prioritizing Mimir Global Teams and official news for time-sensitive requests.
- Added regression coverage for these runtime, scope, media, and knowledge paths.

## 1.8.0
- Expanded fan-service recognition for gentle affection, focused attention, eye contact, voice/name requests, additional fluster cues, and direct "you're my type" admiration.
- Added semantic cue-shape guidance so Gemini can distinguish compliments, affection requests, bold requests, challenges, focused attention, and flustered admissions without selecting canned replies.
- Kept all fan-service wording dynamically generated and context-sensitive.
- Added regression coverage for the new detector paths and cue-shape contract.

## 1.7.0
- Expanded Hades's fan-service reaction repertoire beyond the existing tease/flirt/challenge lanes.
- Added composed indulgence, dry disbelief, mock-formal rulings, elegant approval, playful offense, caught-you observations, amused permission, quiet sincerity, graceful deflection, patient amusement, understated fluster, and theatrical verdicts.
- Improved repeated fan-service handling so variation changes the underlying reaction style instead of only swapping words.
- Added recent-reply continuity guidance so variety stays natural rather than becoming a mechanical rotation.
- Added regression tests for the expanded reaction repertoire.


## 1.6.0
- Improved Hades fan-service reaction quality and character presence.
- Added specific-cue-first reaction guidance so Hades reacts to what was actually said before adding flavor.
- Added more distinct reaction lanes: dry amusement, mock reprimand, elegant approval, measured flirtation, and restrained moments of fluster.
- Reduced generic roleplay filler, stock pickup-line behavior, repetitive openings, and forced end-of-message questions.
- Strengthened composure/authority guidance so Hades feels knowingly confident instead of generically eager.
- Added smoke-test contracts for the improved reaction voice.

## 1.5.0
- Added captivated/mesmerized fan-service cues such as being under Hades' spell, wrapped around her finger, living rent-free in the Administrator's head, and being unable to look away.
- Added theatrical devotion cues including worship, serving, being at Hades' feet, and devoted little-lamb language.
- Added playful-jealousy detection while explicitly preventing possessive or dependency-driven behavior.
- Expanded admiration detection for Hades' voice, presence, distraction, eye contact, and lingering attention.
- Expanded affectionate cues for forehead/cheek/hand kisses, hand-holding, leaning on a shoulder, sitting beside Hades, and similar non-explicit closeness.
- Kept all fan-service dynamically generated; no new canned response bank was introduced.

## 1.4.0
- Expanded Hades-directed social detection for date invitations, shared meals, scent/perfume/whiff requests, close-proximity banter, and lap/thigh comfort requests.
- Added broader Aether Gazer character-name scope recognition so named characters can be discussed without requiring a second lore keyword.
- Expanded contextual follow-up handling for phrases such as "how did you know?" so ongoing dialogue no longer falls into the unrelated-topic gate.
- Added regression coverage for the expanded social/fan-service cases drawn from the bot's real Discord conversation behavior.

## 1.3.0
- Loaded the canonical `hades_reference.json` at runtime to prevent Hades data drift.
- Fixed correction-message scope matching.
- Validated generated replies before committing them to conversation memory.
- Removed duplicated conversation transcript from the Gemini request prompt.
- Added external-source prompt hardening for URL Context.
- Added confidence-aware fan-service classification and reduced broad false positives.
- Prioritized emotional intent over affectionate fan-service cues.
- Balanced automatic GIF/image selection and made media state per-user/per-channel.
- Aligned CI with the declared Python 3.11 runtime.
- Updated `google-genai` to 2.28.0.
- Hardened diagnostics and disconnected-latency handling.
- Added regression coverage for the audit fixes.

## 1.0.0-gold
- Added production build/version reporting.
- Added privacy and staff diagnostics commands.
- Added GitHub Actions smoke CI.
- Removed local `.env` from release packages.
- Documented Render GitHub App access and On Commit deployment.
