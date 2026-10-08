# Hades Discord Bot 1.8.0

## Fan-service expansion
- Added more gentle, non-explicit affection cues: hair play, cheek touches, head/face gestures, nose boops, collar fixes, and forehead touches.
- Added focused-attention cues around Hades's voice, saying her name, and deliberate eye contact.
- Added more indirect attraction/fluster wording, including "you're exactly my type" and "you got me folding."
- Added semantic cue-shape hints for Gemini. These hints describe the user's social move; they do not select a canned response.
- Kept recent-reply continuity and reaction-lane variety as the primary drivers of response style.



## Expanded social behavior
- Date invitations and shared meal plans are recognized as Hades-directed social interaction.
- Scent/perfume/whiff requests and close-proximity requests are handled as playful, non-explicit fan-service cues rather than unrelated-topic refusals.
- Common continuation questions such as "how did you know?" inherit the active Hades conversation when history exists.
- More Aether Gazer character names are recognized directly by the strict scope gate.
- New smoke coverage mirrors the problematic conversation patterns seen in the Discord export.

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
