from discord import app_commands
from discord.ext import commands
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
        print(interaction.user.name + " used track status command")
        response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True})
        
        if response.status_code == 200:
            responseJSON = response.json()
            data = responseJSON.get("data", [])

            if data and "requestedUsername" in data[0]:
                guild = interaction.guild
                category = guild.get_channel(1288642965882933301)
                if not self.bot.TrackingStatus.get(data[0]["name"]) or not discord.utils.get(category.channels, name=data[0]["name"].lower()):
                    channel = discord.utils.get(category.channels, name=data[0]["name"].lower()) or await guild.create_text_channel(data[0]["name"], category=category)
                    self.bot.TrackingStatus[data[0]["name"]] = [channel, [interaction.user.mention]]
                    await interaction.response.send_message(f"Tracking in {channel.mention}")
                elif self.bot.TrackingStatus.get(data[0]["name"]) and interaction.user.mention not in self.bot.TrackingStatus[data[0]["name"]][1]:
                    self.bot.TrackingStatus[data[0]["name"]][1].append(interaction.user.mention)
                    await interaction.response.send_message(f"added to notification list for: {self.bot.TrackingStatus[data[0]["name"]][0].mention}")
                else:
                    await interaction.response.send_message("This username is already being tracked.", delete_after=5)
            else:
                await interaction.response.send_message("Username doesn't exist.", delete_after=3, ephemeral=True)
        else:
            await interaction.response.send_message("Error trying to verify username.", delete_after=3, ephemeral=True)

    # -------------------------------- Track times ------------------------------- #

    @mainGroup.command(name="times", description="Creates a channel and tracks the queue times from a user.")
    @app_commands.describe(username="Player username to track.")
    async def TrackQueueTimes(self, interaction: discord.Interaction, username: str):
        print(interaction.user.name + " used track times command")
        response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True})
        
        if response.status_code == 200:
            responseJSON = response.json()
            data = responseJSON.get("data", [])

            if data and "requestedUsername" in data[0]:
                guild = interaction.guild
                category = guild.get_channel(1288638401947504725)
                if not self.bot.Tracking.get(data[0]["name"], False) or not discord.utils.get(category.channels, name=data[0]["name"].lower()):

                    channel = discord.utils.get(category.channels, name=data[0]["name"].lower()) or await guild.create_text_channel(data[0]["name"], category=category)
                    self.bot.Tracking[data[0]["name"]] = [channel, [interaction.user.mention]]
                    await interaction.response.send_message(f"Tracking in {channel.mention}")
                elif self.bot.Tracking.get(data[0]["name"]) and interaction.user.mention not in self.bot.Tracking[data[0]["name"]][1]:
                    self.bot.Tracking[data[0]["name"]][1].append(interaction.user.mention)
                    await interaction.response.send_message(f"added to notification list for: {self.bot.TrackingStatus[data[0]["name"]][0].mention}")
                else:
                    await interaction.response.send_message("This username is already being tracked.", delete_after=5)
            else:
                await interaction.response.send_message("Username doesn't exist.", delete_after=3, ephemeral=True)
        else:
            await interaction.response.send_message("Error trying to verify username.", delete_after=3, ephemeral=True)

    # ---------------------------- Stop tracking times --------------------------- #

    @stopSubGroup.command(name="times",description="stop notifications/tracking for a user.")
    @app_commands.describe(username="Player username to stop tracking.")
    async def StopTimesTrack(self, interaction: discord.Interaction, username: str):
        print(interaction.user.name + " used track status command")
        response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True})
        
        if response.status_code == 200:
            responseJSON = response.json()
            data = responseJSON.get("data", [])

            if data and "requestedUsername" in data[0]:
                if self.bot.Tracking.get(data[0]["name"]):
                    if len(self.bot.Tracking.get(data[0]["name"])[1]) == 1:
                        self.bot.Tracking.pop(data[0]["name"])
                        await self.bot.Tracking.get(data[0]["name"])[0].delete()
                        await interaction.response.send_message(f"Stopped tracking **{username}**")
                    else: 
                        self.bot.Tracking.get(data[0]["name"])[1].remove(interaction.user.mention)
                        await interaction.response.send_message(f"Removed from notifications for **{username}**")
                else:
                    await interaction.response.send_message("This username is not being tracked.", delete_after=5)
            else:
                await interaction.response.send_message("Username doesn't exist.", delete_after=3, ephemeral=True)
        else:
            await interaction.response.send_message("Error trying to verify username.", delete_after=3, ephemeral=True)

    # --------------------------- Stop tracking status --------------------------- #

    @stopSubGroup.command(name="status",description="stop notifications/tracking for a user.")
    @app_commands.describe(username="Player username to stop tracking.")
    async def StopStatusTrack(self, interaction: discord.Interaction, username: str):
        print(interaction.user.name + " used track status command")
        response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True})
        
        if response.status_code == 200:
            responseJSON = response.json()
            data = responseJSON.get("data", [])

            if data and "requestedUsername" in data[0]:
                if self.bot.TrackingStatus.get(data[0]["name"]):
                    if len(self.bot.TrackingStatus.get(data[0]["name"])[1]) == 1:
                        self.bot.TrackingStatus.pop(data[0]["name"])
                        await self.bot.TrackingStatus.get(data[0]["name"])[0].delete()
                        await interaction.response.send_message(f"Stopped tracking **{username}**")
                    else: 
                        self.bot.TrackingStatus.get(data[0]["name"])[1].remove(interaction.user.mention)
                        await interaction.response.send_message(f"Removed from notifications for **{username}**")
                else:
                    await interaction.response.send_message("This username is not being tracked.", delete_after=5)
            else:
                await interaction.response.send_message("Username doesn't exist.", delete_after=3, ephemeral=True)
        else:
            await interaction.response.send_message("Error trying to verify username.", delete_after=3, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(TrackCommands(bot))