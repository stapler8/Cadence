import discord
from discord import app_commands
from discord.ext import commands

servers = {}

class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rofl")
    async def rofl(self, interaction: discord.Interaction):
        with open('./img/roflcopter.gif', 'rb') as f:
            picture = discord.File(f)
            await interaction.response.send_message(file=picture)


    @app_commands.command(name="setting")
    async def setting(self, interaction: discord.Interaction, setting: str, value: str):
        


async def setup(bot):
    await bot.add_cog(Misc(bot))
