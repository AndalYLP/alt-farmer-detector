import asyncio

import discord
from discord.ext import commands

from .joinsoff_snipe import JoinsOffSnipeCommand
from .snipe_player import SnipePlayerCommand


async def setup(bot: commands.Bot):
    await asyncio.gather(
        bot.add_cog(SnipePlayerCommand(bot)), bot.add_cog(JoinsOffSnipeCommand(bot))
    )
