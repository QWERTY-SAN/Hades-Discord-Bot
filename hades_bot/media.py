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

from .gifs import HADES_GIF_URLS

logger = logging.getLogger("hades-bot.media")

# GIF settings intentionally live here instead of .env.
# The only user-editable GIF setting is HADES_GIF_URLS in gifs.py.
GIF_AUTO_MODE = "every_mention"
GIF_COOLDOWN_SECONDS = 300.0
GIF_RECENT_COUNT = 6
GIF_CACHE_SECONDS = 900.0
GIF_MAX_BYTES = 8_000_000
GIF_REQUEST_TIMEOUT = 15.0


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
    """GIF manager with caching, validation, cooldowns, and deduplication."""

    def __init__(self) -> None:
        self._rng = SystemRandom()
        self._last_sent: dict[str, float] = {}
        self._recent_hashes: dict[str, deque[str]] = defaultdict(
            lambda: deque(maxlen=GIF_RECENT_COUNT)
        )
        self._cache: dict[str, GifCacheItem] = {}
        self._session: aiohttp.ClientSession | None = None
        self.entries = self._parse_entries(tuple(HADES_GIF_URLS))

    @staticmethod
    def _parse_entries(urls: tuple[str, ...]) -> tuple[GifEntry, ...]:
        entries: list[GifEntry] = []
        expanded: list[str] = []
        for raw in urls:
            expanded.extend(
                part.strip()
                for part in raw.replace("\n", ",").split(",")
                if part.strip()
            )

        seen: set[str] = set()
        for raw in expanded:
            item = raw.strip()
            parsed = urlparse(item)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                logger.warning("Ignoring invalid Hades GIF URL: %s", item)
                continue
            if item in seen:
                continue
            seen.add(item)
            entries.append(GifEntry(url=item))
        return tuple(entries)

    @property
    def configured_count(self) -> int:
        return len(self.entries)

    @property
    def cached_count(self) -> int:
        return len(self._cache)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=GIF_REQUEST_TIMEOUT)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
        self._session = None

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

    def should_auto_send(self, message: discord.Message, trigger: str) -> bool:
        if not self.entries:
            return False
        if GIF_AUTO_MODE == "off":
            return False
        if GIF_AUTO_MODE == "every_mention" and trigger != "mention":
            return False
        if GIF_AUTO_MODE == "every_command" and trigger != "command":
            return False
        if GIF_AUTO_MODE == "first_reply" and trigger != "mention":
            return False

        key = self._key(message)
        now = time.monotonic()
        last_sent = self._last_sent.get(key)
        if last_sent is not None and now - last_sent < GIF_COOLDOWN_SECONDS:
            return False
        return True

    async def _fetch(self, entry: GifEntry) -> GifCacheItem | None:
        now = time.monotonic()
        cached = self._cache.get(entry.url)
        if cached and now - cached.fetched_at < GIF_CACHE_SECONDS:
            return cached

        session = await self._get_session()
        try:
            async with session.get(entry.url, allow_redirects=True) as response:
                if response.status != 200:
                    logger.warning(
                        "Hades GIF returned HTTP %s: %s",
                        response.status,
                        entry.url,
                    )
                    return None

                content_type = (response.headers.get("Content-Type") or "").lower()
                declared_size = response.content_length
                if declared_size and declared_size > GIF_MAX_BYTES:
                    logger.warning("Skipping oversized Hades GIF: %s bytes", declared_size)
                    return None

                data = await response.content.read(GIF_MAX_BYTES + 1)
                if len(data) > GIF_MAX_BYTES:
                    logger.warning("Skipping oversized Hades GIF: %s", entry.url)
                    return None

                looks_like_gif = data[:6] in {b"GIF87a", b"GIF89a"}
                url_says_gif = entry.url.lower().split("?", 1)[0].endswith(".gif")
                if not looks_like_gif or ("image/gif" not in content_type and not url_says_gif):
                    logger.warning(
                        "Skipping non-GIF response: %s (%s)",
                        entry.url,
                        content_type or "unknown",
                    )
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

            try:
                await destination.send(
                    file=discord.File(BytesIO(item.data), filename="hades.gif")
                )
            except discord.HTTPException as exc:
                logger.warning("Discord rejected Hades GIF %s: %s", entry.url, exc)
                continue

            recent.append(item.digest)
            self._last_sent[key] = time.monotonic()
            return True

        # If every GIF is currently in the recent-history window, allow one reuse
        # rather than failing completely.
        if not force and recent:
            for entry in candidates:
                item = await self._fetch(entry)
                if item is None:
                    continue
                try:
                    await destination.send(
                        file=discord.File(BytesIO(item.data), filename="hades.gif")
                    )
                except discord.HTTPException as exc:
                    logger.warning("Discord rejected fallback Hades GIF %s: %s", entry.url, exc)
                    continue
                recent.append(item.digest)
                self._last_sent[key] = time.monotonic()
                return True

        return False
