# Changelog

## Unreleased — Hades web dashboard

- Added a Hades-themed responsive dashboard at the service root with connection status, uptime, guild count, runtime metrics, and process metadata.
- Added a diagnostics view with health/readiness links and recent runtime error state, plus a command reference with copy-to-clipboard interactions.
- Added `/api/status` for the dashboard while preserving `/health` and `/ready` JSON endpoints for operations and Render.
- Kept the dashboard read-only and self-hosted its frontend assets; no new runtime dependency or API-key exposure was added.
- Added startup smoke checks for dashboard assets and route contracts.

## Unreleased — Separate AI provider modules

- Split Gemini SDK calls, Groq SDK calls, and fallback routing into separate modules under `hades_bot/ai/providers/`.
- Kept the fallback sequence as Gemini 3.5 Flash-Lite → Gemini 3.1 Flash-Lite → Groq.
- Treat empty Gemini responses as failures and continue to the next provider rather than returning an empty reply.
- Keep Gemini URL Context-only instructions out of the Groq prompt when the Google tool cannot be used.
- Close both AI SDK clients during shutdown and expose per-provider fallback counters in `h!diagnose` and `h!status`.
- Add regression tests for fallback order, Gemini recovery, credential rejection, and total provider failure.


## 2.7.3 — 2026-10-14

### In-character vocal requests and contextual game follow-ups
- Recognized direct requests to say playful phrases such as "ara-ara" and routed them through Hades's voice/fan-service guidance instead of the generic scope refusal.
- Added a narrow continuation detector for unfinished clauses such as "Can be pierced though for tanky gears", allowing Hades to use active conversation context or ask a concise clarification when the missing subject is unknown.
- Improved prompt guidance to answer requested vocal performances directly and continue Aether Gazer gameplay/build discussion without inventing mechanics.
- Preserved hard blocks for unrelated specialist work, sports, other games, politics/news/finance, and unrelated how-to requests.
- Added regression tests for both reported failures.

## 2.7.2 — 2026-10-14

### Natural food-choice conversation
- Added explicit detection for short food either/or questions, including "steak or pasta?", "pizza or sushi?", and "ramen versus adobo?".
- Routed meal choices through Hades's food-chat mode instead of leaving them in the generic personal-question lane.
- Strengthened prompt guidance to choose one option with a brief in-character reason rather than returning an unrelated-topic refusal or bouncing the decision back.
- Kept recipes, ingredient lists, cooking instructions, and existing hard off-topic boundaries blocked.
- Added regression tests for food-choice classification, conversation mode, and scope behavior.

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
