from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from random import SystemRandom
from urllib.parse import urlparse

import discord

from .gifs import HADES_GIF_URLS

logger = logging.getLogger("hades-bot.media")

# GIF behavior is intentionally internal. The only user-editable GIF setting is
# the URL list in hades_bot/gifs.py.
GIF_AUTO_MODE = "every_mention"
GIF_COOLDOWN_SECONDS = 300.0
GIF_RECENT_COUNT = 6
GIF_STATE_TTL_SECONDS = 7200.0
MAX_TRACKED_CHANNELS = 1000


@dataclass(frozen=True, slots=True)
class GifEntry:
    url: str


class HadesMedia:
    """Sends original external GIF URLs; never downloads or re-uploads them."""

    def __init__(self) -> None:
        self._rng = SystemRandom()
        self._last_sent: dict[str, float] = {}
        self._channel_touched: dict[str, float] = {}
        self._recent_urls: dict[str, deque[str]] = defaultdict(
            lambda: deque(maxlen=GIF_RECENT_COUNT)
        )
        self.entries = self._parse_entries(tuple(HADES_GIF_URLS))

    @staticmethod
    def _parse_entries(urls: tuple[str, ...]) -> tuple[GifEntry, ...]:
        entries: list[GifEntry] = []
        seen: set[str] = set()
        for raw in urls:
            for part in raw.replace("\n", ",").split(","):
                item = part.strip()
                if not item:
                    continue
                parsed = urlparse(item)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    logger.warning("Ignoring invalid Hades GIF URL: %s", item)
                    continue
                if item in seen:
                    continue
                seen.add(item)
                entries.append(GifEntry(item))
        return tuple(entries)

    @property
    def configured_count(self) -> int:
        return len(self.entries)

    async def close(self) -> None:
        # No network session exists: GIFs are never downloaded.
        return None

    def _cooldown_key(self, message: discord.Message) -> str:
        guild = message.guild.id if message.guild else "dm"
        return f"{guild}:{message.channel.id}:{message.author.id}"

    def _history_key(self, message: discord.Message) -> str:
        guild = message.guild.id if message.guild else "dm"
        return f"{guild}:{message.channel.id}"

    async def prune(self) -> int:
        """Drop stale GIF cooldown/history entries so long-running services stay bounded."""
        now = time.monotonic()
        removed = 0
        stale_users = [key for key, stamp in self._last_sent.items() if now - stamp >= GIF_STATE_TTL_SECONDS]
        for key in stale_users:
            self._last_sent.pop(key, None)
            removed += 1
        if len(self._recent_urls) > MAX_TRACKED_CHANNELS:
            active_by_channel = {
                key: self._channel_touched.get(key, 0.0)
                for key in self._recent_urls
            }
            keep = set(
                sorted(
                    active_by_channel,
                    key=active_by_channel.get,
                    reverse=True,
                )[:MAX_TRACKED_CHANNELS]
            )
            for key in list(self._recent_urls):
                if key not in keep:
                    self._recent_urls.pop(key, None)
                    self._channel_touched.pop(key, None)
                    removed += 1
        return removed

    def should_auto_send(self, message: discord.Message, trigger: str) -> bool:
        if not self.entries:
            return False
        if GIF_AUTO_MODE != "every_mention" or trigger != "mention":
            return False
        now = time.monotonic()
        key = self._cooldown_key(message)
        last_sent = self._last_sent.get(key)
        return last_sent is None or now - last_sent >= GIF_COOLDOWN_SECONDS

    def _choose(self, message: discord.Message, force: bool) -> GifEntry | None:
        candidates = list(self.entries)
        self._rng.shuffle(candidates)
        recent = self._recent_urls[self._history_key(message)]
        for entry in candidates:
            if force or entry.url not in recent:
                return entry
        return candidates[0] if candidates else None

    async def send_gif(
        self,
        destination: discord.abc.Messageable,
        message: discord.Message,
        *,
        force: bool = False,
    ) -> bool:
        if not self.entries:
            return False

        entry = self._choose(message, force)
        if entry is None:
            return False

        # Embed the ORIGINAL URL. Discord may proxy it internally for display,
        # but the bot never creates an attachment or a Discord CDN upload.
        embed = discord.Embed()
        embed.set_image(url=entry.url)
        try:
            await destination.send(
                embed=embed,
                allowed_mentions=discord.AllowedMentions.none(),
            )
        except discord.HTTPException as exc:
            logger.warning("Discord rejected external Hades GIF %s: %s", entry.url, exc)
            return False

        history_key = self._history_key(message)
        sent_at = time.monotonic()
        self._recent_urls[history_key].append(entry.url)
        self._channel_touched[history_key] = sent_at
        self._last_sent[self._cooldown_key(message)] = sent_at
        logger.info("Sent Hades GIF embed")
        return True
