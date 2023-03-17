import discord
from discord import app_commands
from discord.ext import commands

import random
import json
import time

# import our global settings file
import settings

experience = {}
levels = []

# get experience and level values
try:
    with open("./data/experience.json", "x") as f:
        json.dump({}, f)
        print("No levels file found, creating one")

except FileExistsError:
    with open("./data/experience.json") as f:
        experience = json.load(f)
    print("Loaded levels data")

try:
    with open("./cfg/levels.json", "x") as f:
        lvl = [250]
        for i in range(settings.settings["levelsMaxLevel"]):
            lvl.append(int(lvl[len(lvl) - 1] * 1.3 + 50))
        json.dump(lvl, f)

except FileExistsError:
    with open ("./cfg/levels.json") as f:
        levels = json.load(f)


async def writeExperience():
    try:
        with open("data/experience.json", "w") as f:
            json.dump(experience, f)

    except Exception as ex:
        print(f"WARN: Could not write to file.\nEXCEPTION: {ex}")
        
async def getLevel(experience):
    currentLevel = 0

    for level in levels:
        # print (f"{experience}, {currentLevel}")
        if experience >= level:
            currentLevel += 1

        else:
            break

    return currentLevel

class Levels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        @bot.event
        async def on_message(message: str):

            if message.author.bot:
                return

            userid = str(message.author.id)
            if userid not in experience.keys():

                experience[userid] = {"experience": 10, "timestamp": time.time(), "level": 0, "name": message.author.name, "messageCount": 1}
                print(f"Added {message.author.name} to experience")

                await writeExperience()

            else:

                # make sure user isn't getting exp too fast
                if time.time() - experience[userid]["timestamp"] >= int(settings.settings["levelsExpCooldown"]):
                    experience[userid]["experience"] += random.randrange(10, 20)
                    experience[userid]["timestamp"] = time.time()
                    experience[userid]['name'] = message.author.name
                    experience[userid]['messageCount'] += 1

                    # check if user's level has gone up
                    if await getLevel(experience[userid]['experience']) > experience[userid]["level"]:

                        newlevel = await getLevel(experience[userid]["experience"])
                        experience[userid]["level"] = newlevel

                        # message user on level up
                        if settings.settings["levelsMinLevelToMention"] <= newlevel:
                            if settings.settings["levelsPingOnLevelUp"]:
                                await message.channel.send(f"{message.author.mention} is now level {experience[userid]['level']}!")
                            else:
                                await message.channel.send(f"{message.author.user} is now level {experience[userid]['level']}")

                    await writeExperience()
                    print(f"Added xp to {message.author.name}")

                else:
                    experience[userid]['messageCount'] += 1

    @app_commands.command(name="level")
    async def level(self, interaction: discord.Interaction, user: str = ""):
        """Get your current level"""

        username = ""
        level = 0
        exp = 0
        msgCount = 0

        if not user:

            username = interaction.user.name

            if str(interaction.user.id) in experience.keys():
                userid = str(interaction.user.id)
                level = experience[userid]['level']
                exp = experience[userid]['experience']
                msgCount = experience[userid]['messageCount']
                username = interaction.user.name

        else:
            for usr in experience.values():

                if usr['name'].lower() == user.lower():
                    level = usr['level']
                    exp = usr['experience']
                    msgCount = usr['messageCount']
                    username = usr['name']

                    break

        embed = discord.Embed(title=f"{username}:", description=f"Level: {level}\nExperience: {exp}\nMessages: {msgCount}")
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        """Get the server's exp leaderboard"""
        sortedLevels = sorted(experience.items(), key=lambda x: x[1]['experience'], reverse=True)
        leaderboard = await self.getLeaderboard(sortedLevels)

        embed = discord.Embed(title="Leaderboard", description=leaderboard)
        await interaction.response.send_message(embed=embed)

    async def getLeaderboard(self, leaderboard):
        # get a sorted leaderboard from a sorted dict of dicts
        output = ""

        # if less than 5 users in dict, display all users
        size = 5 if len(leaderboard) >= 5 else len(leaderboard)

        for i in range(size):
            user = leaderboard[i][1]
            output += f"{i + 1}: {user['name']}: Level {user['level']}, {user['experience']} Exp, {user['messageCount']} messages.\n"

        return output

async def setup(bot):
    await bot.add_cog(Levels(bot))