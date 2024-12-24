from discord.ext import commands

from .stop_track import StopTrackCommand
from .track import TrackCommand


async def setup(bot: commands.Bot):
    await bot.add_cog(TrackCommand(bot))
    await bot.add_cog(StopTrackCommand(bot))
