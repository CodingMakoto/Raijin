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
from discord.ext import commands
import mysql.connector

from config.env import Database


load_dotenv()
raijin_token = os.getenv("BOT_TOKEN")
intents = discord.Intents.all()
bot = discord.Bot(intents=intents)
DEFAULT_COLOR = 0x37266A
ERROR_COLOR = 0xFF0000


@bot.event
async def on_guild_join(guild):
    """
    Send a message when Raijin is joining a guild
    """
    file = discord.File("res/images/raijin/avatar.png", filename="avatar.png")
    en_file = open("res/lang/en_EN.json", encoding="utf-8")
    messages = json.load(en_file)
    welcoming = discord.Embed(
        title=messages["guild"]["welcome"]["title"],
        description=messages["guild"]["welcome"]["details"],
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
async def on_connect():
    """
    Sync the commands when the bot is connected
    """
    await bot.sync_commands()


@bot.event
async def on_ready():
    """
    Send a message when the bot is ready
    """
    conn = None
    try:
        db = Database()
        conn = db.connect()
        await bot.change_presence(activity=discord.Game(name="Plane of Euthymia"))
        print("Ei is Ready")
    except mysql.connector.Error:
        print("Ei cannot connect to the database")
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()


@bot.event
async def on_application_command_error(
    ctx: discord.ApplicationContext, error: discord.DiscordException
):
    """
    Send a message when an error appear on command call
    """
    if not isinstance(error, commands.CommandOnCooldown):
        owner = await bot.fetch_user(577176157040934922)
        errors_message = discord.Embed(
            description=f"**An error occured with Ei** : `{error}`", color=ERROR_COLOR
        )
        await owner.send(embed=errors_message)

    if isinstance(error, (discord.ApplicationCommandError, mysql.connector.Error)):
        with open("res/lang/en_EN.json", encoding="utf-8") as en_file:
            messages = json.load(en_file)

        local = time.localtime()
        current_time = time.strftime("%H:%M:%S", local)
        errors = discord.Embed(
            title=messages["errors"]["commands"]["title"],
            description=messages["errors"]["commands"]["details"],
            color=ERROR_COLOR,
        )
        errors.set_footer(text=f"Detected at {current_time} UTC")
        await ctx.respond(embed=errors, ephemeral=True)

    if isinstance(error, commands.CommandOnCooldown):
        with open("res/lang/en_EN.json", encoding="utf-8") as en_file:
            messages = json.load(en_file)

        cooldown = round(error.retry_after)
        errors = discord.Embed(
            description=messages["errors"]["cooldown"].format(remaining_time=cooldown),
            color=ERROR_COLOR,
        )
        await ctx.respond(embed=errors, ephemeral=True)


bot.load_extension("src.account")
bot.load_extension("src.help")
bot.load_extension("src.adventure.profile")
bot.load_extension("src.adventure.quests")
bot.load_extension("src.adventure.astral")

bot.run(raijin_token)
