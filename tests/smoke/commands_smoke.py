from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BOT = (ROOT / "hades_bot" / "bot.py").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")

REQUIRED = (
    "@bot.command(name=\"about\")",
    "@bot.command(name=\"version\")",
    "@bot.command(name=\"privacy\")",
    "@bot.command(name=\"diagnose\")",
)

for marker in REQUIRED:
    assert marker in BOT, f"Missing command marker: {marker}"

for command in ("h!about", "h!version", "h!privacy", "h!diagnose"):
    assert command in README, f"Missing README command: {command}"

print("command smoke test: ok")

assert 'embed=info_embed(' in BOT

IMAGES = (ROOT / "hades_bot" / "media" / "images.py").read_text(encoding="utf-8")
assert "HADES_IMAGE_URLS" in IMAGES
assert IMAGES.count("https://") >= 2

MEDIA = (ROOT / "hades_bot" / "media" / "media.py").read_text(encoding="utf-8")
assert "def should_auto_send_media" in MEDIA
assert "def choose_auto_media_embed" in MEDIA
assert "async def send_gif" in MEDIA
assert "async def send_image" in MEDIA
