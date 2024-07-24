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

import random
import os
import asyncio
import json

import discord
from discord import SlashCommandGroup

import audioread
from mutagen.mp3 import MP3


class MusicDisabled(discord.ui.View):
    """
    Music Disabled class is made to ensure that next and shuffle
    buttons are disabled for every song
    They are empty because they are disabled all the time
    """

    def __init__(self, musiccog, context):
        discord.ui.View.__init__(self, timeout=None)
        self.musiccog = musiccog
        self.context = context

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏯️")
    async def play_pause_callback(self, button, interaction):
        """
        Play if the song is paused or pause if the song is played
        """
        button.disabled = False
        await self.musiccog.m_pause(self.context)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏹️")
    async def stop_callback(self, button, interaction):
        """
        Stop the song and quit the channel
        """
        button.disabled = True
        await self.musiccog.m_stop(self.context)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(style=discord.ButtonStyle.secondary, disabled=True, emoji="⏭️")
    async def next_callback(self):
        """
        Disabled for every song because the shuffle mode is activated
        """
        pass

    @discord.ui.button(style=discord.ButtonStyle.secondary, disabled=True, emoji="🔀")
    async def shuffle_callback(self):
        """
        Disabled for every song because the shuffle mode is activated
        """
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
        """
        Play if the song is paused or pause if the song is played
        """
        button.disabled = False
        await self.musiccog.m_pause(self.context)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏹️")
    async def stop_callback(self, button, interaction):
        """
        Stop the song and quit the channel
        """
        button.disabled = True
        await self.musiccog.m_stop(self.context)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏭️")
    async def next_callback(self, button, interaction):
        """
        Stop the song and change to the next one
        """
        button.disabled = False
        await interaction.message.delete()
        await self.musiccog.m_next(self.context)

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="🔀")
    async def shuffle_callback(self, button, interaction):
        """
        Activate shuffle mode and desactivate next and shuffle buttons
        """
        button.disabled = True
        await interaction.message.delete()
        await self.musiccog.m_shuffle(self.context)


class Music(discord.Cog):
    """
    Music Cog is the main function to play, resume, stop and shuffle music
    The default bitrate is 128 and the shuffle command is playing
    automatically music
    """

    def __init__(self, bot):
        self.bot = bot
        self.default_color = 0x37266A
        self.fr_file = open(os.path.dirname(__file__) + '/../res/lang/fr_FR.json',
                            encoding="utf-8")
        self.fr_lang = json.load(self.fr_file)
        self.en_file = open(os.path.dirname(__file__) + '/../res/lang/en_EN.json',
                            encoding="utf-8")
        self.en_lang = json.load(self.en_file)

    @staticmethod
    def duration(length):
        minutes = length // 60
        length %= 60
        seconds = length
        return minutes, seconds

    dj = SlashCommandGroup(
        "dj", "The commands about DJ Raijin"
    )

    @dj.command(name="raijin", description="🎧 Listen to Inazuma Music")
    async def m_start(self, ctx):
        """
        Ensure that the user is in a voice channel, start a song from the
        tracks folder and send a message to the user
        """
        vc = ctx.voice_client
        ffmpeg_options = {'options': '-vn -loglevel quiet'}

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
                    song = discord.FFmpegOpusAudio("res/tracks/" + choice, bitrate=64,
                                                   **ffmpeg_options)
                    title = choice.replace(".mp3", "")

                    if not song:
                        warning = discord.Embed(description="<:raidenangry:1080897820854329376> \
                            An error occured with the song, \
                            please retry later", color=self.default_color)
                        await ctx.respond(embed=warning, ephemeral=True)

                    with audioread.audio_open(f"res/tracks/{choice}") as f:
                        total = f.duration
                        minutes, seconds = self.duration(int(total))

                    mp3 = MP3(f"res/tracks/{choice}")
                    bitrate = mp3.info.bitrate / 1000

                    file = discord.File("res/images/rote.jpg", filename="rote.jpg")
                    info = discord.Embed(
                        title=title,
                        description=f"・**Duration**: \
                        `{minutes}:{seconds}`" + f"\n・**Bitrate**: `{bitrate}` \
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

    @staticmethod
    async def m_next(self, ctx):
        """
        Ensure that the user is in a voice channel, stop the song and change to
        a new one
        """
        vc = ctx.voice_client
        ffmpeg_options = {'options': '-vn -loglevel quiet'}

        if ctx.author.voice:
            if not vc:
                vc = await ctx.author.voice.channel.connect()
            if ctx.author.voice.channel.id == vc.channel.id:
                if ctx.voice_client.is_playing():
                    vc.stop()
                choice = random.choice(os.listdir("res/tracks/"))
                song = discord.FFmpegOpusAudio("res/tracks/" + choice, bitrate=64, **ffmpeg_options)
                title = choice.replace(".mp3", "")

                if not song:
                    warning = discord.Embed(description="<:raidenangry:1080897820854329376> \
                        An error occured with the song, please \
                        retry later", color=self.default_color)
                    await ctx.respond(embed=warning, ephemeral=True)

                with audioread.audio_open(f"res/tracks/{choice}") as f:
                    total = f.duration
                    minutes, seconds = self.duration(int(total))

                mp3 = MP3(f"res/tracks/{choice}")
                bitrate = mp3.info.bitrate / 1000

                file = discord.File("res/images/rote.jpg", filename="rote.jpg")
                info = discord.Embed(
                    title=title,
                    description=f"・**Duration**: \
                    `{minutes}:{seconds}`" + f"\n・**Bitrate**: `{bitrate}` \
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

    @staticmethod
    async def m_stop(self, ctx):
        """
        Ensure that the user is in a voice channel, stop the song and
        quit the voice channel
        """
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

    @staticmethod
    async def m_pause(ctx):
        """
        Ensure that the user is in a voice channel, pause the song
        if playing or play the song if paused
        """
        vc = ctx.voice_client

        if vc:
            if ctx.voice_client.is_playing():
                vc.pause()
            else:
                vc.resume()

    @staticmethod
    async def m_shuffle(self, ctx):
        """
        Ensure that the user is in a voice channel and activate
        the shuffle mode
        """
        vc = ctx.voice_client
        ffmpeg_options = {'options': '-vn -loglevel quiet'}

        if vc:
            if not vc:
                vc = await ctx.author.voice.channel.connect()
            if ctx.author.voice.channel.id == vc.channel.id:
                if ctx.voice_client.is_playing():
                    vc.stop()
                choice = random.choice(os.listdir("res/tracks/"))
                song = discord.FFmpegOpusAudio("res/tracks/"
                                               + choice, bitrate=64, **ffmpeg_options)
                title = choice.replace(".mp3", "")

                if not song:
                    warning = discord.Embed(description="<:raidenangry:1080897820854329376> \
                        An error occured with the song, please \
                        retry later", color=self.default_color)
                    await self.ctx.respond(embed=warning, ephemeral=True)

                with audioread.audio_open(f"tracks/{choice}") as f:
                    total = f.duration
                    minutes, seconds = self.duration(int(total))

                mp3 = MP3(f"res/tracks/{choice}")
                bitrate = mp3.info.bitrate / 1000

                file = discord.File("res/images/rote.jpg", filename="rote.jpg")
                info = discord.Embed(
                    title=title,
                    description=f"・**Duration**: \
                    `{minutes}:{seconds}`" + f"\n・**Bitrate**: `{bitrate}`\
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
    """
    Add the main music cog to the main file
    """
    bot.add_cog(Music(bot))
