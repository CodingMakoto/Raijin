"""
The atlas file is providing commands related to Astralia Island,
the user can learn more about his adventure with Raijin.

Command:
    - atlas
"""

import os.path
import json

import discord
from discord.ui import Select, View
from discord import Option, SlashCommandGroup
import mysql.connector

from config.env import Database


class Astral(discord.Cog):
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

    astral = SlashCommandGroup(
        "astral", "All the commands related to the astral foundation"
    )

    @astral.command(name="atlas", description="📖 Learn more about Astralia Island")
    async def atlas(
        self,
        ctx,
        request: Option(
            str,
            "Select a category to get more informations",
            choices=["Astralia", "Bestiary", "Currency"],
            required=False,
        ),  # type: ignore
    ):
        """
        The atlas command is used to display the information
        about Astralia Island, the user can select a category
        to get more details about the adventure.
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
                message = selected_language["profile"]["account"]["not_existing"][
                    "author"
                ]
                error = discord.Embed(description=message, color=self.error_color)
                await ctx.respond(embed=error, ephemeral=True)
                return

            async def monsters_callback(interaction):
                selected_value = interaction.data["values"][0]
                monster = discord.Embed(
                    title=selected_language["astral"]["bestiary"]["monsters"][
                        selected_value
                    ]["label"],
                    description=selected_language["astral"]["bestiary"]["monsters"][
                        selected_value
                    ]["description"],
                    color=self.default_color,
                )
                conn, cursor = self.get_conn_cursor()
                try:
                    cursor.execute(
                        "SELECT `DONE`, `QUEST1`, `QUEST2`, `QUEST3` FROM `Quests` WHERE `ID` = %s AND `GUILD` = %s",
                        (ctx.author.id, ctx.guild.id),
                    )
                    quest_exist = cursor.fetchone()

                    if quest_exist and quest_exist[0] != "True":
                        if selected_value == "mosshide":
                            atlas_monster_quest = 4
                        elif selected_value == "mystralith":
                            atlas_monster_quest = 5
                        else:
                            atlas_monster_quest = None
                        for i in range(1, 4):
                            if (
                                atlas_monster_quest is not None
                                and quest_exist[i]
                                == selected_language["quests"]["daily"]["quests"][
                                    atlas_monster_quest
                                ]
                            ):
                                cursor.execute(
                                    f"UPDATE `Quests` SET `DONE` = %s, `QUEST{i}` = %s WHERE `ID` = %s AND `GUILD` = %s",
                                    (
                                        "Pending",
                                        selected_language["quests"]["daily"][
                                            "quest_done"
                                        ],
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
                finally:
                    cursor.close()
                    conn.close()
                await interaction.response.edit_message(embed=monster, view=None)

            async def currency_callback(interaction):
                selected_value = interaction.data["values"][0]
                currency = discord.Embed(
                    title=selected_language["astral"]["currency"][selected_value][
                        "label"
                    ],
                    description=selected_language["astral"]["currency"][selected_value][
                        "description"
                    ],
                    color=self.default_color,
                )
                conn, cursor = self.get_conn_cursor()
                try:
                    cursor.execute(
                        "SELECT `DONE`, `QUEST1`, `QUEST2`, `QUEST3` FROM `Quests` WHERE `ID` = %s AND `GUILD` = %s",
                        (ctx.author.id, ctx.guild.id),
                    )
                    quest_exist = cursor.fetchone()

                    if quest_exist and quest_exist[0] != "True":
                        if selected_value == "astralcoin":
                            atlas_currency_quest = 6
                        elif selected_value == "astralecho":
                            atlas_currency_quest = 7
                        else:
                            atlas_currency_quest = None
                        for i in range(1, 4):
                            if (
                                atlas_currency_quest is not None
                                and quest_exist[i]
                                == selected_language["quests"]["daily"]["quests"][
                                    atlas_currency_quest
                                ]
                            ):
                                cursor.execute(
                                    f"UPDATE `Quests` SET `DONE` = %s, `QUEST{i}` = %s WHERE `ID` = %s AND `GUILD` = %s",
                                    (
                                        "Pending",
                                        selected_language["quests"]["daily"][
                                            "quest_done"
                                        ],
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
                finally:
                    cursor.close()
                    conn.close()
                await interaction.response.edit_message(embed=currency, view=None)

            if request is not None:
                if request == "Astralia":
                    astralia = discord.Embed(
                        title=selected_language["astral"]["astralia"]["title"],
                        description=selected_language["astral"]["astralia"][
                            "description"
                        ],
                        color=self.default_color,
                    )
                    await ctx.respond(embed=astralia)
                    return
                if request == "Bestiary":
                    selected_atlas = selected_language["astral"]["bestiary"]["title"]
                    category = Select(
                        options=[
                            discord.SelectOption(
                                label=selected_language["astral"]["bestiary"][
                                    "monsters"
                                ]["mosshide"]["label"],
                                value="mosshide",
                            ),
                            discord.SelectOption(
                                label=selected_language["astral"]["bestiary"][
                                    "monsters"
                                ]["mystralith"]["label"],
                                value="mystralith",
                            ),
                        ],
                        placeholder=selected_language["astral"]["selection"],
                        min_values=1,
                        max_values=1,
                    )
                if request == "Currency":
                    selected_atlas = selected_language["astral"]["currency"]["title"]
                    category = Select(
                        options=[
                            discord.SelectOption(
                                label=selected_language["astral"]["currency"][
                                    "astralecho"
                                ]["label"],
                                emoji="<:astralecho:1317495053479972894>",
                                value="astralecho",
                            ),
                            discord.SelectOption(
                                label=selected_language["astral"]["currency"][
                                    "astralcoin"
                                ]["label"],
                                emoji="<:astralcoin:1317503233249378334>",
                                value="astralcoin",
                            ),
                        ],
                        placeholder=selected_language["astral"]["selection"],
                        min_values=1,
                        max_values=1,
                    )

                view = View()
                view.add_item(category)
                category.callback = (
                    monsters_callback if request == "Bestiary" else currency_callback
                )
                entity = discord.Embed(
                    description=selected_atlas, color=self.default_color
                )
                await ctx.respond(embed=entity, view=view)
            else:
                atlas = discord.Embed(
                    title=selected_language["astral"]["title"],
                    description=selected_language["astral"]["description"],
                    color=self.default_color,
                )
                await ctx.respond(embed=atlas)
        except mysql.connector.Error:
            raise
        finally:
            cursor.close()
            conn.close()


def setup(bot):
    """
    Add the Astral cog to the main file
    """
    bot.add_cog(Astral(bot))
