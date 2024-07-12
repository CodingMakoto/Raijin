"""
The music file is providing commands to
play/pause/stop/shuffle music of Inazuma from
Genshin Impact.

Commands:
    - play
    - pause
    - next
    - shuffle (automatic)
    - stop
"""


import discord
from discord import SlashCommandGroup

import random
import sys
import os
import asyncio
import json
import audioread
import ffmpeg
from mutagen.mp3 import MP3
import mysql.connector

sys.path.append("..")
from sql.fetch import *


class MusicDisabled(discord.ui.View):
    """
    Music Disabled class is made to ensure that next and shuffle
    buttons are disabled for every music
    They are empty because they are disabled all the time
    """
    def __init__(self, musiccog, context):
        discord.ui.View.__init__(self, timeout=None)
        self.musiccog = musiccog
        self.context = context

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏯️")
    async def play_pause_callback(self, button, interaction):
        button.disabled = False
        await self.musiccog.m_pause(self.context)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏹️")
    async def stop_callback(self, button, interaction):
        button.disabled = True
        await self.musiccog.m_stop(self.context)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(style=discord.ButtonStyle.secondary, disabled=True, emoji="⏭️")
    async def next_callback(self):
        pass

    @discord.ui.button(style=discord.ButtonStyle.secondary, disabled=True, emoji="🔀")
    async def shuffle_callback(self):
        pass


class MusicPlay(discord.ui.View):
    """
    Music Play is the normal class for the play function buttons containing :
        - play, pause, next and shuffle functions
    This class is called for the normal player only
    """
    def __init__(self, musiccog, context):
        discord.ui.View.__init__(self, timeout=None)
        self.musiccog = musiccog
        self.context = context

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏯️")
    async def play_pause_callback(self, button, interaction):
        button.disabled = False
        await self.musiccog.m_pause(self.context)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏹️")
    async def stop_callback(self, button, interaction):
        button.disabled = True
        await self.musiccog.m_stop(self.context)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏭️")
    async def next_callback(self, button, interaction):
        button.disabled = False
        await interaction.message.delete()
        await self.musiccog.m_next(self.context)

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="🔀")
    async def shuffle_callback(self, button, interaction):
        button.disabled = True
        await interaction.message.delete()
        await self.musiccog.m_shuffle(self.context)


class Music(discord.Cog):
    """
    Music Cog is the main function to play, resume, stop and shuffle music
    The default bitrate is 128pbs and the shuffle command is playing
    automatically music
    """
    def __init__(self, bot):
        self.bot = bot
        self.default_color = 0x37266A
        self.fr_FR_file = open(os.path.dirname(__file__) + '/../res/lang/fr_FR.json')
        self.en_EN_file = open(os.path.dirname(__file__) + '/../res/lang/en_EN.json')
        self.fr_FR = json.load(self.fr_FR_file)
        self.en_EN = json.load(self.en_EN_file)
        self.mydb = Fetch(self.bot).setInit()
        self.cursor = self.mydb.cursor()


    dj = SlashCommandGroup(
        "dj", "The commands about DJ Raijin"
    )

    @dj.command(name="raijin", description="🎧 Listen to Inazuma Music")
    async def m_start(self, ctx):
        self.mydb.ping(reconnect=True)

        vc = ctx.voice_client
        FFMPEG_OPTIONS = {'options': '-vn -loglevel quiet'}

        lang = Fetch(self.bot).getLang(self, self.cursor, ctx.author.id, ctx.guild.id)

        if lang == "Français":
            list = self.fr_FR
        else:
            list = self.en_EN
        if ctx.author.voice:
            if not vc:
                vc = await ctx.author.voice.channel.connect()
            if ctx.author.voice.channel.id == vc.channel.id:
                if ctx.voice_client.is_playing():
                    warning = discord.Embed(description="<:raidenangry:1080897820854329376> \
                        Raijin is already playing a song, use \
                        : `/music next` to listen to another song", color=self.default_color)
                    await ctx.respond(embed=warning, ephemeral=True)
                else:
                    choice = random.choice(os.listdir("res/tracks/"))
                    song = discord.FFmpegOpusAudio("res/tracks/" + choice, bitrate=64, **FFMPEG_OPTIONS)
                    title = choice.replace(".mp3", "")

                    if not song:
                        warning = discord.Embed(description="<:raidenangry:1080897820854329376> \
                            An error occured with the song, \
                            please retry later", color=self.default_color)
                        await ctx.respond(embed=warning, ephemeral=True)

                    def duration(length):
                        mins = length // 60
                        length %= 60
                        seconds = length
                        return mins, seconds

                    with audioread.audio_open(f"res/tracks/{choice}") as f:
                        total = f.duration
                        mins, seconds = duration(int(total))

                    mp3 = MP3(f"res/tracks/{choice}")
                    bitrate = mp3.info.bitrate / 1000

                    file = discord.File("res/images/rote.jpg", filename="rote.jpg")
                    info = discord.Embed(
                        title=title,
                        description=f"・**Duration**: \
                        `{mins}:{seconds}`" + f"\n・**Bitrate**: `{bitrate}` \
                        Kbps\n・**Album**: Realm of Tranquil Eternity",
                        color=self.default_color
                    )
                    info.set_image(url="attachment://rote.jpg")
                    info.set_footer(text="By Yu-Peng Chen and HOYO-MIX")

                    await ctx.respond(embed=info, file=file, view=MusicPlay(self, ctx))
                    vc.play(song)
            else:
                warning = discord.Embed(description="<:raidenangry:1080897820854329376> \
                    You must be in the same voice channel as\
                    Raijin", color=self.default_color)
                await ctx.respond(embed=warning, ephemeral=True)
        else:
            warning = discord.Embed(description="<:raidenangry:1080897820854329376> \
                You need to join a Voice Channel before playing", color=self.default_color)
            await ctx.respond(embed=warning, ephemeral=True)

    async def m_next(self, ctx):
        vc = ctx.voice_client
        FFMPEG_OPTIONS = {'options': '-vn -loglevel quiet'}

        if ctx.author.voice:
            if not vc:
                vc = await ctx.author.voice.channel.connect()
            if ctx.author.voice.channel.id == vc.channel.id:
                if ctx.voice_client.is_playing():
                    vc.stop()
                choice = random.choice(os.listdir("res/tracks/"))
                song = discord.FFmpegOpusAudio("res/tracks/" + choice, bitrate=64, **FFMPEG_OPTIONS)
                title = choice.replace(".mp3", "")

                if not song:
                    warning = discord.Embed(description="<:raidenangry:1080897820854329376> \
                        An error occured with the song, please \
                        retry later", color=self.default_color)
                    await ctx.respond(embed=warning, ephemeral=True)

                def duration(length):
                    mins = length // 60
                    length %= 60
                    seconds = length
                    return mins, seconds

                with audioread.audio_open(f"res/tracks/{choice}") as f:
                    total = f.duration
                    mins, seconds = duration(int(total))

                mp3 = MP3(f"res/tracks/{choice}")
                bitrate = mp3.info.bitrate / 1000

                file = discord.File("res/images/rote.jpg", filename="rote.jpg")
                info = discord.Embed(
                    title=title,
                    description=f"・**Duration**: \
                    `{mins}:{seconds}`" + f"\n・**Bitrate**: `{bitrate}` \
                    Kbps\n・**Album**: Realm of Tranquil Eternity",
                    color=self.default_color
                )
                info.set_image(url="attachment://rote.jpg")
                info.set_footer(text="By Yu-Peng Chen and HOYO-MIX")

                await ctx.respond(embed=info, file=file, view=MusicPlay(self, ctx))
                vc.play(song)
            else:
                warning = discord.Embed(description="<:raidenangry:1080897820854329376> \
                    You must be in the same voice channel as\
                    Raijin", color=self.default_color)
                await ctx.respond(embed=warning, ephemeral=True)
        else:
            warning = discord.Embed(description="<:raidenangry:1080897820854329376> \
                You need to join a Voice Channel before playing", color=self.default_color)
            await ctx.respond(embed=warning, ephemeral=True)

    async def m_stop(self, ctx):
        vc = ctx.voice_client

        if vc:
            if ctx.voice_client.is_playing():
                vc.stop()
            await vc.disconnect()
            info = discord.Embed(description="<:raidenbird:1080897824440455288> \
                Music stopped, Raijin leaved the channel", color=self.default_color)
            await ctx.respond(embed=info, ephemeral=True)
        else:
            error = discord.Embed(description="<:raidenangry:1080897820854329376> \
                Raijin isn't connected to a Voice Channel, use \
                `/music play` to connect and start", color=self.default_color)
            await ctx.respond(embed=error, ephemeral=True)

    async def m_pause(self, ctx):
        vc = ctx.voice_client

        if vc:
            if ctx.voice_client.is_playing():
                vc.pause()
            else:
                vc.resume()

    async def m_shuffle(self, ctx):
        vc = ctx.voice_client
        FFMPEG_OPTIONS = {'options': '-vn -loglevel quiet'}

        if vc:
            if not vc:
                vc = await ctx.author.voice.channel.connect()
            if ctx.author.voice.channel.id == vc.channel.id:
                if ctx.voice_client.is_playing():
                    vc.stop()
                choice = random.choice(os.listdir("res/tracks/"))
                song = discord.FFmpegOpusAudio("res/tracks/" \
                    + choice, bitrate=64, **FFMPEG_OPTIONS)
                title = choice.replace(".mp3", "")

                if not song:
                    warning = discord.Embed(description="<:raidenangry:1080897820854329376> \
                        An error occured with the song, please \
                        retry later", color=self.default_color)
                    await self.ctx.respond(embed=warning, ephemeral=True)

                def duration(length):
                    mins = length // 60
                    length %= 60
                    seconds = length
                    return mins, seconds

                with audioread.audio_open(f"tracks/{choice}") as f:
                    total = f.duration
                    mins, seconds = duration(int(total))

                mp3 = MP3(f"res/tracks/{choice}")
                bitrate = mp3.info.bitrate / 1000

                file = discord.File("res/images/rote.jpg", filename="rote.jpg")
                info = discord.Embed(
                    title=title,
                    description=f"・**Duration**: \
                    `{mins}:{seconds}`" + f"\n・**Bitrate**: `{bitrate}`\
                    Kbps\n・**Album**: Realm of Tranquil Eternity",
                    color=self.default_color
                )
                info.set_image(url="attachment://rote.jpg")
                info.set_footer(text="By Yu-Peng Chen and HOYO-MIX")

                msg = await ctx.respond(embed=info, file=file, view=MusicDisabled(self, ctx))
                vc.play(song)
                await asyncio.sleep(total)
                await msg.delete()
                await self.m_shuffle(ctx)


def setup(bot):
    bot.add_cog(Music(bot))
