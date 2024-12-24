import traceback

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

import RobloxPy
from CommandDescriptions import TrackDesc
from utils import UserNotFound, error_embed

# ------------------------------------ Cog ----------------------------------- #


class TrackCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    mainGroup = app_commands.Group(name="track", description="Track commands")

    stopSubGroup = app_commands.Group(
        name="stop", description="stop commands", parent=mainGroup
    )

    # ------------------------------- track status ------------------------------- #

    @mainGroup.command(name="status", description=TrackDesc.trackStatus)
    @app_commands.describe(username=TrackDesc.username)
    async def TrackStatus(self, interaction: discord.Interaction, username: str):
        logger.log(
            "COMMAND",
            f"{interaction.user.name} used {interaction.command.name} command",
        )

        try:
            user = RobloxPy.Users.get_users_by_username(
                username
            ).get_by_requested_username(username)

            if not user:
                raise UserNotFound(username)

            userId = user.userId
            guild = interaction.guild
            category = guild.get_channel(1288642965882933301)

            if not self.bot.TrackingStatus.get(userId) or not discord.utils.get(
                category.channels, name=username.lower()
            ):
                channel = discord.utils.get(
                    category.channels, name=username.lower()
                ) or await guild.create_text_channel(username, category=category)

                self.bot.TrackingStatus[userId] = [channel, [interaction.user.mention]]

                await interaction.response.send_message(
                    f"Tracking in {channel.mention}"
                )
            elif (
                self.bot.TrackingStatus.get(userId)
                and interaction.user.mention not in self.bot.TrackingStatus[userId][1]
            ):
                self.bot.TrackingStatus[userId][1].append(interaction.user.mention)

                await interaction.response.send_message(
                    f"added to notification list for: {self.bot.TrackingStatus[userId][0].mention}"
                )
            else:
                await interaction.response.send_message(
                    "This username is already being tracked.", delete_after=5
                )
        except Exception as e:
            logger.exception(e)
            await interaction.response.send_message(embed=error_embed(e))

    # -------------------------------- Track times ------------------------------- #

    @mainGroup.command(name="times", description=TrackDesc.trackTimes)
    @app_commands.describe(username=TrackDesc.username)
    async def TrackQueueTimes(self, interaction: discord.Interaction, username: str):
        logger.log(
            "COMMAND",
            f"{interaction.user.name} used {interaction.command.name} command",
        )

        try:
            user = RobloxPy.Users.get_users_by_username(
                username
            ).get_by_requested_username(username)

            if not user:
                raise UserNotFound(username)

            userId = user.userId
            guild = interaction.guild
            category = guild.get_channel(1288638401947504725)

            if not self.bot.Tracking.get(userId, False) or not discord.utils.get(
                category.channels, name=username.lower()
            ):
                channel = discord.utils.get(
                    category.channels, name=username.lower()
                ) or await guild.create_text_channel(username, category=category)

                self.bot.Tracking[userId] = [channel, [interaction.user.mention]]

                await interaction.response.send_message(
                    f"Tracking in {channel.mention}"
                )
            elif (
                self.bot.Tracking.get(userId)
                and interaction.user.mention not in self.bot.Tracking[userId][1]
            ):
                self.bot.Tracking[userId][1].append(interaction.user.mention)

                await interaction.response.send_message(
                    f"added to notification list for: {self.bot.TrackingStatus[userId][0].mention}"
                )
            else:
                await interaction.response.send_message(
                    "This username is already being tracked.", delete_after=5
                )
        except Exception as e:
            logger.exception(e)
            await interaction.response.send_message(embed=error_embed(e))

    # ---------------------------- Stop tracking times --------------------------- #

    @stopSubGroup.command(name="times", description=TrackDesc.stopTracking)
    @app_commands.describe(username=TrackDesc.usernameStop)
    async def StopTimesTrack(self, interaction: discord.Interaction, username: str):
        logger.log(
            "COMMAND",
            f"{interaction.user.name} used {interaction.command.name} command",
        )

        try:
            user = RobloxPy.Users.get_users_by_username(
                username
            ).get_by_requested_username(username)

            if not user:
                raise UserNotFound(username)

            userId = user.userId

            if self.bot.Tracking.get(userId):
                if len(self.bot.Tracking.get(userId)[1]) == 1:
                    await interaction.response.send_message(
                        f"Stopped tracking **{username}**"
                    )

                    await self.bot.Tracking.get(userId)[0].delete()
                    self.bot.Tracking.pop(userId)
                else:
                    self.bot.Tracking.get(userId)[1].remove(interaction.user.mention)

                    await interaction.response.send_message(
                        f"Removed from notifications for **{username}**"
                    )
            else:
                await interaction.response.send_message(
                    "This username is not being tracked.", delete_after=5
                )
        except Exception as e:
            logger.exception(e)
            await interaction.response.send_message(embed=error_embed(e))

    # --------------------------- Stop tracking status --------------------------- #

    @stopSubGroup.command(name="status", description=TrackDesc.stopTracking)
    @app_commands.describe(username=TrackDesc.usernameStop)
    async def StopStatusTrack(self, interaction: discord.Interaction, username: str):
        logger.log(
            "COMMAND",
            f"{interaction.user.name} used {interaction.command.name} command",
        )

        try:
            user = RobloxPy.Users.get_users_by_username(
                username
            ).get_by_requested_username(username)

            if not user:
                raise UserNotFound(username)

            userId = user.userId

            if self.bot.TrackingStatus.get(userId):
                if len(self.bot.TrackingStatus.get(userId)[1]) == 1:
                    await interaction.response.send_message(
                        f"Stopped tracking **{username}**"
                    )

                    await self.bot.TrackingStatus.get(userId)[0].delete()
                    self.bot.TrackingStatus.pop(userId)
                else:
                    self.bot.TrackingStatus.get(userId)[1].remove(
                        interaction.user.mention
                    )

                    await interaction.response.send_message(
                        f"Removed from notifications for **{username}**"
                    )
            else:
                await interaction.response.send_message(
                    "This username is not being tracked.", delete_after=5
                )
        except Exception as e:
            logger.exception(e)
            await interaction.response.send_message(embed=error_embed(e))


async def setup(bot: commands.Bot):
    await bot.add_cog(TrackCommands(bot))
