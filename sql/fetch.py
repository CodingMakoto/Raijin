"""
The fetch file is providing commands to
fetch/update/insert user informations
of/into Raijin database.

Commands:
    - setInit
    - getAccount
    - getLang
"""


import asyncio
import discord
from discord.errors import ApplicationCommandError
import mysql.connector


class Fetch(discord.Cog):
    def __init__(self, bot):
        self.bot = bot


    def setInit(self):
        try:
            self.mydb = mysql.connector.connect(
                host="",
                user="",
                password="",
                database="",
                auth_plugin="",
            )
            return self.mydb
        except TimeoutError or ConnectionError:
            raise ApplicationCommandError("Cannot connect to the database, please retry later")


    def getAccount(self, ctx, cursor, member: int, guild: int):
        cursor.execute(
            f"SELECT `NAME` FROM `Account` WHERE `ID` = '{member}' AND `GUILD` = '{guild}'"
        )
        account_exist = cursor.fetchone()
        if account_exist is not None:
            return True
        else:
            return None


    def getLang(self, ctx, cursor, member: int, guild: int):
        lang = ""
        cursor.execute(
            f"SELECT `LANG` FROM `Account` WHERE `ID` = '{member}' AND `GUILD` = '{guild}'"
        )
        lang_fetch = cursor.fetchone()
        if lang_fetch is not None:
            for languages in lang_fetch:
                lang += languages
            return lang
        else:
            return None


def setup(bot):
    bot.add_cog(Fetch(bot))
