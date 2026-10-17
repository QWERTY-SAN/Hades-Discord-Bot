from __future__ import annotations

import asyncio
import logging
import random

import discord
from discord.ext import commands, tasks

from . import __version__
from .ai.chat import HadesChat
from .ai.gemini_client import AIServiceError, GeminiService, UnsafeModelOutputError
from .config import SETTINGS
from .core.memory import ConversationMemory
from .core.scope import is_hades_scope_allowed, scope_block_reason
from .core.support_trigger import is_mental_breakdown_trigger
from .core.utils import CooldownManager, sanitize_model_output, split_message, strip_bot_mentions
from .media.media import HadesMedia
from .web import record_runtime_metric, set_runtime_error, update_discord_state

logger = logging.getLogger("hades-bot")
ALLOWED_MENTIONS = discord.AllowedMentions.none()

# Automatically react to short acknowledgements from this specific user.
# Only exact acknowledgement messages match; ordinary sentences are left alone.
SPECIAL_OK_USER_ID = 1387001030797164618
SPECIAL_ACKNOWLEDGEMENT_RESPONSES = {
    "ok": (
        "Mm? Just ‘ok’? How terribly stingy of you, little lamb. I was hoping for a little more attention than that. 🌙",
        "One tiny ‘ok’ and you think you may leave me hanging? How cruel. Come, give me a little more than that. 😏",
        "How concise. Are you being obedient, or are you simply trying to make me curious? ✨",
        "That is all? Hm. I suppose I shall have to coax a proper answer out of you myself. 🎭",
        "Very well, little lamb. I shall accept that little crumb of a reply—for now. 🖤",
    ),
    "k": (
        "Oh, how eloquent. One whole letter? You are spoiling me. 🙄🌙",
        "A single ‘k.’ Truly, you leave me breathless. Try again, little lamb. 😏",
        "So miserly with your words. Am I going to have to earn a longer reply? 🎭",
    ),
    "okay": (
        "‘Okay,’ is it? Good. Then stay a little longer and keep me company. 🌙",
        "How agreeable. I do like it when you make things easy for me, little lamb. 😌",
        "Mm, accepted. Though I still think you could spare me a few more words. ✨",
        "There we are. See? You can be charming when you try. 💋",
    ),
}

SCOPE_FALLBACKS = (
    "Mm. That is not quite a subject I care to entertain, Administrator. Bring me something from Aether Gazer—or simply talk to me.",
    "That topic is not one I intend to pursue, little lamb. Try an Aether Gazer question, or ask me something more personal.",
    "No. That thread leads nowhere interesting for me. Change the subject, and I may surprise you. 🌙",
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
        self.support_cooldowns = CooldownManager(30.0)
        self.media = HadesMedia()
        self._rng = random.SystemRandom()

    async def setup_hook(self) -> None:
        self.maintenance_loop.start()
        self.cooldown_maintenance_loop.start()

    async def close(self) -> None:
        if self.maintenance_loop.is_running():
            self.maintenance_loop.cancel()
        if self.cooldown_maintenance_loop.is_running():
            self.cooldown_maintenance_loop.cancel()
        await self.media.close()
        await self.hades_chat.close()
        await super().close()

    def conversation_key(self, message: discord.Message) -> str:
        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)):
            return f"dm:{message.channel.id}:user:{message.author.id}"
        guild_id = message.guild.id if message.guild else "no-guild"
        return f"guild:{guild_id}:channel:{message.channel.id}:user:{message.author.id}"

    async def send_chunks(self, message: discord.Message, text: str, *, attach_auto_media: bool = False, trigger: str = "mention") -> None:
        chunks = split_message(text)
        media_embed = None
        if attach_auto_media and self.media.should_auto_send_media(message, trigger):
            media_embed = self.media.choose_auto_media_embed(message)
        for index, chunk in enumerate(chunks):
            if index == 0:
                await message.reply(
                    chunk,
                    mention_author=False,
                    allowed_mentions=ALLOWED_MENTIONS,
                    embed=media_embed,
                )
                self.media.record_auto_media_sent(message, media_embed)
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

    async def handle_ai_message(
        self,
        message: discord.Message,
        content: str,
        trigger: str = "mention",
        *,
        direct_reply: bool = False,
        support_trigger: bool = False,
    ) -> None:
        record_runtime_metric("messages_seen")
        content = content.strip()
        if not content:
            response = self._rng.choice(EMPTY_CALL_RESPONSES)
            media_embed = self.media.choose_auto_media_embed(message) if self.media.should_auto_send_media(message, trigger) else None
            await message.reply(response, mention_author=False, allowed_mentions=ALLOWED_MENTIONS, embed=media_embed)
            self.media.record_auto_media_sent(message, media_embed)
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
        if not support_trigger and not is_hades_scope_allowed(
            content, has_history=has_history, direct_reply=direct_reply
        ):
            record_runtime_metric("scope_blocks")
            try:
                refusal = await self.hades_chat.scope_refusal(scope_block_reason(content))
            except Exception:
                refusal = self._rng.choice(SCOPE_FALLBACKS)
            await self.send_chunks(message, refusal)
            return

        remaining = 0.0 if support_trigger else await self.cooldowns.try_acquire(key)
        if remaining > 0:
            await message.reply(
                f"Patience, Administrator. Wait `{remaining:.1f}s`.",
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return

        record_runtime_metric("ai_requests")
        try:
            async with message.channel.typing():
                reply = await self.hades_chat.ask(key, content)
            reply = sanitize_model_output(reply)
            if not reply:
                record_runtime_metric("ai_failures")
                set_runtime_error("Gemini returned an empty response")
                await self.cooldowns.release(key)
                await message.reply("Tsk. You have my attention. Try that again.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
                return
            await self.send_chunks(message, reply, attach_auto_media=(trigger in {"mention", "command"}), trigger=trigger)
            record_runtime_metric("ai_successes")
            set_runtime_error(None)
        except UnsafeModelOutputError:
            record_runtime_metric("ai_failures")
            set_runtime_error("blocked forbidden-topic model output")
            logger.warning("Blocked forbidden-topic model output for %s", key)
            await self.cooldowns.release(key)
            refusal = await self.hades_chat.scope_refusal("an unrelated or forbidden topic")
            await self.send_chunks(message, refusal)
            return
        except AIServiceError as exc:
            record_runtime_metric("ai_failures")
            set_runtime_error(exc.user_message)
            await self.cooldowns.release(key)
            await message.reply(exc.user_message, mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
        except RuntimeError:
            record_runtime_metric("ai_failures")
            set_runtime_error("response queue full")
            await self.cooldowns.release(key)
            await message.reply("The response queue is full. Try again in a moment.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
        except Exception:
            record_runtime_metric("ai_failures")
            set_runtime_error("unexpected AI handling failure")
            await self.cooldowns.release(key)
            logger.exception("Unexpected AI handling failure")
            await message.reply("Something went wrong behind the curtain. Try again in a moment.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)

    async def on_ready(self) -> None:
        update_discord_state(ready=True, user=str(self.user) if self.user else None, guild_count=len(self.guilds))
        logger.info("Logged in as %s", self.user)
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.CustomActivity(name=f"{SETTINGS.bot_prefix}help @GitHub"),
        )

    async def on_disconnect(self) -> None:
        update_discord_state(ready=False)
        set_runtime_error("Discord disconnected")

    async def on_resumed(self) -> None:
        update_discord_state(
            ready=True,
            user=str(self.user) if self.user else None,
            guild_count=len(self.guilds),
        )
        logger.info("Discord session resumed")

    @tasks.loop(seconds=SETTINGS.memory_prune_interval)
    async def maintenance_loop(self) -> None:
        try:
            await self.hades_chat.prune_memory()
            await self.media.prune()
        except Exception:
            logger.exception("Maintenance pass failed; the loop will continue.")
            set_runtime_error("maintenance pass failed")

    @maintenance_loop.before_loop
    async def before_maintenance(self) -> None:
        await self.wait_until_ready()

    @tasks.loop(seconds=SETTINGS.cooldown_prune_interval)
    async def cooldown_maintenance_loop(self) -> None:
        try:
            await self.cooldowns.prune()
            await self.support_cooldowns.prune()
        except Exception:
            logger.exception("Cooldown cleanup failed; the loop will continue.")
            set_runtime_error("cooldown cleanup failed")

    @cooldown_maintenance_loop.before_loop
    async def before_cooldown_maintenance(self) -> None:
        await self.wait_until_ready()

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        await self.process_commands(message)
        content = message.content or ""
        if content.startswith(SETTINGS.bot_prefix):
            return

        # Special case: react to this user's short acknowledgements without a mention.
        # Ignore case and trailing punctuation, but require the entire message to match.
        if message.author.id == SPECIAL_OK_USER_ID:
            acknowledgement = content.strip().casefold().strip(" \\t\\r\\n.!?…")
            response_pool = SPECIAL_ACKNOWLEDGEMENT_RESPONSES.get(acknowledgement)
            if response_pool:
                await message.reply(
                    self._rng.choice(response_pool),
                    mention_author=False,
                    allowed_mentions=ALLOWED_MENTIONS,
                )
                return

        # This one keyword trigger is intentionally limited to the requested channel.
        # A separate cooldown prevents repeated phrase spam without using the normal
        # chat cooldown, which could otherwise replace a supportive reply with "wait".
        if is_mental_breakdown_trigger(getattr(message.channel, "id", None), content):
            support_key = f"support:channel:{message.channel.id}:user:{message.author.id}"
            if await self.support_cooldowns.try_acquire(support_key) > 0:
                return
            clean_content = strip_bot_mentions(content, self.user.id if self.user else 0)
            await self.handle_ai_message(
                message,
                clean_content,
                trigger="support_keyword",
                support_trigger=True,
            )
            return

        private = isinstance(message.channel, (discord.DMChannel, discord.GroupChannel))
        mentioned = self.user is not None and self.user in message.mentions
        replied = False if private or mentioned else await self.is_reply_to_hades(message)
        if not private and not mentioned and not replied:
            return
        clean_content = content.strip() if private else strip_bot_mentions(content, self.user.id if self.user else 0)
        trigger = "mention" if mentioned else "reply"
        await self.handle_ai_message(message, clean_content, trigger=trigger, direct_reply=replied)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"Use `{SETTINGS.bot_prefix}hades <message>` to talk to me.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
            return
        logger.error("Command error: %s", error)
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
    if not bot.media.image_configured_count:
        await ctx.reply("The portrait gallery is empty. Configure image URLs in the media library first.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
        return
    remaining = bot.media.cooldown_remaining(ctx.message, "image")
    if remaining > 0:
        await ctx.reply(f"The portrait gallery is resting. Try again in `{remaining:.0f}s`.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
        return
    sent = await bot.media.send_image(ctx.channel, ctx.message)
    if not sent:
        await ctx.reply("The portrait refused to appear. Check the configured image URLs and try again.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


@bot.command(name="gif", aliases=["hadesgif"])
async def gif_command(ctx: commands.Context) -> None:
    if not bot.media.configured_count:
        await ctx.reply("The performance library is empty. Configure GIF URLs in the media library first.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
        return
    remaining = bot.media.cooldown_remaining(ctx.message, "gif")
    if remaining > 0:
        await ctx.reply(f"The curtain needs a brief pause. Try another GIF in `{remaining:.0f}s`.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
        return
    sent = await bot.media.send_gif(ctx.channel, ctx.message)
    if not sent:
        await ctx.reply("The performance refused to load. Check the configured GIF URLs and try again.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


@bot.command(name="ping")
async def ping_command(ctx: commands.Context) -> None:
    latency = bot.latency
    latency_text = "unavailable" if latency == float("inf") else f"{round(latency * 1000)}ms"
    await ctx.reply(f"The connection is functioning. ⚡ `{latency_text}`.", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


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
    if ctx.guild and not (ctx.author.guild_permissions.manage_guild or ctx.author.guild_permissions.administrator):
        await ctx.reply("That information is for those managing the stage. 🎭", mention_author=False, allowed_mentions=ALLOWED_MENTIONS)
        return
    memory_count = await bot.hades_chat.memory.conversation_count()
    ready = bot.is_ready()
    latency_ms = f"{round(bot.latency * 1000)}ms" if bot.latency < float("inf") else "unavailable"
    discord_state = "OK" if ready else "NOT READY"
    gemini_state = "configured" if SETTINGS.gemini_api_key else "MISSING"
    token_state = "configured" if SETTINGS.discord_token else "MISSING"
    description = "\n".join([
        f"Discord connection: `{discord_state}`",
        f"Gemini API key: `{gemini_state}`",
        f"Discord token: `{token_state}`",
        f"Gemini model: `{SETTINGS.gemini_model}`",
        f"Gemini model hierarchy: `{' → '.join(bot.hades_chat.gemini.model_hierarchy())}`",
        f"Last successful model: `{bot.hades_chat.gemini.last_successful_model or 'not yet used'}`",
        f"Successful model fallbacks: `{bot.hades_chat.gemini.fallback_count}`",
        "Hades scope: `enforced`",
        f"Memory: `{memory_count}` active conversations",
        f"AI requests: `{bot.hades_chat.active_requests}/{SETTINGS.max_concurrent_requests}` active",
        f"Latency: `{latency_ms}`",
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
    hierarchy = " → ".join(bot.hades_chat.gemini.model_hierarchy())
    last_model = bot.hades_chat.gemini.last_successful_model or "not yet used"
    status_text = (
        f"Model: `{SETTINGS.gemini_model}`\n"
        f"Hierarchy: `{hierarchy}`\n"
        f"Last successful model: `{last_model}`\n"
        f"Fallbacks used: `{bot.hades_chat.gemini.fallback_count}`\n"
        f"Guilds: `{len(bot.guilds)}`\n"
        f"Memory: `{count}` active conversations\n"
        f"Requests: `{bot.hades_chat.active_requests}/{SETTINGS.max_concurrent_requests}` active\n"
        f"Total AI requests: `{bot.hades_chat.total_requests}`\n"
        f"Auto media: `mention / {SETTINGS.bot_prefix}hades`\n"
        f"GIFs: `{bot.media.configured_count}` external URLs\n"
        f"Images: `{bot.media.image_configured_count}` external URLs\n"
        f"Latency: `{'unavailable' if bot.latency == float('inf') else str(round(bot.latency * 1000)) + 'ms'}`"
    )
    await ctx.reply(embed=info_embed("🌙 Hades Status", status_text), mention_author=False, allowed_mentions=ALLOWED_MENTIONS)


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


def run() -> None:
    bot.run(SETTINGS.discord_token)
