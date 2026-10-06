from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

assert not (ROOT / ".env").exists(), "real .env must never be shipped"
assert (ROOT / ".github" / "workflows" / "ci.yml").exists()

bot = (ROOT / "hades_bot" / "bot.py").read_text(encoding="utf-8")
assert '@bot.command(name="about"' in bot
assert '@bot.command(name="privacy")' in bot
assert '@bot.command(name="diagnose"' in bot
assert "RENDER_GIT_COMMIT" in (ROOT / "hades_bot" / "version.py").read_text(encoding="utf-8")

render = (ROOT / "render.yaml").read_text(encoding="utf-8")
assert "autoDeployTrigger: checksPass" in render
assert "branch: main" in render
assert "healthCheckPath: /health" in render

print("gold release checks passed")
