import discord
from discord import app_commands
from loguru import logger

import RobloxPy
from config.constants import USERS_COLLECTION
from config.embeds import error_embed
from utils.exceptions import UserNotFound


@app_commands.command(name="player", description="Add a player to the loop.")
@app_commands.describe(
    username="the username to add.",
    groupname="Group name, None = no group.",
    alt_account="True if its an alt account.",
)
async def add_player(
    interaction: discord.Interaction,
    username: str,
    alt_account: bool,
    groupname: str,
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
                    "GroupName": groupname,
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
                        "GroupName": groupname,
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
