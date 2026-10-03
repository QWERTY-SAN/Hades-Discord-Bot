from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY_FILES = sorted((ROOT / "hades_bot").glob("*.py")) + [ROOT / "main.py"]

for path in PY_FILES:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

config_source = (ROOT / "hades_bot/config.py").read_text(encoding="utf-8")
gemini_source = (ROOT / "hades_bot/gemini_client.py").read_text(encoding="utf-8")
render_source = (ROOT / "render.yaml").read_text(encoding="utf-8")
media_source = (ROOT / "hades_bot/media.py").read_text(encoding="utf-8")
gifs_source = (ROOT / "hades_bot/gifs.py").read_text(encoding="utf-8")
env_source = (ROOT / ".env.example").read_text(encoding="utf-8")
scope_source = (ROOT / "hades_bot/scope.py").read_text(encoding="utf-8")

assert "emojis_enabled: bool" in config_source
assert 'emojis_enabled=_bool("EMOJIS_ENABLED", True)' in config_source
assert "SETTINGS.emojis_enabled" in gemini_source
assert "EMOJIS_ENABLED" in render_source
assert "HADES_GIF_URLS" in gifs_source
assert "discord.File" not in media_source
assert "_get_session" not in media_source
assert "discord.File" not in media_source
assert "HADES_GIF_URLS" not in env_source
assert "smug" not in gifs_source.lower()
assert "happy" not in gifs_source.lower()
assert "neutral" not in gifs_source.lower()
assert "annoyed" not in gifs_source.lower()
assert "is_specialist_request" in scope_source

print(f"Static smoke check passed for {len(PY_FILES)} Python files.")
