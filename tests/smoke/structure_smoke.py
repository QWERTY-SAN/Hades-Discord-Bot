from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EXPECTED = [
    ROOT / "hades_bot" / "bot.py",
    ROOT / "hades_bot" / "core" / "scope.py",
    ROOT / "hades_bot" / "ai" / "gemini_client.py",
    ROOT / "hades_bot" / "ai" / "providers" / "gemini.py",
    ROOT / "hades_bot" / "ai" / "providers" / "groq.py",
    ROOT / "hades_bot" / "ai" / "providers" / "router.py",
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

TESTS = ROOT / "tests"
assert (ROOT / "docs" / "README.md").exists(), "documentation index is missing"
assert (TESTS / "smoke").is_dir(), "executable smoke checks directory is missing"
assert (TESTS / "unit").is_dir(), "pytest suite directory is missing"
assert list((TESTS / "unit").glob("test_*.py")), "pytest tests are missing"
misplaced_pytest = list((TESTS / "smoke").glob("test_*.py"))
assert not misplaced_pytest, f"pytest tests should live under tests/unit: {misplaced_pytest}"

