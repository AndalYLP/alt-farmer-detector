from discord import app_commands
from discord.ext import commands

from commands.utils_commands.purge import purge_command


class create_utils_group(app_commands.Group):
    def __init__(self):
        super().__init__(name="utils", description="Utils commands")


utils_group = create_utils_group()

utils_group.add_command(purge_command)


class utils_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.tree.add_command(utils_group)


async def setup(bot: commands.Bot):
    await bot.add_cog(utils_cog(bot))
