import asyncio
from time import time

import discord
from discord import app_commands
from loguru import logger

import RobloxPy
from config.colors import presenceTypeCode
from config.command_description import SnipeDesc
from config.embeds import error_embed
from utils.exceptions import InvalidAmountOfUsernames, UserNotFound

debounce = False
current_data = None
current_images = None
tokens_time = None
busy = False


@app_commands.command(name="player", description=SnipeDesc.snipePlayerJoinsOff)
@app_commands.describe(
    usernames=SnipeDesc.usernameJoinsOff, forceupdate=SnipeDesc.forceUpdate
)
async def snipe_joinsoff(
    interaction: discord.Interaction, usernames: str, forceupdate: bool
):
    logger.log(
        "COMMAND",
        f"{interaction.user.name} used {interaction.command.name} command",
    )

    if busy:
        await interaction.response.send_message(
            "The command is currently busy, please try again later."
        )
        return

    if debounce and forceupdate:
        await interaction.response.send_message(
            "The command is currently on cooldown, please try again later."
        )
        return

    await interaction.response.defer(thinking=True)

    try:
        usernames = [
            username.strip() for username in usernames.replace(",", " ").split()
        ]

        if len(usernames) < 1:
            raise InvalidAmountOfUsernames(1)

        thumbnailObject, users = RobloxPy.Thumbnails.get_users_avatar_from_username(
            *usernames
        )

        for username in usernames:
            if not users.get_by_requested_username(username):
                raise UserNotFound(username)

        if forceupdate:
            debounce = True
            busy = True

            servers_group = RobloxPy.Games.get_all_servers(6872265039)
            current_data = servers_group
            tokens_time = time()
        else:
            server_group: RobloxPy.Games.Servers.ServerGroup = current_data

        current_images = await server_group.get_player_thumbnails()

        for thumbnail in thumbnailObject.thumbnails:
            if thumbnail in current_images:
                await interaction.followup.send(
                    content=f"<t:{int(time())}:R>{f"Data from:<t:{int(tokens_time)}:R>" if not forceupdate else ""}",
                    embed=discord.Embed(
                        color=presenceTypeCode[2][0],
                        title=f"Found {users.get_by_requested_username(username).username}'s server!",
                        description=f"Game: **BedWars** (yes.)\nLobby: **True** (yes.)\nGameId: **{current_images.get_by_imageurl(thumbnail.imageUrl).requestId}**",
                    ),
                )
            else:
                await interaction.followup.send(
                    embed=discord.Embed(
                        color=16765440,
                        title="Error",
                        description=f"didn't find the given player {users.get_by_userid(thumbnail.targetId).username}.",
                    ),
                )

            await asyncio.sleep(60)
            debounce = False

    except Exception as e:
        logger.exception(e)
        busy = False
        await interaction.response.send_message(embed=error_embed(e))

        if debounce:
            await asyncio.sleep(60)
            debounce = False
