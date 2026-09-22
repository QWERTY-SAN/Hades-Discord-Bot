import logging

import discord
from discord.ext import commands, tasks

from .chat import HadesChat
from .config import (
    BOT_PREFIX,
    DISCORD_TOKEN,
    GROQ_API_KEY,
    GROQ_MODEL,
    MAX_CONCURRENT_REQUESTS,
    MAX_HISTORY,
    MAX_INPUT_CHARS,
    MAX_OUTPUT_TOKENS,
<<<<<<< HEAD
    MEMORY_PRUNE_INTERVAL,
=======
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505
    MEMORY_TTL_SECONDS,
    MAX_CONVERSATIONS,
    USER_COOLDOWN,
    COOLDOWN_PRUNE_INTERVAL,
    validate,
)
from .groq_client import GroqService
from .memory import ConversationMemory
from .utils import CooldownManager, split_message, strip_bot_mentions
from .web import update_discord_state


logger = logging.getLogger("hades-bot")
ALLOWED_MENTIONS = discord.AllowedMentions.none()

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
            groq=GroqService(
                api_key=GROQ_API_KEY,
                model=GROQ_MODEL,
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

    async def setup_hook(self) -> None:
        if not self._maintenance_started:
            self.maintenance_loop.start()
            self._maintenance_started = True

    def conversation_key(self, message: discord.Message) -> str:
        if isinstance(message.channel, discord.DMChannel):
            return f"dm:{message.author.id}"

        guild_id = message.guild.id if message.guild else "no-guild"
        return f"guild:{guild_id}:channel:{message.channel.id}:user:{message.author.id}"

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
<<<<<<< HEAD
=======

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
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505

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

    def _consume_cooldown(self, user_id: int) -> float:
        return self.cooldowns.consume(user_id)

    async def handle_ai_message(self, message: discord.Message, content: str) -> None:
        remaining = self._consume_cooldown(message.author.id)
        if remaining > 0:
            await message.reply(
                f"Patience, Administrator. Wait {remaining:.1f}s.",
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
<<<<<<< HEAD
            )
            return

        content = content.strip()
        if len(content) > MAX_INPUT_CHARS:
            await message.reply(
                (
                    "That's quite a manuscript, little lamb. Keep the message "
                    f"under `{MAX_INPUT_CHARS}` characters."
                ),
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
=======
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505
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
<<<<<<< HEAD
            logger.warning(
                "AI request failed for user %s: %s",
                message.author.id,
                exc,
            )
=======
            logger.warning("AI request failed for user %s: %s", message.author.id, exc)

>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505
            await message.reply(
                "Tsk. The strings are resisting me. Try again shortly, little lamb.",
                mention_author=False,
                allowed_mentions=ALLOWED_MENTIONS,
<<<<<<< HEAD
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

=======
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

>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505
    async def on_connect(self) -> None:
        logger.info("Connected to Discord gateway.")

    async def on_disconnect(self) -> None:
        update_discord_state(ready=False)
<<<<<<< HEAD
        logger.warning("Disconnected from Discord gateway; discord.py will attempt to reconnect.")
=======
        logger.warning("Disconnected from Discord gateway; reconnecting if possible.")
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505

    async def on_resumed(self) -> None:
        logger.info("Discord session resumed.")

    async def on_ready(self) -> None:
        username = str(self.user) if self.user else None
<<<<<<< HEAD
        self._started_at = self._started_at or discord.utils.utcnow()
=======
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505

        logger.info(
            "Logged in as %s (%s)",
            self.user,
            self.user.id if self.user else "unknown",
        )
        logger.info("Connected to %d guild(s)", len(self.guilds))
        logger.info("Groq model: %s", GROQ_MODEL)
        logger.info("Command prefix: %s", BOT_PREFIX)
<<<<<<< HEAD
<<<<<<< HEAD
        logger.info("Max concurrent Gemini requests: %d", MAX_CONCURRENT_REQUESTS)
<<<<<<< HEAD
=======
        logger.info("Max concurrent Groq requests: %d", MAX_CONCURRENT_REQUESTS)
>>>>>>> parent of 39d2903 (revert back to gemini 3.5-lite)
=======
        logger.info("Max concurrent Groq requests: %d", MAX_CONCURRENT_REQUESTS)
>>>>>>> parent of 39d2903 (revert back to gemini 3.5-lite)
        logger.info("Max input characters: %d", MAX_INPUT_CHARS)
=======
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505

        update_discord_state(
            ready=True,
            user=username,
            guild_count=len(self.guilds),
        )

        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name="Aether Gazer"),
        )

    @tasks.loop(seconds=900)
    async def maintenance_loop(self) -> None:
        removed_memory = self.hades_chat.prune_memory()
        removed_cooldowns = self.cooldowns.prune(COOLDOWN_PRUNE_INTERVAL)

        if removed_memory or removed_cooldowns:
            logger.info(
                "Maintenance: removed %d expired conversations and %d stale cooldowns.",
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

    remaining = bot._consume_cooldown(ctx.author.id)
    if remaining > 0:
        await ctx.reply(
            f"Patience, Administrator. Wait {remaining:.1f}s.",
            mention_author=False,
            allowed_mentions=ALLOWED_MENTIONS,
        )
        return

<<<<<<< HEAD
    if len(prompt) > MAX_INPUT_CHARS:
        await ctx.reply(
            f"Keep your message under `{MAX_INPUT_CHARS}` characters, little lamb.",
            mention_author=False,
            allowed_mentions=ALLOWED_MENTIONS,
        )
        return

=======
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505
    try:
        async with ctx.typing():
            reply = await bot.hades_chat.ask(
                bot.conversation_key(ctx.message),
<<<<<<< HEAD
                prompt.strip(),
=======
                prompt,
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505
            )

        await bot.send_chunks(
            destination=ctx.channel,
            text=reply,
            reply_to=ctx.message,
        )
    except Exception:
        logger.exception("%s%s failed", BOT_PREFIX, ctx.invoked_with or "hades")
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
<<<<<<< HEAD
        (
            f"Conversation memory: `{messages}` message(s) in this chat.\n"
            f"Active conversations: `{conversations}`.\n"
            f"Memory expires after `{MEMORY_TTL_SECONDS // 3600}` hour(s)."
        ),
        mention_author=False,
        allowed_mentions=ALLOWED_MENTIONS,
=======
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
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505
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
<<<<<<< HEAD
=======

>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505
    if not isinstance(bot, HadesBot):
        return

    await ctx.reply(
        (
            "**Hades Status**\n"
            f"Model: `{GROQ_MODEL}`\n"
            f"Guilds: `{len(bot.guilds)}`\n"
            f"Memory: `{bot.hades_chat.memory.conversation_count()}` active conversations\n"
<<<<<<< HEAD
            f"Requests active: `{bot.hades_chat.active_requests}/{MAX_CONCURRENT_REQUESTS}`\n"
            f"Total AI requests: `{bot.hades_chat.total_requests}`\n"
=======
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505
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
<<<<<<< HEAD
            f"`{BOT_PREFIX}ask <message>` — Same as `hades`\n"
            f"`{BOT_PREFIX}reset` / `{BOT_PREFIX}forget` / `{BOT_PREFIX}clear` — Clear your conversation\n"
            f"`{BOT_PREFIX}memory` — Show conversation-memory stats\n"
            f"`{BOT_PREFIX}ping` — Check Discord latency\n"
            f"`{BOT_PREFIX}status` — Show bot status\n"
            f"`{BOT_PREFIX}hadeshelp` / `{BOT_PREFIX}help` — Show this help\n\n"
            "Mention Hades or reply directly to one of her messages to talk to her."
=======
            f"`{BOT_PREFIX}reset` / `{BOT_PREFIX}forget` — Clear your conversation\n"
            f"`{BOT_PREFIX}memory` — Show conversation-memory stats\n"
            f"`{BOT_PREFIX}ping` — Check Discord latency\n"
            f"`{BOT_PREFIX}status` — Show bot status\n"
            f"`{BOT_PREFIX}hadeshelp` — Show this help\n\n"
            "You can also mention Hades or reply directly to one of her messages."
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505
        ),
        mention_author=False,
        allowed_mentions=ALLOWED_MENTIONS,
    )


def run() -> None:
    validate()
<<<<<<< HEAD
    bot = HadesBot()

    bot.add_command(commands.Command(hades_command, name="hades", aliases=["ask"]))
    bot.add_command(commands.Command(reset_command, name="reset", aliases=["forget", "clear"]))
    bot.add_command(commands.Command(memory_command, name="memory"))
    bot.add_command(commands.Command(ping_command, name="ping"))
    bot.add_command(commands.Command(status_command, name="status"))
    bot.add_command(commands.Command(help_command, name="hadeshelp", aliases=["help"]))
=======

    bot = HadesBot()

    bot.add_command(commands.Command(hades_command, name="hades"))
    bot.add_command(commands.Command(reset_command, name="reset"))
    bot.add_command(commands.Command(reset_command, name="forget"))
    bot.add_command(commands.Command(memory_command, name="memory"))
    bot.add_command(commands.Command(ping_command, name="ping"))
    bot.add_command(commands.Command(status_command, name="status"))
    bot.add_command(commands.Command(help_command, name="hadeshelp"))
>>>>>>> dddf6d19d3182cd9bdad89b51d129fc0e7f37505

    try:
        bot.run(DISCORD_TOKEN, log_handler=None)
    finally:
        update_discord_state(ready=False)
