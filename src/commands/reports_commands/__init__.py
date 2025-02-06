from discord.ext import commands

from commands.reports_commands.add_player import add_player
from commands.reports_commands.mute import mute
from commands.reports_commands.notifications import notifications
from commands.reports_commands.resume import resume_loop
from commands.reports_commands.stop import stop_loop
from utils.categories import add_sub_group, reports_group

add_sub_group.add_command(add_player)
reports_group.add_command(mute)
reports_group.add_command(notifications)
reports_group.add_command(resume_loop)
reports_group.add_command(stop_loop)


class reports_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.tree.add_command(reports_group)


async def setup(bot: commands.Bot):
    await bot.add_cog(reports_cog(bot))
