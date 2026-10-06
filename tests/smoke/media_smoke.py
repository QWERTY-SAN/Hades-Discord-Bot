from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
media = (ROOT / "hades_bot" / "media" / "media.py").read_text(encoding="utf-8")
bot = (ROOT / "hades_bot" / "bot.py").read_text(encoding="utf-8")

assert "AUTO_MEDIA_COOLDOWN_SECONDS = 300.0" in media
assert "def should_auto_send_media" in media
assert "async def send_auto_media" not in media
assert "kind, url = self.rng.choice(choices)" in media
assert "should_auto_send_gif(message, trigger)" not in bot
assert "should_auto_send_image(message, trigger)" not in bot
assert bot.count("should_auto_send_media(message, trigger)") == 1
assert "choose_auto_media_embed(message)" in bot
assert "attach_auto_media=(trigger == \"mention\")" in bot

print("Media smoke checks passed")
