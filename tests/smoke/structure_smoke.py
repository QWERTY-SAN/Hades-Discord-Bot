from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EXPECTED = [
    ROOT / "hades_bot" / "bot.py",
    ROOT / "hades_bot" / "core" / "scope.py",
    ROOT / "hades_bot" / "ai" / "gemini_client.py",
    ROOT / "hades_bot" / "knowledge" / "lore.py",
    ROOT / "hades_bot" / "media" / "gifs.py",
    ROOT / "data" / "aether_gazer" / "game_knowledge.json",
    ROOT / "data" / "aether_gazer" / "characters" / "hades_reference.json",
]

missing = [str(p.relative_to(ROOT)) for p in EXPECTED if not p.exists()]
assert not missing, missing

text = (ROOT / "hades_bot" / "media" / "media.py").read_text(encoding="utf-8")
assert "content=entry.url" not in text
assert "embed.set_image(url=url)" in text

print("Structure smoke checks passed")
