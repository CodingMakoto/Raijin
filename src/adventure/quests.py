"""
The quests file is providing commands to view and play quests
with Raijin.

Commands:
    - daily
    - bosses
"""

import os.path
import json
import time
import glob
import random
from pathlib import Path
from functools import partial

import discord
from discord import SlashCommandGroup
from discord.ui import View, Button
import mysql.connector

from config.env import Database
from src.callbacks.quests_callbacks import getBiome, bosses_action


class Quests(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_color = 0x37266A
        self.error_color = 0xFF0000
        self.db = Database()
        self.conn = self.db.connect()
        self.cursor = self.conn.cursor()
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

    quests = SlashCommandGroup("quests", "All about your quests with Raijin")

    @quests.command(name="daily", description="⌛ Discover your daily quests")
    async def daily(self, ctx):
        """
        The daily command is used to display the daily quests
        available for the user, the user can complete them
        to earn rewards.
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

            cursor.execute(
                "SELECT `TIME` FROM `Cooldown` WHERE `ID` = %s AND `GUILD` = %s AND `COMMAND` = %s",
                (ctx.author.id, ctx.guild.id, "daily"),
            )
            cooldown = cursor.fetchone()

            current_time = float(time.time())

            if cooldown is None:
                cursor.execute(
                    "INSERT INTO `Cooldown` (`ID`, `GUILD`, `COMMAND`, `TIME`) VALUES (%s, %s, %s, %s)",
                    (ctx.author.id, ctx.guild.id, "daily", current_time),
                )
                conn.commit()
                last_used = current_time
                no_cooldown = True
            else:
                last_used = float(cooldown[0])
                no_cooldown = False

            cursor.execute(
                "SELECT `DONE`, `QUEST1`, `QUEST2`, `QUEST3` FROM `Quests` WHERE `ID` = %s AND `GUILD` = %s",
                (ctx.author.id, ctx.guild.id),
            )
            completed = cursor.fetchone()

            if completed:
                if (
                    completed[0] != "False"
                    and current_time - last_used < 86400
                    and no_cooldown is False
                ):
                    if completed[0] == "True":
                        done = discord.Embed(
                            description=selected_language["quests"]["daily"][
                                "completed"
                            ]
                            + f" <t:{int(last_used + 86400)}:R>",
                            color=self.default_color,
                        )
                        await ctx.respond(embed=done)
                        return
                    else:
                        quest_count = 0
                        for i in range(1, 4):
                            if (
                                completed[i]
                                == selected_language["quests"]["daily"]["quest_done"]
                            ):
                                quest_count += 1
                        if quest_count == 3:
                            cursor.execute(
                                "UPDATE `Quests` SET `DONE` = %s WHERE `ID` = %s AND `GUILD` = %s",
                                ("True", ctx.author.id, ctx.guild.id),
                            )
                            conn.commit()

                    quest1_emoji = (
                        "<:quests:1149295158089748561>"
                        if completed[1]
                        != selected_language["quests"]["daily"]["quest_done"]
                        else "<:questscompleted:1153781763496222821>"
                    )
                    quest2_emoji = (
                        "<:quests:1149295158089748561>"
                        if completed[2]
                        != selected_language["quests"]["daily"]["quest_done"]
                        else "<:questscompleted:1153781763496222821>"
                    )
                    quest3_emoji = (
                        "<:quests:1149295158089748561>"
                        if completed[3]
                        != selected_language["quests"]["daily"]["quest_done"]
                        else "<:questscompleted:1153781763496222821>"
                    )
                    selected_quests_str = (
                        selected_language["quests"]["daily"]["description"]
                        + f"{quest1_emoji} {completed[1]}\n{quest2_emoji} {completed[2]}\n{quest3_emoji} {completed[3]}"
                    )
                    tasks = discord.Embed(
                        title=selected_language["quests"]["daily"]["title"],
                        description=selected_quests_str,
                        color=self.default_color,
                    )
                    await ctx.respond(embed=tasks)
                else:
                    cursor.execute(
                        "UPDATE `Cooldown` SET `TIME` = %s WHERE `ID` = %s AND `GUILD` = %s AND `COMMAND` = %s",
                        (current_time, ctx.author.id, ctx.guild.id, "daily"),
                    )
                    conn.commit()
                    selected_quests = random.sample(
                        selected_language["quests"]["daily"]["quests"], 3
                    )
                    cursor.execute(
                        "UPDATE `Quests` SET `QUEST1` = %s, `QUEST2` = %s, `QUEST3` = %s, `DONE` = %s WHERE `ID` = %s AND `GUILD` = %s",
                        (
                            selected_quests[0],
                            selected_quests[1],
                            selected_quests[2],
                            "Pending",
                            ctx.author.id,
                            ctx.guild.id,
                        ),
                    )
                    conn.commit()
                    selected_quests_str = (
                        selected_language["quests"]["daily"]["description"]
                        + f"<:quests:1149295158089748561> {selected_quests[0]}\n<:quests:1149295158089748561> {selected_quests[1]}\n<:quests:1149295158089748561> {selected_quests[2]}"
                    )
                    tasks = discord.Embed(
                        title=selected_language["quests"]["daily"]["title"],
                        description=selected_quests_str,
                        color=self.default_color,
                    )
                    await ctx.respond(embed=tasks)

        except mysql.connector.Error:
            raise
        finally:
            cursor.close()
            conn.close()

    @quests.command(name="bosses", description="🛡️ Fight a boss")
    async def bosses(self, ctx):
        """
        The bosses command is used to fight a boss and earn rewards
        by completing the quest, the user can choose between three attacks
        with different chances of success.
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

            cursor.execute(
                "SELECT `TIME` FROM `Cooldown` WHERE `ID` = %s AND `GUILD` = %s AND `COMMAND` = %s",
                (ctx.author.id, ctx.guild.id, "bosses"),
            )
            cooldown = cursor.fetchone()

            current_time = float(time.time())

            if cooldown is None:
                cursor.execute(
                    "INSERT INTO `Cooldown` (`ID`, `GUILD`, `COMMAND`, `TIME`) VALUES (%s, %s, %s, %s)",
                    (ctx.author.id, ctx.guild.id, "bosses", current_time),
                )
                conn.commit()
                no_cooldown = True
                last_used = current_time
            else:
                no_cooldown = False
                last_used = float(cooldown[0])

            if current_time - last_used < 43200 and no_cooldown is False:
                done = discord.Embed(
                    description=selected_language["cooldowns"]["bosses"]
                    + f" <t:{int(last_used + 43200)}:R>",
                    color=self.default_color,
                )
                await ctx.respond(embed=done)
            else:
                cursor.execute(
                    "UPDATE `Cooldown` SET `TIME` = %s WHERE `ID` = %s AND `GUILD` = %s AND `COMMAND` = %s",
                    (current_time, ctx.author.id, ctx.guild.id, "bosses"),
                )
                conn.commit()
                images = glob.glob("./res/images/quests/monsters/*.jpg")
                quest = random.choice(images)
                monster = Path(quest).stem
                file = discord.File(quest, filename="fight.jpg")
                fight = discord.Embed(
                    title=selected_language["quests"]["bosses"]["title"],
                    description=selected_language["quests"]["bosses"][
                        getBiome(monster)
                    ],
                    color=self.default_color,
                )
                fight.set_image(url="attachment://fight.jpg")

                first_range = [1, 2, 3, 4, 5, 6, 7, 8]
                first_chances = [75, 70, 65, 60, 50, 30, 15, 10]
                first_button = random.choices(first_range, weights=first_chances, k=1)[
                    0
                ]
                first_action = Button(
                    label=selected_language["quests"]["bosses"]["fight"][
                        f"{first_button}"
                    ],
                    style=discord.ButtonStyle.primary,
                )

                second_range = [val for val in first_range if val != first_button]
                second_chances = [
                    first_chances[i]
                    for i in range(len(first_range))
                    if first_range[i] != first_button
                ]
                second_button = random.choices(
                    second_range, weights=second_chances, k=1
                )[0]
                second_action = Button(
                    label=selected_language["quests"]["bosses"]["fight"][
                        f"{second_button}"
                    ],
                    style=discord.ButtonStyle.primary,
                )

                third_range = [val for val in second_range if val != second_button]
                third_chances = [
                    second_chances[i]
                    for i in range(len(second_range))
                    if second_range[i] != second_button
                ]
                third_button = random.choices(third_range, weights=third_chances, k=1)[
                    0
                ]
                third_action = Button(
                    label=selected_language["quests"]["bosses"]["fight"][
                        f"{third_button}"
                    ],
                    style=discord.ButtonStyle.primary,
                )

                first_action.callback = partial(
                    bosses_action,
                    author=ctx.author,
                    guild=ctx.guild,
                    selected_language=selected_language,
                    default_color=self.default_color,
                    attack=first_button,
                    monster=monster,
                )
                second_action.callback = partial(
                    bosses_action,
                    author=ctx.author,
                    guild=ctx.guild,
                    selected_language=selected_language,
                    default_color=self.default_color,
                    attack=second_button,
                    monster=monster,
                )
                third_action.callback = partial(
                    bosses_action,
                    author=ctx.author,
                    guild=ctx.guild,
                    selected_language=selected_language,
                    default_color=self.default_color,
                    attack=third_button,
                    monster=monster,
                )
                view = View()
                view.add_item(first_action)
                view.add_item(second_action)
                view.add_item(third_action)
                await ctx.respond(embed=fight, file=file, view=view)
        except mysql.connector.Error:
            raise
        finally:
            cursor.close()
            conn.close()


def setup(bot):
    """
    Add the Quests cog to the main file
    """
    bot.add_cog(Quests(bot))
