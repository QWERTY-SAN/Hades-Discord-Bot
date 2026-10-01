# Hades Discord Bot — Balanced Scope Update

This update is based on the current `main` branch of `QWERTY-SAN/Hades-Discord-Bot`.

## Changed files

Replace:

- `hades_bot/scope.py`
- `hades_bot/persona.py`

## Scope behavior

The gate is now balanced:

- Aether Gazer discussion is allowed.
- Casual conversation is allowed even when it is unrelated to Aether Gazer.
- Casual mentions of PCs, school, other games, etc. do not automatically trigger a refusal.
- Clearly unrelated informational or task requests are redirected before Gemini.
- Generic phrases such as `what is`, `how do I`, and `explain` are not treated as off-topic by themselves.
- Aether Gazer keywords do not automatically allow an unrelated programming/technical request.
- Mythological Hades references are separated from the Aether Gazer character.

`bot.py` already calls the scope function before Gemini and uses the same check for
`h!hades`, so no routing rewrite is required for this balanced change.
