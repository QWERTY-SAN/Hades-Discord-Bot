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


MOOD_KEYWORDS: dict[str, tuple[str, ...]] = {
    "happy": (
        "happy", "glad", "great", "nice", "yay", "love", "loved", "cute",
        "thank", "thanks", "thank you", "awesome", "amazing", "wonderful", "hehe",
    ),
    "smug": (
        "brat", "smug", "arrogant", "confident", "prove it", "you think", "really?",
        "sure", "obviously", "clever", "fool", "idiot", "tease", "teasing",
    ),
    "annoyed": (
        "annoying", "annoyed", "stop", "shut up", "ugh", "hate", "angry", "mad",
        "irritating", "irritated", "seriously", "damn", "wtf",
    ),
    "surprised": (
        "what?!", "really?!", "wait", "huh?!", "no way", "seriously?!", "surprise",
        "surprised", "unexpected", "whaat", "how?!",
    ),
    "neutral": (),
}


@dataclass(slots=True)
class GifEntry:
    url: str
    mood: str = "neutral"


@dataclass(slots=True)
class GifCacheItem:
    data: bytes
    digest: str
    content_type: str
    fetched_at: float


class HadesMedia:
    """GIF manager with mood selection, caching, validation, cooldowns and deduplication."""

    def __init__(self) -> None:
        self._rng = SystemRandom()
        self._last_sent: dict[str, float] = {}
        self._recent_hashes: dict[str, deque[str]] = defaultdict(
            lambda: deque(maxlen=SETTINGS.hades_gif_recent_count)
        )
        self._cache: dict[str, GifCacheItem] = {}
        self._session: aiohttp.ClientSession | None = None

        self.entries = self._parse_entries(tuple(HADES_GIF_URLS))
        self._by_mood: dict[str, list[GifEntry]] = defaultdict(list)
        for entry in self.entries:
            self._by_mood[entry.mood].append(entry)
            if entry.mood != "neutral":
                self._by_mood["neutral"].append(entry)

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

            mood = "neutral"
            if "=>" in item:
                prefix, url = item.split("=>", 1)
                prefix = prefix.strip().lower()
                if prefix in MOOD_KEYWORDS:
                    mood = prefix
                    item = url.strip()

            parsed = urlparse(item)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                logger.warning("Ignoring invalid Hades GIF URL: %s", item)
                continue
            normalized = item.strip()
            if normalized in seen:
                continue
            seen.add(normalized)
            entries.append(GifEntry(url=normalized, mood=mood))
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

    @staticmethod
    def detect_mood(text: str) -> str:
        lowered = text.casefold()
        best_mood = "neutral"
        best_score = 0
        for mood, keywords in MOOD_KEYWORDS.items():
            if mood == "neutral":
                continue
            score = sum(1 for keyword in keywords if keyword in lowered)
            if score > best_score:
                best_mood = mood
                best_score = score
        return best_mood

    def should_auto_send(self, message: discord.Message, trigger: str) -> bool:
        if not SETTINGS.hades_gif_enabled or SETTINGS.hades_gif_mode == "off":
            return False
        if not self.entries:
            return False

        mode = SETTINGS.hades_gif_mode
        if mode == "every_response":
            match = True
        elif mode == "every_mention":
            match = trigger == "mention"
        elif mode == "every_command":
            match = trigger == "command"
        elif mode == "first_reply":
            key = self._key(message)
            match = key not in self._last_sent
        else:
            match = False
        if not match:
            return False

        if mode != "first_reply":
            last = self._last_sent.get(self._key(message), 0.0)
            if time.monotonic() - last < SETTINGS.hades_gif_cooldown_seconds:
                return False
        return True

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=SETTINGS.hades_gif_request_timeout),
                headers={"User-Agent": "Hades-Discord-Bot/1.0"},
            )
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    def _choose_candidates(self, text: str) -> list[GifEntry]:
        mood = self.detect_mood(text)
        candidates = list(self._by_mood.get(mood, ()))
        if not candidates:
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
        candidates = self._choose_candidates(text)

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
                    file=discord.File(BytesIO(item.data), filename=f"hades-{entry.mood}.{extension}")
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
                        file=discord.File(BytesIO(item.data), filename=f"hades-{entry.mood}.gif")
                    )
                except discord.HTTPException:
                    continue
                recent.append(item.digest)
                self._last_sent[key] = time.monotonic()
                return True

        return False
