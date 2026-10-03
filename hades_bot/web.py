from aiohttp import web

from .config import SETTINGS

_state = {"discord_ready": False, "discord_user": None, "guild_count": 0}


def update_discord_state(*, ready: bool, user: str | None = None, guild_count: int = 0) -> None:
    _state.update({"discord_ready": ready, "discord_user": user, "guild_count": guild_count})


async def index(request: web.Request) -> web.Response:
    return web.json_response({"service": "Hades Discord AI Bot", "status": "online" if _state["discord_ready"] else "starting", **_state})


async def health(request: web.Request) -> web.Response:
    return web.json_response({"service": "hades-discord-bot", "status": "ok", **_state})


async def ready(request: web.Request) -> web.Response:
    ready_state = _state["discord_ready"]
    return web.json_response({"service": "hades-discord-bot", "status": "ready" if ready_state else "not-ready", **_state}, status=200 if ready_state else 503)


async def start_health_server() -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/health", health)
    app.router.add_get("/ready", ready)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", SETTINGS.port)
    await site.start()
    return runner


def start_web_server() -> None:
    import asyncio
    import threading

    def runner() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_health_server())
        loop.run_forever()

    threading.Thread(target=runner, daemon=True).start()
