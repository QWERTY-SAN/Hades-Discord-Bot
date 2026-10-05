# Changelog

## Gold preparation build (unreleased)

- Rate-limit AI-generated scope refusals as well as ordinary Gemini responses.
- Apply the input length limit before any model-backed response path.
- Restrict detailed `h!status` output to the bot owner or authorized guild staff, including in DMs.
- Remove the unused `STRICT_AETHER_TOPIC` toggle because topic enforcement is intentionally always on.
- Remove `.env` from the distributable and document how to untrack a previously committed local environment file.
- Add GitHub Actions tests for pushes and pull requests, including cooldown-path and status-privacy checks.
- Fix the fan-service matcher for natural requests such as “give me a hug” and “give me a cuddle.”
- Document liveness versus Discord readiness checks and add an explicit release checklist.
