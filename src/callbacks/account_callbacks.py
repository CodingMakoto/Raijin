"""
The account callbacks file is providing callbacks for the account file
(Functions using buttons and other view components)

Functions:
    - end_yes
    - end_no
"""

import discord

from config.env import Database


async def end_yes(interaction, author, guild, selected_language, default_color):
    """
    Delete the account of the user and send a confirmation message
    """
    db = Database()
    conn = db.connect()
    cursor = conn.cursor()

    delete = discord.Embed(
        description=selected_language["account"]["deletion"]["deleted"].format(
            user=author.mention
        ),
        color=default_color,
    )
    cursor.execute(
        "DELETE FROM `Account` WHERE `ID` = %s AND `GUILD` = %s", (author.id, guild.id)
    )
    conn.commit()
    cursor.execute(
        "DELETE FROM `Story` WHERE `ID` = %s AND `GUILD` = %s", (author.id, guild.id)
    )
    conn.commit()
    cursor.execute(
        "DELETE FROM `Quests` WHERE `ID` = %s AND `GUILD` = %s", (author.id, guild.id)
    )
    conn.commit()
    cursor.execute(
        "DELETE FROM `Cooldown` WHERE `ID` = %s AND `GUILD` = %s", (author.id, guild.id)
    )
    conn.commit()
    await interaction.response.edit_message(embed=delete, view=None)


async def end_no(interaction, author, selected_language, default_color):
    """
    Cancel the account deletion and send a cancellation message
    """
    stop = discord.Embed(
        description=selected_language["account"]["deletion"]["cancelled"].format(
            user=author.mention
        ),
        color=default_color,
    )
    await interaction.response.edit_message(embed=stop, view=None)
