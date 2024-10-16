from discord import app_commands
from discord.ext import commands
import traceback
import RobloxPy
import requests
import discord

# ------------------------------------ Cog ----------------------------------- #

class TrackCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    mainGroup = app_commands.Group(name="track", description="Track commands")
    
    stopSubGroup = app_commands.Group(name="stop", description="stop commands", parent=mainGroup)
    
    # ------------------------------- track status ------------------------------- #

    @mainGroup.command(name="status", description="Creates a channel and tracks the status from a user.")
    @app_commands.describe(username="Player username to track.")
    async def TrackStatus(self, interaction: discord.Interaction, username: str):
        print(f"{interaction.user.name} used {interaction.command.name} command")
        
        try:
            userId = RobloxPy.Users.getIds(username)[username]
            if userId:
                guild = interaction.guild
                category = guild.get_channel(1288642965882933301)

                if not self.bot.TrackingStatus.get(userId) or not discord.utils.get(category.channels, name=username.lower()):
                    channel = discord.utils.get(category.channels, name=username.lower()) or await guild.create_text_channel(username, category=category)

                    self.bot.TrackingStatus[userId] = [channel, [interaction.user.mention]]

                    await interaction.response.send_message(f"Tracking in {channel.mention}")
                elif self.bot.TrackingStatus.get(userId) and interaction.user.mention not in self.bot.TrackingStatus[userId][1]:
                    self.bot.TrackingStatus[userId][1].append(interaction.user.mention)

                    await interaction.response.send_message(f"added to notification list for: {self.bot.TrackingStatus[userId][0].mention}")
                else:
                    await interaction.response.send_message("This username is already being tracked.", delete_after=5)
        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(embed=discord.Embed(color=16765440,title="Error",description=e.args[0]), delete_after=5)

    # -------------------------------- Track times ------------------------------- #

    @mainGroup.command(name="times", description="Creates a channel and tracks the queue times from a user.")
    @app_commands.describe(username="Player username to track.")
    async def TrackQueueTimes(self, interaction: discord.Interaction, username: str):
        print(f"{interaction.user.name} used {interaction.command.name} command")

        try:
            userId = RobloxPy.Users.getIds(username)[username]
            if userId:
                guild = interaction.guild
                category = guild.get_channel(1288638401947504725)

                if not self.bot.Tracking.get(userId, False) or not discord.utils.get(category.channels, name=username.lower()):
                    channel = discord.utils.get(category.channels, name=username.lower()) or await guild.create_text_channel(username, category=category)

                    self.bot.Tracking[userId] = [channel, [interaction.user.mention]]

                    await interaction.response.send_message(f"Tracking in {channel.mention}")
                elif self.bot.Tracking.get(userId) and interaction.user.mention not in self.bot.Tracking[userId][1]:
                    self.bot.Tracking[userId][1].append(interaction.user.mention)

                    await interaction.response.send_message(f"added to notification list for: {self.bot.TrackingStatus[userId][0].mention}")
                else:
                    await interaction.response.send_message("This username is already being tracked.", delete_after=5)
        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(embed=discord.Embed(color=16765440,title="Error",description=e.args[0]), delete_after=5)

    # ---------------------------- Stop tracking times --------------------------- #

    @stopSubGroup.command(name="times",description="stop notifications/tracking for a user.")
    @app_commands.describe(username="Player username to stop tracking.")
    async def StopTimesTrack(self, interaction: discord.Interaction, username: str):
        print(f"{interaction.user.name} used {interaction.command.name} command")

        try:
            userId = RobloxPy.Users.getIds(username)[username]
            if userId:
                if self.bot.Tracking.get(userId):
                    if len(self.bot.Tracking.get(userId)[1]) == 1:
                        await interaction.response.send_message(f"Stopped tracking **{username}**")
                        
                        await self.bot.Tracking.get(userId)[0].delete()
                        self.bot.Tracking.pop(userId)
                    else: 
                        self.bot.Tracking.get(userId)[1].remove(interaction.user.mention)

                        await interaction.response.send_message(f"Removed from notifications for **{username}**")
                else:
                    await interaction.response.send_message("This username is not being tracked.", delete_after=5)
        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(embed=discord.Embed(color=16765440,title="Error",description=e.args[0]), delete_after=5)

    # --------------------------- Stop tracking status --------------------------- #

    @stopSubGroup.command(name="status",description="stop notifications/tracking for a user.")
    @app_commands.describe(username="Player username to stop tracking.")
    async def StopStatusTrack(self, interaction: discord.Interaction, username: str):
        print(f"{interaction.user.name} used {interaction.command.name} command")
        try:
            userId = RobloxPy.Users.getIds(username)[username]
            if userId:
                if self.bot.TrackingStatus.get(userId):
                    if len(self.bot.TrackingStatus.get(userId)[1]) == 1:
                        await interaction.response.send_message(f"Stopped tracking **{username}**")
                        
                        await self.bot.TrackingStatus.get(userId)[0].delete()
                        self.bot.TrackingStatus.pop(userId)
                    else: 
                        self.bot.TrackingStatus.get(userId)[1].remove(interaction.user.mention)

                        await interaction.response.send_message(f"Removed from notifications for **{username}**")
                else:
                    await interaction.response.send_message("This username is not being tracked.", delete_after=5)
        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(embed=discord.Embed(color=16765440,title="Error",description=e.args[0]), delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(TrackCommands(bot))