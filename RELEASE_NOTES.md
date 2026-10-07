# Hades Discord Bot 1.3.0

## Reliability
- Generated replies are scope-checked before they enter memory.
- Conversation prompt history is no longer duplicated.
- Correction detection handles common forms such as "not exactly", "that's not what I meant", and "I meant...".
- Diagnostics remain safe while Discord is reconnecting.

## Hades behavior
- Fan-service detection now exposes confidence and separates strong cues from soft attention/fandom cues.
- Emotional messages take priority over affectionate fan-service cues.
- Broad phrases that can be ordinary conversation no longer force flirty mode.
- Hades remains dynamic: Gemini generates the reply rather than selecting canned responses.

## Knowledge
- `hades_reference.json` is now the canonical runtime Hades reference.
- Stable character facts remain separate from dated gameplay/meta snapshots.
- URL Context material is explicitly treated as untrusted reference data.

## Media
- Automatic GIF/image selection now chooses the media type evenly when both are configured.
- Automatic media cooldown/history is keyed per user and channel.

## Runtime
- CI follows `.python-version` (Python 3.11).
- Updated `google-genai` to 2.28.0.
- Gemini model remains `gemini-3.5-flash-lite`.
