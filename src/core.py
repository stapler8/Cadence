import discord
from discord import app_commands
from discord.ext import commands

import json

import settings

servers = {}


async def write_cfg():
    try:
        # await write_settings()

        with open("cfg/cfg.json", "w") as f:
            json.dump(settings.settings, f)

    except Exception as ex:
        print(f"WARN: Could not write to file.\nEXCEPTION: {ex}")


class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setadminrole")
    async def setadminrole(self, interaction: discord.Interaction, role_id: str):
        """Set the admin role during initial setup"""

        if settings.settings["adminRoleID"] != 0:
            await interaction.response.send_message("Admin role ID already set", ephemeral=True)
            return

        try:
            settings.settings["adminRoleID"] = int(role_id)
            await write_cfg()
            await interaction.response.send_message(
                "Admin Role ID set!\nNote: Bot must restart for this setting to be applied", ephemeral=True)

        except Exception as ex:
            await interaction.response.send_message(f"Exception: {ex}", ephemeral=True)

    @app_commands.command(name="setting")
    @app_commands.checks.has_role(settings.settings["adminRoleID"])
    async def setting(self, interaction: discord.Interaction, setting: str, value: str):
        """Modify a setting value"""

        if setting.lower() == "adminroleid":
            await interaction.response.send_message("Error: adminRoleID must be set with /setadminrole", ephemeral=True)
            return
        if setting.lower() == "version":
            await interaction.response.send_message("Error: version can not be changed", ephemeral=True)
            return

        for s in settings.settings:
            if setting.lower() == s.lower():
                setting = s
                break
        else:
            await interaction.response.send_message(f"Invalid setting {setting}, see README.md", ephemeral=True)
            return

        try:

            # set booleans to lowercase
            if value.lower() == "true" or value.lower() == "false":
                value = value.lower()
            settings.settings[setting] = type(settings.settings[setting])(value)
            await interaction.response.send_message(f"Setting {setting} changed to {value}",
                                                    ephemeral=True)

        except Exception as ex:
            await interaction.response.send_message(f"Setting {setting} cannot be changed to {value}\n" +
                                                    f"error: {ex}", ephemeral=True)
            return

        try:
            await write_cfg()

        finally:
            await interaction.response.send_message(f"Setting {setting} successfully changed to {value}",
                                                    ephemeral=True)

    @setting.error
    async def setting_handler(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message("Command /setting requires Administrator role", ephemeral=True)

    @app_commands.command(name="getsetting")
    @app_commands.checks.has_role(settings.settings["adminRoleID"])
    async def getsetting(self, interaction: discord.Interaction, setting: str):
        """Get the value of a setting"""

        if setting.lower() in (s.lower() for s in settings.settings):
            await interaction.response.send_message(f"Setting {setting} has a value of {settings.settings[setting]}",
                                                    ephemeral=True)

        else:
            await interaction.response.send_message(f"Invalid setting {setting}, see README.md",
                                                    ephemeral=True)

    @getsetting.error
    async def getsetting_handler(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message("Command /getsetting requires Administrator role", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Misc(bot))
