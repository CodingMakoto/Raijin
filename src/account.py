"""
The account file is providing commands to manage the user account
with Raijin.

Commands:
    - start
    - end
"""

import os.path
import json

import discord
from discord.ext import commands
from discord import Option, SlashCommandGroup
from discord.ui import View, Button
import mysql.connector
from functools import partial

from config.env import Database
from src.callbacks.account_callbacks import end_yes, end_no


class Account(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_color = 0x37266A
        self.error_color = 0xFF0000
        self.db = Database()
        self.conn = self.db.connect()
        self.cursor = self.conn.cursor()
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

    account = SlashCommandGroup("account", "Everything about your Account with Raijin")

    @account.command(name="start", description="🔍 Ready for a new adventure ?")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def start(
        self,
        ctx,
        language: Option(
            str,
            "What language do you want to use ?",
            choices=["Français", "English"],
            required=True,
        ),  # type: ignore
        uid: Option(
            str,
            "You can enter your Genshin Impact UID to be used with other commands",
            required=False,
        ),  # type: ignore
        nickname: Option(
            str, "You can choose a name for this adventure", required=False
        ),  # type: ignore
    ):
        """
        The start command is used to create a new account
        with Raijin, the user can choose a language and a nickname.
        The user can also enter a Genshin Impact UID to be used
        with other commands.
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

            name = nickname or ctx.author.display_name
            uid = uid or "0"
            uid_valid = (
                uid != "0" and (len(uid) == 9 or len(uid) == 10) and uid.isnumeric()
            ) or uid == "0"

            if fetched_account is not None:
                selected_language = (
                    self.fr_lang if fetched_account[0] == "Français" else self.en_lang
                )
                error = discord.Embed(
                    description=selected_language["account"]["creation"]["existing"],
                    color=self.error_color,
                )
                await ctx.respond(embed=error, ephemeral=True)
            else:
                selected_language = (
                    self.fr_lang if language == "Français" else self.en_lang
                )
                if uid_valid:
                    cursor.execute(
                        "INSERT INTO `Account` (`ID`, `GUILD`, `UID`, `NAME`, `LANG`) VALUES \
                        (%s, %s, %s, %s, %s)",
                        (ctx.author.id, ctx.guild.id, uid, name, language),
                    )
                    conn.commit()
                    cursor.execute(
                        "INSERT INTO `Story` (`ID`, `GUILD`, `CHAPTER`, `COINS`, `ECHOS`, `BOSSES`, `HEALTH`, `STATUES`) VALUES \
                        (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (ctx.author.id, ctx.guild.id, 1, 0, 0, 0, 10000, 0),
                    )
                    conn.commit()
                    cursor.execute(
                        "INSERT INTO `Quests` (`ID`, `GUILD`, `QUEST1`, `QUEST2`, `QUEST3`, `DONE`) VALUES \
                        (%s, %s, %s, %s, %s, %s)",
                        (ctx.author.id, ctx.guild.id, "None", "None", "None", "False"),
                    )
                    conn.commit()
                    creation = discord.Embed(
                        description=selected_language["account"]["creation"][
                            "created"
                        ].format(user=ctx.author.mention),
                        color=self.default_color,
                    )
                    await ctx.respond(embed=creation)
                else:
                    error = discord.Embed(
                        description=selected_language["account"]["creation"][
                            "wrong_uid"
                        ],
                        color=self.error_color,
                    )
                    await ctx.respond(embed=error, ephemeral=True)
        except mysql.connector.Error:
            raise
        finally:
            cursor.close()
            conn.close()

    @account.command(name="end", description="🧳 Return to your home world")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def end(self, ctx):
        """
        The end command is used to close the account of the user
        by erasing all the user information.
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

                confirm = discord.Embed(
                    description=selected_language["account"]["deletion"][
                        "confirmation"
                    ].format(user=ctx.author.mention),
                    color=self.default_color,
                )

                no = Button(
                    label=selected_language["account"]["deletion"]["no_button"],
                    style=discord.ButtonStyle.danger,
                )
                yes = Button(
                    label=selected_language["account"]["deletion"]["yes_button"],
                    style=discord.ButtonStyle.green,
                )
                yes.callback = partial(
                    end_yes,
                    author=ctx.author,
                    guild=ctx.guild,
                    selected_language=selected_language,
                    default_color=self.default_color,
                )
                no.callback = partial(
                    end_no,
                    author=ctx.author,
                    selected_language=selected_language,
                    default_color=self.default_color,
                )
                view = View()
                view.add_item(no)
                view.add_item(yes)
                await ctx.respond(embed=confirm, view=view, ephemeral=True)
            else:
                selected_language = self.en_lang
                error = discord.Embed(
                    description=selected_language["errors"]["account"],
                    color=self.error_color,
                )
                await ctx.respond(embed=error, ephemeral=True)
        except mysql.connector.Error:
            raise
        finally:
            cursor.close()
            conn.close()


def setup(bot):
    """
    Add the Account cog to the main file
    """
    bot.add_cog(Account(bot))
