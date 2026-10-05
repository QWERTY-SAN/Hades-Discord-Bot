# Deployment

Render build command:

```text
pip install -r requirements.txt
```

Start command:

```text
python main.py
```

Liveness check: `/health` (used by Render; confirms the web process serves HTTP).
Readiness check: `/ready` (HTTP 200 only when Discord is connected, otherwise HTTP 503). Monitor `/ready` separately when debugging Discord connectivity; do not use it as the Render liveness check.

Store `DISCORD_TOKEN` and `GEMINI_API_KEY` as Render environment secrets. Keep GIF URLs in `hades_bot/media/gifs.py`, not `.env`. For local development, copy `.env.example` to `.env`. Never commit the local `.env` file; if it is already tracked, run `git rm --cached .env` and commit the removal. Rotate credentials if real values were ever committed.
