import asyncio

import discord
from discord.ext import commands

from .added_with import AddedWithCommand
from .ingame import InGameCommand
from .mutuals import MutualsCommand


async def setup(bot: commands.Bot):
    asyncio.gather(
        bot.add_cog(MutualsCommand(bot)),
        bot.add_cog(InGameCommand(bot)),
        bot.add_cog(AddedWithCommand(bot)),
    )
