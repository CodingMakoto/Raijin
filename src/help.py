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
from dotenv import load_dotenv

load_dotenv(dotenv_path="../")
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_database = os.getenv("DB_DATABASE")
db_auth_plugin = os.getenv("DB_AUTH_PLUGIN")


class Help(discord.Cog):
    """
    Help class is made to help a user by sending a
    message to choose a category and get appropriate help
    for a command. The user can also get help directly
    by specifying a command name as a parameter
    """
    def __init__(self, bot):
        self.bot = bot
        self.default_color = 0x37266a
        self.mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_database,
            auth_plugin=db_auth_plugin
        )
        self.cursor = self.mydb.cursor()
        self.fr_file = open(os.path.dirname(__file__) + '/../res/lang/fr_FR.json',
            encoding="utf-8")
        self.en_file = open(os.path.dirname(__file__) + '/../res/lang/en_EN.json',
            encoding="utf-8")
        self.fr_lang = json.load(self.fr_file)
        self.en_lang = json.load(self.en_file)


    @discord.slash_command(name="help", description="📋 Request Raijin help")
    async def help(
        self,
        ctx,
    ):
        """
        Send a help menu with multiple choice/Send details about a specific command
        """
        self.mydb.ping(reconnect=True)

        self.cursor.execute(f"SELECT `LANG` FROM `Account` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'")
        fetched_account = self.cursor.fetchone()

        if fetched_account is not None:
            selected_language = self.fr_lang if fetched_account[0] == "Français" else self.en_lang
        else:
            selected_language = self.en_lang

        category = Select(
            options=[
                discord.SelectOption(label=selected_language['help']['options']['account']['title'],
                    value="Account",
                    description=selected_language['help']['options']['account']['description'],
                    emoji="<:raidencards:1287740296662220931>")
            ],
            placeholder=selected_language['help']['selection'],
            min_values=1,
            max_values=1
        )
        menu = discord.Embed(
            title=selected_language['help']['title'],
            description=selected_language['help']['description'],
            color=self.default_color
        )

        async def category_callback(interaction):
            selected_value = interaction.data["values"][0]
            if selected_value == "Account":
                story = discord.Embed(
                    title=selected_language['help']['callback']['account']['title'],
                    description=selected_language['help']['callback']['account']['description'],
                    color=self.default_color
                )
                await interaction.response.edit_message(embed=story, view=None)

        view = View()
        view.add_item(category)
        category.callback = category_callback
        await ctx.respond(embed=menu, view=view)



def setup(bot):
    """
    Add the Help cog to the main file
    """
    bot.add_cog(Help(bot))
