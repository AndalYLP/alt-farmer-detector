from discord import app_commands
from discord.ext import commands
import RobloxPy
import requests
import discord
import aiohttp
import asyncio
import time
import os

# --------------------------- Environment variables -------------------------- #

COOKIE = os.environ.get("COOKIE")

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

    joinsOffGroup = app_commands.Group(name="joinsoff", description="joinsoff commands", parent=mainGroup)
    
    # --------------------------- Snipe player command --------------------------- #

    @mainGroup.command(name="player",description="Send player status.")
    @app_commands.describe(usernames="Players to snipe, e.g: scrapzi, generalcyans or scrapzi generalcyans.")
    async def player(self, interaction: discord.Interaction, usernames:str):
        print(f"{interaction.user.name} used {interaction.command.name} command")

        if usernames.find(","):
            usernames.split(",")
        else:
            usernames.split(" ")

        try:
            presenceGroup, userIds = RobloxPy.Presence.getPresenceFromUsername(usernames)

            embeds = []
            for presence in presenceGroup.presences:
                lobbyStatus = "True" if presence.placeId == 6872265039 else "False"
                username = userIds[presence.userId]

                color = 2686720 if presence.userPresenceType == 2 else 46847 if presence.userPresenceType == 1 else 7763574
                title = username + (" is in a game" if presence.userPresenceType == 2 else " is online" if presence.userPresenceType == 1 else f" is offline")
                description = f"Game: **{presence.lastlocation}**" + (f"\nLobby: **{lobbyStatus}**\nGameId: **{presence.jobId}**" if presence.userPresenceType == 2 and presence.gameId == 6872265039 else "")
                embed = discord.Embed(color=color if (not presence.userPresenceType == 2 or lobbyStatus == "True") else 1881856,title=title,description=description if presence.userPresenceType == 2 and not presence.gameId == None else None)

                embeds.append(embed)
            
            embedGroups = [[embed for embed in embeds[i:i + 10]] for i in range(0, len(embeds), 10)]
            for i, embedGroup in enumerate(embedGroups):
                if i != 0:
                    await interaction.followup.send(content=f"<t:{int(time.time())}:R>", embed=embedGroup)
                else:
                    await interaction.response.send_message(content=f"<t:{int(time.time())}:R>", embed=embedGroup)
        except Exception as e:
            await interaction.response.send_message(embed=discord.Embed(color=16765440,title="Error",description=e.args[0]), delete_after=5)

    @joinsOffGroup.command(name="player",description="Send player status, only works with bedwars.")
    @app_commands.describe(username="Player username to snipe.", forceupdate="If true you will get the latest data and update the current data, if false you will search through the current data")
    async def joinsOffPlayer(self, interaction: discord.Interaction, username:str, forceupdate:bool):
        print(f"{interaction.user.name} used {interaction.command.name} command")
        global Debounce, currentData, TokensTime, busy

        if busy:
            await interaction.response.send_message("Im busy rn!.", delete_after=3, ephemeral=True)
        
        if Debounce and forceupdate:
            await interaction.response.send_message("On cooldown, pls wait.", delete_after=3, ephemeral=True)

        await interaction.response.defer(thinking=True)

        try:
            thumbnail, userId = RobloxPy.Thumbnails.getUsersAvatarFromUsername(username)
            if forceupdate:
                busy = True
                serverGroup = RobloxPy.Games.getAllServers(6872265039)
                currentData = serverGroup
                TokensTime = round(time.time())
                busy = False
                Debounce = True
            else:
                serverGroup:RobloxPy.Games.ServerGroup = currentData
                
            imageUrls = serverGroup.getPlayerThumbnails().getAllImageUrls()
            if thumbnail.imageUrl in imageUrls:
                await interaction.followup.send(content=f"<t:{int(time.time())}:R>" + (f"Data from:<t:{int(TokensTime)}:R>" if forceupdate else ""), embed=discord.Embed(
                    color=2686720,
                    title=f"Found {username}'s server!",
                    description=f"Game: **Bedwars** (yes.)\nLobby: **True** (yes.)\nGameId: **{imageUrls[thumbnail.imageUrl]}**" 
                ))
            else:
                await interaction.followup.send(embed=discord.Embed(color=16765440,title="Error",description="didn't find the given player."), delete_after=5)

            await asyncio.sleep(60)
            Debounce = False

        except Exception as e:
            busy = Debounce = False
            await interaction.followup.send(embed=discord.Embed(color=16765440,title="Error",description=e.args[0]))


async def setup(bot: commands.Bot):
    await bot.add_cog(SnipeCommands(bot))