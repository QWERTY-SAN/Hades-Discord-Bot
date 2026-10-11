# Hades Discord Bot 2.2.0

## Conversation quality
- Expanded contextual recognition for check-ins, personal gestures, and unusual gift offers.
- Keeps unrelated recipe requests outside the strict Aether Gazer scope, with more context-specific Hades refusals.
- Preserves dynamic Gemini replies and the contextual fan-service layer.

## Media behavior
- Automatic media can accompany a Hades mention or an `h!hades` / `h!ask` response.
- Exactly one image or GIF can be attached to an automatic response; plain replies stay media-free.
- Auto-media cooldown/history/metrics are committed only after a successful send.
- Manual `h!gif` and `h!image` commands honor their own cooldowns and explain waits.

## Reliability
- Expired conversation history is cleared when a fresh unlocked session opens.
- Memory/media cleanup and user cooldown cleanup respect separate configured intervals.
- Custom Discord status: `h!help @GitHub`.
- Python compilation and the CI smoke/pytest suite passed for the tested changes.
