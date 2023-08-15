import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View, RoleSelect

import random

import settings


class Roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Create our test command with an optional message argument
    @app_commands.command(name="colour")
    async def colour(self, interaction: discord.Interaction):
        """Select a colour!"""

        colours = []
        for role in interaction.guild.roles:
            if role.name.startswith(settings.settings["colourPrefix"]):
                colours.append(discord.SelectOption(label=role.name))
        select = discord.ui.Select(placeholder="Select your colour", options=colours)

        async def colour_callback(interaction: discord.Interaction):

            newrole = discord.Role
            for role in interaction.guild.roles:
                if select.values[0] == role.name:
                    newrole = role
                    break

            for role in interaction.user.roles:
                if role.name.startswith(settings.settings["colourPrefix"]):
                    await interaction.user.remove_roles(role)

            await interaction.user.add_roles(newrole)
            await interaction.response.send_message(f"Role {newrole.name} added!", ephemeral=True)

        select.callback = colour_callback

        view = View()
        view.add_item(select)

        await interaction.response.send_message("Select your colour: ", view=view, ephemeral=True)


# add our cog to the bot, so it's all run on startup.
async def setup(bot):
    await bot.add_cog(Roles(bot))
