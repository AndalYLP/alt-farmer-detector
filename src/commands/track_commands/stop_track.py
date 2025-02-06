import discord
from discord import app_commands
from loguru import logger

import RobloxPy
from config.command_description import TrackDesc
from config.embeds import error_embed
from main import Bot
from utils.exceptions import UserNotFound


@app_commands.command(name="track", description=TrackDesc.stopTracking)
@app_commands.describe(username=TrackDesc.username)
async def stop(interaction: discord.Interaction, username: str):
    logger.log(
        "COMMAND",
        f"{interaction.user.name} used {interaction.command.name} command",
    )

    try:
        user = RobloxPy.Users.get_users_by_username(username).get_by_requested_username(
            username
        )

        if not user:
            raise UserNotFound(username)

        userId = user.userId

        if not Bot.tracking.get(userId):
            await interaction.response.send_message(
                "This username is not being tracked.", delete_after=5
            )
            return

        if len(Bot.tracking.get(userId)[1]) == 1:
            await interaction.response.send_message(f"Stopped tracking **{username}**")

            await Bot.tracking.get(userId)[0].delete()
            Bot.tracking.pop(userId)
        else:
            Bot.tracking.get(userId)[1].remove(interaction.user.mention)

            await interaction.response.send_message(
                f"Removed from notifications for **{username}**"
            )

    except Exception as e:
        logger.exception(e)
        await interaction.response.send_message(embed=error_embed(e))
