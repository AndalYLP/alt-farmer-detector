import time

from discord import app_commands
from discord.ext import commands
from collections import Counter
from loguru import logger
import discord

from utils import (
    format_mutuals_embed,
    error_embed,
    UserNotFound,
    format_user_embed,
    format_addedwith_embed,
)
from CommandDescriptions import FriendsDesc
import RobloxPy

# ------------------------------------ Cog ----------------------------------- #


class FriendsCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    mainGroup = app_commands.Group(name="friends", description="friends commands")

    # ---------------------------------- Mutuals --------------------------------- #

    @mainGroup.command(name="mutuals", description=FriendsDesc.mutuals)
    @app_commands.describe(
        usernames=FriendsDesc.usernamesMutuals, strict=FriendsDesc.strict
    )
    async def mutuals(
        self, interaction: discord.Interaction, usernames: str, strict: bool
    ):
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

            friends, users = await RobloxPy.Friends.get_friend_users_from_username(
                *usernames
            )

            for username in usernames:
                if not users.get_by_requested_username(username):
                    raise UserNotFound(username)

            counter = Counter(
                [friend for friendList in friends.values() for friend in friendList]
            )

            if strict:
                mutuals = {
                    item: count
                    for item, count in counter.items()
                    if count == len(friends)
                }
            else:
                mutuals = {item: count for item, count in counter.items() if count == 2}

            if mutuals:
                embed = format_mutuals_embed(mutuals, users, strict)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("no mutuals found.")
        except Exception as e:
            logger.exception(e)
            await interaction.response.send_message(embed=error_embed(e))

    # ------------------------------ in-game command ----------------------------- #

    @mainGroup.command(name="ingame", description=FriendsDesc.ingame)
    @app_commands.describe(
        sameserver=FriendsDesc.sameserver, username=FriendsDesc.username
    )
    async def ingame(
        self, interaction: discord.Interaction, username: str, sameserver: bool
    ):
        logger.log(
            "COMMAND",
            f"{interaction.user.name} used {interaction.command.name} command",
        )

        try:
            targetPresence, user = await RobloxPy.Presence.get_presence_from_username(
                username
            )
            user = user.get_by_requested_username(username)
            targetPresence = targetPresence.get_by_userid(user.userId)

            if not user:
                raise UserNotFound(username)

            friends = await user.get_friends()

            presences = await RobloxPy.Presence.get_presence(*friends)
            presences.filter_by_presence_types(2)

            friendsUsers = RobloxPy.Users.get_users_by_userid(*presences.userIds)

            embeds = []
            for presence in presences.presences:
                if not sameserver or (sameserver and (presence == targetPresence)):
                    embeds.append(
                        format_user_embed(
                            presenceType=presence.userPresenceType,
                            username=friendsUsers.get_by_userid(
                                presence.userId
                            ).username,
                            game=presence.lastlocation,
                            lobby="True" if presence.placeId == 6872265039 else "False",
                            jobId=presence.jobId,
                            groupOrLastOnline=presence.lastOnline,
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

    # ------------------------------- Added command ------------------------------ #

    @mainGroup.command(name="added", description=FriendsDesc.added)
    @app_commands.describe(
        target=FriendsDesc.target, usernames=FriendsDesc.usernamesAdded
    )
    async def addedwith(
        self, interaction: discord.Interaction, target: str, usernames: str
    ):
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

            users = RobloxPy.Users.get_users_by_username(*usernames, target)

            for username in [*usernames, target]:
                if not users.get_by_requested_username(username):
                    raise UserNotFound(username)

            friends = await RobloxPy.Friends.get_friend_users(
                users.get_by_requested_username(target)
            )
            friends = friends[users.get_by_requested_username(target)]

            counter = Counter(friends + users.userIds)
            addedWith = [item for item, count in counter if count == 2]

            format_addedwith_embed(
                target=users.get_by_requested_username(target).username,
                addedwith=addedWith,
                users=users,
            )

        except Exception as e:
            logger.exception(e)
            await interaction.response.send_message(embed=error_embed(e))


async def setup(bot: commands.Bot):
    await bot.add_cog(FriendsCommands(bot))
