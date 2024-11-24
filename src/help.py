"""
The help file is providing commands to help
a user with Raijin commands.

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
    """
    Help class is made to help a user by sending a
    message to choose a category and get appropriate help
    for a command. The user can also get help directly
    by specifying a command name as a parameter
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.conn = self.db.connect()
        self.cursor = self.conn.cursor()
        self.default_color = 0x37266a
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

    @discord.slash_command(name="help", description="📋 Request Raijin help")
    async def help(
        self,
        ctx,
    ):
        """
        Send a help menu with multiple choice/Send details about a specific command
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

        category = Select(
            options=[
                discord.SelectOption(
                    label=selected_language["help"]["options"]["account"]["title"],
                    value="Account",
                    description=selected_language["help"]["options"]["account"][
                        "description"
                    ],
                    emoji="<:raidencards:1287740296662220931>",
                ),
                discord.SelectOption(
                    label=selected_language["help"]["options"]["profile"]["title"],
                    value="Profile",
                    description=selected_language["help"]["options"]["profile"][
                        "description"
                    ],
                    emoji="<:raidenfight:1189307569739661312>",
                )
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
            if selected_value == "Account":
                account = discord.Embed(
                    title=selected_language["help"]["callback"]["account"]["title"],
                    description=selected_language["help"]["callback"]["account"][
                        "description"
                    ],
                    color=self.default_color,
                )
                await interaction.response.edit_message(embed=account, view=None)
            if selected_value == "Profile":
                account = discord.Embed(
                    title=selected_language["help"]["callback"]["profile"]["title"],
                    description=selected_language["help"]["callback"]["profile"][
                        "description"
                    ],
                    color=self.default_color,
                )
                await interaction.response.edit_message(embed=account, view=None)

        view = View()
        view.add_item(category)
        category.callback = category_callback
        await ctx.respond(embed=menu, view=view)


def setup(bot):
    """
    Add the Help cog to the main file
    """
    bot.add_cog(Help(bot))
