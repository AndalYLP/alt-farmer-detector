import traceback
import asyncio
import time
import os

from discord import app_commands
from discord.ext import commands
from loguru import logger
import discord

from utils import format_user_embed, error_embed, presenceTypeCode, UserNotFound
from CommandDescriptions import SnipeDesc
import RobloxPy

# --------------------------------- Data -------------------------------- #

Debounce = False
currentData = None
TokensTime = None
busy = False

# ------------------------------------ Cog ----------------------------------- #


class SnipeCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    mainGroup = app_commands.Group(name="snipe", description="Snipe commands")

    joinsOffGroup = app_commands.Group(
        name="joinsoff", description="joinsoff commands", parent=mainGroup
    )

    # --------------------------- Snipe player command --------------------------- #

    @mainGroup.command(name="player", description=SnipeDesc.snipePlayer)
    @app_commands.describe(usernames=SnipeDesc.usernamesSnipe)
    async def player(self, interaction: discord.Interaction, usernames: str):
        logger.log(
            "COMMAND",
            f"{interaction.user.name} used {interaction.command.name} command",
        )

        try:
            if "," in usernames:
                usernames = usernames.split(",")
            else:
                usernames = usernames.split()

            if not isinstance(usernames, list):
                usernames = [usernames]

            presenceGroup, users = await RobloxPy.Presence.get_presence_from_username(
                *usernames
            )

            for username in usernames:
                if not users.get_by_requested_username(username):
                    raise UserNotFound(username)

            embeds = []
            for presence in presenceGroup.presences:
                user = users.get_by_userid(presence.userId)

                embeds.append(
                    format_user_embed(
                        presenceType=presence.userPresenceType,
                        username=user.username,
                        game=presence.lastlocation,
                        lobby="True" if presence.placeId == 6872265039 else "False",
                        jobId=presence.jobId,
                        groupOrLastOnline=presence.lastOnline,
                        thumbnail=user.get_thumbnail().imageUrl,
                    )
                )

            embedGroups = [
                [embed for embed in embeds[i : i + 10]]
                for i in range(0, len(embeds), 10)
            ]
            for i, embedGroup in enumerate(embedGroups):
                if i != 0:
                    await interaction.followup.send(
                        content=f"<t:{int(time.time())}:R>", embeds=embedGroup
                    )
                else:
                    await interaction.response.send_message(
                        content=f"<t:{int(time.time())}:R>", embeds=embedGroup
                    )
        except Exception as e:
            logger.exception(e)
            await interaction.response.send_message(embed=error_embed(e))

    # -------------------------- Joins off snipe command ------------------------- #
    @joinsOffGroup.command(name="player", description=SnipeDesc.snipePlayerJoinsOff)
    @app_commands.describe(
        username=SnipeDesc.usernameJoinsOff, forceupdate=SnipeDesc.forceupdate
    )
    async def joinsOffPlayer(
        self, interaction: discord.Interaction, username: str, forceupdate: bool
    ):
        logger.log(
            "COMMAND",
            f"{interaction.user.name} used {interaction.command.name} command",
        )

        global Debounce, currentData, TokensTime, busy

        if busy:
            await interaction.response.send_message(
                "Im busy rn!.", delete_after=3, ephemeral=True
            )

        if Debounce and forceupdate:
            await interaction.response.send_message(
                "On cooldown, pls wait.", delete_after=3, ephemeral=True
            )

        await interaction.response.defer(thinking=True)

        try:
            thumbnailObject, users = RobloxPy.Thumbnails.get_users_avatar_from_username(
                username
            )

            if not users.get_by_requested_username(username):
                raise UserNotFound(username)

            thumbnail = thumbnailObject.get_by_targetid(
                users.get_by_requested_username(username).userId
            )

            if forceupdate:
                busy = True
                serverGroup = RobloxPy.Games.get_all_servers(6872265039)
                currentData = serverGroup
                TokensTime = round(time.time())
                busy = False
                Debounce = True
            else:
                serverGroup: RobloxPy.Games.Servers.ServerGroup = currentData

            imageUrls = await serverGroup.get_player_thumbnails()

            if thumbnail in imageUrls:
                await interaction.followup.send(
                    content=f"<t:{int(time.time())}:R>{f"Data from:<t:{int(TokensTime)}:R>" if forceupdate else ""}",
                    embed=discord.Embed(
                        color=presenceTypeCode[2][0],
                        title=f"Found {users.get_by_requested_username(username).username}'s server!",
                        description=f"Game: **Bedwars** (yes.)\nLobby: **True** (yes.)\nGameId: **{imageUrls.get_by_imageurl(thumbnail.imageUrl).requestId}**",
                    ),
                )
            else:
                await interaction.followup.send(
                    embed=discord.Embed(
                        color=16765440,
                        title="Error",
                        description="didn't find the given player.",
                    ),
                )

            await asyncio.sleep(60)
            Debounce = False

        except Exception as e:
            logger.exception(e)
            busy = False
            await interaction.followup.send(embed=error_embed(e))

            if Debounce:
                await asyncio.sleep(60)
                Debounce = False


async def setup(bot: commands.Bot):
    await bot.add_cog(SnipeCommands(bot))
