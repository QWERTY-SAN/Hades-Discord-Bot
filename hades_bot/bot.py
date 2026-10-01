import logging
import random

import discord
from discord.ext import commands, tasks

from .chat import HadesChat
from .config import (
    BOT_PREFIX,
    DISCORD_TOKEN,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_CONCURRENT_REQUESTS,
    MAX_HISTORY,
    MAX_INPUT_CHARS,
    MAX_OUTPUT_TOKENS,
    MEMORY_PRUNE_INTERVAL,
    MEMORY_TTL_SECONDS,
    MAX_CONVERSATIONS,
    USER_COOLDOWN,
    COOLDOWN_PRUNE_INTERVAL,
    validate,
)
from .gemini_client import GeminiService
from .memory import ConversationMemory
from .utils import CooldownManager, split_message, strip_bot_mentions
from .web import update_discord_state


logger = logging.getLogger("hades-bot")

ALLOWED_MENTIONS = discord.AllowedMentions.none()

EMPTY_CALL_RESPONSES = (
    "You summoned me, little lamb. Speak.",
    "Yes, Administrator?",
    "You have my attention.",
    "Go on.",
    "What is it?",
    "I'm listening.",
)

COOLDOWN_RESPONSE = (
    "Patience, Administrator. Wait {remaining:.1f}s."
)

AI_FAILURE_RESPONSES = (
    "Tsk. The strings are resisting me. Try again shortly, little lamb.",
    "The strings are tangled. Give me a moment and try again.",
    "Something is interfering with the performance. Try again shortly.",
)

UNEXPECTED_FAILURE_RESPONSE = (
    "Something went wrong behind the curtain. Try again in a moment."
)


class HadesBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=BOT_PREFIX,
            intents=intents,
            help_command=None,
        )

        self.hades_chat = HadesChat(
            gemini=GeminiService(
                api_key=GEMINI_API_KEY,
                model=GEMINI_MODEL,
                max_output_tokens=MAX_OUTPUT_TOKENS,
            ),
            memory=ConversationMemory(
                max_messages=MAX_HISTORY,
                ttl_seconds=MEMORY_TTL_SECONDS,
                max_conversations=MAX_CONVERSATIONS,
            ),
        )

        self.cooldowns = CooldownManager(USER_COOLDOWN)
        self._started_at = None
        self._maintenance_started = False
        self._rng = random.Random()

    async def setup_hook(self) -> None:
        if not self._maintenance_started:
            self.maintenance_loop.start()
            self._maintenance_started = True

    def conversation_key(self, message: discord.Message) -> str:
        if isinstance(message.channel, discord.DMChannel):
            return f"dm:{message.author.id}"

        guild_id = message.guild.id if message.guild else "no-guild"

        return (
            f"guild:{guild_id}:"
            f"channel:{message.channel.id}:"
            f"user:{message.author.id}"
        )

    async def send_chunks(
        self,
        destination,
        text: str,
        reply_to: discord.Message | None = None,
    ) -> None:
        chunks = split_message(text)

        for index, chunk in enumerate(chunks):
            if index == 0 and reply_to is not None:
                await reply_to.reply(
                    chunk,
                    mention_author=False,
                    allowed_mentions=ALLOWED_MENTIONS,
                )
            else:
                await destination.send(
                    chunk,
                    allowed_mentions=ALLOWED_MENTIONS,
                )

    async def is_reply_to_hades(self, message: discord.Message) -> bool:
        reference = message.reference

        if (
            reference is None
            or reference.message_id is None
            or self.user is None
        ):
            return False

        resolved = reference.resolved

        if isinstance(resolved, discord.Message):
            return resolved.author.id == self.user.id

        try:
            referenced_message = await message.channel.fetch_message(
                reference.message_id
            )
        except (
            discord.NotFound,
            discord.Forbidden,
            discord.HTTPException,
        ):
            return False

        return referenced_message.author.id == self.user.id

    def _cooldown_key(self, message: discord.Message) -> str:
        return self.conversation_key(message)

    def _try_acquire_cooldown(self, message: discord.Message) -> float:
        return self.cooldowns.try_acquire(
            self._cooldown_key(message)
        )

    def _release_cooldown(self, message: discord.Message) -> None:
        self.cooldowns.release(
            self._cooldown_key(message)
        )

    async def handle_ai_message(
        self,
        message: discord.Message,
        content: str,
    ) -> None:
        content = content.strip()

        if len(content) > MAX_INPUT_CHARS:
            await message.reply(
                (
                    "That's quite a manuscript, little lamb. Keep the message "
                    f"under `{MAX_INPUT_CHARS}` characters."
                ),
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return

        remaining = self._try_acquire_cooldown(message)

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
        except RuntimeError as exc:
            self._release_cooldown(message)

            logger.warning(
                "AI request failed for user %s: %s",
                message.author.id,
                exc,
            )

            await message.reply(
                self._rng.choice(AI_FAILURE_RESPONSES),
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return
        except Exception:
            self._release_cooldown(message)

            logger.exception(
                "Unexpected AI handling failure"
            )

            await message.reply(
                UNEXPECTED_FAILURE_RESPONSE,
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return

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

        logger.warning(
            "Disconnected from Discord gateway; "
            "discord.py will attempt to reconnect."
        )

    async def on_resumed(self) -> None:
        logger.info("Discord session resumed.")

    async def on_ready(self) -> None:
        username = str(self.user) if self.user else None

        self._started_at = (
            self._started_at or discord.utils.utcnow()
        )

        logger.info(
            "Logged in as %s (%s)",
            self.user,
            self.user.id if self.user else "unknown",
        )
        logger.info(
            "Connected to %d guild(s)",
            len(self.guilds),
        )
        logger.info(
            "Gemini model: %s",
            GEMINI_MODEL,
        )
        logger.info(
            "Command prefix: %s",
            BOT_PREFIX,
        )
        logger.info(
            "Max concurrent Gemini requests: %d",
            MAX_CONCURRENT_REQUESTS,
        )
        logger.info(
            "Max input characters: %d",
            MAX_INPUT_CHARS,
        )

        update_discord_state(
            ready=True,
            user=username,
            guild_count=len(self.guilds),
        )

        await self.change_presence(
            status=discord.Status.online,
            activity=discord.CustomActivity(
                name="Pulling the strings",
            ),
        )

    @tasks.loop(seconds=MEMORY_PRUNE_INTERVAL)
    async def maintenance_loop(self) -> None:
        removed_memory = self.hades_chat.prune_memory()
        removed_cooldowns = self.cooldowns.prune(
            COOLDOWN_PRUNE_INTERVAL
        )

        if removed_memory or removed_cooldowns:
            logger.info(
                "Maintenance: removed %d expired conversations "
                "and %d stale cooldowns.",
                removed_memory,
                removed_cooldowns,
            )

    @maintenance_loop.before_loop
    async def before_maintenance(self) -> None:
        await self.wait_until_ready()

    @maintenance_loop.error
    async def maintenance_error(
        self,
        error: BaseException,
    ) -> None:
        logger.exception(
            "Maintenance loop failed: %s",
            error,
        )

    async def on_message(
        self,
        message: discord.Message,
    ) -> None:
        if message.author.bot:
            return

        await self.process_commands(message)

        if message.content.startswith(BOT_PREFIX):
            return

        is_dm = isinstance(
            message.channel,
            discord.DMChannel,
        )

        mentioned = (
            self.user is not None
            and self.user in message.mentions
        )

        replied_to_hades = False

        if not is_dm and not mentioned:
            replied_to_hades = await self.is_reply_to_hades(
                message
            )

        if not is_dm and not mentioned and not replied_to_hades:
            return

        if is_dm:
            content = message.content.strip()
        else:
            content = strip_bot_mentions(
                message.content,
                self.user.id if self.user else 0,
            )

        if not content:
            await message.reply(
                self._rng.choice(EMPTY_CALL_RESPONSES),
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return

        await self.handle_ai_message(
            message,
            content,
        )


async def hades_command(
    ctx: commands.Context,
    *,
    prompt: str | None = None,
) -> None:
    bot = ctx.bot

    if not isinstance(bot, HadesBot):
        return

    if not prompt:
        await ctx.reply(
            f"Usage: `{BOT_PREFIX}hades <message>`",
            mention_author=False,
            allowed_mentions=ALLOWED_MENTIONS,
        )
        return

    prompt = prompt.strip()

    if len(prompt) > MAX_INPUT_CHARS:
        await ctx.reply(
            (
                f"Keep your message under `{MAX_INPUT_CHARS}` "
                "characters, little lamb."
            ),
            mention_author=False,
            allowed_mentions=ALLOWED_MENTIONS,
        )
        return

    remaining = bot._try_acquire_cooldown(ctx.message)

    if remaining > 0:
        await ctx.reply(
            COOLDOWN_RESPONSE.format(remaining=remaining),
            mention_author=False,
            allowed_mentions=ALLOWED_MENTIONS,
        )
        return

    try:
        async with ctx.typing():
            reply = await bot.hades_chat.ask(
                bot.conversation_key(ctx.message),
                prompt,
            )
    except Exception:
        bot._release_cooldown(ctx.message)

        logger.exception(
            "%s%s failed",
            BOT_PREFIX,
            ctx.invoked_with or "hades",
        )

        await ctx.reply(
            "The strings are tangled. Try again in a moment.",
            mention_author=False,
            allowed_mentions=ALLOWED_MENTIONS,
        )
        return

    try:
        await bot.send_chunks(
            destination=ctx.channel,
            text=reply,
            reply_to=ctx.message,
        )
    except discord.HTTPException:
        logger.exception("Discord command response failed")


async def reset_command(ctx: commands.Context) -> None:
    bot = ctx.bot

    if not isinstance(bot, HadesBot):
        return

    bot.hades_chat.reset(
        bot.conversation_key(ctx.message)
    )

    await ctx.reply(
        "*Hades calmly gathers the strings.* "
        "There. Your conversation is forgotten.",
        mention_author=False,
        allowed_mentions=ALLOWED_MENTIONS,
    )


async def memory_command(ctx: commands.Context) -> None:
    bot = ctx.bot

    if not isinstance(bot, HadesBot):
        return

    key = bot.conversation_key(ctx.message)
    messages = bot.hades_chat.memory.message_count(key)

    await ctx.reply(
        (
            f"Your conversation memory: `{messages}` message(s).\n"
            f"Memory expires after "
            f"`{MEMORY_TTL_SECONDS // 3600}` hour(s)."
        ),
        mention_author=False,
        allowed_mentions=ALLOWED_MENTIONS,
    )


async def ping_command(ctx: commands.Context) -> None:
    bot = ctx.bot

    if not isinstance(bot, HadesBot):
        return

    latency = round(bot.latency * 1000)

    await ctx.reply(
        f"The connection is functioning. `{latency}ms`.",
        mention_author=False,
        allowed_mentions=ALLOWED_MENTIONS,
    )


async def status_command(ctx: commands.Context) -> None:
    bot = ctx.bot

    if not isinstance(bot, HadesBot):
        return

    if ctx.guild is not None and not (
        ctx.author.guild_permissions.manage_guild
        or ctx.author.guild_permissions.administrator
    ):
        await ctx.reply(
            "That information is for those managing the stage.",
            mention_author=False,
            allowed_mentions=ALLOWED_MENTIONS,
        )
        return

    await ctx.reply(
        (
            "**Hades Status**\n"
            f"Model: `{GEMINI_MODEL}`\n"
            f"Guilds: `{len(bot.guilds)}`\n"
            f"Memory: `{bot.hades_chat.memory.conversation_count()}` "
            "active conversations\n"
            f"Requests active: "
            f"`{bot.hades_chat.active_requests}/"
            f"{MAX_CONCURRENT_REQUESTS}`\n"
            f"Total AI requests: `{bot.hades_chat.total_requests}`\n"
            f"Latency: `{round(bot.latency * 1000)}ms`"
        ),
        mention_author=False,
        allowed_mentions=ALLOWED_MENTIONS,
    )


async def help_command(ctx: commands.Context) -> None:
    await ctx.reply(
        (
            "**Hades — Aether Gazer AI**\n\n"
            f"`{BOT_PREFIX}hades <message>` — Talk to Hades\n"
            f"`{BOT_PREFIX}ask <message>` — Same as `hades`\n"
            f"`{BOT_PREFIX}reset` / `{BOT_PREFIX}forget` / "
            f"`{BOT_PREFIX}clear` — Clear your conversation\n"
            f"`{BOT_PREFIX}memory` — Show your conversation-memory stats\n"
            f"`{BOT_PREFIX}ping` — Check Discord latency\n"
            f"`{BOT_PREFIX}status` — Show bot status (staff)\n"
            f"`{BOT_PREFIX}hadeshelp` / `{BOT_PREFIX}help` — "
            "Show this help\n\n"
            "Mention Hades or reply directly to one of her messages "
            "to talk to her."
        ),
        mention_author=False,
        allowed_mentions=ALLOWED_MENTIONS,
    )


def run() -> None:
    validate()

    bot = HadesBot()

    bot.add_command(
        commands.Command(
            hades_command,
            name="hades",
            aliases=["ask"],
        )
    )

    bot.add_command(
        commands.Command(
            reset_command,
            name="reset",
            aliases=["forget", "clear"],
        )
    )

    bot.add_command(
        commands.Command(
            memory_command,
            name="memory",
        )
    )

    bot.add_command(
        commands.Command(
            ping_command,
            name="ping",
        )
    )

    bot.add_command(
        commands.Command(
            status_command,
            name="status",
        )
    )

    bot.add_command(
        commands.Command(
            help_command,
            name="hadeshelp",
            aliases=["help"],
        )
    )

    try:
        bot.run(
            DISCORD_TOKEN,
            log_handler=None,
        )
    finally:
        update_discord_state(ready=False)
