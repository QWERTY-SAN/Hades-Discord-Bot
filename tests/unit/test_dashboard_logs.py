from types import SimpleNamespace

from hades_bot import web


def test_dashboard_logs_redact_credentials_and_normalize_messages(monkeypatch):
    monkeypatch.setattr(
        web,
        "SETTINGS",
        SimpleNamespace(
            discord_token="discord-secret-sample-value",
            gemini_api_key="gemini-secret-sample-value",
            groq_api_key="groq-secret-sample-value",
        ),
    )
    before = web._latest_log_id()

    web.record_dashboard_log(
        "warning",
        "Trying fallback with discord-secret-sample-value gemini-secret-sample-value "
        "groq-secret-sample-value api_key=extra-secret-value\nnext line",
        source="ai.router",
    )

    entries = web.get_dashboard_logs(since_id=before, limit=5)
    assert len(entries) == 1
    entry = entries[0]
    assert entry["level"] == "WARNING"
    assert entry["source"] == "ai.router"
    assert "[REDACTED]" in entry["message"]
    assert "discord-secret-sample-value" not in entry["message"]
    assert "gemini-secret-sample-value" not in entry["message"]
    assert "groq-secret-sample-value" not in entry["message"]
    assert "extra-secret-value" not in entry["message"]
    assert "\\n" not in entry["message"]
    assert len(entry["message"]) <= web.LOG_MESSAGE_LIMIT


def test_dashboard_log_api_buffer_is_bounded():
    before = web._latest_log_id()
    for index in range(web.LOG_BUFFER_SIZE + 5):
        web.record_dashboard_log("INFO", f"test event {index}", source="unit-test")

    entries = web.get_dashboard_logs(since_id=before, limit=web.LOG_BUFFER_SIZE)
    assert len(entries) <= web.LOG_BUFFER_SIZE
    assert entries[-1]["message"] == f"test event {web.LOG_BUFFER_SIZE + 4}"
