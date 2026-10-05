# Deployment

## Render

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
python main.py
```

Health check:

```text
/health
```

Readiness check:

```text
/ready
```

The repository's `render.yaml` is configured for the `main` branch with `autoDeployTrigger: commit`, so Render should automatically deploy a new commit once the service is linked to the repository. Render's current documentation confirms `commit` means deploy on each commit to the linked branch.

### GitHub access

On GitHub, make sure the Render GitHub App is installed and has repository access to:

```text
QWERTY-SAN/Hades-Discord-Bot
```

In Render, verify:

```text
Repository: QWERTY-SAN/Hades-Discord-Bot
Branch: main
Auto-Deploy: On Commit
```

### Secrets

Store `DISCORD_TOKEN` and `GEMINI_API_KEY` as Render environment variables/secrets. Do not commit `.env`. The repository only includes `.env.example`.

### CI

GitHub Actions runs compile checks and smoke tests on pushes and pull requests to `main`. After CI has been stable, Render can optionally be changed from **On Commit** to **After CI Checks Pass**.
