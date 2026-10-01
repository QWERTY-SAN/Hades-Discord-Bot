import logging
import random

import discord
from discord.ext import commands, tasks

from .chat import HadesChat
from .config import SETTINGS
from .gemini_client import AIServiceError, GeminiService
from .memory import ConversationMemory
from .scope import is_hades_scope_allowed, off_topic_response
from .utils import CooldownManager, sanitize_model_output, split_message, strip_bot_mentions
from .web import update_discord_state

logger = logging.getLogger("hades-bot")
ALLOWED_MENTIONS = discord.AllowedMentions.none()

EMPTY_CALL_RESPONSES = (
    "You summoned me, little lamb. Speak. 🌙",
    "Yes, Administrator? 😏",
    "You have my attention. ✨",
    "Go on. 🎭",
    "What is it? 🕯️",
    "I'm listening. 🌙",
)
COOLDOWN_RESPONSE = "Patience, Administrator. ⏳ Wait {remaining:.1f}s."
QUEUE_FAILURE_RESPONSE = "The response queue is full. ⚠️ Try again in a moment."
AI_FAILURE_RESPONSES = (
    "Tsk. The strings are resisting me. 🪢 Try again shortly, little lamb.",
    "The strings are tangled. 🪢 Give me a moment and try again.",
    "Something is interfering with the performance. ⚡ Try again shortly.",
)
UNEXPECTED_FAILURE_RESPONSE = "Something went wrong behind the curtain. 🎭 Try again in a moment."


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
            gemini=GeminiService(),
            memory=ConversationMemory(
                max_history=SETTINGS.max_history,
                ttl_seconds=SETTINGS.memory_ttl_seconds,
                max_conversations=SETTINGS.max_conversations,
            ),
        )
        self.cooldowns = CooldownManager(SETTINGS.user_cooldown)
        self._rng = random.SystemRandom()
        self._maintenance_started = False

    async def setup_hook(self) -> None:
        if not self._maintenance_started:
            self.maintenance_loop.start()
            self._maintenance_started = True

    async def close(self) -> None:
        if self.maintenance_loop.is_running():
            self.maintenance_loop.cancel()
        await self.hades_chat.close()
        await super().close()

    def conversation_key(self, message: discord.Message) -> str:
        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)):
            return f"dm:{message.author.id}"
        guild_id = message.guild.id if message.guild else "no-guild"
        return (
            f"guild:{guild_id}:"
            f"channel:{message.channel.id}:"
            f"user:{message.author.id}"
        )

    async def send_chunks(self, destination, text: str, reply_to: discord.Message | None = None) -> None:
        for index, chunk in enumerate(split_message(text)):
            if index == 0 and reply_to is not None:
                await reply_to.reply(
                    chunk,
                    mention_author=False,
                    allowed_mentions=ALLOWED_MENTIONS,
                )
            else:
                await destination.send(chunk, allowed_mentions=ALLOWED_MENTIONS)

    async def is_reply_to_hades(self, message: discord.Message) -> bool:
        reference = message.reference
        if reference is None or reference.message_id is None or self.user is None:
            return False

        resolved = reference.resolved
        if isinstance(resolved, discord.Message):
            return resolved.author.id == self.user.id

        try:
            referenced_message = await message.channel.fetch_message(reference.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return False
        return referenced_message.author.id == self.user.id

    def _cooldown_key(self, message: discord.Message) -> str:
        return self.conversation_key(message)

    async def _try_acquire_cooldown(self, message: discord.Message) -> float:
        return await self.cooldowns.try_acquire(self._cooldown_key(message))

    async def _release_cooldown(self, message: discord.Message) -> None:
        await self.cooldowns.release(self._cooldown_key(message))

    async def handle_ai_message(self, message: discord.Message, content: str) -> None:
        content = content.strip()
        if not content:
            await message.reply(
                self._rng.choice(EMPTY_CALL_RESPONSES),
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return

        if SETTINGS.strict_aether_topic and not is_hades_scope_allowed(content):
            await message.reply(
                off_topic_response(),
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return

        if len(content) > SETTINGS.max_input_chars:
            await message.reply(
                (
                    "That's quite a manuscript, little lamb. 📜 Keep the message "
                    f"under `{SETTINGS.max_input_chars:,}` characters."
                ),
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return

        remaining = await self._try_acquire_cooldown(message)
        if remaining > 0:
            await message.reply(
                COOLDOWN_RESPONSE.format(remaining=remaining),
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return

        try:
            async with message.channel.typing():
                reply = await self.hades_chat.ask(
                    self.conversation_key(message),
                    content,
                )
        except AIServiceError as exc:
            await self._release_cooldown(message)
            logger.warning("Gemini failure for user %s: %s", message.author.id, exc)
            await message.reply(
                exc.user_message,
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return
        except RuntimeError as exc:
            await self._release_cooldown(message)
            logger.warning("AI queue failure for user %s: %s", message.author.id, exc)
            await message.reply(
                QUEUE_FAILURE_RESPONSE,
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return
        except Exception:
            await self._release_cooldown(message)
            logger.exception("Unexpected AI handling failure")
            await message.reply(
                UNEXPECTED_FAILURE_RESPONSE,
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return

        reply = sanitize_model_output(reply)
        try:
            await self.send_chunks(
                destination=message.channel,
                text=reply,
                reply_to=message,
            )
        except discord.HTTPException:
            logger.exception("Discord send failed")

    async def on_connect(self) -> None:
        logger.info("Connected to Discord gateway.")

    async def on_disconnect(self) -> None:
        update_discord_state(ready=False)
        logger.warning("Disconnected from Discord gateway; reconnecting.")

    async def on_resumed(self) -> None:
        logger.info("Discord session resumed.")

    async def on_ready(self) -> None:
        username = str(self.user) if self.user else None
        logger.info("Logged in as %s (%s)", self.user, self.user.id if self.user else "unknown")
        logger.info("Connected to %d guild(s)", len(self.guilds))
        logger.info("Gemini model: %s", SETTINGS.gemini_model)
        logger.info("Gemini thinking level: %s", SETTINGS.gemini_thinking_level)
        logger.info("Command prefix: %s", SETTINGS.bot_prefix)
        logger.info("Strict Aether-Gazer scope: %s", SETTINGS.strict_aether_topic)
        update_discord_state(ready=True, user=username, guild_count=len(self.guilds))
        await self.change_presence(status=discord.Status.online, activity=None)

    @tasks.loop(seconds=SETTINGS.memory_prune_interval)
    async def maintenance_loop(self) -> None:
        removed_memory = await self.hades_chat.prune_memory()
        removed_cooldowns = await self.cooldowns.prune(SETTINGS.cooldown_prune_interval)
        if removed_memory or removed_cooldowns:
            logger.info(
                "Maintenance: removed %d conversations and %d stale cooldowns.",
                removed_memory,
                removed_cooldowns,
            )

    @maintenance_loop.before_loop
    async def before_maintenance(self) -> None:
        await self.wait_until_ready()

    @maintenance_loop.error
    async def maintenance_error(self, error: BaseException) -> None:
        logger.exception("Maintenance loop failed: %s", error)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        await self.process_commands(message)
        content = message.content or ""
        if content.startswith(SETTINGS.bot_prefix):
            return

        is_private = isinstance(message.channel, (discord.DMChannel, discord.GroupChannel))
        mentioned = self.user is not None and self.user in message.mentions

        replied_to_hades = False
        if not is_private and not mentioned:
            replied_to_hades = await self.is_reply_to_hades(message)
        if not is_private and not mentioned and not replied_to_hades:
            return

        if is_private:
            clean_content = content.strip()
        else:
            clean_content = strip_bot_mentions(content, self.user.id if self.user else 0)

        await self.handle_ai_message(message, clean_content)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(
                f"Use `{SETTINGS.bot_prefix}hades <message>` to talk to me.",
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"Patience, Administrator. Wait `{error.retry_after:.1f}s`.",
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return
        logger.exception("Command error in %s: %s", getattr(ctx.command, "qualified_name", "unknown"), error)
        await ctx.reply(
            "Something went wrong behind the curtain. Try again in a moment.",
            mention_author=False,
            allowed_mentions=ALLOWED_MENTIONS,
        )


bot = HadesBot()


@bot.command(name="hades", aliases=["ask"])
async def hades_command(ctx: commands.Context, *, prompt: str | None = None) -> None:
    if not prompt:
        await ctx.reply(
            f"Usage: `{SETTINGS.bot_prefix}hades <message>`",
            mention_author=False,
            allowed_mentions=ALLOWED_MENTIONS,
        )
        return
    await bot.handle_ai_message(ctx.message, prompt.strip())


@bot.command(name="reset", aliases=["forget", "clear"])
async def reset_command(ctx: commands.Context) -> None:
    key = bot.conversation_key(ctx.message)
    await bot.hades_chat.reset(key)
    await bot.cooldowns.release(key)
    await ctx.reply(
        "*Hades calmly gathers the strings.* 🪢 There. Your conversation is forgotten.",
        mention_author=False,
        allowed_mentions=ALLOWED_MENTIONS,
    )


@bot.command(name="memory")
async def memory_command(ctx: commands.Context) -> None:
    key = bot.conversation_key(ctx.message)
    messages = await bot.hades_chat.memory.message_count(key)
    await ctx.reply(
        f"Your conversation memory: `{messages}` message(s).\n"
        f"Memory expires after `{SETTINGS.memory_ttl_seconds // 3600}` hour(s).",
        mention_author=False,
        allowed_mentions=ALLOWED_MENTIONS,
    )


@bot.command(name="ping")
async def ping_command(ctx: commands.Context) -> None:
    latency = round(bot.latency * 1000)
    await ctx.reply(
        f"The connection is functioning. ⚡ `{latency}ms`.",
        mention_author=False,
        allowed_mentions=ALLOWED_MENTIONS,
    )


@bot.command(name="status")
async def status_command(ctx: commands.Context) -> None:
    if ctx.guild is not None and not (
        ctx.author.guild_permissions.manage_guild
        or ctx.author.guild_permissions.administrator
    ):
        await ctx.reply(
            "That information is for those managing the stage. 🎭",
            mention_author=False,
            allowed_mentions=ALLOWED_MENTIONS,
        )
        return
    memory_count = await bot.hades_chat.memory.conversation_count()
    await ctx.reply(
        "**🌙 Hades Status**\n"
        f"Model: `{SETTINGS.gemini_model}`\n"
        f"Guilds: `{len(bot.guilds)}`\n"
        f"Memory: `{memory_count}` active conversations\n"
        f"Requests active: `{bot.hades_chat.active_requests}/{SETTINGS.max_concurrent_requests}`\n"
        f"Total AI requests: `{bot.hades_chat.total_requests}`\n"
        f"Latency: `{round(bot.latency * 1000)}ms`",
        mention_author=False,
        allowed_mentions=ALLOWED_MENTIONS,
    )


@bot.command(name="hadeshelp", aliases=["help"])
async def help_command(ctx: commands.Context) -> None:
    prefix = SETTINGS.bot_prefix
    await ctx.reply(
        "**🌙 Hades — Aether Gazer AI**\n\n"
        f"`{prefix}hades <message>` — Talk to Hades\n"
        f"`{prefix}ask <message>` — Same as `hades`\n"
        f"`{prefix}reset` / `{prefix}forget` / `{prefix}clear` — Clear your conversation\n"
        f"`{prefix}memory` — Show your current conversation memory\n"
        f"`{prefix}ping` — Check Discord latency\n"
        f"`{prefix}status` — Show bot status (staff)\n"
        f"`{prefix}hadeshelp` / `{prefix}help` — Show this help\n\n"
        "Mention Hades, message her directly, or reply to one of her messages. ✨",
        mention_author=False,
        allowed_mentions=ALLOWED_MENTIONS,
    )


def run() -> None:
    bot.run(SETTINGS.discord_token, reconnect=True)
