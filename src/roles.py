# import dependencies
import discord
from discord import app_commands
from discord.ext import commands

import asyncio
from settings import settings


async def getcolours(guild):
    colours = []
    for role in guild.roles:
        if role.name.startswith(settings["colourPrefix"]):
            colours.append(discord.SelectOption(label=role.name, value=role.id))

    return colours

# class Selector(discord.ui.view):
#
#     @discord.ui.select(options=colours)
#     async def select_callback(self, select, interaction: discord.Interaction):


class Roles(commands.Cog):

    colours = []

    def __init__(self, bot):
        self.bot = bot
        self.colours = getcolours(bot.guild)










async def setup(bot):
    await bot.add_cog(Roles(bot))
