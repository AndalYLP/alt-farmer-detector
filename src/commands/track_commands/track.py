import discord
from discord import app_commands
from loguru import logger

import RobloxPy
from config.command_description import TrackDesc
from config.constants import TRACKING_CATEGORY
from config.embeds import error_embed
from main import Bot
from utils.exceptions import UserNotFound


@app_commands.command(name="status", description=TrackDesc.trackStatus)
@app_commands.describe(username=TrackDesc.username)
async def status(interaction: discord.Interaction, username: str):
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
        guild = interaction.guild
        category = guild.get_channel(TRACKING_CATEGORY)

        if not Bot.tracking.get(userId) or not discord.utils.get(
            category.channels, name=username.lower()
        ):
            channel = discord.utils.get(
                category.channels, name=username.lower()
            ) or await guild.create_text_channel(username, category=category)

            Bot.tracking[userId] = [channel, [interaction.user.mention]]

            await interaction.response.send_message(f"Tracking in {channel.mention}")
        elif (
            Bot.tracking.get(userId)
            and interaction.user.mention not in Bot.tracking[userId][1]
        ):
            Bot.tracking[userId][1].append(interaction.user.mention)

            await interaction.response.send_message(
                f"added to notification list for: {Bot.tracking[userId][0].mention}"
            )
        else:
            await interaction.response.send_message(
                "This username is already being tracked.", delete_after=5
            )

    except Exception as e:
        logger.exception(e)
        await interaction.response.send_message(embed=error_embed(e))
