# Changelog

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
