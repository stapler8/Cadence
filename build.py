import os

from discord import app_commands
import discord
from discord.ext import commands

from settings import server, settings

from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():

    for extension in os.listdir("./src"):
        if extension.endswith('.py') and not extension.startswith("__init__") and not extension.startswith("video"):
            print(f"Loading extension {extension}")

            try:
                await bot.load_extension(f'src.{extension[:-3]}')
                print(f"Loaded {extension}")

            except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                print(f"{extension} already loaded")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")

    except Exception as ex:
        print(ex)

    print("Bot is ready!")


@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user.mention}", ephemeral=True)


@bot.tree.command(name="say")
@app_commands.describe(thing_to_say="What should I say?")
async def say(interaction: discord.Interaction, thing_to_say: str):
    await interaction.response.send_message(f"{interaction.user.name} said {thing_to_say}")


# @bot.tree.command(name="rofl")
# async def rofl(interaction: discord.Interaction):
#     await interaction.response.send_message('**ROFLCOPTER** https://c.tenor.com/hYZmNf2vDd0AAAAC/roflcopter.gif')

print("Loading bot")
bot.run(os.getenv("TOKEN"))
