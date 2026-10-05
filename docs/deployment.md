# Deployment

Render build command:

```text
pip install -r requirements.txt
```

Start command:

```text
python main.py
```

Health check: `/health`
Readiness check: `/ready`

Store `DISCORD_TOKEN` and `GEMINI_API_KEY` as Render environment secrets. Keep GIF URLs in `hades_bot/media/gifs.py`, not `.env`.
