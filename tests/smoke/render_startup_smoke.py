import inspect
import os
from pathlib import Path

os.environ.setdefault("DISCORD_TOKEN", "ci-test-token")
os.environ.setdefault("GEMINI_API_KEY", "ci-test-key")

import main  # noqa: E402
from hades_bot.config import SETTINGS, validate_settings  # noqa: E402
from hades_bot.web import start_web_server  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
render = (ROOT / "render.yaml").read_text(encoding="utf-8")

assert callable(main.run)
assert main.run is not None
assert callable(validate_settings)
assert SETTINGS.web_host == "0.0.0.0"
assert SETTINGS.web_port == 10000
assert list(inspect.signature(start_web_server).parameters) == ["host", "port"]
assert "buildCommand: pip install -r requirements.txt" in render
assert "startCommand: python main.py" in render
assert "healthCheckPath: /health" in render
assert "autoDeployTrigger: commit" in render

print("Render startup smoke checks passed")
