import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from config.command_description import UtilsDesc
from config.embeds import error_embed
from utils.categories import utils_group
from utils.exceptions import ProtectedCategory


class PurgeCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.debug("im being called correctly")

    @utils_group.command(name="purge", description=UtilsDesc.purge)
    @app_commands.describe(amount=UtilsDesc.amount)
    async def purge_command(self, interaction: discord.Interaction, amount: int):
        logger.log(
            "COMMAND",
            f"{interaction.user.name} used {interaction.command.name} command",
        )

        try:
            if interaction.channel.category_id not in [
                1290762586161414164,
                1290715720321208462,
                1298707633594961950,
                1277035299528114187,
            ]:
                deleted = await interaction.channel.purge(limit=amount)

                await interaction.response.send_message(
                    content=f"purged {len(deleted)} message{"s" if len(deleted) > 1 else ""}."
                )
            else:
                raise ProtectedCategory(
                    interaction.channel.category.name, interaction.command.name
                )
        except Exception as e:
            logger.exception(e)
            await interaction.response.send_message(embed=error_embed(e))
