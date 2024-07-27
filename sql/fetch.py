"""
The fetch file is providing commands to
fetch/update/insert user information
of/into Raijin database.

Commands:
    - getAccount
    - getLang
"""

import discord
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='../')
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_database = os.getenv("DB_DATABASE")
db_auth_plugin = os.getenv("DB_AUTH_PLUGIN")


class Fetch(discord.Cog):
    """
    Fetch class purpose is to have all the useful queries
    in a single file to save lines on others
    """

    def __init__(self, bot):
        self.bot = bot
        self.mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_database,
            auth_plugin=db_auth_plugin,
        )
        self.cursor = self.mydb.cursor()

    def getaccount(self, member: int, guild: int):
        """
        Look for an existing account with the information given,
        return None if not existing
        """
        self.cursor.execute(
            f"SELECT `NAME` FROM `Account` WHERE `ID` = '{member}' AND `GUILD` = '{guild}'"
        )
        account_exist = self.cursor.fetchone()
        if account_exist is not None:
            return True
        return None

    def getlang(self, member: int, guild: int):
        """
        Look for an existing language with the information given,
        return None if not existing
        """
        lang = ""
        self.cursor.execute(
            f"SELECT `LANG` FROM `Account` WHERE `ID` = '{member}' AND `GUILD` = '{guild}'"
        )
        lang_fetch = self.cursor.fetchone()
        if lang_fetch is not None:
            for languages in lang_fetch:
                lang += languages
            return lang
        return None


def setup(bot):
    """
    Add the Fetch cog to the main file
    """
    bot.add_cog(Fetch(bot))
