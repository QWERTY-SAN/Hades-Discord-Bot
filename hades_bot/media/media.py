from __future__ import annotations

import random
import time
from collections import defaultdict, deque
from urllib.parse import urlparse

import discord

from .gifs import HADES_GIF_URLS
from .images import HADES_IMAGE_URLS

AUTO_MEDIA_COOLDOWN_SECONDS = 300.0
GIF_COOLDOWN_SECONDS = 300.0
IMAGE_COOLDOWN_SECONDS = 300.0
RECENT_COUNT = 6
STATE_TTL_SECONDS = 7200.0


class HadesMedia:
    def __init__(self) -> None:
        self.rng = random.SystemRandom()
        self.gifs = tuple(self._valid_urls(HADES_GIF_URLS))
        self.images = tuple(self._valid_urls(HADES_IMAGE_URLS))
        self._last_auto: dict[str, float] = {}
        self._last_gif: dict[str, float] = {}
        self._last_image: dict[str, float] = {}
        self._recent_gif: dict[str, deque[str]] = defaultdict(lambda: deque(maxlen=RECENT_COUNT))
        self._recent_image: dict[str, deque[str]] = defaultdict(lambda: deque(maxlen=RECENT_COUNT))

    @staticmethod
    def _valid_urls(urls: list[str]) -> list[str]:
        output: list[str] = []
        for url in urls:
            parsed = urlparse(url)
            if parsed.scheme in {"http", "https"} and parsed.netloc:
                output.append(url)
        return output

    @property
    def configured_count(self) -> int:
        return len(self.gifs)

    @property
    def image_configured_count(self) -> int:
        return len(self.images)

    def _key(self, message: discord.Message) -> str:
        guild = message.guild.id if message.guild else "dm"
        return f"{guild}:{message.channel.id}"

    def _cooldown_ready(self, store: dict[str, float], key: str, cooldown: float, *, force: bool) -> bool:
        if force:
            return True
        stamp = store.get(key, 0.0)
        return (time.monotonic() - stamp) >= cooldown

    @staticmethod
    def _fresh_options(urls: tuple[str, ...], recent: deque[str]) -> list[str]:
        if not urls:
            return []
        recent_set = set(recent)
        return [url for url in urls if url not in recent_set] or list(urls)

    def should_auto_send_media(self, message: discord.Message, trigger: str) -> bool:
        if trigger != "mention" or not self.gifs and not self.images:
            return False
        return self._cooldown_ready(
            self._last_auto,
            self._key(message),
            AUTO_MEDIA_COOLDOWN_SECONDS,
            force=False,
        )

    def choose_auto_media_embed(self, message: discord.Message) -> discord.Embed | None:
        key = self._key(message)
        gif_options = self._fresh_options(self.gifs, self._recent_gif[key])
        image_options = self._fresh_options(self.images, self._recent_image[key])
        if not gif_options and not image_options:
            return None

        if gif_options and image_options:
            kind = self.rng.choice(("gif", "image"))
            options = gif_options if kind == "gif" else image_options
            url = self.rng.choice(options)
        elif gif_options:
            kind, url = "gif", self.rng.choice(gif_options)
        else:
            kind, url = "image", self.rng.choice(image_options)
        self._last_auto[key] = time.monotonic()
        embed = discord.Embed()
        embed.set_image(url=url)
        if kind == "gif":
            self._recent_gif[key].append(url)
        else:
            self._recent_image[key].append(url)
        return embed

    async def send_gif(self, channel, message: discord.Message, *, force: bool = False) -> bool:
        if not self.gifs:
            return False
        key = self._key(message)
        if not self._cooldown_ready(self._last_gif, key, GIF_COOLDOWN_SECONDS, force=force):
            return False
        recent = self._recent_gif[key]
        options = self._fresh_options(self.gifs, recent)
        url = self.rng.choice(options)
        recent.append(url)
        self._last_gif[key] = time.monotonic()
        await channel.send(embed=discord.Embed().set_image(url=url))
        return True

    async def send_image(self, channel, message: discord.Message, *, force: bool = False) -> bool:
        if not self.images:
            return False
        key = self._key(message)
        if not self._cooldown_ready(self._last_image, key, IMAGE_COOLDOWN_SECONDS, force=force):
            return False
        recent = self._recent_image[key]
        options = self._fresh_options(self.images, recent)
        url = self.rng.choice(options)
        recent.append(url)
        self._last_image[key] = time.monotonic()
        await channel.send(embed=discord.Embed().set_image(url=url))
        return True

    async def prune(self) -> int:
        now = time.monotonic()
        removed = 0
        for store in (self._last_auto, self._last_gif, self._last_image):
            for key, stamp in list(store.items()):
                if now - stamp >= STATE_TTL_SECONDS:
                    store.pop(key, None)
                    removed += 1

        live_keys = set(self._last_auto) | set(self._last_gif) | set(self._last_image)
        for store in (self._recent_gif, self._recent_image):
            for key in list(store):
                if key not in live_keys:
                    store.pop(key, None)
                    removed += 1
        return removed

    async def close(self) -> None:
        return None
