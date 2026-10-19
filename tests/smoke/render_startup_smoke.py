import inspect
import os
from pathlib import Path

os.environ.setdefault("DISCORD_TOKEN", "ci-test-token")
os.environ.setdefault("GEMINI_API_KEY", "ci-test-key")
os.environ.setdefault("GROQ_API_KEY", "ci-test-groq-key")

import main  # noqa: E402
from hades_bot.config import SETTINGS, validate_settings  # noqa: E402
from hades_bot.web import start_web_server  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
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
assert "key: GROQ_API_KEY" in render
assert SETTINGS.groq_api_key
validate_settings()
assert "autoDeployTrigger: checksPass" in render

# The web root serves the dashboard while operational probes stay JSON endpoints.
web_source = (ROOT / "hades_bot" / "web.py").read_text(encoding="utf-8")
dashboard = (ROOT / "hades_bot" / "static" / "index.html").read_text(encoding="utf-8")
dashboard_css = (ROOT / "hades_bot" / "static" / "dashboard.css").read_text(encoding="utf-8")
dashboard_js = (ROOT / "hades_bot" / "static" / "dashboard.js").read_text(encoding="utf-8")
assert 'app.router.add_get("/", _index)' in web_source
assert 'app.router.add_get("/api/status", _api_status)' in web_source
assert 'app.router.add_static(' in web_source and '"/static/"' in web_source
assert 'Content-Security-Policy' in web_source
assert "Command Center" in dashboard
assert 'data-panel="overview"' in dashboard
assert 'data-panel="diagnostics"' in dashboard
assert 'data-panel="commands"' in dashboard
assert "/api/status" in dashboard_js
assert "h!hades" in dashboard
assert "h!diagnose" in dashboard
assert "@import url(" not in dashboard_css  # Keep assets self-hosted and CSP-compatible.

print("Render startup and dashboard smoke checks passed")
