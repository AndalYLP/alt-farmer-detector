import discord
from discord import app_commands
from loguru import logger

import RobloxPy
from config.command_description import ReportsDesc
from config.constants import USERS_COLLECTION
from config.embeds import error_embed
from utils.exceptions import UserNotFound


@app_commands.command(name="player", description=ReportsDesc.add_player)
@app_commands.describe(
    username=ReportsDesc.username,
    group_name=ReportsDesc.group_name,
    alt_account=ReportsDesc.alt_account,
)
async def add_player(
    interaction: discord.Interaction,
    username: str,
    alt_account: bool,
    group_name: str,
):
    logger.log(
        "COMMAND",
        f"{interaction.user.name} used {interaction.command.name} command",
    )

    try:
        user = RobloxPy.Users.get_users_by_username(username)
        user = user.get_by_requested_username(username)

        if not user:
            raise UserNotFound(username)

        if not USERS_COLLECTION.find_one({"UserID": user.userId}):
            result = USERS_COLLECTION.insert_one(
                {
                    "UserID": user.userId,
                    "Username": user.username,
                    "isAlt": alt_account,
                    "GroupName": group_name,
                }
            )
            if result.inserted_id:
                await interaction.response.send_message(
                    "Username added to the loop.", delete_after=3
                )
        else:
            USERS_COLLECTION.update_one(
                {"UserID": user.userId},
                {
                    "$set": {
                        "Username": user.username,
                        "isAlt": alt_account,
                        "GroupName": group_name,
                    }
                },
            )
            await interaction.response.send_message(
                "That username is already on the list, updated his data.",
                delete_after=3,
                ephemeral=True,
            )

    except Exception as e:
        logger.exception(e)
        await interaction.response.send_message(embed=error_embed(e))
