import os

import discord
from discord.ext import commands

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
        print("Syncing commands")
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")

    except Exception as ex:
        print(ex)

    print("Bot is ready!")

print("Loading bot")
bot.run(os.getenv("TOKEN"))
