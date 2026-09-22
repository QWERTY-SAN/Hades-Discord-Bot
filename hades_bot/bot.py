import logging

import discord
from discord.ext import commands

from .chat import HadesChat
from .config import (
    BOT_PREFIX,
    DISCORD_TOKEN,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_HISTORY,
    MAX_OUTPUT_TOKENS,
    USER_COOLDOWN,
    validate,
)
from .gemini_client import GeminiService
from .memory import ConversationMemory
from .utils import CooldownManager, split_message, strip_bot_mentions


logger = logging.getLogger("hades-bot")


class HadesBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=BOT_PREFIX,
            intents=intents,
            help_command=None,
        )

        memory = ConversationMemory(MAX_HISTORY)
        gemini = GeminiService(
            api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL,
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )

        self.hades_chat = HadesChat(
            gemini=gemini,
            memory=memory,
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
                )
            else:
                await destination.send(chunk)

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

        except Exception:
            logger.exception("AI request failed")

            await message.reply(
                "Tsk. Something went wrong behind the curtain. Try again in a moment.",
                mention_author=False,
            )

    async def setup_hook(self) -> None:
        logger.info("Hades bot setup complete.")

    async def on_ready(self) -> None:
        logger.info(
            "Logged in as %s (%s)",
            self.user,
            self.user.id if self.user else "unknown",
        )
        logger.info("Connected to %d guild(s)", len(self.guilds))
        logger.info("Gemini model: %s", GEMINI_MODEL)
        logger.info("Command prefix: %s", BOT_PREFIX)

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

        if not is_dm and not mentioned:
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
            )
            return

        await self.handle_ai_message(message, content)



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
        )
        return

    remaining = bot.cooldowns.consume(ctx.author.id)

    if remaining > 0:
        await ctx.reply(
            f"Patience, Administrator. Wait {remaining:.1f}s.",
            mention_author=False,
        )
        return

    key = bot.conversation_key(ctx.message)

    try:
        async with ctx.typing():
            reply = await bot.hades_chat.ask(key, prompt)

        await bot.send_chunks(
            destination=ctx.channel,
            text=reply,
            reply_to=ctx.message,
        )

    except Exception:
        logger.exception("h!hades failed")
        await ctx.reply(
            "The strings are tangled. Try again.",
            mention_author=False,
        )


async def reset_command(ctx: commands.Context) -> None:
    bot = ctx.bot

    if not isinstance(bot, HadesBot):
        return

    bot.hades_chat.reset(bot.conversation_key(ctx.message))

    await ctx.reply(
        "*Hades gathers the puppets' strings.* There. Your conversation has been reset.",
        mention_author=False,
    )


async def ping_command(ctx: commands.Context) -> None:
    bot = ctx.bot

    if not isinstance(bot, HadesBot):
        return

    latency = round(bot.latency * 1000)

    await ctx.reply(
        f"The connection is functioning. `{latency}ms`.",
        mention_author=False,
    )


async def help_command(ctx: commands.Context) -> None:
    await ctx.reply(
        (
            "**Hades — Aether Gazer AI**\n\n"
            f"`{BOT_PREFIX}hades <message>` — Talk to Hades\n"
            f"`{BOT_PREFIX}reset` — Reset your conversation memory\n"
            f"`{BOT_PREFIX}ping` — Check bot latency\n\n"
            "You can also mention me directly:\n"
            "`@Hades hello`"
        ),
        mention_author=False,
    )



def run() -> None:
    validate()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    bot = HadesBot()

    bot.add_command(commands.Command(hades_command, name="hades"))
    bot.add_command(commands.Command(reset_command, name="reset"))
    bot.add_command(commands.Command(ping_command, name="ping"))
    bot.add_command(commands.Command(help_command, name="hadeshelp"))

    bot.run(DISCORD_TOKEN, log_handler=None)
