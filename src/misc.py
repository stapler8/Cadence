import discord
from discord import app_commands
from discord.ext import commands

import json

from settings import settings

servers = {}

class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def writecfg(self, output):
        try:
            with open("cfg/cfg.json", "w") as f:
                json.dump(settings, f)

        except Exception as ex:
            print(f"WARN: Could not write to file.\nEXCEPTION: {ex}")

    @app_commands.command(name="rofl")
    async def rofl(self, interaction: discord.Interaction):
        with open('./img/roflcopter.gif', 'rb') as f:
            picture = discord.File(f)
            await interaction.response.send_message(file=picture)

    @app_commands.command(name="setting")
    async def setting(self, interaction: discord.Interaction, setting: str, value: str):
        if setting in settings.keys():
            try:
                settings[setting] = value
                await interaction.response.send_message(f"Setting {setting} changed to {value}",
                                                        ephemeral=True)

            except Exception as ex:
                await interaction.response.send_message(f"Setting {setting} cannot be changed to {value}\n" +
                                                  f"error: {ex}", ephemeral=True)
                return

            try:
                await self.writecfg(settings)

            finally:
                await interaction.response.send_message(f"Setting {setting} successfully changed to {value}",
                                                        ephemeral=True)

        else:
            await interaction.response.send_message(f"Invalid setting {setting}, see README.md",
                                                    ephemeral=True)

    @app_commands.command(name="getsetting")
    async def getsetting(self, interaction: discord.Interaction, setting: str):
        if setting in settings.keys():
            await interaction.response.send_message(f"Setting {setting} has a value of {settings[setting]}",
                                                    ephemeral=True)

        else:
            await interaction.response.send_message(f"Invalid setting {setting}, see README.md",
                                                    ephemeral=True)


async def setup(bot):
    await bot.add_cog(Misc(bot))
