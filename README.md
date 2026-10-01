# Hades Discord Bot — Improvement Bundle

These files are intended to be copied over the matching files in the current repository.

## Changes

- Added an application-level Aether Gazer scope gate in `hades_bot/scope.py`.
- Unrelated substantive questions no longer reach Gemini.
- Programming/code requests are blocked before Gemini, including mixed requests such as an Aether Gazer bot written in Python.
- Casual social conversation is still allowed.
- Removed the old persona instruction that explicitly told Hades to answer technical, school, and real-world questions.
- Strengthened Hades characterization, canon discipline, anti-generic-assistant behavior, and natural conversation rules.
- Cooldowns are now per conversation instead of global per user.
- Input validation and scope checks happen before consuming the AI cooldown.
- `h!memory` only shows the current conversation instead of exposing the bot's global active conversation count to everyone.
- `h!status` is restricted to server administrators.
- Model output is sanitized for raw Discord mentions.
- Retry backoff now has jitter to reduce synchronized retry bursts.
- Empty mentions use varied Hades responses.

No secrets or environment values are included.
