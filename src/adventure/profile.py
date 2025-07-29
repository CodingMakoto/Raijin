"""
The profile file is providing commands to view and manage informations about
the user adventure with Raijin and Genshin Impact.

Commands:
    - in-game
    - uid
    - astral
"""

import os
import json
import asyncio

import discord
from discord.ext import commands
from discord import Option, SlashCommandGroup

import mysql.connector
import aiohttp

from config.env import Database


class Profile(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.conn = self.db.connect()
        self.cursor = self.conn.cursor()
        self.default_color = 0x37266A
        self.error_color = 0xFF0000
        with open(
            os.path.dirname(__file__) + "/../../res/lang/fr_FR.json", encoding="utf-8"
        ) as fr_file:
            self.fr_lang = json.load(fr_file)
        with open(
            os.path.dirname(__file__) + "/../../res/lang/en_EN.json", encoding="utf-8"
        ) as en_file:
            self.en_lang = json.load(en_file)

    def __del__(self):
        self.db.close()

    def get_conn_cursor(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        return conn, cursor

    profile = SlashCommandGroup(
        "profile", "All about your adventure with Raijin and Genshin Impact"
    )

    @profile.command(name="in-game", description="🕹️ Your real in-game stats")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def in_game(
        self,
        ctx,
        member: Option(
            discord.Member,
            "You can see the profile of another member in the server",
            required=False,
        ),  # type: ignore
    ):
        """
        The in-game command is used to display the in-game profile
        of the user or another member in the server, it shows the details
        of the Genshin Impact account.
        """
        if ctx.guild is None:
            error = discord.Embed(
                description="<:raidenannoyed:1287740293386469396> This command is not available outside a server",
                color=0xFF0000,
            )
            await ctx.respond(embed=error)
            return

        conn, cursor = self.get_conn_cursor()
        try:
            user = member if member is not None else ctx.author

            cursor.execute(
                "SELECT `LANG` FROM `Account` WHERE `ID` = %s AND `GUILD` = %s",
                (user.id, ctx.guild.id),
            )
            fetched_account = cursor.fetchone()

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
                    else selected_language["profile"]["account"]["not_existing"][
                        "author"
                    ]
                )
                error = discord.Embed(description=message, color=self.error_color)
                await ctx.respond(embed=error, ephemeral=True)
                return

            cursor.execute(
                "SELECT `UID` FROM `Account` WHERE `ID` = %s AND `GUILD` = %s",
                (user.id, ctx.guild.id),
            )
            uid_registered = cursor.fetchone()

            if uid_registered is not None and uid_registered[0] != "0":
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

            player = None
            await ctx.defer()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"https://enka.network/api/uid/{uid}?info", timeout=5
                    ) as response:
                        response.raise_for_status()
                        player = await response.json()
            except (
                asyncio.TimeoutError,
                aiohttp.ClientResponseError,
                aiohttp.ClientError,
            ):
                error = discord.Embed(
                    description=selected_language["profile"]["api_failed"],
                    color=self.error_color,
                )
                await ctx.followup.send(embed=error, ephemeral=True)
                return

            if player is None:
                error = discord.Embed(
                    description=selected_language["profile"]["api_failed"],
                    color=self.error_color,
                )
                await ctx.followup.send(embed=error, ephemeral=True)
                return

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
            await ctx.followup.send(embed=profile)
        except mysql.connector.Error:
            raise
        finally:
            cursor.close()
            conn.close()

    @profile.command(
        name="uid", description="💾️ Register or remove your UID from Raijin"
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def uid(
        self,
        ctx,
        uid: Option(
            str,
            "Enter your Genshin Impact UID to save it or remove it with Raijin",
            required=True,
        ),  # type: ignore
    ):
        """
        The uid command is used to register or remove the Genshin Impact UID from Raijin.
        """
        if ctx.guild is None:
            error = discord.Embed(
                description="<:raidenannoyed:1287740293386469396> This command is not available outside a server",
                color=0xFF0000,
            )
            await ctx.respond(embed=error)
            return

        conn, cursor = self.get_conn_cursor()
        try:
            cursor.execute(
                "SELECT `LANG` FROM `Account` WHERE `ID` = %s AND `GUILD` = %s",
                (ctx.author.id, ctx.guild.id),
            )
            fetched_account = cursor.fetchone()

            if fetched_account is not None:
                selected_language = (
                    self.fr_lang if fetched_account[0] == "Français" else self.en_lang
                )
            else:
                selected_language = self.en_lang
                error = discord.Embed(
                    description=selected_language["errors"]["account"],
                    color=self.error_color,
                )
                await ctx.respond(embed=error, ephemeral=True)
                return

            if len(uid) != 9 and len(uid) != 10:
                error = discord.Embed(
                    description=selected_language["profile"]["account"]["uid"][
                        "invalid"
                    ],
                    color=self.error_color,
                )
                await ctx.respond(embed=error, ephemeral=True)
                return

            cursor.execute(
                "SELECT `UID` FROM `Account` WHERE `ID` = %s AND `GUILD` = %s",
                (ctx.author.id, ctx.guild.id),
            )
            uid_fetched = cursor.fetchone()

            if uid_fetched[0] == "0":
                cursor.execute(
                    "UPDATE `Account` SET `UID` = %s WHERE `ID` = %s AND `GUILD` = %s",
                    (uid, ctx.author.id, ctx.guild.id),
                )
                conn.commit()
                message = discord.Embed(
                    description=selected_language["profile"]["account"]["uid"]["saved"],
                    color=self.default_color,
                )
                await ctx.respond(embed=message)
            else:
                cursor.execute(
                    "UPDATE `Account` SET `UID` = '0' WHERE `ID` = %s AND `GUILD` = %s",
                    (ctx.author.id, ctx.guild.id),
                )
                conn.commit()
                message = discord.Embed(
                    description=selected_language["profile"]["account"]["uid"][
                        "removed"
                    ],
                    color=self.default_color,
                )
                await ctx.respond(embed=message)
        except mysql.connector.Error:
            raise
        finally:
            cursor.close()
            conn.close()

    @profile.command(
        name="astral", description="📜 Your adventure on the Astralia Island"
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def astral(self, ctx):
        """
        The astral command is used to display the adventure profile
        of the user on the Astralia Island with every details
        of the adventure.
        """
        if ctx.guild is None:
            error = discord.Embed(
                description="<:raidenannoyed:1287740293386469396> This command is not available outside a server",
                color=0xFF0000,
            )
            await ctx.respond(embed=error)
            return

        conn, cursor = self.get_conn_cursor()
        try:
            cursor.execute(
                "SELECT `LANG`, `NAME` FROM `Account` WHERE `ID` = %s AND `GUILD` = %s",
                (ctx.author.id, ctx.guild.id),
            )
            fetched_account = cursor.fetchone()

            if fetched_account is not None:
                selected_language = (
                    self.fr_lang if fetched_account[0] == "Français" else self.en_lang
                )
            else:
                selected_language = self.en_lang
                error = discord.Embed(
                    description=selected_language["errors"]["account"],
                    color=self.error_color,
                )
                await ctx.respond(embed=error, ephemeral=True)
                return

            cursor.execute(
                "SELECT `CHAPTER`, `COINS`, `ECHOS`, `BOSSES`, `HEALTH`, `STATUES` FROM `Story` WHERE `ID` = %s AND `GUILD` = %s",
                (ctx.author.id, ctx.guild.id),
            )
            fetched_values = cursor.fetchone()

            if fetched_values is None:
                error = discord.Embed(
                    description=selected_language["errors"]["account"],
                    color=self.error_color,
                )
                await ctx.respond(embed=error, ephemeral=True)
                return

            chapter = fetched_values[0]
            coins = fetched_values[1]
            echos = fetched_values[2]
            bosses = fetched_values[3]
            health = fetched_values[4]
            statues = fetched_values[5]
            name = (
                ctx.author.display_name
                if fetched_account[1] == "0"
                else fetched_account[1]
            )

            profile = discord.Embed(
                title=selected_language["profile"]["astral"]["title"].format(user=name),
                description=selected_language["profile"]["astral"][
                    "description"
                ].format(
                    chapter=chapter,
                    coins=coins,
                    echos=echos,
                    bosses=bosses,
                    health=health,
                    statues=statues,
                ),
                color=self.default_color,
            )

            cursor.execute(
                "SELECT `DONE`, `QUEST1`, `QUEST2`, `QUEST3` FROM `Quests` WHERE `ID` = %s AND `GUILD` = %s",
                (ctx.author.id, ctx.guild.id),
            )
            quest_exist = cursor.fetchone()

            if quest_exist and quest_exist[0] != "True":
                for i in range(1, 4):
                    if (
                        quest_exist[i]
                        == selected_language["quests"]["daily"]["quests"][2]
                    ):
                        cursor.execute(
                            f"UPDATE `Quests` SET `DONE` = %s, `QUEST{i}` = %s WHERE `ID` = %s AND `GUILD` = %s",
                            (
                                "Pending",
                                selected_language["quests"]["daily"]["quest_done"],
                                ctx.author.id,
                                ctx.guild.id,
                            ),
                        )
                        conn.commit()
                        cursor.execute(
                            "SELECT `COINS`, `ECHOS` FROM `Story` WHERE `ID` = %s AND `GUILD` = %s",
                            (ctx.author.id, ctx.guild.id),
                        )
                        result = cursor.fetchone()
                        if result:
                            coins, echos = result
                            coins = int(coins) + 10
                            echos = int(echos) + 1
                            cursor.execute(
                                "UPDATE `Story` SET `COINS` = %s, `ECHOS` = %s WHERE `ID` = %s AND `GUILD` = %s",
                                (coins, echos, ctx.author.id, ctx.guild.id),
                            )
                            conn.commit()
                        break

            await ctx.respond(embed=profile)
        except mysql.connector.Error:
            raise
        finally:
            cursor.close()
            conn.close()


def setup(bot):
    """
    Add the Profile cog to the main file
    """
    bot.add_cog(Profile(bot))
