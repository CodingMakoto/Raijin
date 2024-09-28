"""
The story file is providing commands to create an account
with Raijin, delete an account, start/continue the story mode and
see the daily quests of a user.

Commands:
    - start
    - end
"""


import os.path
import json

import discord
from discord import Option, SlashCommandGroup
from discord.ui import View, Button

import mysql.connector
from dotenv import load_dotenv

load_dotenv(dotenv_path="../../")
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_database = os.getenv("DB_DATABASE")
db_auth_plugin = os.getenv("DB_AUTH_PLUGIN")


class Account(discord.Cog):
    """
    Account class is made to create a user account to play
    with Raijin or delete an existing account to reset the information
    or stop the adventure. The user can create an account with custom
    parameters.
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
        self.fr_file = open(os.path.dirname(__file__) + '/../../res/lang/fr_FR.json',
            encoding="utf-8")
        self.en_file = open(os.path.dirname(__file__) + '/../../res/lang/en_EN.json',
            encoding="utf-8")
        self.fr_lang = json.load(self.fr_file)
        self.en_lang = json.load(self.en_file)

    account = SlashCommandGroup(
        "account", "Everything about your Account"
    )

    @account.command(name="start", description="🔍 Ready for a new adventure ?")
    async def start(
        self,
        ctx,
        language: Option(str, "What language do you want to use ?", choices=["Français","English"], required=True),
        uid: Option(str, "You can enter your real UID to be used with other commands", required=False),
        nickname: Option(str, "You can choose a name for this adventure", required=False)
    ):
        """
        Create an account with the user name of the name specified,
        with 0 as uid or the uid specified if the uid is correct and
        with English or French language
        """
        self.mydb.ping(reconnect=True)

        self.cursor.execute(f"SELECT `LANG` FROM `Account` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'")
        fetched_account = self.cursor.fetchone()

        name = nickname or ctx.author.name
        uid = uid or "0"
        uid_valid = (uid != "0" and len(uid) == 9 and uid.isnumeric()) or uid == "0"

        if fetched_account is not None:
            self.cursor.execute(f"SELECT `LANG` FROM `Account` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'")
            lang = self.cursor.fetchone()[0]
            lang_list = self.fr_lang if lang == "Français" else self.en_lang
            warning = discord.Embed(description=lang_list['account']['creation']['existing'], color=self.default_color)
            await ctx.respond(embed=warning, ephemeral=True)
        else:
            lang_list = self.fr_lang if language == "Français" else self.en_lang
            if uid_valid:
                self.cursor.execute(f"INSERT INTO `Account` (`ID`, `GUILD`, `UID`, `NAME`, `LANG`) VALUES \
                    ('{ctx.author.id}', '{ctx.guild.id}', '{uid}', '{name}', '{language}')")
                self.mydb.commit()
                creation = discord.Embed(description=lang_list['account']['creation']['created'].format(user=ctx.author.mention), color=self.default_color)
                await ctx.respond(embed=creation)
            else:
                warning = discord.Embed(description=lang_list['account']['creation']['wrong_uid'], color=self.default_color)
                await ctx.respond(embed=warning)


    @account.command(name="end", description="🧳 Return to your home world")
    async def end(self, ctx):
        """
        Close the account of the user by erasing all the user information
        """
        self.mydb.ping(reconnect=True)

        self.cursor.execute(f"SELECT `LANG` FROM `Account` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'")
        fetched_account = self.cursor.fetchone()

        self.cursor.execute(f"SELECT `CHAPTER` FROM `Story` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'")
        story_progress = self.cursor.fetchone()

        if fetched_account is not None:
            self.cursor.execute(f"SELECT `LANG` FROM `Account` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'")
            lang = self.cursor.fetchone()[0]
            lang_list = self.fr_lang if lang == "Français" else self.en_lang

            async def yes_callback(interaction):
                delete = discord.Embed(description=lang_list['account']['deletion']['deleted'].format(user=ctx.author.mention), color=self.default_color)
                self.cursor.execute(f"DELETE FROM `Account` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'")
                self.mydb.commit()
                if story_progress is not None:
                    self.cursor.execute(f"DELETE FROM `Story` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'")
                    self.mydb.commit()
                await interaction.response.send_message(embed=delete, ephemeral=True)

            async def no_callback(interaction):
                stop = discord.Embed(description=lang_list['account']['deletion']['cancelled'].format(user=ctx.author.mention), color=self.default_color)
                await interaction.response.send_message(embed=stop, ephemeral=True)

            confirm = discord.Embed(description=lang_list['account']['deletion']['confirmation'].format(user=ctx.author.mention), color=self.default_color)
            no = Button(label=lang_list['account']['deletion']['no_button'], style=discord.ButtonStyle.danger)
            yes = Button(label=lang_list['account']['deletion']['yes_button'], style=discord.ButtonStyle.green)
            no.callback = no_callback
            yes.callback = yes_callback
            view = View()
            view.add_item(no)
            view.add_item(yes)
            await ctx.respond(embed=confirm, view=view, ephemeral=True)
        else:
            warning = discord.Embed(description="<:raidenangry:1080897820854329376> \
                You do not have an account to delete", color=self.default_color)
            await ctx.respond(embed=warning, ephemeral=True)

def setup(bot):
    """
    Add the Account cog to the main file
    """
    bot.add_cog(Account(bot))
