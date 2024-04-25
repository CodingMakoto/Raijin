"""
The main file is providing events for guild,
commands and connection.

Events:
    - on_guild_join
    - on_command_error
    - on_connect
    - on_ready
"""


import discord


intents = discord.Intents.all()
bot = discord.Bot(intents=intents)


DEFAULT_COLOR = 0x37266A


@bot.event
async def on_guild_join(guild):
    """
    Send a message when Raijin is joining a guild
    """
    file = discord.File(
        "images/avatar-wb.png", filename="avatar.png"
    )
    title = "<:raidenbird:1080897824440455288>  Raijin Discord Bot"
    welcoming = discord.Embed(
        title=title,
        description="So... you want to start a new adventure with me ?\n\n\
        > ・ Raijin Discord Bot is an Unofficial Genshin Impact \
        Discord Bot using ONLY Slash Commands\n> ・ I can start the adventure\
        for you with `account start`\n> ・ To end the adventure with me use \
        `/account end`\n> ・ When your account is created use `/story mode`\
        and enjoy the adventure <:raidenangry:1080897820854329376>\n\
        > ・ During your adventure you can fight bosses, recover your health with Archons Statues,\
        fight hilichurls, discover daily quests and more...\n> ・ I let you discover that by yourself\
        using `/help` <:raidenlaugh:1080898399336931429>\n> ・ You have more\
        questions ? Well then I let you enter in Raijin City ⚡ :\
        https://discord.gg/2AePNcphrs\n\n<:beta:1233039955631276172> **Warning**: Currently \
        in **BETA** version, some commands may not\
        work as expected",
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
    Send a message when an error appear on command call
    """
    if isinstance(error, discord.ApplicationCommandError):
        errors = discord.Embed(
            title="There was an error while executing command",
            description=f"Error: `{error}`",
            color=DEFAULT_COLOR,
        )
        await ctx.respond(embed=errors)


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
    print("Raijin Beta is Ready")


bot.load_extension("help")
bot.load_extension("personal")
bot.load_extension("story")
bot.load_extension("music")
bot.load_extension("fetch")


bot.run("TOKEN")
