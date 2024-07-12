"""
The help file is providing commands to help
a user with Raijin commands.

Commands:
    - help
"""


import os
import json
import sys

import discord
from discord import Option
from discord.ui import Select, View

sys.path.append("..")
from sql.fetch import *


class Help(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_color = 0x37266a
        self.fr_FR_file = open(os.path.dirname(__file__) + '/../res/lang/fr_FR.json')
        self.en_EN_file = open(os.path.dirname(__file__) + '/../res/lang/en_EN.json')
        self.fr_FR = json.load(self.fr_FR_file)
        self.en_EN = json.load(self.en_EN_file)
        self.mydb = Fetch(bot).setInit()
        self.cursor = self.mydb.cursor()


    @discord.slash_command(name="help", description="⚡ Request Raiden Shogun Help")
    async def help(
        self,
        ctx,
        command: Option(
            str,
            description="Get details about a specific command",
            required = False,
            default = None
        )
    ):
        """
        Send a help menu with multiple choice/Send details about a specific command
        """
        self.mydb.ping(reconnect=True)

        lang = Fetch(self.bot).getLang(self, self.cursor, ctx.author.id, ctx.guild.id)

        if lang == "Français":
            list = self.fr_FR
        else:
            list = self.en_EN
        if command is not None:
            if command in list['commands']:
                element = discord.Embed(
                    title=list['commands'][command]['title'],
                    description=list['commands'][command]['details'],
                    color=self.default_color
                )
                await ctx.respond(embed=element)
                return
            else:
                error = discord.Embed(
                    title=list['errors']['commands']['title'],
                    description=list['errors']['commands']['details'],
                    color=0xFF0000
                )
                await ctx.respond(embed=error)
                return

        m_title = list['help']['title']
        m_description = list['help']['description']
        m_category = Select(
            options=[
                discord.SelectOption(label=list['help']['options']['story']['title'], value="H", \
                    description=list['help']['options']['story']['description'], emoji="<:heizouimthebest:1081239099039547472>"),
                discord.SelectOption(label=list['help']['options']['shops']['title'], value="S", \
                    description=list['help']['options']['shops']['description'], emoji="<:ayatomilkteatime:1081241425846472704>"),
                discord.SelectOption(label=list['help']['options']['quests']['title'], value="Q", \
                    description=list['help']['options']['quests']['description'], emoji="<:paimonrelieved:1081240022423974008>"),
                discord.SelectOption(label=list['help']['options']['personal']['title'], value="P", \
                    description=list['help']['options']['personal']['description'], emoji="<:raidenbird:1080897824440455288>")
                ],
            placeholder=list['help']['selection'],
            min_values=1,
            max_values=1
        )
        file = discord.File("res/images/avatar-wb.png", filename="avatar.png")
        menu = discord.Embed(
            title=m_title,
            description=m_description,
            color=self.default_color
        )
        menu.set_thumbnail(url="attachment://avatar.png")

        async def m_callback(interaction):
            selected_value = interaction.data["values"][0]
            if selected_value == "H":
                story = discord.Embed(
                    title=list['help']['callback']['title'],
                    description=list['help']['callback']['description'],
                    color=self.default_color
                )
                await interaction.response.send_message(embed=story)

        m_view = View()
        m_view.add_item(m_category)
        m_category.callback = m_callback
        await ctx.respond(embed=menu, file=file, view=m_view, ephemeral=True)



def setup(bot):
     bot.add_cog(Help(bot))
