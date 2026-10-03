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

# GIF behavior is intentionally kept internal.
# The only user-editable GIF setting is HADES_GIF_URLS in gifs.py.
GIF_AUTO_MODE = "every_mention"
GIF_COOLDOWN_SECONDS = 300.0
GIF_RECENT_COUNT = 6


@dataclass(frozen=True, slots=True)
class GifEntry:
    url: str


class HadesMedia:
    """Sends configured external GIF URLs directly; never downloads or re-uploads them."""

    def __init__(self) -> None:
        self._rng = SystemRandom()
        self._last_sent: dict[str, float] = {}
        self._recent_urls: dict[str, deque[str]] = defaultdict(
            lambda: deque(maxlen=GIF_RECENT_COUNT)
        )
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
        # External GIFs are never cached or downloaded by the bot.
        return 0

    async def close(self) -> None:
        """Compatibility hook; there is no HTTP session to close."""
        return None

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

    async def send_gif(
        self,
        destination,
        message: discord.Message,
        *,
        force: bool = False,
        text: str = "",
    ) -> bool:
        """Send the original configured GIF URL directly to Discord."""
        del text  # Kept for compatibility with existing callers.

        if not self.entries:
            return False

        key = self._key(message)
        history_key = self._history_key(message)
        recent = self._recent_urls[history_key]
        candidates = self._choose_candidates()

        # First prefer a URL that is not in the recent per-channel history.
        for entry in candidates:
            if not force and entry.url in recent:
                continue
            try:
                # Sending the URL itself is intentional. Discord handles the
                # preview from the original host; the bot never re-uploads it.
                await destination.send(
                    entry.url,
                    allowed_mentions=discord.AllowedMentions.none(),
                )
            except discord.HTTPException as exc:
                logger.warning("Discord rejected Hades GIF URL %s: %s", entry.url, exc)
                continue

            recent.append(entry.url)
            self._last_sent[key] = time.monotonic()
            logger.info("Sent external Hades GIF URL: %s", entry.url)
            return True

        # If every URL is in recent history, reuse one rather than sending nothing.
        if not force and recent:
            for entry in candidates:
                try:
                    await destination.send(
                        entry.url,
                        allowed_mentions=discord.AllowedMentions.none(),
                    )
                except discord.HTTPException:
                    continue
                recent.append(entry.url)
                self._last_sent[key] = time.monotonic()
                logger.info("Reused external Hades GIF URL: %s", entry.url)
                return True

        return False
