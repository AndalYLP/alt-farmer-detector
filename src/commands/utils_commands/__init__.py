import discord
from discord import app_commands
from discord.ext import commands

from commands.utils_commands.purge import PurgeCommand


async def setup(bot: commands.Bot):
    await bot.add_cog(PurgeCommand(bot))
