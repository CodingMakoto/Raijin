"""
The quests callbacks file is providing callbacks for the quests file
(Functions using buttons and other view components)

Functions:
    - getBiome
    - bosses_action
"""

import discord

from config.env import Database


def getBiome(monster):
    """
    Get the biome of the monster based on its name
    """
    match monster:
        case "mosshide":
            return "luminara_beach"
        case "mystralith":
            return "verdant_forest"
        case _:
            return "makoto"


async def bosses_action(
    interaction, author, guild, selected_language, default_color, attack, monster
):
    """
    Select the rewards for the boss fight based on the attack type
    """
    db = Database()
    conn = db.connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT `COINS`, `ECHOS`, `BOSSES` FROM `Story` WHERE `ID` = %s AND `GUILD` = %s",
        (author.id, guild.id),
    )
    result = cursor.fetchone()
    coins, echos, bosses = result
    coins = int(coins)
    echos = int(echos)
    bosses = int(bosses)

    rewards = selected_language["quests"]["bosses"]["rewards"]["quantity"][
        f"{attack}"
    ].split(",")
    coins += int(rewards[0])
    echos += int(rewards[1])
    bosses += 1

    cursor.execute(
        "UPDATE `Story` SET `COINS` = %s, `ECHOS` = %s, `BOSSES`= %s WHERE `ID` = %s AND `GUILD` = %s",
        (coins, echos, bosses, author.id, guild.id),
    )
    conn.commit()

    cursor.execute(
        "SELECT `DONE`, `QUEST1`, `QUEST2`, `QUEST3` FROM `Quests` WHERE `ID` = %s AND `GUILD` = %s",
        (author.id, guild.id),
    )
    quest_exist = cursor.fetchone()

    if quest_exist and quest_exist[0] != "True":
        if monster == "mosshide":
            monster_quest = 0
        elif monster == "mystralith":
            monster_quest = 1
        else:
            monster_quest = None
        for i in range(1, 4):
            if monster_quest is not None and (
                (
                    quest_exist[i]
                    == selected_language["quests"]["daily"]["quests"][monster_quest]
                )
                or (quest_exist[i] == selected_language["quests"]["daily"]["quests"][3])
            ):
                cursor.execute(
                    f"UPDATE `Quests` SET `DONE` = %s, `QUEST{i}` = %s WHERE `ID` = %s AND `GUILD` = %s",
                    (
                        "Pending",
                        selected_language["quests"]["daily"]["quest_done"],
                        author.id,
                        guild.id,
                    ),
                )
                conn.commit()
                cursor.execute(
                    "SELECT `COINS`, `ECHOS` FROM `Story` WHERE `ID` = %s AND `GUILD` = %s",
                    (author.id, guild.id),
                )
                result = cursor.fetchone()
                if result:
                    coins, echos = result
                    coins = int(coins) + 10
                    echos = int(echos) + 1
                    cursor.execute(
                        "UPDATE `Story` SET `COINS` = %s, `ECHOS` = %s WHERE `ID` = %s AND `GUILD` = %s",
                        (coins, echos, author.id, guild.id),
                    )
                    conn.commit()
                break

    biome = getBiome(monster)
    file = discord.File(f"./res/images/quests/{biome}.jpg", filename="biome.jpg")
    victory = discord.Embed(
        title=selected_language["quests"]["bosses"]["title"],
        description=selected_language["quests"]["bosses"]["rewards"][f"{attack}"],
        color=default_color,
    )
    victory.set_image(url="attachment://biome.jpg")
    await interaction.response.edit_message(embed=victory, file=file, view=None)
