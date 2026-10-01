import asyncio
import logging

from hades_bot.bot import bot
from hades_bot.config import SETTINGS
from hades_bot.web import start_health_server, update_discord_state


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("hades-bot.main")


async def async_main() -> None:
    health_runner = await start_health_server()
    try:
        logger.info("Starting Hades bot with model %s", SETTINGS.gemini_model)
        await bot.start(SETTINGS.discord_token)
    finally:
        update_discord_state(ready=False)
        await bot.close()
        await health_runner.cleanup()


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
