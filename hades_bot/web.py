from __future__ import annotations

import asyncio
import threading
from typing import Any

from aiohttp import web

_state: dict[str, Any] = {
    "ready": False,
    "user": None,
    "guild_count": 0,
}


def update_discord_state(**values: Any) -> None:
    _state.update(values)


async def _index(request: web.Request) -> web.Response:
    return web.json_response({"service": "hades-discord-bot", "status": "ok", **_state})


async def _health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", **_state})


async def _ready(request: web.Request) -> web.Response:
    status = 200 if _state.get("ready") else 503
    return web.json_response({"ready": bool(_state.get("ready"))}, status=status)


async def _run_app(host: str, port: int) -> None:
    app = web.Application()
    app.router.add_get("/", _index)
    app.router.add_get("/health", _health)
    app.router.add_get("/ready", _ready)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    while True:
        await asyncio.sleep(3600)


def start_web_server(host: str, port: int) -> threading.Thread:
    def runner() -> None:
        asyncio.run(_run_app(host, port))

    thread = threading.Thread(target=runner, name="hades-web", daemon=True)
    thread.start()
    return thread
