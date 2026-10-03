from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from io import BytesIO
from random import SystemRandom
from urllib.parse import urlparse

import aiohttp
import discord

from .config import SETTINGS
from .gifs import HADES_GIF_URLS

logger = logging.getLogger("hades-bot.media")


@dataclass(slots=True)
class GifEntry:
    url: str


@dataclass(slots=True)
class GifCacheItem:
    data: bytes
    digest: str
    content_type: str
    fetched_at: float


class HadesMedia:
    """GIF manager with caching, validation, cooldowns and deduplication."""

    def __init__(self) -> None:
        self._rng = SystemRandom()
        self._last_sent: dict[str, float] = {}
        self._recent_hashes: dict[str, deque[str]] = defaultdict(
            lambda: deque(maxlen=SETTINGS.hades_gif_recent_count)
        )
        self._cache: dict[str, GifCacheItem] = {}
        self._session: aiohttp.ClientSession | None = None

        self.entries = self._parse_entries(tuple(HADES_GIF_URLS))

    @staticmethod
    def _parse_entries(urls: tuple[str, ...]) -> tuple[GifEntry, ...]:
        entries: list[GifEntry] = []
        expanded: list[str] = []
        for raw in urls:
            expanded.extend(part.strip() for part in raw.replace("\n", ",").split(",") if part.strip())

        seen: set[str] = set()
        for raw in expanded:
            item = raw.strip()
            if not item:
                continue

            parsed = urlparse(item)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                logger.warning("Ignoring invalid Hades GIF URL: %s", item)
                continue

            normalized = item
            if normalized in seen:
                continue
            seen.add(normalized)
            entries.append(GifEntry(url=normalized))
        return tuple(entries)

    @property
    def configured_count(self) -> int:
        return len(self.entries)

    @property
    def cached_count(self) -> int:
        return len(self._cache)

    def _key(self, message: discord.Message) -> str:
        guild = message.guild.id if message.guild else "dm"
        channel = message.channel.id
        user = message.author.id
        return f"{guild}:{channel}:{user}"

    def _history_key(self, message: discord.Message) -> str:
        guild = message.guild.id if message.guild else "dm"
        channel = message.channel.id
        return f"{guild}:{channel}"

    def _choose_candidates(self) -> list[GifEntry]:
        candidates = list(self.entries)
        self._rng.shuffle(candidates)
        return candidates

    async def _fetch(self, entry: GifEntry) -> GifCacheItem | None:
        now = time.monotonic()
        cached = self._cache.get(entry.url)
        if cached and now - cached.fetched_at < SETTINGS.hades_gif_cache_seconds:
            return cached

        session = await self._get_session()
        try:
            async with session.get(entry.url, allow_redirects=True) as response:
                if response.status != 200:
                    logger.warning("Hades GIF returned HTTP %s: %s", response.status, entry.url)
                    return None
                content_type = (response.headers.get("Content-Type") or "").lower()
                declared_size = response.content_length
                if declared_size and declared_size > SETTINGS.hades_gif_max_bytes:
                    logger.warning("Skipping oversized Hades GIF: %s bytes", declared_size)
                    return None

                data = await response.content.read(SETTINGS.hades_gif_max_bytes + 1)
                if len(data) > SETTINGS.hades_gif_max_bytes:
                    logger.warning("Skipping oversized Hades GIF: %s", entry.url)
                    return None

                # Accept normal image/gif responses and hosts that omit Content-Type when the URL says .gif.
                looks_like_gif = data[:6] in {b"GIF87a", b"GIF89a"}
                url_says_gif = entry.url.lower().split("?", 1)[0].endswith(".gif")
                if not looks_like_gif or ("image/gif" not in content_type and not url_says_gif):
                    logger.warning("Skipping non-GIF response: %s (%s)", entry.url, content_type or "unknown")
                    return None

                digest = hashlib.sha256(data).hexdigest()
                item = GifCacheItem(
                    data=data,
                    digest=digest,
                    content_type=content_type or "image/gif",
                    fetched_at=now,
                )
                self._cache[entry.url] = item
                return item
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as exc:
            logger.warning("Hades GIF fetch failed for %s: %s", entry.url, exc)
            return None

    async def send_gif(
        self,
        destination,
        message: discord.Message,
        *,
        force: bool = False,
        text: str = "",
    ) -> bool:
        if not self.entries:
            return False

        key = self._key(message)
        history_key = self._history_key(message)
        recent = self._recent_hashes[history_key]
        candidates = self._choose_candidates()

        for entry in candidates:
            item = await self._fetch(entry)
            if item is None:
                continue
            if not force and item.digest in recent:
                continue

            recent.append(item.digest)
            extension = "gif"
            try:
                await destination.send(
                    file=discord.File(BytesIO(item.data), filename=f"hades.{extension}")
                )
            except discord.HTTPException as exc:
                logger.warning("Discord rejected Hades GIF %s: %s", entry.url, exc)
                continue

            self._last_sent[key] = time.monotonic()
            return True

        # If every GIF is currently in the recent-history window, allow one reuse instead of failing.
        if not force and recent:
            for entry in candidates:
                item = await self._fetch(entry)
                if item is None:
                    continue
                try:
                    await destination.send(
                        file=discord.File(BytesIO(item.data), filename="hades.gif")
                    )
                except discord.HTTPException:
                    continue
                recent.append(item.digest)
                self._last_sent[key] = time.monotonic()
                return True

        return False
