import asyncio
import os
from copyreg import constructor
from threading import Thread

import discord
from discord.ext import commands
from flask import Flask
from loguru import logger
from waitress import serve

import RobloxPy
from config.constants import COOKIE, TOKEN
from reports import get_status

app = Flask(__name__)


@app.route("/")
def answer():
    return "Alive"


Thread(target=lambda: serve(app, host="0.0.0.0", port=8080)).start()


RobloxPy.cookies.set_cookie(COOKIE)
logger.level("COMMAND", no=25, color="<yellow>")


class Bot(commands.Bot):
    async def setup_hook(self):
        await self.loadExtensions()

    async def loadExtensions(self):
        commands_path = os.path.join(os.path.dirname(__file__), "commands")
        extensions = []

        if not os.path.isdir(commands_path):
            logger.error(f"The commands directory does not exist: {commands_path}")
            return

        for filename in os.listdir(commands_path):
            extensions.append("commands." + filename)

        for extension in extensions:
            try:
                await self.load_extension(extension)
                logger.info(f"Loaded extension {extension}")
            except Exception as e:
                logger.exception(e)


bot = Bot(command_prefix="!", intents=discord.Intents.all())
bot.tracking = {}


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user.name} ({bot.user.id})")

    await bot.change_presence(activity=discord.Game(name="Ranked BedWars"))

    bot.loop.create_task(get_status(bot))
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {synced} tree(s)")
    except Exception as e:
        logger.error(f"Failed to sync tree(s): {e}")


asyncio.run(bot.start(TOKEN))
