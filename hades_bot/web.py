from __future__ import annotations

import asyncio
import json
import logging
import re
import threading
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aiohttp import web

from .config import SETTINGS
from .version import APP_NAME, APP_VERSION, branch, runtime, short_commit

logger = logging.getLogger("hades-bot.web")
STATIC_DIR = Path(__file__).resolve().parent / "static"
LOG_BUFFER_SIZE = 300
LOG_MESSAGE_LIMIT = 360

DASHBOARD_HEADERS = {
    "Content-Security-Policy": "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'self'; frame-ancestors 'none'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
}
JSON_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}

_started_at = time.monotonic()
_state_lock = threading.Lock()
_log_lock = threading.Lock()
_log_sequence = 0
_log_entries: deque[dict[str, Any]] = deque(maxlen=LOG_BUFFER_SIZE)
_state: dict[str, Any] = {
    "ready": False,
    "user": None,
    "guild_count": 0,
    "last_error": None,
    "messages_seen": 0,
    "ai_requests": 0,
    "ai_successes": 0,
    "ai_failures": 0,
    "scope_blocks": 0,
    "media_sent": 0,
}


def _redact(value: str) -> str:
    """Remove likely credentials from operational data before it leaves the process."""
    result = str(value)
    for secret in (SETTINGS.discord_token, SETTINGS.gemini_api_key, SETTINGS.groq_api_key):
        if secret and len(secret) >= 8:
            result = result.replace(secret, "[REDACTED]")
    result = re.sub(r"(?i)(bearer\s+)[a-z0-9._~+/-]+=*", r"\1[REDACTED]", result)
    result = re.sub(r"(?i)(api[_ -]?key\s*[=:]\s*)[^\s,;]+", r"\1[REDACTED]", result)
    result = re.sub(r"\b(?:gsk_[A-Za-z0-9]{12,}|AIza[0-9A-Za-z_-]{20,})\b", "[REDACTED]", result)
    result = re.sub(r"\b[A-Za-z\d_-]{20,}\.[A-Za-z\d_-]{5,}\.[A-Za-z\d_-]{20,}\b", "[REDACTED]", result)
    result = " ".join(result.replace("\x00", "").split())
    return result[:LOG_MESSAGE_LIMIT]


def record_dashboard_log(level: str, message: str, source: str = "runtime") -> None:
    """Append a deliberately small, secret-redacted operational event to the in-memory log."""
    global _log_sequence
    safe_level = str(level).upper()
    if safe_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        safe_level = "INFO"
    safe_source = re.sub(r"[^a-zA-Z0-9_.-]", "", str(source))[:48] or "runtime"
    safe_message = _redact(message)
    with _log_lock:
        _log_sequence += 1
        _log_entries.append({
            "id": _log_sequence,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": safe_level,
            "source": safe_source,
            "message": safe_message,
        })


def get_dashboard_logs(*, since_id: int = 0, limit: int = 100) -> list[dict[str, Any]]:
    bounded_limit = min(LOG_BUFFER_SIZE, max(1, int(limit)))
    cursor = max(0, int(since_id))
    with _log_lock:
        items = [dict(entry) for entry in _log_entries if int(entry["id"]) > cursor]
    return items[-bounded_limit:]


def _latest_log_id() -> int:
    with _log_lock:
        return int(_log_entries[-1]["id"]) if _log_entries else _log_sequence


class _RouterDashboardLogHandler(logging.Handler):
    """Capture provider-routing messages only; do not stream arbitrary application logs."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            record_dashboard_log(
                record.levelname,
                record.getMessage(),
                source="ai.router",
            )
        except Exception:
            self.handleError(record)


_router_logger = logging.getLogger("hades-bot.ai.router")
if not any(isinstance(handler, _RouterDashboardLogHandler) for handler in _router_logger.handlers):
    _router_logger.addHandler(_RouterDashboardLogHandler(level=logging.INFO))


def record_runtime_metric(name: str, amount: int = 1) -> None:
    with _state_lock:
        if name not in _state:
            return
        try:
            _state[name] = max(0, int(_state[name]) + amount)
        except (TypeError, ValueError):
            logger.warning("Unable to update runtime metric %s", name)


def set_runtime_error(error: str | None) -> None:
    message = _redact(error) if error else None
    changed = False
    with _state_lock:
        if _state["last_error"] != message:
            _state["last_error"] = message
            changed = True
    if message and changed:
        record_dashboard_log("ERROR", message, source="runtime")


def update_discord_state(**values: Any) -> None:
    changed = False
    with _state_lock:
        before = dict(_state)
        _state.update(values)
        if values.get("ready") is True:
            _state["last_error"] = None
        changed = before != _state
        if changed:
    if changed and "ready" in values:
        if values["ready"]:
            record_dashboard_log("INFO", "Discord gateway connected", source="discord")
        else:
            record_dashboard_log("WARNING", "Discord gateway disconnected", source="discord")


def update_web_error(error: str) -> None:
    # Keep raw exception text in the host logs only; never expose it in the dashboard.
    set_runtime_error("Web server failed; inspect host logs for details")
    record_dashboard_log("ERROR", "Web server failed; inspect host logs for details", source="web")
    logger.error("Web/runtime state error: %s", _redact(error))


def _base_payload() -> dict[str, Any]:
    with _state_lock:
        state = dict(_state)
    return {
        "service": "hades-discord-bot",
        "name": APP_NAME,
        "version": APP_VERSION,
        "runtime": runtime(),
        "commit": short_commit(),
        "branch": branch(),
        "uptime_seconds": max(0, round(time.monotonic() - _started_at)),
        "gemini_model": SETTINGS.gemini_model,
        "gemini_fallback_models": list(SETTINGS.gemini_fallback_models),
        "groq_model": SETTINGS.groq_model,
        **state,
    }


async def _index(request: web.Request) -> web.Response:
    return web.FileResponse(
        STATIC_DIR / "index.html",
        headers={**DASHBOARD_HEADERS, "Cache-Control": "no-store"},
    )


async def _health(request: web.Request) -> web.Response:
    return web.json_response(
        {"status": "ok", **_base_payload()},
        headers=JSON_HEADERS,
    )


async def _api_status(request: web.Request) -> web.Response:
    return web.json_response(
        {"status": "ok", **_base_payload()},
        headers=JSON_HEADERS,
    )


async def _api_logs(request: web.Request) -> web.Response:
    try:
        since_id = max(0, int(request.query.get("since", "0")))
        limit = min(LOG_BUFFER_SIZE, max(1, int(request.query.get("limit", "100"))))
    except (TypeError, ValueError):
        return web.json_response(
            {"status": "error", "message": "since and limit must be integers"},
            status=400,
            headers=JSON_HEADERS,
        )
    return web.json_response(
        {"status": "ok", "logs": get_dashboard_logs(since_id=since_id, limit=limit), "cursor": _latest_log_id()},
        headers=JSON_HEADERS,
    )


async def _api_events(request: web.Request) -> web.StreamResponse:
    """Server-sent events: stream runtime snapshots and operational logs to open dashboards."""
    response = web.StreamResponse(
        status=200,
        headers={
            **DASHBOARD_HEADERS,
            "Content-Type": "text/event-stream; charset=utf-8",
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
    await response.prepare(request)

    raw_cursor = request.headers.get("Last-Event-ID", "0")
    try:
        cursor = max(0, int(raw_cursor or "0"))
    except ValueError:
        cursor = 0

    try:
        if cursor == 0:
            backlog = get_dashboard_logs(limit=100)
            cursor = int(backlog[-1]["id"]) if backlog else _latest_log_id()
            initial = {"status": _base_payload(), "logs": backlog, "cursor": cursor}
            await response.write(
                f"id: {cursor}\nevent: bootstrap\ndata: {json.dumps(initial, separators=(',', ':'))}\n\n".encode("utf-8")
            )
        else:
            await response.write(
                f"event: snapshot\ndata: {json.dumps(_base_payload(), separators=(',', ':'))}\n\n".encode("utf-8")
            )

        last_keepalive = time.monotonic()
        while True:
            await asyncio.sleep(1)
            payload = _base_payload()
            await response.write(
                f"event: snapshot\ndata: {json.dumps(payload, separators=(',', ':'))}\n\n".encode("utf-8")
            )
            entries = get_dashboard_logs(since_id=cursor, limit=LOG_BUFFER_SIZE)
            for entry in entries:
                cursor = max(cursor, int(entry["id"]))
                await response.write(
                    f"id: {cursor}\nevent: log\ndata: {json.dumps(entry, separators=(',', ':'))}\n\n".encode("utf-8")
                )
            if time.monotonic() - last_keepalive >= 15:
                await response.write(b": keepalive\n\n")
                last_keepalive = time.monotonic()
    except (ConnectionResetError, BrokenPipeError):
        return response
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.debug("Dashboard event stream closed", exc_info=True)
    return response


async def _ready(request: web.Request) -> web.Response:
    payload = _base_payload()
    ready = bool(payload.get("ready"))
    return web.json_response(
        {"status": "ready" if ready else "starting", **payload},
        status=200 if ready else 503,
        headers=JSON_HEADERS,
    )


async def _run_app(host: str, port: int) -> None:
    app = web.Application()
    app.router.add_get("/", _index)
    app.router.add_get("/health", _health)
    app.router.add_get("/ready", _ready)
    app.router.add_get("/api/status", _api_status)
    app.router.add_get("/api/logs", _api_logs)
    app.router.add_get("/api/events", _api_events)
    app.router.add_static(
        "/static/",
        path=STATIC_DIR,
        show_index=False,
        append_version=True,
    )

    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    try:
        site = web.TCPSite(runner, host, port)
        await site.start()
        record_dashboard_log("INFO", "Web dashboard started", source="web")
        logger.info("Dashboard and health server listening on %s:%s", host, port)
        while True:
            await asyncio.sleep(3600)
    finally:
        await runner.cleanup()


def start_web_server(host: str, port: int) -> threading.Thread:
    def runner() -> None:
        try:
            asyncio.run(_run_app(host, port))
        except Exception as exc:
            update_web_error(str(exc))
            logger.exception("Dashboard/health server stopped unexpectedly")

    thread = threading.Thread(target=runner, name="hades-web", daemon=True)
    thread.start()
    return thread
