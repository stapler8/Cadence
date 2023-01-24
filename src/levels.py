import discord
from discord import app_commands
from discord.ext import commands

import random
import json
import time

# import our global settings file
from settings import settings

# add a custom setting for our file
settings["testMessage"] = "Hello!"

experience = {}
levels = []

# get experience and level values
try:
    with open("data/experience.json", "x") as f:
        json.dump({}, f)
        print("No levels file found, creating one")

except FileExistsError:
    with open("data/experience.json") as f:
        experience = json.load(f)
    print("Loaded levels data")

try:
    with open("cfg/levels.json", "x") as f:
        lvl = [100]
        for i in range(100):
            lvl.append(int(lvl[len(lvl) - 1] * 1.2 + 50))
        json.dump(lvl, f)

except FileExistsError:
    with open ("cfg/levels.json") as f:
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
        print (f"{experience}, {currentLevel}")
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

                experience[userid] = {"experience": 10, "timestamp": time.time()}
                print(f"Added {message.author.name} to experience")

                await writeExperience()

            else:

                # make sure user isn't getting exp too fast
                if time.time() - experience[userid]["timestamp"] >= 15:
                    experience[userid]["experience"] += random.randrange(10, 20)
                    experience[userid]["timestamp"] = time.time()

                    await writeExperience()
                    print(f"Added xp to {message.author.name}")

    @app_commands.command(name="level")
    async def level(self, interaction: discord.Interaction):
        """Get your current level"""
        if str(interaction.user.id) not in experience.keys():
            await interaction.response.send_message("Your level is 0")

        else:
            userid = str(interaction.user.id)
            userlevel = await getLevel(experience[userid]["experience"])
            await interaction.response.send_message(f"Your level is {userlevel}")


    # Create our test command with an optional message argument
    # @app_commands.command(name="level")
    # async def test(self, interaction: discord.Interaction, message: str = settings["testMessage"]):
    #
    #     # send our response to the user. if the message should be viewable by all, exclude the ephemeral argument.
    #     await interaction.response.send_message(message, ephemeral=True)


# add our cog to the bot, so it's all run on startup.
async def setup(bot):
    await bot.add_cog(Levels(bot))