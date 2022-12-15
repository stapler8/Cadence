import discord
from discord import app_commands
from discord.ext import commands

import random

# import our global settings file
from settings import settings

# add a custom setting for our file
settings["testMessage"] = "Hello!"

class Template(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Create our test command with an optional message argument
    @app_commands.command(name="test")
    async def test(self, interaction: discord.Interaction, message: str = settings["testMessage"]):

        # send our response to the user. if the message should be viewable by all, exclude the ephemeral argument.
        await interaction.response.send_message(message, ephemeral=True)


# add our cog to the bot, so it's all run on startup.
async def setup(bot):
    await bot.add_cog(Template(bot))