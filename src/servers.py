import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View, RoleSelect

import json

# import our global settings file
from settings import settings

servers = {}

# get server data from file
try:
    with open("data/servers.json", "x") as f:
        json.dump({}, f)
        print("No server file found, creating one")

except FileExistsError:
    with open("data/servers.json") as f:
        servers = json.load(f)
    print("Loaded server data")

async def writeServers():
    try:
        with open("data/servers.json", "w") as f:
            json.dump(servers, f)

    except Exception as ex:
        print(f"WARN: Could not write to file.\nEXCEPTION: {ex}")

async def checkID(interaction: discord.Interaction, role: int):
    for role in interaction.user.roles:
        if role.id == role:
            return True
    return False

class Servers(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Create our test command with an optional message argument
    @app_commands.command(name="addserver")
    @app_commands.checks.has_role(settings["adminRoleID"])
    async def addserver(self, interaction: discord.Interaction, name: str, address: str, description: str = ""):
        """Add a server to the list"""

        if not name or not address:
            interaction.response.send_message(f"Error: Servers require a name and address", ephemeral=True)

        if name.lower() in servers.keys():
            interaction.response.send_message(f"Error: {name} already in server list", ephemeral=True)
            return

        newserver = {
            "name": name.lower(),
            "address": address,
            "description": description
        }

        servers[name.lower()] = newserver
        await writeServers()
        await interaction.response.send_message(f"{name} added to server list", ephemeral=True)

    @app_commands.command(name="servers")
    async def servers(self, interaction: discord.Interaction):
        """View information about a server"""

        # Optionally disallow unauthorised access to the server list
        if settings["clubhouseRoleID"] != 0:
            if not await checkID(interaction, settings["clubhouseRoleID"]):
                await interaction.response.send_message("Error: You do not have the required role to use this command",
                                                        ephemeral=True)
                return

        if not servers:
            await interaction.response.send_message("No servers found", ephemeral=True)
            return

        # Create our list of servers for the selector
        serverlist = []
        for server in servers.keys():
            serverlist.append(discord.SelectOption(label=server))
        select = discord.ui.Select(placeholder="Select a server", options=serverlist)

        async def servers_callback(interaction: discord.Interaction):

            # Find the server the user selected
            selection = {}
            for server in servers:
                if select.values[0].lower() == server:
                    selection = servers[server]
                    break

            if not selection['description']:
                selection['description'] = "None"
            await interaction.response.send_message(f"""Server Info:
            Name: {selection['name']}
            Address: {selection['address']}
            \nDescription: {selection['description']}""", ephemeral=True)

        select.callback = servers_callback

        view = View()
        view.add_item(select)

        await interaction.response.send_message("Select a server: ", view=view, ephemeral=True)

    @app_commands.command(name="removeserver")
    @app_commands.checks.has_role(settings["adminRoleID"])
    async def removeserver(self, interaction: discord.Interaction, name: str):
        """Remove a server from the list"""

        if not name:
            await interaction.response.send_message(f"Error: Must provide a name", ephemeral=True)
            return

        if not name.lower() in servers.keys():
            await interaction.response.send_message(f"Error: Server name not found", ephemeral=True)
            return

        servers.pop(name.lower())
        await writeServers()
        await interaction.response.send_message(f"Server {name} successfully removed", ephemeral=True)

# add our cog to the bot, so it's all run on startup.
async def setup(bot):
    await bot.add_cog(Servers(bot))