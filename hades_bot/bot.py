import logging

import discord
from discord.ext import commands

from .chat import HadesChat
from .config import (
    BOT_PREFIX,
    DISCORD_TOKEN,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_CONCURRENT_REQUESTS,
    MAX_HISTORY,
    MAX_OUTPUT_TOKENS,
    MEMORY_TTL_SECONDS,
    MAX_CONVERSATIONS,
    USER_COOLDOWN,
    validate,
)
from .gemini_client import GeminiService
from .memory import ConversationMemory
from .utils import CooldownManager, split_message, strip_bot_mentions
from .web import update_discord_state


logger = logging.getLogger("hades-bot")

ALLOWED_MENTIONS = discord.AllowedMentions.none()


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

        if reference is None or reference.message_id is None or self.user is None:
            return False

        resolved = reference.resolved

        if isinstance(resolved, discord.Message):
            return resolved.author.id == self.user.id

        try:
            referenced_message = await message.channel.fetch_message(
                reference.message_id
            )
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return False

        return referenced_message.author.id == self.user.id

    async def handle_ai_message(
        self,
        message: discord.Message,
        content: str,
    ) -> None:
        remaining = self.cooldowns.consume(message.author.id)

        if remaining > 0:
            await message.reply(
                f"Patience, Administrator. Wait {remaining:.1f}s.",
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return

        key = self.conversation_key(message)

        try:
            async with message.channel.typing():
                reply = await self.hades_chat.ask(key, content)

            await self.send_chunks(
                destination=message.channel,
                text=reply,
                reply_to=message,
            )

        except RuntimeError as exc:
            logger.warning("AI request failed for user %s: %s", message.author.id, exc)

            await message.reply(
                "Tsk. The strings are resisting me. Try again shortly, little lamb.",
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )

        except discord.HTTPException:
            logger.exception("Discord send failed")

        except Exception:
            logger.exception("Unexpected AI handling failure")

            await message.reply(
                "Something went wrong behind the curtain. Try again in a moment.",
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )

    async def on_connect(self) -> None:
        logger.info("Connected to Discord gateway.")

    async def on_disconnect(self) -> None:
        update_discord_state(ready=False)
        logger.warning("Disconnected from Discord gateway; reconnecting if possible.")

    async def on_resumed(self) -> None:
        logger.info("Discord session resumed.")

    async def on_ready(self) -> None:
        username = str(self.user) if self.user else None

        logger.info(
            "Logged in as %s (%s)",
            self.user,
            self.user.id if self.user else "unknown",
        )
        logger.info("Connected to %d guild(s)", len(self.guilds))
        logger.info("Gemini model: %s", GEMINI_MODEL)
        logger.info("Command prefix: %s", BOT_PREFIX)
        logger.info("Max concurrent Gemini requests: %d", MAX_CONCURRENT_REQUESTS)

        update_discord_state(
            ready=True,
            user=username,
            guild_count=len(self.guilds),
        )

        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name="Aether Gazer"),
        )

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        await self.process_commands(message)

        if message.content.startswith(BOT_PREFIX):
            return

        is_dm = isinstance(message.channel, discord.DMChannel)
        mentioned = self.user is not None and self.user in message.mentions
        replied_to_hades = False

        if not is_dm and not mentioned:
            replied_to_hades = await self.is_reply_to_hades(message)

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
                "You summoned me, little lamb. Speak.",
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
            )
            return

        await self.handle_ai_message(message, content)


async def hades_command(ctx: commands.Context, *, prompt: str | None = None) -> None:
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

    remaining = bot.cooldowns.consume(ctx.author.id)

    if remaining > 0:
        await ctx.reply(
            f"Patience, Administrator. Wait {remaining:.1f}s.",
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

        await bot.send_chunks(
            destination=ctx.channel,
            text=reply,
            reply_to=ctx.message,
        )

    except Exception:
        logger.exception("h!hades failed")
        await ctx.reply(
            "The strings are tangled. Try again in a moment.",
            mention_author=False,
            allowed_mentions=ALLOWED_MENTIONS,
        )


async def reset_command(ctx: commands.Context) -> None:
    bot = ctx.bot

    if not isinstance(bot, HadesBot):
        return

    bot.hades_chat.reset(bot.conversation_key(ctx.message))

    await ctx.reply(
        "*Hades calmly gathers the strings.* There. Your conversation is forgotten.",
        mention_author=False,
        allowed_mentions=ALLOWED_MENTIONS,
    )


async def memory_command(ctx: commands.Context) -> None:
    bot = ctx.bot

    if not isinstance(bot, HadesBot):
        return

    key = bot.conversation_key(ctx.message)
    messages = bot.hades_chat.memory.message_count(key)
    conversations = bot.hades_chat.memory.conversation_count()

    await ctx.reply(
        (
            f"Conversation memory: `{messages}` message(s) in this chat.\n"
            f"Active conversations: `{conversations}`."
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

    await ctx.reply(
        (
            "**Hades Status**\n"
            f"Model: `{GEMINI_MODEL}`\n"
            f"Guilds: `{len(bot.guilds)}`\n"
            f"Memory: `{bot.hades_chat.memory.conversation_count()}` active conversations\n"
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
            f"`{BOT_PREFIX}reset` / `{BOT_PREFIX}forget` — Clear your conversation\n"
            f"`{BOT_PREFIX}memory` — Show conversation-memory stats\n"
            f"`{BOT_PREFIX}ping` — Check Discord latency\n"
            f"`{BOT_PREFIX}status` — Show bot status\n"
            f"`{BOT_PREFIX}hadeshelp` — Show this help\n\n"
            "You can also mention Hades or reply directly to one of her messages."
        ),
        mention_author=False,
        allowed_mentions=ALLOWED_MENTIONS,
    )


def run() -> None:
    validate()

    bot = HadesBot()

    bot.add_command(commands.Command(hades_command, name="hades"))
    bot.add_command(commands.Command(reset_command, name="reset"))
    bot.add_command(commands.Command(reset_command, name="forget"))
    bot.add_command(commands.Command(memory_command, name="memory"))
    bot.add_command(commands.Command(ping_command, name="ping"))
    bot.add_command(commands.Command(status_command, name="status"))
    bot.add_command(commands.Command(help_command, name="hadeshelp"))

    try:
        bot.run(DISCORD_TOKEN, log_handler=None)
    finally:
        update_discord_state(ready=False)
