from __future__ import annotations

import asyncio
import logging
import random

import discord
from discord.ext import commands, tasks

from . import __version__
from .ai.chat import HadesChat
from .ai.gemini_client import AIServiceError, GeminiService
from .config import SETTINGS
from .core.memory import ConversationMemory
from .core.scope import contains_forbidden_topic, is_hades_scope_allowed, scope_block_reason
from .core.utils import CooldownManager, sanitize_model_output, split_message, strip_bot_mentions
from .media.media import HadesMedia
from .web import update_discord_state

logger = logging.getLogger("hades-bot")
ALLOWED_MENTIONS = discord.AllowedMentions.none()

SCOPE_FALLBACKS = (
    "Mm. I have no interest in that matter, Administrator. Ask me about something within my realm.",
    "That lies outside my stage, little lamb. Bring me something from Aether Gazer instead.",
    "Some subjects are simply too dull to deserve my attention. Choose something closer to my world. 🌙",
)
EMPTY_CALL_RESPONSES = (
    "You summoned me, little lamb. Speak. 🌙",
    "Yes, Administrator? 😏",
    "You have my attention. ✨",
    "Go on. 🎭",
    "What is it? 🕯️",
    "I'm listening. 🌙",
)


class HadesBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=SETTINGS.bot_prefix,
            intents=intents,
            help_command=None,
            allowed_mentions=ALLOWED_MENTIONS,
        )
        self.hades_chat = HadesChat(
            GeminiService(),
            ConversationMemory(
                SETTINGS.max_history,
                SETTINGS.memory_ttl_seconds,
                SETTINGS.max_conversations,
            ),
            max_concurrent_requests=SETTINGS.max_concurrent_requests,
        )
        self.cooldowns = CooldownManager(SETTINGS.user_cooldown)
        self.media = HadesMedia()
        self._rng = random.SystemRandom()

    async def setup_hook(self) -> None:
        self.maintenance_loop.start()

    async def close(self) -> None:
        if self.maintenance_loop.is_running():
            self.maintenance_loop.cancel()
        await self.media.close()
        await self.hades_chat.close()
        await super().close()

    def conversation_key(self, message: discord.Message) -> str:
        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)):
            return f"dm:{message.author.id}"
        guild_id = message.guild.id if message.guild else "no-guild"
        return f"guild:{guild_id}:channel:{message.channel.id}:user:{message.author.id}"

    async def send_chunks(self, message: discord.Message, text: str, *, attach_auto_media: bool = False) -> None:
        chunks = split_message(text)
        media_embed = None
        if attach_auto_media and self.media.should_auto_send_media(message, "mention"):
            media_embed = self.media.choose_auto_media_embed(message)
        for index, chunk in enumerate(chunks):
            if index == 0:
                await message.reply(
                    chunk,
                    mention_author=False,
                    allowed_mentions=ALLOWED_MENTIONS,
                    embed=media_embed,
                )
            else:
                await message.channel.send(chunk, allowed_mentions=ALLOWED_MENTIONS)

    async def is_reply_to_hades(self, message: discord.Message) -> bool:
        ref = message.reference
        if ref is None or ref.message_id is None or self.user is None:
            return False
        if isinstance(ref.resolved, discord.Message):
            return ref.resolved.author.id == self.user.id
        try:
            referenced = await message.channel.fetch_message(ref.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return False
        return referenced.author.id == self.user.id

    async def handle_ai_message(self, message: discord.Message, content: str, trigger: str = "mention") -> None:
        content = content.strip()
        if not content:
            response = self._rng.choice(EMPTY_CALL_RESPONSES)
            media_embed = self.media.choose_auto_media_embed(message) if self.media.should_auto_send_media(message, trigger) else None
            await message.reply(response, mention_author=False, allowed_mentions=ALLOWED_MENTIONS, embed=media_embed)
            return

        if len(content) > SETTINGS.max_input_chars:
            await message.reply(
                f"That's quite a manuscript, little lamb. Keep it under `{SETTINGS.max_input_chars:,}` characters.",
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return

        key = self.conversation_key(message)
        has_history = await self.hades_chat.memory.has_history(key)
        if not is_hades_scope_allowed(content, has_history=has_history):
            try:
                refusal = await self.hades_chat.scope_refusal(scope_block_reason(content))
            except Exception:
                refusal = self._rng.choice(SCOPE_FALLBACKS)
            await self.send_chunks(message, refusal)
            return

        remaining = await self.cooldowns.try_acquire(key)
        if remaining > 0:
            await message.reply(
                f"Patience, Administrator. Wait `{remaining:.1f}s`.",
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return

        try:
            async with message.channel.typing():
                reply = await self.hades_chat.ask(key, content)
            if contains_forbidden_topic(reply):
                logger.warning("Blocked forbidden-topic model output for %s", key)
                await self.cooldowns.release(key)
                refusal = await self.hades_chat.scope_refusal("an unrelated or forbidden topic")
                await self.send_chunks(message, refusal)
                return
            reply = sanitize_model_output(reply)
            if not reply:
                await self.cooldowns.release(key)
                await message.reply("Tsk. You have my attention. Try that again.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
                return
            await self.send_chunks(message, reply, attach_auto_media=(trigger == "mention"))
        except AIServiceError as exc:
            await self.cooldowns.release(key)
            await message.reply(exc.user_message, mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
        except RuntimeError:
            await self.cooldowns.release(key)
            await message.reply("The response queue is full. Try again in a moment.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
        except Exception:
            await self.cooldowns.release(key)
            logger.exception("Unexpected AI handling failure")
            await message.reply("Something went wrong behind the curtain. Try again in a moment.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)

    async def on_ready(self) -> None:
        update_discord_state(ready=True, user=str(self.user) if self.user else None, guild_count=len(self.guilds))
        logger.info("Logged in as %s", self.user)
        await self.change_presence(status=discord.Status.online, activity=discord.Game(name="Aether Gazer"))

    async def on_disconnect(self) -> None:
        update_discord_state(ready=False)

    @tasks.loop(seconds=SETTINGS.memory_prune_interval)
    async def maintenance_loop(self) -> None:
        await self.hades_chat.prune_memory()
        await self.cooldowns.prune()
        await self.media.prune()

    @maintenance_loop.before_loop
    async def before_maintenance(self) -> None:
        await self.wait_until_ready()

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        await self.process_commands(message)
        content = message.content or ""
        if content.startswith(SETTINGS.bot_prefix):
            return
        private = isinstance(message.channel, (discord.DMChannel, discord.GroupChannel))
        mentioned = self.user is not None and self.user in message.mentions
        replied = False if private or mentioned else await self.is_reply_to_hades(message)
        if not private and not mentioned and not replied:
            return
        clean_content = content.strip() if private else strip_bot_mentions(content, self.user.id if self.user else 0)
        trigger = "mention" if mentioned else "reply"
        await self.handle_ai_message(message, clean_content, trigger=trigger)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"Use `{SETTINGS.bot_prefix}hades <message>` to talk to me.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
            return
        logger.exception("Command error: %s", error)
        await ctx.reply("Something went wrong behind the curtain. Try again shortly.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


bot = HadesBot()


def info_embed(title: str, description: str) -> discord.Embed:
    embed = discord.Embed(title=title, description=description)
    embed.set_footer(text=f"Hades Bot {__version__}")
    return embed


@bot.command(name="hades", aliases=["ask"])
async def hades_command(ctx: commands.Context, *, prompt: str | None = None) -> None:
    if not prompt:
        await ctx.reply(f"Usage: `{SETTINGS.bot_prefix}hades <message>`", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
        return
    await bot.handle_ai_message(ctx.message, prompt, trigger="command")


@bot.command(name="reset", aliases=["forget", "clear"])
async def reset_command(ctx: commands.Context) -> None:
    key = bot.conversation_key(ctx.message)
    await bot.hades_chat.reset(key)
    await bot.cooldowns.release(key)
    await ctx.reply("*Hades calmly gathers the strings.* There. Your conversation is forgotten. 🪢", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


@bot.command(name="memory")
async def memory_command(ctx: commands.Context) -> None:
    count = await bot.hades_chat.memory.message_count(bot.conversation_key(ctx.message))
    await ctx.reply(f"Your conversation memory: `{count}` message(s).\nExpires after `{SETTINGS.memory_ttl_seconds // 3600}` hour(s).", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


@bot.command(name="image", aliases=["hadesimage"])
async def image_command(ctx: commands.Context) -> None:
    sent = await bot.media.send_image(ctx.channel, ctx.message, force=True)
    if not sent:
        await ctx.reply("The portrait refused to appear. Check the configured image URLs.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


@bot.command(name="gif", aliases=["hadesgif"])
async def gif_command(ctx: commands.Context) -> None:
    sent = await bot.media.send_gif(ctx.channel, ctx.message, force=True)
    if not sent:
        await ctx.reply("The performance refused to load. Check the configured GIF URLs.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


@bot.command(name="ping")
async def ping_command(ctx: commands.Context) -> None:
    await ctx.reply(f"The connection is functioning. ⚡ `{round(bot.latency * 1000)}ms`.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


@bot.command(name="about")
async def about_command(ctx: commands.Context) -> None:
    await ctx.reply(embed=info_embed("🌙 Hades — Aether Gazer AI", f"Character-focused Hades bot.\nVersion: `{__version__}`\nModel: `{SETTINGS.gemini_model}`\nPrefix: `{SETTINGS.bot_prefix}`\nMemory: per-user/per-channel, in-memory\nScope: Aether Gazer / Hades-focused conversation\n\nShe is meant to feel like Hades herself—not a generic assistant. 🎭"), mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


@bot.command(name="version")
async def version_command(ctx: commands.Context) -> None:
    await ctx.reply(embed=info_embed("Hades Bot — Version", f"Version: `{__version__}`\ndiscord.py: `{discord.__version__}`\nGemini model: `{SETTINGS.gemini_model}`"), mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


@bot.command(name="privacy")
async def privacy_command(ctx: commands.Context) -> None:
    await ctx.reply(embed=info_embed("🔒 Privacy", f"• Conversation memory is kept in the bot process and is not written to a local database.\n• Memory expires after `{SETTINGS.memory_ttl_seconds // 3600}` hour(s), or use `{SETTINGS.bot_prefix}reset`.\n• Messages used for AI replies are sent to the configured Gemini API.\n• Do not send passwords, API keys, payment details, or other secrets."), mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


@bot.command(name="diagnose")
async def diagnose_command(ctx: commands.Context) -> None:
    memory_count = await bot.hades_chat.memory.conversation_count()
    ready = bot.is_ready()
    latency_ms = round(bot.latency * 1000) if bot.latency < float("inf") else "unavailable"
    discord_state = "OK" if ready else "NOT READY"
    gemini_state = "configured" if SETTINGS.gemini_api_key else "MISSING"
    token_state = "configured" if SETTINGS.discord_token else "MISSING"
    description = "\n".join([
        f"Discord connection: `{discord_state}`",
        f"Gemini API key: `{gemini_state}`",
        f"Discord token: `{token_state}`",
        f"Gemini model: `{SETTINGS.gemini_model}`",
        "Hades scope: `enforced`",
        f"Memory: `{memory_count}` active conversations",
        f"AI requests: `{bot.hades_chat.active_requests}/{SETTINGS.max_concurrent_requests}` active",
        f"Latency: `{latency_ms}ms`",
        f"Version: `{__version__}`",
        "No Gemini test request was sent.",
    ])
    await ctx.reply(embed=info_embed("🩺 Hades Diagnostics", description), mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


@bot.command(name="status")
async def status_command(ctx: commands.Context) -> None:
    if ctx.guild and not (ctx.author.guild_permissions.manage_guild or ctx.author.guild_permissions.administrator):
        await ctx.reply("That information is for those managing the stage. 🎭", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
        return
    count = await bot.hades_chat.memory.conversation_count()
    await ctx.reply(embed=info_embed("🌙 Hades Status", f"Model: `{SETTINGS.gemini_model}`\nGuilds: `{len(bot.guilds)}`\nMemory: `{count}` active conversations\nRequests: `{bot.hades_chat.active_requests}/{SETTINGS.max_concurrent_requests}` active\nTotal AI requests: `{bot.hades_chat.total_requests}`\nAuto media: `mention cooldown`\nGIFs: `{bot.media.configured_count}` external URLs\nImages: `{bot.media.image_configured_count}` external URLs\nLatency: `{round(bot.latency * 1000)}ms`"), mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


@bot.command(name="hadeshelp", aliases=["help"])
async def help_command(ctx: commands.Context) -> None:
    p = SETTINGS.bot_prefix
    text = (
        f"`{p}hades <message>` — Talk to Hades\n"
        f"`{p}ask <message>` — Same as hades\n"
        f"`{p}reset` / `{p}forget` / `{p}clear` — Clear conversation\n"
        f"`{p}memory` — Show memory count\n"
        f"`{p}gif` — Send a Hades GIF\n"
        f"`{p}image` — Send a Hades image\n"
        f"`{p}ping` — Check latency\n"
        f"`{p}about` / `{p}version` / `{p}privacy` / `{p}diagnose` — Bot information\n"
        f"`{p}status` — Admin/server status\n\n"
        "You can also mention me or reply to one of my messages."
    )
    await ctx.reply(embed=info_embed("🌙 Hades — Aether Gazer AI", text), mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
