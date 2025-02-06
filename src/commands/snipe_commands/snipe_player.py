from time import time

import discord
from discord import app_commands
from loguru import logger

import RobloxPy
from config.command_description import SnipeDesc
from config.constants import GAME_ID
from config.embeds import error_embed, format_user_embed
from utils.exceptions import InvalidAmountOfUsernames, UserNotFound


@app_commands.command(name="player", description=SnipeDesc.snipePlayer)
@app_commands.describe(usernames=SnipeDesc.usernamesSnipe)
async def snipe_player(interaction: discord.Interaction, usernames: str):
    logger.log(
        "COMMAND",
        f"{interaction.user.name} used {interaction.command.name} command",
    )

    try:
        usernames = [
            username.strip() for username in usernames.replace(",", " ").split()
        ]

        if len(usernames) < 1:
            raise InvalidAmountOfUsernames(1)

        presence_group, users = await RobloxPy.Presence.get_presence_from_username(
            *usernames
        )

        for username in usernames:
            if not users.get_by_requested_username(username):
                raise UserNotFound(username)

        embeds = []
        for presence in presence_group.presences:
            user = users.get_by_userid(presence.userId)

            embeds.append(
                format_user_embed(
                    presenceType=presence.userPresenceType,
                    username=user.username,
                    game=presence.lastlocation,
                    lobby="True" if presence.placeId == GAME_ID else "False",
                    jobId=presence.jobId,
                    groupOrLastOnline=presence.lastOnline,
                    thumbnail=user.get_thumbnail().imageUrl,
                )
            )

        embedGroups = [
            [embed for embed in embeds[i : i + 10]] for i in range(0, len(embeds), 10)
        ]
        for i, embedGroup in enumerate(embedGroups):
            if i != 0:
                await interaction.followup.send(
                    content=f"<t:{int(time())}:R>", embeds=embedGroup
                )
            else:
                await interaction.response.send_message(
                    content=f"<t:{int(time())}:R>", embeds=embedGroup
                )

    except Exception as e:
        logger.exception(e)
        await interaction.response.send_message(embed=error_embed(e))
