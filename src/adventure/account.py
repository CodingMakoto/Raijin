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

from config.env import Database


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
        self.error_color = 0xff0000
        self.db = Database()
        self.conn = self.db.connect()
        self.cursor = self.conn.cursor()
        with open(os.path.dirname(__file__) + '/../../res/lang/fr_FR.json',
            encoding="utf-8") as fr_file:
            self.fr_lang = json.load(fr_file)
        with open(os.path.dirname(__file__) + '/../../res/lang/en_EN.json',
            encoding="utf-8") as en_file:
            self.en_lang = json.load(en_file)

    def __del__(self):
        self.db.close()

    account = SlashCommandGroup(
        "account", "Everything about your Account with Raijin"
    )

    @account.command(name="start", description="🔍 Ready for a new adventure ?")
    async def start(
        self,
        ctx,
        language: Option(str, "What language do you want to use ?", choices=["Français","English"], required=True),
        uid: Option(str, "You can enter your Genshin Impact UID to be used with other commands", required=False),
        nickname: Option(str, "You can choose a name for this adventure", required=False)
    ):
        """
        Create an account with the user name of the name specified,
        with 0 as uid or the uid specified if the uid is correct and
        with English or French language
        """
        try:
            self.conn.ping(reconnect=True)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error:
            raise

        self.cursor.execute(f"SELECT `LANG` FROM `Account` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'")
        fetched_account = self.cursor.fetchone()

        name = nickname or ctx.author.name
        uid = uid or "0"
        uid_valid = (uid != "0" and len(uid) == 9 and uid.isnumeric()) or uid == "0"

        if fetched_account is not None:
            selected_language = self.fr_lang if fetched_account[0] == "Français" else self.en_lang
            error = discord.Embed(description=selected_language['account']['creation']['existing'], color=self.error_color)
            await ctx.respond(embed=error, ephemeral=True)
        else:
            selected_language = self.fr_lang if language == "Français" else self.en_lang
            if uid_valid:
                self.cursor.execute(f"INSERT INTO `Account` (`ID`, `GUILD`, `UID`, `NAME`, `LANG`) VALUES \
                    ('{ctx.author.id}', '{ctx.guild.id}', '{uid}', '{name}', '{language}')")
                self.conn.commit()
                creation = discord.Embed(description=selected_language['account']['creation']['created'].format(user=ctx.author.mention), color=self.default_color)
                await ctx.respond(embed=creation)
            else:
                error = discord.Embed(description=selected_language['account']['creation']['wrong_uid'], color=self.error_color)
                await ctx.respond(embed=error)


    @account.command(name="end", description="🧳 Return to your home world")
    async def end(self, ctx):
        """
        Close the account of the user by erasing all the user information
        """
        try:
            self.conn.ping(reconnect=True)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error:
            raise

        self.cursor.execute(f"SELECT `LANG` FROM `Account` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'")
        fetched_account = self.cursor.fetchone()

        if fetched_account is not None:
            selected_language = self.fr_lang if fetched_account[0] == "Français" else self.en_lang

            self.cursor.execute(f"SELECT `CHAPTER` FROM `Story` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'")
            story_progress = self.cursor.fetchone()

            async def yes_callback(interaction):
                delete = discord.Embed(description=selected_language['account']['deletion']['deleted'].format(user=ctx.author.mention), color=self.default_color)
                self.cursor.execute(f"DELETE FROM `Account` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'")
                self.conn.commit()
                if story_progress is not None:
                    self.cursor.execute(f"DELETE FROM `Story` WHERE `ID` = '{ctx.author.id}' AND `GUILD` = '{ctx.guild.id}'")
                    self.conn.commit()
                await interaction.response.edit_message(embed=delete, view=None)

            async def no_callback(interaction):
                stop = discord.Embed(description=selected_language['account']['deletion']['cancelled'].format(user=ctx.author.mention), color=self.default_color)
                await interaction.response.edit_message(embed=stop, view=None)

            confirm = discord.Embed(description=selected_language['account']['deletion']['confirmation'].format(user=ctx.author.mention), color=self.default_color)
            no = Button(label=selected_language['account']['deletion']['no_button'], style=discord.ButtonStyle.danger)
            yes = Button(label=selected_language['account']['deletion']['yes_button'], style=discord.ButtonStyle.green)
            no.callback = no_callback
            yes.callback = yes_callback
            view = View()
            view.add_item(no)
            view.add_item(yes)
            await ctx.respond(embed=confirm, view=view, ephemeral=True)
        else:
            selected_language = self.en_lang
            error = discord.Embed(description=selected_language['errors']['account']['details'], color=self.error_color)
            await ctx.respond(embed=error, ephemeral=True)


def setup(bot):
    """
    Add the Account cog to the main file
    """
    bot.add_cog(Account(bot))
