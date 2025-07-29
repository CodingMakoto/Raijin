"""
The help file is providing commands to help a user with
Raijin's commands and features.

Commands:
    - help
"""

import os
import json

import discord
from discord.ui import Select, View
import mysql.connector

from config.env import Database


class Help(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.conn = self.db.connect()
        self.cursor = self.conn.cursor()
        self.default_color = 0x37266A
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

    def get_conn_cursor(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        return conn, cursor

    @discord.slash_command(name="help", description="📋 Request Raijin help")
    async def help(
        self,
        ctx,
    ):
        """
        The help command is used to display the help menu
        with the different categories and commands available.
        """
        conn, cursor = self.get_conn_cursor()
        try:
            if ctx.guild is None:
                selected_language = self.en_lang
            else:
                cursor.execute(
                    "SELECT `LANG` FROM `Account` WHERE `ID` = %s AND `GUILD` = %s",
                    (ctx.author.id, ctx.guild.id),
                )
                fetched_account = cursor.fetchone()

                if fetched_account is not None:
                    selected_language = (
                        self.fr_lang
                        if fetched_account[0] == "Français"
                        else self.en_lang
                    )
                else:
                    selected_language = self.en_lang

            category = Select(
                options=[
                    discord.SelectOption(
                        label=selected_language["help"]["options"]["account"]["title"],
                        value="account",
                        description=selected_language["help"]["options"]["account"][
                            "description"
                        ],
                        emoji="<:raidencards:1287740296662220931>",
                    ),
                    discord.SelectOption(
                        label=selected_language["help"]["options"]["profile"]["title"],
                        value="profile",
                        description=selected_language["help"]["options"]["profile"][
                            "description"
                        ],
                        emoji="<:raidenfight:1189307569739661312>",
                    ),
                    discord.SelectOption(
                        label=selected_language["help"]["options"]["quests"]["title"],
                        value="quests",
                        description=selected_language["help"]["options"]["quests"][
                            "description"
                        ],
                        emoji="<:raidenleaving:1189307571237044297>",
                    ),
                    discord.SelectOption(
                        label=selected_language["help"]["options"]["astral"]["title"],
                        value="astral",
                        description=selected_language["help"]["options"]["astral"][
                            "description"
                        ],
                        emoji="<:raidenbird:1080897824440455288>",
                    ),
                ],
                placeholder=selected_language["help"]["selection"],
                min_values=1,
                max_values=1,
            )
            menu = discord.Embed(
                title=selected_language["help"]["title"],
                description=selected_language["help"]["description"],
                color=self.default_color,
            )

            async def category_callback(interaction):
                selected_value = interaction.data["values"][0]
                selected_category = discord.Embed(
                    title=selected_language["help"]["callback"][selected_value][
                        "title"
                    ],
                    description=selected_language["help"]["callback"][selected_value][
                        "description"
                    ],
                    color=self.default_color,
                )
                await interaction.response.edit_message(
                    embed=selected_category, view=None
                )

            view = View()
            view.add_item(category)
            category.callback = category_callback
            await ctx.respond(embed=menu, view=view)
        except mysql.connector.Error:
            raise
        finally:
            cursor.close()
            conn.close()


def setup(bot):
    """
    Add the Help cog to the main file
    """
    bot.add_cog(Help(bot))
