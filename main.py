"""
The main file is providing events for guild,
commands and connection.

Events:
    - on_guild_join
    - on_application_command_error
    - on_connect
    - on_ready
"""


import time
import json
import os
from dotenv import load_dotenv
import discord


load_dotenv()
raijin_token = os.getenv("BOT_TOKEN")
intents = discord.Intents.all()
bot = discord.Bot(intents=intents)
DEFAULT_COLOR = 0x37266A


@bot.event
async def on_guild_join(guild):
    """
    Send a message when Raijin is joining a guild
    """
    file = discord.File(
        "res/images/avatar-wb.png", filename="avatar.png"
    )
    en_file = open('res/lang/en_EN.json', encoding="utf-8")
    messages = json.load(en_file)
    title = "<:raidenbird:1080897824440455288>  Raijin Discord Bot"
    welcoming = discord.Embed(
        title=title,
        description=messages['welcome'],
        color=DEFAULT_COLOR,
    )
    welcoming.set_thumbnail(url="attachment://avatar.png")
    welcoming.set_footer(text="Created and Developed by Makoto#7116")

    channel = discord.utils.get(guild.text_channels)
    if channel.permissions_for(guild.me).send_messages:
        await channel.send(embed=welcoming, file=file)
    else:
        await guild.owner.send(embed=welcoming, file=file)


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext,
    error: discord.DiscordException):
    """
    Send a message when an error appear on command call/execution
    """
    if isinstance(error, discord.ApplicationCommandError):
        local = time.localtime()
        current_time = time.strftime("%H:%M:%S", local)
        errors = discord.Embed(
            title="Error while executing the command",
            description=f"Please report this error below in our discord\
            server <:raidencry:1189307566606520501>\n`{error}`",
            color=0xFF0000,
        )
        errors.set_footer(text=f"Detected at {current_time} UTC")
        await ctx.respond(embed=errors)
        print("Error detected:", error)


@bot.event
async def on_connect():
    """
    Register new commands and sync modified commands with the API
    """
    await bot.sync_commands()


@bot.event
async def on_ready():
    """
    Send a message when the bot is ready
    """
    print("Raijin is Ready")


bot.load_extension("src.adventure.account")
bot.load_extension("src.help")


bot.run(raijin_token)
