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

Debounce = False
TokensTotal = {}
TokensTime = None
busy = False

class AvatarFetcher:
    def __init__(self, user_id, username, interaction):
        self.user_id = str(user_id)
        self.image_url = None
        self.found = False
        self.username = username
        self.interaction:discord.Interaction = interaction

    async def fetch_image_url(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?size=48x48&format=png&userIds={self.user_id}") as response:
                if response.status == 200:
                    self.image_url = (await response.json())["data"][0]["imageUrl"]
                else:
                    await self.interaction.followup.send("Request status code isn't 200 (Thumbnail API).")

    async def fetch_batch_data(self, session:aiohttp.ClientSession, data, Force, tokens):
        global busy
        async with session.post("https://thumbnails.roblox.com/v1/batch", json=data, headers={"Cookie": COOKIE}) as response:
            if response.status == 200:
                result = await response.json()
                found_data = {item["imageUrl"]: item["requestId"].split(":")[1] for item in result["data"]}
                
                if self.found:
                    return
                
                if self.image_url in found_data.keys():
                    self.found = True
                    busy = False
                    color = 2686720
                    title = f"Found {self.username}'s server!"
                    description = f"Game: **Bedwars** (yes.)\nLobby: **True** (yes.)\nGameId: **{tokens[found_data[self.image_url]]}**" 
                    embed = discord.Embed(color=color,title=title,description=description)
                    await self.interaction.followup.send(content=f"<t:{int(time.time())}:R>" + (f"Data from:<t:{int(TokensTime)}:R>" if Force else ""),embed=embed)
                    print("FOUND!", flush=True)
                else:
                    print("NOT FOUND", flush=True)
            else:
                print("error thumbnail api", await response.json())

    async def check_images(self, tokens, forced):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(0, len(tokens), 100):
                token_batch = [self.token_format(token) for token in list(tokens.keys())[i:i + 100]]
                tasks.append(self.fetch_batch_data(session, token_batch, forced, tokens))
            await asyncio.gather(*tasks)

    @staticmethod
    def token_format(token):
        return {
            "requestId": f"0:{token}:AvatarHeadshot:48x48:png:regular",
            "type": "AvatarHeadShot",
            "targetId": 0,
            "format": "png",
            "size": "48x48",
            "token": token,
        }

    async def run(self):
        global busy, TokensTotal, TokensTime
        busy = True
        await self.fetch_image_url()
        next_cursor = None

        async with aiohttp.ClientSession() as session:
            while not self.found:
                response = await session.get(f"https://games.roblox.com/v1/games/6872265039/servers/public?limit=100" + (f"&cursor={next_cursor}" if next_cursor else ""))
                if response.status == 200:
                    response_json = await response.json()
                    tokens = {token: server["id"] for server in response_json["data"] for token in server["playerTokens"]}
                    TokensTotal.update(tokens)
                    TokensTime = time.time()
                    await self.check_images(tokens, False)
                    next_cursor = response_json.get("nextPageCursor")
                    if not next_cursor:
                        busy = False
                        break
                else:
                    await self.interaction.followup.send("Request status code isn't 200 (Games API), waiting 60 seconds.", ephemeral=True)
                    await asyncio.sleep(60)

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
        global Debounce, TokensTotal, TokensTime, busy
        if busy:
            await interaction.response.send_message("Im busy rn!.", delete_after=3, ephemeral=True)
        
        if Debounce and forceupdate:
            await interaction.response.send_message("On cooldown, pls wait.", delete_after=3, ephemeral=True)
        print(interaction.user.name + " Used snipe player command")

        await interaction.response.defer(thinking=True)
        response = requests.post("https://users.roblox.com/v1/usernames/users",json={"usernames": [username],"excludeBannedUsers": True})
        if response.status_code == 200:
            responseJSON = response.json()

            data = responseJSON.get("data", [])
            if data and "requestedUsername" in data[0]:
                id = data[0].get("id")
                Username = data[0].get("name")

                if forceupdate:
                    Debounce = True
                    fetcher = AvatarFetcher(id, Username, interaction)
                    await fetcher.run()
                    if not fetcher.found:
                        await interaction.followup.send("Didn't find the given player.", ephemeral=True)
                    await asyncio.sleep(60)
                    Debounce = False
                else:
                    fetcher = AvatarFetcher(id, Username, interaction)
                    await fetcher.check_images(TokensTotal, True)

                await interaction.followup.send("Finished.", ephemeral=True)
            else:
                await interaction.followup.send("Username doesn't exist.", ephemeral=True)
        else:
            await interaction.followup.send("Request status code isn't 200 (Users API).", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SnipeCommands(bot))