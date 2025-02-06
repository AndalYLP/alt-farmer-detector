from discord.ext import commands

from commands.list_commands.by_group import by_group
from commands.list_commands.get_list import get_list
from utils.categories import list_group

list_group.add_command(by_group)
list_group.add_command(get_list)


class list_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.tree.add_command(list_group)


async def setup(bot: commands.Bot):
    await bot.add_cog(list_cog(bot))
