from aiohttp import web

from .config import SETTINGS

_state = {
    "discord_ready": False,
    "discord_user": None,
    "guild_count": 0,
}


def update_discord_state(
    *, ready: bool, user: str | None = None, guild_count: int = 0
) -> None:
    _state["discord_ready"] = ready
    _state["discord_user"] = user
    _state["guild_count"] = guild_count


def _snapshot() -> dict:
    return dict(_state)


async def index(request: web.Request) -> web.Response:
    state = _snapshot()
    return web.json_response(
        {
            "service": "Hades Discord AI Bot",
            "status": "online" if state["discord_ready"] else "starting",
            **state,
        }
    )


async def health(request: web.Request) -> web.Response:
    state = _snapshot()
    return web.json_response(
        {
            "service": "hades-discord-bot",
            "status": "ok",
            **state,
        },
        status=200,
    )


async def ready(request: web.Request) -> web.Response:
    state = _snapshot()
    code = 200 if state["discord_ready"] else 503
    return web.json_response(
        {
            "service": "hades-discord-bot",
            "status": "ready" if state["discord_ready"] else "not-ready",
            **state,
        },
        status=code,
    )


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


# Backward-compatible alias used by main.py.
def start_web_server() -> None:
    import asyncio
    import threading

    def runner() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_health_server())
        loop.run_forever()

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
