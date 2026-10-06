from __future__ import annotations

import asyncio
import logging
import threading
import time
from typing import Any

from aiohttp import web

from .version import APP_NAME, APP_VERSION, branch, runtime, short_commit

logger = logging.getLogger("hades-bot.web")

_started_at = time.time()
_state: dict[str, Any] = {
    "ready": False,
    "user": None,
    "guild_count": 0,
    "last_error": None,
}


def update_discord_state(**values: Any) -> None:
    _state.update(values)
    if values.get("ready") is True:
        _state["last_error"] = None


def update_web_error(error: str) -> None:
    _state["last_error"] = error
    logger.error("Web/runtime state error: %s", error)


def _base_payload() -> dict[str, Any]:
    return {
        "service": "hades-discord-bot",
        "name": APP_NAME,
        "version": APP_VERSION,
        "runtime": runtime(),
        "commit": short_commit(),
        "branch": branch(),
        "uptime_seconds": max(0, round(time.time() - _started_at)),
        **_state,
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
