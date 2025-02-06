from discord.ext import commands

from commands.friends_commands.added_with import added_with
from commands.friends_commands.ingame import ingame
from commands.friends_commands.mutuals import mutuals
from utils.categories import friends_group

friends_group.add_command(added_with)
friends_group.add_command(ingame)
friends_group.add_command(mutuals)


class friends_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.tree.add_command(friends_group)


async def setup(bot: commands.Bot):
    await bot.add_cog(friends_cog(bot))
