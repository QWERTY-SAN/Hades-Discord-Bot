from __future__ import annotations

import asyncio
import logging
import threading
import time
from typing import Any

from aiohttp import web

from .version import APP_NAME, APP_VERSION, branch, runtime, short_commit

logger = logging.getLogger("hades-bot.web")

_started_at = time.monotonic()
_state_lock = threading.Lock()
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



def record_runtime_metric(name: str, amount: int = 1) -> None:
    with _state_lock:
        if name not in _state:
            return
        try:
            _state[name] = max(0, int(_state[name]) + amount)
        except (TypeError, ValueError):
            logger.warning("Unable to update runtime metric %s", name)


def set_runtime_error(error: str | None) -> None:
    with _state_lock:
        _state["last_error"] = error


def update_discord_state(**values: Any) -> None:
    with _state_lock:
        _state.update(values)
        if values.get("ready") is True:
            _state["last_error"] = None


def update_web_error(error: str) -> None:
    _state["last_error"] = error
    logger.error("Web/runtime state error: %s", error)


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
        **state,
    }


async def _index(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", **_base_payload()})


async def _health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", **_base_payload()})


async def _ready(request: web.Request) -> web.Response:
    ready = bool(_state.get("ready"))
    return web.json_response(
        {"status": "ready" if ready else "starting", **_base_payload()},
        status=200 if ready else 503,
    )


async def _run_app(host: str, port: int) -> None:
    app = web.Application()
    app.router.add_get("/", _index)
    app.router.add_get("/health", _health)
    app.router.add_get("/ready", _ready)

    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    try:
        site = web.TCPSite(runner, host, port)
        await site.start()
        logger.info("Health server listening on %s:%s", host, port)
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
            logger.exception("Health server stopped unexpectedly")

    thread = threading.Thread(target=runner, name="hades-web", daemon=True)
    thread.start()
    return thread
