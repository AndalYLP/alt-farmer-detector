from discord.ext import commands

from commands.snipe_commands.joinsoff_snipe import snipe_joinsoff
from commands.snipe_commands.snipe_player import snipe_player
from utils.categories import joinsoff_sub_group, snipe_group

joinsoff_sub_group.add_command(snipe_joinsoff)
snipe_group.add_command(snipe_player)


class snipe_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.tree.add_command(snipe_group)


async def setup(bot: commands.Bot):
    await bot.add_cog(snipe_cog(bot))
