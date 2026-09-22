# Hades Discord AI Bot

A modular Discord AI chatbot that roleplays as **Hades from Aether Gazer** using the Gemini API.

The bot is designed to run on **Render Web Service** and supports Discord mentions, DMs, prefix commands, conversation memory, automatic retries, and basic request protection.

## Features

- Python + `discord.py`
- Gemini API via `google-genai`
- Gemini 3.5 Flash-Lite
- `h!` command prefix
- Hades roleplay personality based on *Aether Gazer*
- Automatic replies when Hades is mentioned
- Direct-message support
- Reply-to-Hades support
- Per-user, per-channel conversation memory
- Automatic cleanup of inactive conversations
- Bounded memory usage
- Per-user cooldown
- Global Gemini request limit
- Gemini request timeout and retry handling
- Discord 2,000-character response splitting
- Protection against accidental Discord mentions such as `@everyone` and `@here`
- `/health` HTTP endpoint for Render
- `h!reset`
- `h!forget`
- `h!memory`
- `h!status`
- `h!ping`
- `h!hadeshelp`
- Environment-variable based secret management
- Automatic Render deployment from GitHub

## Commands

```text
h!hades <message>