# Hades Discord AI Bot

A modular Discord AI chatbot that roleplays as Hades from Aether Gazer using Gemini.

## What changed

This build adds a small gameplay-reference layer to reduce hallucinations and, in particular, stop Hades from blending different Aether Gazer modes together.

The bot now:

- Injects only the relevant gameplay reference when a known mode is mentioned.
- Keeps Recurring Dream, Hazard Zone, Dimensional Variable, Causality Survey, Past Grudges, Iterative Testing, Hypothetical Deduction, Battle Sweep/Raid, and Flaneuring distinct.
- Avoids inventing exact reset schedules, reward amounts, boss lineups, stage counts, and patch-specific mechanics when they are not known.
- Uses lower Gemini sampling by default for more consistent factual answers.
- Actually applies `GEMINI_THINKING_LEVEL` from the environment.
- Fixes the topic filter so normal Aether Gazer questions such as `how do I clear Recurring Dream?` are allowed.

## Commands

`h!hades <message>`

`h!ask <message>`

`h!reset`, `h!forget`, `h!clear`

`h!memory`

`h!ping`

`h!status` (server administrators)

`h!hadeshelp`, `h!help`

You can also mention Hades, reply directly to one of her messages, or DM the bot.

## Local setup

1. Install Python 3.12.
2. Create a virtual environment.
3. Install requirements with `pip install -r requirements.txt`.
4. Put your real `DISCORD_TOKEN` and `GEMINI_API_KEY` in `.env`.
5. Enable Discord Message Content Intent for the bot.
6. Run `python main.py`.

Never commit real credentials.

## Render

Build command:

`pip install -r requirements.txt`

Start command:

`python main.py`

Health check:

`/health`

The included `render.yaml` is configured for automatic deploys on commits to `main`.
