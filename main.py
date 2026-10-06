import logging

from hades_bot.bot import run
from hades_bot.config import SETTINGS, validate_settings
from hades_bot.web import start_web_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


if __name__ == "__main__":
    validate_settings()
    start_web_server(SETTINGS.web_host, SETTINGS.web_port)
    run()
