from discord.ext import commands

from .joinsoff_snipe import JoinsOffSnipeCommand
from .snipe_player import SnipePlayerCommand


async def setup(bot: commands.Bot):
    await bot.add_cog(SnipePlayerCommand(bot))
    await bot.add_cog(JoinsOffSnipeCommand(bot))
