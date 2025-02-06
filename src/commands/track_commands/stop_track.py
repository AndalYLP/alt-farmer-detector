import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

import RobloxPy
from config.command_description import TrackDesc
from config.embeds import error_embed
from utils.categories import get_stop_sub_group, get_track_group
from utils.exceptions import UserNotFound


class StopTrackCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    stop_sub_group = get_stop_sub_group(get_track_group())

    @stop_sub_group.command(name="track", description=TrackDesc.stopTracking)
    @app_commands.describe(username=TrackDesc.username)
    async def stop(self, interaction: discord.Interaction, username: str):
        logger.log(
            "COMMAND",
            f"{interaction.user.name} used {interaction.command.name} command",
        )

        try:
            user = RobloxPy.Users.get_users_by_username(
                username
            ).get_by_requested_username(username)

            if not user:
                raise UserNotFound(username)

            userId = user.userId

            if not self.bot.tracking.get(userId):
                await interaction.response.send_message(
                    "This username is not being tracked.", delete_after=5
                )
                return

            if len(self.bot.tracking.get(userId)[1]) == 1:
                await interaction.response.send_message(
                    f"Stopped tracking **{username}**"
                )

                await self.bot.tracking.get(userId)[0].delete()
                self.bot.tracking.pop(userId)
            else:
                self.bot.tracking.get(userId)[1].remove(interaction.user.mention)

                await interaction.response.send_message(
                    f"Removed from notifications for **{username}**"
                )

        except Exception as e:
            logger.exception(e)
            await interaction.response.send_message(embed=error_embed(e))
