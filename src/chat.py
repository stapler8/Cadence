import discord
from discord import app_commands
from discord.ext import commands

import random

# import our global settings file
import settings


class Chat(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="flip")
    async def flip(self, interaction: discord.Interaction):
        """Flip a coin!"""

        if random.choice(["Heads", "Tails"]) == "Heads":
            with open('./img/coin-heads.png', 'rb') as f:
                picture = discord.File(f)
                await interaction.response.send_message(file=picture)

        else:
            with open('./img/coin-tails.png', 'rb') as f:
                picture = discord.File(f)
                await interaction.response.send_message(file=picture)

    @app_commands.command(name="roll")
    async def roll(self, interaction: discord.Interaction, amount: int = 3, sides: int = 6):
        """Roll some dice!"""

        if sides < 1 or sides > settings.settings["maxDieSize"]:
            await interaction.response.send_message(f"Sides must be > 0 and <= {settings.settings['maxDieSize']}",
                                                    ephemeral=True)
            return

        if amount < 1 or amount > settings.settings["maxDice"]:
            await interaction.response.send_message(f"Amount of dice must be >0 and <= {settings.settings['maxDice']}",
                                                    ephemeral=True)
            return

        message = "Your rolls:"

        for die in range(amount):
            result = random.randint(1, sides)
            if die % settings.settings["rollsPerLine"] == 0:
                message += '\n'
            message += f"{result}\t"

        await interaction.response.send_message(message)

    @app_commands.command(name="rofl")
    async def rofl(self, interaction: discord.Interaction):
        """ROFLCOPTER!"""

        with open('./img/roflcopter.gif', 'rb') as f:
            picture = discord.File(f)
            await interaction.response.send_message(file=picture)


# add our cog to the bot, so it's all run on startup.
async def setup(bot):
    await bot.add_cog(Chat(bot))
