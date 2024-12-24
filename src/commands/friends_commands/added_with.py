from typing import Counter

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

import RobloxPy
from config.command_description import FriendsDesc
from config.embeds import error_embed, format_added_with_embed
from utils.categories import friends_group
from utils.exceptions import InvalidAmountOfUsernames, UserNotFound


class AddedWithCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @friends_group.command(name="added", description=FriendsDesc.added)
    @app_commands.describe(
        target=FriendsDesc.target, usernames=FriendsDesc.usernamesAdded
    )
    async def added_with(
        self, interaction: discord.Interaction, target: str, usernames: str
    ):
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

            users = RobloxPy.Users.get_users_by_username(*usernames, target)

            for username in [*usernames, target]:
                if not users.get_by_requested_username(username):
                    raise UserNotFound(username)

            target_user = users.get_by_requested_username(target)
            friends = await RobloxPy.Friends.get_friend_users(target_user.userId)
            friends = friends[target_user.userId]

            counter = Counter(friends + users.userIds)
            added_with = [k for k, v in counter.items() if v > 1]

            if added_with:
                embed = format_added_with_embed(
                    target=users.get_by_requested_username(target).username,
                    added_with=added_with,
                    users=users,
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    "The given usernames are not added with the target."
                )
        except Exception as e:
            logger.exception(e)
            await interaction.response.send_message(
                embed=error_embed("An error occurred.")
            )
