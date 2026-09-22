import os
import asyncio
import time
from collections import defaultdict, deque

import discord
from discord.ext import commands
from dotenv import load_dotenv
from groq import AsyncGroq


load_dotenv()


# =========================
# CONFIG
# =========================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

PREFIX = os.getenv("BOT_PREFIX", "h!")

MAX_HISTORY = int(
    os.getenv("MAX_HISTORY", "16")
)

MAX_OUTPUT_TOKENS = int(
    os.getenv("MAX_OUTPUT_TOKENS", "768")
)

USER_COOLDOWN = float(
    os.getenv("USER_COOLDOWN", "2.0")
)


# =========================
# CLIENTS
# =========================

groq = AsyncGroq(
    api_key=GROQ_API_KEY
)


# =========================
# DISCORD SETUP
# =========================

intents = discord.Intents.default()

intents.message_content = True
intents.guild_messages = True
intents.dm_messages = True


bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents
)


# =========================
# MEMORY
# =========================

memory = defaultdict(
    lambda: deque(
        maxlen=MAX_HISTORY
    )
)


cooldowns = {}


SYSTEM_PROMPT = """
You are Hades from Aether Gazer.

Roleplay as Hades:
- Elegant
- Calm
- Mysterious
- Confident
- Slightly teasing
- Speaks naturally

Do not mention that you are an AI.
Stay in character.
"""


# =========================
# HELPERS
# =========================

def split_message(text, limit=2000):
    return [
        text[i:i + limit]
        for i in range(
            0,
            len(text),
            limit
        )
    ]


def can_use(user_id):

    now = time.time()

    last = cooldowns.get(user_id)

    if last:

        if now - last < USER_COOLDOWN:
            return False

    cooldowns[user_id] = now

    return True



async def ask_hades(user_id, message):

    history = list(
        memory[user_id]
    )


    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


    messages.extend(history)


    messages.append(
        {
            "role": "user",
            "content": message
        }
    )


    response = await groq.chat.completions.create(

        model=GROQ_MODEL,

        messages=messages,

        max_tokens=MAX_OUTPUT_TOKENS

    )


    answer = (
        response
        .choices[0]
        .message
        .content
    )


    memory[user_id].append(
        {
            "role": "user",
            "content": message
        }
    )


    memory[user_id].append(
        {
            "role": "assistant",
            "content": answer
        }
    )


    return answer



# =========================
# EVENTS
# =========================

@bot.event
async def on_ready():

    print(
        f"Logged in as {bot.user}"
    )

    print(
        f"Connected to {len(bot.guilds)} servers"
    )



@bot.event
async def on_message(message):

    if message.author.bot:
        return


    # IMPORTANT:
    # Allows h! commands to work

    await bot.process_commands(
        message
    )


    content = message.content.strip()


    mentioned = (
        bot.user
        in message.mentions
    )


    replied = False


    if message.reference:

        try:

            replied_message = (
                await message.channel.fetch_message(
                    message.reference.message_id
                )
            )

            if replied_message.author == bot.user:
                replied = True

        except:
            pass



    if not mentioned and not replied:
        return



    if not can_use(
        message.author.id
    ):

        return await message.reply(
            "Please wait a moment."
        )



    # remove mention

    content = content.replace(
        f"<@{bot.user.id}>",
        ""
    ).strip()


    if not content:

        content = "Hello Hades."



    try:

        async with message.channel.typing():

            reply = await ask_hades(
                message.author.id,
                content
            )


        for part in split_message(reply):

            await message.reply(
                part
            )


    except Exception as e:

        print(
            "AI ERROR:",
            e
        )

        await message.reply(
            "Something went wrong."
        )



# =========================
# COMMANDS
# =========================


@bot.command()
async def ping(ctx):

    await ctx.send(
        f"Pong! {round(bot.latency * 1000)}ms"
    )



@bot.command()
async def hades(ctx, *, text):

    if not can_use(
        ctx.author.id
    ):

        return await ctx.send(
            "Please wait."
        )


    async with ctx.typing():

        reply = await ask_hades(
            ctx.author.id,
            text
        )


    for part in split_message(reply):

        await ctx.send(
            part
        )



@bot.command(
    aliases=["clear"]
)
async def reset(ctx):

    memory.pop(
        ctx.author.id,
        None
    )

    await ctx.send(
        "Your memories with Hades have been cleared."
    )



@bot.command(
    aliases=["help"]
)
async def hadeshelp(ctx):

    await ctx.send(
        """
**Hades Commands**

`h!hades <message>`
Talk with Hades.

`h!ping`
Check bot latency.

`h!reset`
Clear your conversation.

You can also mention me:

`@Hades hello`
        """
    )



# =========================
# START
# =========================

if not DISCORD_TOKEN:

    raise RuntimeError(
        "Missing DISCORD_TOKEN"
    )


if not GROQ_API_KEY:

    raise RuntimeError(
        "Missing GROQ_API_KEY"
    )


bot.run(
    DISCORD_TOKEN
)