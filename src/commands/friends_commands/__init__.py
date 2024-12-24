from discord.ext import commands

from .added_with import AddedWithCommand
from .ingame import InGameCommand
from .mutuals import MutualsCommand


async def setup(bot: commands.Bot):
    await bot.add_cog(MutualsCommand(bot))
    await bot.add_cog(InGameCommand(bot))
    await bot.add_cog(AddedWithCommand(bot))
