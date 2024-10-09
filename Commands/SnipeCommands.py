from discord import app_commands
from discord.ext import commands
import requests
import discord
import time
import os

# --------------------------- Environment variables -------------------------- #

COOKIE = os.environ.get("COOKIE")

# ------------------------------------ Cog ----------------------------------- #

class SnipeCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    mainGroup = app_commands.Group(name="snipe", description="Snipe commands")
    
    # --------------------------- Snipe player command --------------------------- #

    @mainGroup.command(name="player",description="Send player status.")
    @app_commands.describe(username="Player username to snipe.")
    async def player(self, interaction: discord.Interaction, username:str):
        print(interaction.user.name + " Used snipe player command")
        response = requests.post("https://users.roblox.com/v1/usernames/users",json={"usernames": [username],"excludeBannedUsers": True})
        if response.status_code == 200:
            responseJSON = response.json()

            data = responseJSON.get("data", [])
            if data and "requestedUsername" in data[0]:
                id = data[0].get("id")
                Username = data[0].get("name")

                response = requests.post("https://presence.roblox.com/v1/presence/users",json={"userIds": [id]},headers={"Cookie": COOKIE})
                
                if response.status_code == 200:
                    responseJSON = response.json()
                    userPresences = responseJSON.get("userPresences", [])

                    if userPresences:
                        doc = userPresences[0]
                        PresenceType = doc["userPresenceType"]

                        GameName = doc["lastLocation"]
                        LobbyStatus = "True" if doc["placeId"] == 6872265039 else "False"
                        GameId = doc["gameId"]

                        color = 2686720 if PresenceType == 2 else 46847 if PresenceType == 1 else 7763574
                        title = f"{Username} is in a game" if PresenceType == 2 else f"{Username} is online" if PresenceType == 1 else f"{Username} is offline"
                        description = f"Game: **{GameName}**" + (f"\nLobby: **{LobbyStatus}**\nGameId: **{GameId}**" if PresenceType == 2 and doc["rootPlaceId"] == 6872265039 else "")
                        embed = discord.Embed(color=color if (not PresenceType == 2 or LobbyStatus == "True") else 1881856,title=title,description=description if PresenceType == 2 and not doc["rootPlaceId"] == None else None)

                        await interaction.response.send_message(content=f"<t:{int(time.time())}:R>", embed=embed)
                    else:
                        await interaction.response.send_message("Error: 2", delete_after=3, ephemeral=True)
                else:
                    await interaction.response.send_message("Request status code isn't 200 (Presence API).", delete_after=3, ephemeral=True)
            else:
                await interaction.response.send_message("Username doesn't exist.", delete_after=3, ephemeral=True)
        else:
            await interaction.response.send_message("Request status code isn't 200 (Users API).", delete_after=3, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SnipeCommands(bot))