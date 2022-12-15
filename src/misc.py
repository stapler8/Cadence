import discord
from discord import app_commands
from discord.ext import commands
import random

import json

from settings import settings

servers = {}


async def writecfg():
    try:
        with open("cfg/cfg.json", "w") as f:
            json.dump(settings, f)

    except Exception as ex:
        print(f"WARN: Could not write to file.\nEXCEPTION: {ex}")


class Misc(commands.Cog):

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
    async def roll(self, interaction: discord.Interaction, amount: int, sides: int):
        """Roll some dice!"""

        if sides < 1 or sides >= 1000:
            await interaction.response.send_message("Sides must be > 0 and < 1000", ephemeral=True)
            return

        if amount < 1 or amount > 30:
            await interaction.response.send_message("Amount of dice must be >0 and <31")
            return



        message = ""
        if amount > 5:
            message += "Your rolls:"

        for die in range(amount):
            result = random.randint(1, sides)
            if die % 5 == 0:
                message += '\n'
            message += f"{result}\t"

        await interaction.response.send_message(message)

    @app_commands.command(name="rofl")
    async def rofl(self, interaction: discord.Interaction):
        """ROFLCOPTER!"""

        with open('./img/roflcopter.gif', 'rb') as f:
            picture = discord.File(f)
            await interaction.response.send_message(file=picture)

    @app_commands.command(name="setadminrole")
    async def setadminrole(self, interaction: discord.Interaction, role_id: str):
        """Set the admin role during initial setup"""

        if settings["adminRoleID"] == 0:
            try:
                settings["adminRoleID"] = int(role_id)
                await writecfg()
                await interaction.response.send_message("Admin Role ID set!", ephemeral=True)
            except Exception as ex:
                await interaction.response.send_message(f"Exception: {ex}", ephemeral=True)

        else:
            await interaction.response.send_message("Admin role ID already set", ephemeral=True)

    @app_commands.command(name="setting")
    @app_commands.checks.has_role(settings["adminRoleID"])
    async def setting(self, interaction: discord.Interaction, setting: str, value: str):
        """Modify a setting value"""

        # make sure our setting exists
        if setting in settings:
            try:

                # set booleans to lowercase
                if value.lower() == "true" or value.lower() == "false":
                    value = value.lower()
                settings[setting] = value
                await interaction.response.send_message(f"Setting {setting} changed to {value}",
                                                        ephemeral=True)

            except Exception as ex:
                await interaction.response.send_message(f"Setting {setting} cannot be changed to {value}\n" +
                                                        f"error: {ex}", ephemeral=True)
                return

            try:
                await writecfg()

            finally:
                await interaction.response.send_message(f"Setting {setting} successfully changed to {value}",
                                                        ephemeral=True)

        else:
            await interaction.response.send_message(f"Invalid setting {setting}, see README.md")

    @setting.error
    async def setting_handler(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message("Command /setting requires Administrator role", ephemeral=True)

    @app_commands.command(name="getsetting")
    @app_commands.checks.has_role(settings["adminRoleID"])
    async def getsetting(self, interaction: discord.Interaction, setting: str):
        """Get the value of a setting"""

        if setting in settings:
            await interaction.response.send_message(f"Setting {setting} has a value of {settings[setting]}",
                                                    ephemeral=True)

        else:
            await interaction.response.send_message(f"Invalid setting {setting}, see README.md",
                                                    ephemeral=True)

    @getsetting.error
    async def getsetting_handler(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message("Command getsetting requires Administrator role", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Misc(bot))
