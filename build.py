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
    print("Bot is ready!")

    for extension in os.listdir("./src"):
        if extension.endswith('.py') and not extension.startswith("__init__") and not extension.startswith("settings"):
            await bot.load_extension(f'src.{extension[:-3]}')

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")

    except Exception as ex:
        print(ex)


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

bot.run(os.getenv("TOKEN"))
