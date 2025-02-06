import asyncio

import discord
from discord.ext import commands

from .stop_track import StopTrackCommand
from .track import TrackCommand


async def setup(bot: commands.Bot):
    await asyncio.gather(
        bot.add_cog(TrackCommand(bot)), bot.add_cog(StopTrackCommand(bot))
    )
