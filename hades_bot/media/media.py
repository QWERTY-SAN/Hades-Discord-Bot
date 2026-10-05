from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from random import SystemRandom
from urllib.parse import urlparse

import discord

from .gifs import HADES_GIF_URLS
from .images import HADES_IMAGE_URLS

logger = logging.getLogger("hades-bot.media")

# GIF behavior is intentionally internal. The only user-editable GIF setting is
# the URL list in hades_bot/media/gifs.py.
AUTO_MEDIA_MODE = "every_mention_random_gif_or_image"
AUTO_MEDIA_COOLDOWN_SECONDS = 300.0
GIF_COOLDOWN_SECONDS = 300.0
IMAGE_COOLDOWN_SECONDS = 300.0
GIF_RECENT_COUNT = 6
IMAGE_RECENT_COUNT = 4
MEDIA_STATE_TTL_SECONDS = 7200.0
MAX_TRACKED_CHANNELS = 1000


@dataclass(frozen=True, slots=True)
class GifEntry:
    url: str


@dataclass(frozen=True, slots=True)
class ImageEntry:
    url: str


class HadesMedia:
    """Handles GIFs and images as separate external-media systems.

    The bot never downloads or re-uploads these assets.
    """

    def __init__(self) -> None:
        self._rng = SystemRandom()
        self._last_gif_sent: dict[str, float] = {}
        self._last_image_sent: dict[str, float] = {}
        self._last_auto_media_sent: dict[str, float] = {}
        self._gif_channel_touched: dict[str, float] = {}
        self._image_channel_touched: dict[str, float] = {}
        self._recent_gif_urls: dict[str, deque[str]] = defaultdict(
            lambda: deque(maxlen=GIF_RECENT_COUNT)
        )
        self._recent_image_urls: dict[str, deque[str]] = defaultdict(
            lambda: deque(maxlen=IMAGE_RECENT_COUNT)
        )
        self.entries = self._parse_entries(tuple(HADES_GIF_URLS), GifEntry)
        self.image_entries = self._parse_entries(tuple(HADES_IMAGE_URLS), ImageEntry)

    @staticmethod
    def _parse_entries(urls: tuple[str, ...], entry_type):
        entries = []
        seen: set[str] = set()
        for raw in urls:
            for part in raw.replace("\n", ",").split(","):
                item = part.strip()
                if not item:
                    continue
                parsed = urlparse(item)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    logger.warning("Ignoring invalid Hades media URL: %s", item)
                    continue
                if item in seen:
                    continue
                seen.add(item)
                entries.append(entry_type(item))
        return tuple(entries)

    @property
    def configured_count(self) -> int:
        return len(self.entries)

    @property
    def image_configured_count(self) -> int:
        return len(self.image_entries)

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
        """Drop stale GIF/image cooldown and history entries."""
        now = time.monotonic()
        removed = 0
        for state in (self._last_gif_sent, self._last_image_sent, self._last_auto_media_sent):
            stale_users = [
                key for key, stamp in state.items()
                if now - stamp >= MEDIA_STATE_TTL_SECONDS
            ]
            for key in stale_users:
                state.pop(key, None)
                removed += 1
        if len(self._recent_gif_urls) > MAX_TRACKED_CHANNELS:
            active_by_channel = {
                key: self._gif_channel_touched.get(key, 0.0)
                for key in self._recent_gif_urls
            }
            keep = set(
                sorted(
                    active_by_channel,
                    key=active_by_channel.get,
                    reverse=True,
                )[:MAX_TRACKED_CHANNELS]
            )
            for key in list(self._recent_gif_urls):
                if key not in keep:
                    self._recent_gif_urls.pop(key, None)
                    self._gif_channel_touched.pop(key, None)
                    removed += 1
        if len(self._recent_image_urls) > MAX_TRACKED_CHANNELS:
            active_by_channel = {
                key: self._image_channel_touched.get(key, 0.0)
                for key in self._recent_image_urls
            }
            keep = set(
                sorted(active_by_channel, key=active_by_channel.get, reverse=True)[:MAX_TRACKED_CHANNELS]
            )
            for key in list(self._recent_image_urls):
                if key not in keep:
                    self._recent_image_urls.pop(key, None)
                    self._image_channel_touched.pop(key, None)
                    removed += 1
        return removed

    def _choose_gif(self, message: discord.Message, force: bool) -> GifEntry | None:
        candidates = list(self.entries)
        self._rng.shuffle(candidates)
        recent = self._recent_gif_urls[self._history_key(message)]
        for entry in candidates:
            if force or entry.url not in recent:
                return entry
        return candidates[0] if candidates else None

    def _choose_image(self, message: discord.Message, force: bool) -> ImageEntry | None:
        candidates = list(self.image_entries)
        self._rng.shuffle(candidates)
        recent = self._recent_image_urls[self._history_key(message)]
        for entry in candidates:
            if force or entry.url not in recent:
                return entry
        return candidates[0] if candidates else None

    def should_auto_send_media(self, message: discord.Message, trigger: str) -> bool:
        """Return whether one automatic media message may be sent.

        GIFs and images remain separate libraries, but the automatic trigger
        uses one shared cooldown so a single Hades response can never send
        both kinds of media.
        """
        if trigger != "mention":
            return False
        if not self.entries and not self.image_entries:
            return False
        now = time.monotonic()
        key = self._cooldown_key(message)
        last_sent = self._last_auto_media_sent.get(key)
        return last_sent is None or now - last_sent >= AUTO_MEDIA_COOLDOWN_SECONDS

    async def send_auto_media(
        self,
        destination: discord.abc.Messageable,
        message: discord.Message,
    ) -> bool:
        """Send exactly one randomly selected automatic media item.

        The GIF and image URL libraries stay completely separate. Only the
        automatic trigger chooses randomly between the two media types.
        Manual ``h!gif`` and ``h!image`` commands are unaffected.
        """
        choices: list[str] = []
        if self.entries:
            choices.append("gif")
        if self.image_entries:
            choices.append("image")
        if not choices:
            return False

        selected = self._rng.choice(choices)
        if selected == "gif":
            sent = await self.send_gif(destination, message)
        else:
            sent = await self.send_image(destination, message)

        if sent:
            self._last_auto_media_sent[self._cooldown_key(message)] = time.monotonic()
            logger.info("Sent one automatic Hades %s", selected)
        return sent

    def should_auto_send_gif(self, message: discord.Message, trigger: str) -> bool:
        """Compatibility helper for older callers.

        Automatic mention handling now uses the shared random-media path.
        """
        if trigger != "mention" or not self.entries:
            return False
        return self.should_auto_send_media(message, trigger)

    def should_auto_send_image(self, message: discord.Message, trigger: str) -> bool:
        """Compatibility helper for older callers.

        Automatic mention handling now uses the shared random-media path.
        """
        if trigger != "mention" or not self.image_entries:
            return False
        return self.should_auto_send_media(message, trigger)

    async def send_auto_gif(self, destination: discord.abc.Messageable, message: discord.Message) -> bool:
        return await self.send_gif(destination, message)

    async def send_auto_image(self, destination: discord.abc.Messageable, message: discord.Message) -> bool:
        if not self.image_entries:
            return False
        return await self.send_image(destination, message)

    async def send_gif(
        self,
        destination: discord.abc.Messageable,
        message: discord.Message,
        *,
        force: bool = False,
    ) -> bool:
        if not self.entries:
            return False

        entry = self._choose_gif(message, force)
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
        self._recent_gif_urls[history_key].append(entry.url)
        self._gif_channel_touched[history_key] = sent_at
        self._last_gif_sent[self._cooldown_key(message)] = sent_at
        logger.info("Sent Hades GIF embed")
        return True


    async def send_image(
        self,
        destination: discord.abc.Messageable,
        message: discord.Message,
        *,
        force: bool = False,
    ) -> bool:
        if not self.image_entries:
            return False

        entry = self._choose_image(message, force)
        if entry is None:
            return False

        try:
            await destination.send(
                entry.url,
                allowed_mentions=discord.AllowedMentions.none(),
            )
        except discord.HTTPException as exc:
            logger.warning("Discord rejected Hades image %s: %s", entry.url, exc)
            return False

        history_key = self._history_key(message)
        sent_at = time.monotonic()
        self._recent_image_urls[history_key].append(entry.url)
        self._image_channel_touched[history_key] = sent_at
        self._last_image_sent[self._cooldown_key(message)] = sent_at
        logger.info("Sent Hades image")
        return True
