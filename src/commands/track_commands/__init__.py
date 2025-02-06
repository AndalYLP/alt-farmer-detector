from discord.ext import commands

from commands.track_commands.stop_track import stop
from commands.track_commands.track import player
from utils.categories import track_group

track_group.add_command(stop)
track_group.add_command(player)


class track_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.tree.add_command(track_group)


async def setup(bot: commands.Bot):
    await bot.add_cog(track_cog(bot))
