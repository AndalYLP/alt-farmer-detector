import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from commands.utils_commands.purge import PurgeCommand
from config.command_description import UtilsDesc
from config.embeds import error_embed
from utils.exceptions import ProtectedCategory


async def setup(bot: commands.Bot):
    await bot.add_cog(PurgeCommand(bot))
