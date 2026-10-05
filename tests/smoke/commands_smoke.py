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
