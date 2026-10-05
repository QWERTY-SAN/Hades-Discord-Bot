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
assert 'https://i.imgur.com/uNBcXQg.jpeg' in IMAGES
assert 'https://i.imgur.com/gQN3GNb.jpeg' in IMAGES
assert IMAGES.count('"https://i.imgur.com/') >= 2

MEDIA = (ROOT / "hades_bot" / "media" / "media.py").read_text(encoding="utf-8")
assert 'async def send_auto_gif(' in MEDIA
assert 'async def send_auto_image(' in MEDIA
assert 'should_auto_send_gif' in MEDIA
assert 'should_auto_send_image' in MEDIA
