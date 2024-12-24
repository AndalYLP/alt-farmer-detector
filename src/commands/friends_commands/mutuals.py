from typing import Counter

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

import RobloxPy
from config.command_description import FriendsDesc
from config.embeds import error_embed, format_mutuals_embed
from utils.categories import friends_group
from utils.exceptions import InvalidAmountOfUsernames, UserNotFound


class MutualsCommand(commands.cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @friends_group.command(name="mutuals", description=FriendsDesc.mutuals)
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
            usernames = [
                username.strip() for username in usernames.replace(",", " ").split()
            ]

            if len(usernames) == 1:
                raise InvalidAmountOfUsernames(1)

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
                mutuals = {k: v for k, v in counter.items() if v == len(usernames)}
            else:
                mutuals = {k: v for k, v in counter.items() if v >= 1}

            if mutuals:
                await interaction.response.send_message(
                    embed=format_mutuals_embed(mutuals, users)
                )
            else:
                await interaction.response.send_message(
                    embed=error_embed("No mutual friends found.")
                )

        except Exception as e:
            logger.exception(e)
            await interaction.response.send_message(embed=error_embed(str(e)))
