"""
The profile file is providing commands to fetch
Genshin Impact user statistics, remove/register an
uid.

Commands:
    - in-game
    - uid
"""

import os
import json

import discord
from discord import Option, SlashCommandGroup

import requests
import mysql.connector

from config.env import Database


class Profile(discord.Cog):
    """
    Profile class is made to fetch and send
    the genshin impact statistics of a member
    in the discord server or the author of the command.
    The users can remove or register an uid into Raijin
    in order to use the in-game command.
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.conn = self.db.connect()
        self.cursor = self.conn.cursor()
        self.default_color = 0x37266a
        self.error_color = 0xff0000
        with open(
            os.path.dirname(__file__) + "/../res/lang/fr_FR.json", encoding="utf-8"
        ) as fr_file:
            self.fr_lang = json.load(fr_file)
        with open(
            os.path.dirname(__file__) + "/../res/lang/en_EN.json", encoding="utf-8"
        ) as en_file:
            self.en_lang = json.load(en_file)

    def __del__(self):
        self.db.close()

    profile = SlashCommandGroup("profile", "All about your adventure with Raijin and Genshin Impact")

    @profile.command(name="in-game", description="🕹️ Your real in-game stats")
    async def in_game(
        self,
        ctx,
        member: Option(
            discord.Member,
            "You can see the profile of another member in the server",
            required=False,
        ),
    ):
        """
        Send the in-game statistics of a specified member or the author of the command
        """
        try:
            self.conn.ping(reconnect=True)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error:
            raise

        user = member if member is not None else ctx.author

        self.cursor.execute(
            f"SELECT `LANG` FROM `Account` WHERE `ID` = '{user.id}' AND `GUILD` = '{ctx.guild.id}'"
        )
        fetched_account = self.cursor.fetchone()

        if fetched_account is not None:
            selected_language = (
                self.fr_lang if fetched_account[0] == "Français" else self.en_lang
            )
        else:
            selected_language = self.en_lang
            message = (
                selected_language["profile"]["account"]["not_existing"][
                    "member"
                ].format(user=user.mention)
                if member is not None
                else selected_language["profile"]["account"]["not_existing"]["author"]
            )
            error = discord.Embed(description=message, color=self.error_color)
            await ctx.respond(embed=error, ephemeral=True)
            return

        self.cursor.execute(
            f"SELECT `UID` FROM `Account` WHERE `ID` = '{user.id}' AND `GUILD` = '{ctx.guild.id}'"
        )
        uid_registered = self.cursor.fetchone()

        if uid_registered is not None:
            uid = uid_registered[0]
        else:
            message = (
                selected_language["profile"]["account"]["uid_not_existing"][
                    "member"
                ].format(user=user.mention)
                if member is not None
                else selected_language["profile"]["account"]["uid_not_existing"][
                    "author"
                ]
            )
            error = discord.Embed(description=message, color=self.default_color)
            await ctx.respond(embed=error, ephemeral=True)
            return

        if len(uid) == 10:
            uid = uid[:-1]
        informations = requests.get(
            f"https://enka.network/api/uid/{uid}?info", timeout=5
        )
        if informations.status_code != 200:
            error = discord.Embed(
                description=selected_language["profile"]["api_failed"],
                color=self.error_color,
            )
            await ctx.respond(embed=error, ephemeral=True)
            return
        player = informations.json()
        nickname = f"{selected_language['profile']['in-game']['title'].format(user=player['playerInfo']['nickname'])}"
        details = f"{selected_language['profile']['in-game']['adventure_level']}: `{player['playerInfo']['level']}`"
        if "signature" in player["playerInfo"]:
            details += f"{selected_language['profile']['in-game']['signature']}: `{player['playerInfo']['signature']}`"
        if "worldLevel" in player["playerInfo"]:
            details += f"{selected_language['profile']['in-game']['world_level']}: `{player['playerInfo']['worldLevel']}`"
        if (
            "towerFloorIndex" in player["playerInfo"]
            and "towerLevelIndex" in player["playerInfo"]
        ):
            details += f"{selected_language['profile']['in-game']['spiral_abyss']}: `{player['playerInfo']['towerFloorIndex']}-{player['playerInfo']['towerLevelIndex']}`"
        if "finishAchievementNum" in player["playerInfo"]:
            details += f"{selected_language['profile']['in-game']['achievements']}: `{player['playerInfo']['finishAchievementNum']}`"
        if "theaterActIndex" in player["playerInfo"]:
            details += f"{selected_language['profile']['in-game']['imaginarium_theater']}: `{player['playerInfo']['theaterActIndex']}`"
        profile = discord.Embed(
            title=nickname,
            description=details,
            color=self.default_color,
        )
        profile.set_thumbnail(url=user.display_avatar.url)
        await ctx.respond(embed=profile)

    @profile.command(
        name="uid", description="💾️ Register or remove your UID from Raijin"
    )
    async def uid(
        self,
        ctx,
        uid: Option(
            str,
            "Enter your Genshin Impact UID to save it or remove it with Raijin",
            required=True,
        ),
    ):
        """
        Register or remove the Genshin Impact UID
        specified by the user from Raijin Database
        """
        try:
            self.conn.ping(reconnect=True)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error:
            raise

        self.cursor.execute(
            f"SELECT `LANG` FROM `Account` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'"
        )
        fetched_account = self.cursor.fetchone()

        if fetched_account is not None:
            selected_language = (
                self.fr_lang if fetched_account[0] == "Français" else self.en_lang
            )
        else:
            selected_language = self.en_lang
            error = discord.Embed(
                description=selected_language["errors"]["account"]["details"],
                color=self.error_color,
            )
            await ctx.respond(embed=error, ephemeral=True)
            return

        if len(uid) != 9 and len(uid) != 10:
            error = discord.Embed(
                description=selected_language["profile"]["account"]["uid"]["invalid"],
                color=self.error_color,
            )
            await ctx.respond(embed=error, ephemeral=True)
            return

        self.cursor.execute(
            f"SELECT `UID` FROM `Account` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'"
        )
        uid_fetched = self.cursor.fetchone()

        if uid_fetched[0] == "0":
            self.cursor.execute(
                f"UPDATE `Account` SET `UID` = '{uid}' WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'"
            )
            self.conn.commit()
            message = discord.Embed(
                description=selected_language["profile"]["account"]["uid"]["saved"],
                color=self.default_color,
            )
            await ctx.respond(embed=message)
        else:
            self.cursor.execute(
                f"UPDATE `Account` SET `UID` = '0' WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'"
            )
            self.conn.commit()
            message = discord.Embed(
                description=selected_language["profile"]["account"]["uid"]["removed"],
                color=self.default_color,
            )
            await ctx.respond(embed=message)


def setup(bot):
    """
    Add the Profile cog to the main file
    """
    bot.add_cog(Profile(bot))
