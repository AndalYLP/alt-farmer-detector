from discord import app_commands
from discord.ext import commands
import requests
import discord
import aiohttp
import asyncio
import time
import os

# --------------------------- Environment variables -------------------------- #

COOKIE = os.environ.get("COOKIE")

# --------------------------------- Functions -------------------------------- #

Credits = 3
TokensTotal = {}
TokensTime = None
notFound = True
busy = False
def tokenFormat(token):
    return {
        "requestId": f"0:{token}:AvatarHeadshot:48x48:png:regular",
        "type": "AvatarHeadShot",
        "targetId": 0,
        "format": "png",
        "size": "48x48",
        "token": token,
    }

async def GetData(session, Data, i, image, Tokens, interaction: discord.Interaction, Username, Forced):
    global notFound, TokensTime
    async with session.post("https://thumbnails.roblox.com/v1/batch",json=Data) as response:
        if response.status == 200:
            data = await response.json()
            thing = {data["imageUrl"]: data["requestId"].split(":")[1] for data in data["data"]}
            if image in thing.keys():
                notFound = False
                color = 2686720
                title = f"Found {Username}'s server!"
                description = f"Game: **Bedwars** (yes.)\nLobby: **True** (yes.)\nGameId: **{Tokens[thing[image]]}**" 
                embed = discord.Embed(color=color,title=title,description=description)
                interaction.followup.send(content=f"<t:{int(time.time())}:R>" + (f"Tokens Time: <t:{TokensTime}:R>" if Forced else ""),embed=embed)
            return

async def CheckImage(Tokens, image, interaction, Username, Forced):
    TokenSubLists = [[tokenFormat(token) for token in list(Tokens.keys())[i:i + 100]] for i in range(0, len(Tokens.keys()), 100)]

    async with aiohttp.ClientSession() as session:
        tasks = [GetData(session, TokenSubList, i, image, Tokens, interaction, Username, Forced) for i, TokenSubList in enumerate(TokenSubLists)]
        await asyncio.gather(*tasks)

# ------------------------------------ Cog ----------------------------------- #

class SnipeCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    mainGroup = app_commands.Group(name="snipe", description="Snipe commands")

    joinsOffGroup = app_commands.Group(name="joinsoff", description="joinsoff commands", parent=mainGroup)
    
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


    @joinsOffGroup.command(name="player",description="Send player status, only works with bedwars.")
    @app_commands.describe(username="Player username to snipe.", forceupdate="If true you will get the latest data and update the current data, if false you will search through the current data")
    async def joinsOffPlayer(self, interaction: discord.Interaction, username:str, forceupdate:bool):
        global Credits, TokensTotal, notFound, TokensTime, busy
        if busy or Credits != 3:
            await interaction.response.send_message("Im busy rn!.", delete_after=3, ephemeral=True)
        print(interaction.user.name + " Used snipe player command")

        await interaction.response.defer(thinking=True)
        response = requests.post("https://users.roblox.com/v1/usernames/users",json={"usernames": [username],"excludeBannedUsers": True})
        if response.status_code == 200:
            responseJSON = response.json()

            data = responseJSON.get("data", [])
            if data and "requestedUsername" in data[0]:
                id = data[0].get("id")
                Username = data[0].get("name")

                response = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?size=48x48&format=png&userIds={id}")
                if response.status_code == 200:
                    responseJSON = response.json()

                    data = responseJSON.get("data", [])
                    if data and "imageUrl" in data[0]:
                        image = data[0]["imageUrl"]
                        if not forceupdate and TokensTotal:
                            await CheckImage(TokensTotal, image, interaction, Username, forceupdate)
                            return

                        notFound = True
                        nextCursor = None
                        busy = True
                        while notFound or Credits != 0:
                            response = requests.get("https://games.roblox.com/v1/games/6872265039/servers/public?limit=100" + (f"&cursor={nextCursor}" if nextCursor else ""))
                            if response.status_code == 200:
                                responseJSON = response.json()

                                Tokens = {token: server["id"] for server in responseJSON["data"] for token in server["playerTokens"]}
                                TokensTotal.update(Tokens)
                                TokensTime = int(time.time())
                                await CheckImage(Tokens, image, interaction,Username, forceupdate)
                                nextCursor = responseJSON["nextPageCursor"]
                                Credits -= 1
                                if Credits == 0:
                                    if notFound:
                                        await interaction.followup.send("Sent 3 requests, waiting 60 seconds.")
                                        time.sleep(60)
                                        Credits = 3
                                        continue
                                    else:
                                        time.sleep(60)
                                        Credits = 3
                                        break
                                    
                                
                                if not nextCursor:
                                    if notFound:
                                        await interaction.followup.send("No servers left, player not found.")
                                    break
                            else:
                                print("Response code is not 200", response.json())
                                time.sleep(30) 
                        busy = False
                    else:
                        await interaction.followup.send("Error getting user's thumbnail.", ephemeral=True)
                else:
                    await interaction.followup.send("Request status code isn't 200 (Thumbnails API).", ephemeral=True)
            else:
                await interaction.followup.send("Username doesn't exist.", ephemeral=True)
        else:
            await interaction.followup.send("Request status code isn't 200 (Users API).", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SnipeCommands(bot))