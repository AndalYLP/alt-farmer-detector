from discord import app_commands
from discord.ext import commands
from collections import Counter
import requests
import discord
import time
import os

# --------------------------- Environment variables -------------------------- #

COOKIE = os.environ.get("COOKIE")

# ------------------------------------ Cog ----------------------------------- #

class FriendsCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    mainGroup = app_commands.Group(name="friends", description="friends commands")
    
    # ---------------------------------- Mutuals --------------------------------- #

    @mainGroup.command(name="mutuals", description="check mutuals between users.")
    @app_commands.describe(usernames="list of usernames, e.g: OrionYeets, chasemaser, ...", strict="True = Everyone should have the same user added")
    async def mutuals(self, interaction: discord.Interaction, usernames: str, strict:bool):
        print(interaction.user.name + " Used mutuals command")
        await interaction.response.defer(thinking=True)

        UsernamesArray = usernames.split(",")
        UsernamesArray = [username.strip() for username in UsernamesArray if username.strip()] 

        if len(UsernamesArray) < 2:
            await interaction.followup.send("You need to give 2+ usernames, e.g: OrionYeets, chasemaser, ...", ephemeral=True)
            return

        response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": UsernamesArray, "excludeBannedUsers": True})
        
        if response.status_code == 200:
            responseJSON = response.json()
            data = responseJSON.get("data", [])

            result = {}
            if data and "requestedUsername" in data[0]:
                for Pdata in data:
                    result[Pdata["requestedUsername"]] = Pdata["id"]

                if len(result) < len(UsernamesArray):
                    for username in UsernamesArray:
                        if username not in result:
                            await interaction.followup.send(f"Username **{username}** not found", ephemeral=True)
                else:
                    FriendsID = []

                    for id in result.values():
                        response = requests.get(f"https://friends.roblox.com/v1/users/{id}/friends/find?userSort=2", headers={"Cookie": COOKIE})
                        responseJSON = response.json()
                        data = responseJSON.get("PageItems", [])

                        currentUser = [Pdata["id"] for Pdata in data]
                        FriendsID.append(currentUser if data else [])

                    if strict:    
                        commonFriends = list(set.intersection(*map(set, FriendsID)))
                    else:
                        JointLists = [item for sublista in FriendsID for item in sublista]
                        counter = Counter(JointLists)

                        commonFriends = {item: count for item, count in counter.items() if count > 1}

                    if len(commonFriends) > 0:
                        if strict:
                            response = requests.post("https://users.roblox.com/v1/users", json={"userIds": commonFriends, "excludeBannedUsers": True})
                            if response.status_code == 200:
                                responseJSON = response.json()

                                data = responseJSON.get("data", [])
                                if data and "id" in data[0]:
                                    embed = discord.Embed(color=8585471,title="Mutuals",description="".join(f"**{i+1}.** ``{str(v["name"])}`` **|** {str(v["id"])}\n" for i,v in enumerate(data)))

                                    await interaction.followup.send(embed=embed)
                                else:
                                    await interaction.followup.send("Error getting usernames.", ephemeral=True)
                            else:
                                await interaction.followup.send("Request status code isn't 200 (Users API).", ephemeral=True)
                        else:
                            response = requests.post("https://users.roblox.com/v1/users", json={"userIds": list(commonFriends.keys()), "excludeBannedUsers": True})

                            if response.status_code == 200:
                                responseJSON = response.json()

                                data = responseJSON.get("data", [])
                                if data and "name" in data[0]:
                                    embed = discord.Embed(color=8585471,title="Mutuals",description="".join(f"**{i+1}.** ``{str(v["name"])}`` **|** {str(v["id"])} **({str(commonFriends[int(v["id"])])})** \n" for i,v in enumerate(data)))

                                    await interaction.followup.send(embed=embed)
                                else:
                                    await interaction.followup.send("Error getting usernames.", ephemeral=True)
                            else:
                                await interaction.followup.send("Request status code isn't 200 (Users API).", ephemeral=True)
                    else:
                        await interaction.followup.send("No mutuals found.")
            else:
                await interaction.followup.send("Error getting usernames.", ephemeral=True)
        else:
            await interaction.followup.send("Request status code isn't 200 (Users API).", ephemeral=True)

    # ------------------------------ in-game command ----------------------------- #

    @mainGroup.command(name="ingame", description="check in-game friends.")
    @app_commands.describe(sameserver="True will only show in same server friends.", username="Player username to check.")
    async def ingame(self, interaction: discord.Interaction, username: str, sameserver:bool):
        print(interaction.user.name + " Used ingame command")
        await interaction.response.defer(thinking=True)

        response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True})
        
        if response.status_code == 200:
            responseJSON = response.json()
            data = responseJSON.get("data", [])

            if data and "requestedUsername" in data[0]:
                response = requests.post("https://presence.roblox.com/v1/presence/users",json={"userIds": [data[0]["id"]]},headers={"Cookie": COOKIE})
                GameId = None
                if response.status_code == 200:
                    responseJSON = response.json()
                    data2 = responseJSON.get("userPresences", [])
                    
                    if data2:
                        GameId = data2[0]["gameId"]
                        if not GameId and sameserver:
                            await interaction.followup.send("Same server is true, but requested user is not in a game.", ephemeral=True)
                            return
                else:
                    await interaction.followup.send("Request status code isn't 200 (Users API).", ephemeral=True)
                    return
                
                response = requests.get(f"https://friends.roblox.com/v1/users/{data[0]["id"]}/friends/find?userSort=2", headers={"Cookie": COOKIE})
                responseJSON = response.json()

                data = responseJSON.get("PageItems", [])
                Friends = [Pdata["id"] for Pdata in data]
                if Friends:
                    IDLists = [Friends[i:i + 30] for i in range(0,len(Friends), 30)]
                    userPresences = []
                    userIds  = []
                    UsernamesFromId = {}
                    for i, SubList in enumerate(IDLists):
                        response = requests.post("https://presence.roblox.com/v1/presence/users",json={"userIds": SubList},headers={"Cookie": COOKIE})
                        if response.status_code == 200:
                            userPresences.extend([presence for presence in response.json().get("userPresences", []) if presence["userPresenceType"] == 2 and (presence["rootPlaceId"] == 6872265039 or presence["rootPlaceId"] == None) and (not sameserver or presence["gameId"] == GameId)])
                            userIds = [presence["userId"] for presence in userPresences]
                        else:
                            await interaction.followup.send(f"Request status code isn't 200.\n{response.json(), i}", ephemeral=True)
                            return
                    
                    if not len(userPresences):
                        await interaction.followup.send("No friends in-game found.", ephemeral=True)

                    response = requests.post("https://users.roblox.com/v1/users", json={"userIds": userIds, "excludeBannedUsers": True})
                    if response.status_code == 200:
                        responseJSON = response.json()
                        data = responseJSON.get("data", [])
                        
                        UsernamesFromId = {UserData["id"]: UserData["name"] for UserData in data}
                    else:
                        await interaction.followup.send("Request status code isn't 200 (Users API).", ephemeral=True)
                        return
                    
                    embeds = []
                    for doc in userPresences:
                        PresenceType = doc["userPresenceType"]

                        GameName = doc["lastLocation"]
                        LobbyStatus = "True" if doc["placeId"] == 6872265039 else "False"
                        GameId = doc["gameId"]

                        color = 2686720
                        title = f"{UsernamesFromId[doc["userId"]]} is in a game"
                        description = f"Game: **{GameName}**" + (f"\nLobby: **{LobbyStatus}**\nGameId: **{GameId}**" if PresenceType == 2 and doc["rootPlaceId"] == 6872265039 else "")
                        embeds.append(discord.Embed(color=color if (not PresenceType == 2 or LobbyStatus == "True") else 1881856,title=title,description=description if PresenceType == 2 and not doc["rootPlaceId"] == None else None))
                    
                    if embeds:
                        subEmbeds = [embeds[i:i + 10] for i in range(0,len(embeds), 10)]
                        for i, embeds in enumerate(subEmbeds):
                            if i == 0:
                                await interaction.followup.send(content=f"<t:{int(time.time())}:R>", embeds=embeds)
                            else:
                                await interaction.channel.send(content=f"<t:{int(time.time())}:R>", embeds=embeds)
                else:
                    await interaction.followup.send("No friends found.", ephemeral=True)
            else:
                await interaction.followup.send("Error getting username.", ephemeral=True)
        else:
            await interaction.followup.send("Request status code isn't 200 (Users API).", ephemeral=True)
    
    # ------------------------------- Added command ------------------------------ #

    @mainGroup.command(name="added", description="Check if the target is added with the given users.")
    @app_commands.describe(target="User to check his friends.", usernames="Users you want to check if they are added with the target, e.g: OrionYeets, chasemaser, ...")
    async def addedwith(self, interaction: discord.Interaction, target: str, usernames:str):
        print(interaction.user.name + " Used added command")
        await interaction.response.defer(thinking=True)

        tName = ""
        response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [target], "excludeBannedUsers": True})
        if response.status_code == 200:
            responseJSON = response.json()
            data = responseJSON.get("data", [])

            if data and "requestedUsername" in data[0]:
                target = data[0]["id"]
                tName = data[0]["name"]
            else:
                await interaction.followup.send("Error getting target's username.", ephemeral=True)
                return
        else:
            await interaction.followup.send("Request status code isn't 200 (Users API).", ephemeral=True)
            return

        UsernamesArray = usernames.split(",")
        UsernamesArray = [username.strip() for username in UsernamesArray if username.strip()]

        response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": UsernamesArray, "excludeBannedUsers": True})
        
        if response.status_code == 200:
            responseJSON = response.json()
            data = responseJSON.get("data", [])

            result = {}
            if data and "requestedUsername" in data[0]:
                for Pdata in data:
                    result[Pdata["requestedUsername"]] = Pdata["id"]

                if len(result) < len(UsernamesArray):  
                    for username in UsernamesArray:
                        if username not in result:
                            await interaction.followup.send(f"Username **{username}** not found", ephemeral=True)
                else:
                    response = requests.get(f"https://friends.roblox.com/v1/users/{target}/friends/find?userSort=2", headers={"Cookie": COOKIE})

                    if response.status_code == 200:
                        responseJSON = response.json()
                        data = responseJSON.get("PageItems", [])
                        
                        Fresult = []
                        if data:
                            for item in data:
                                if item["id"] in result.values():
                                    Fresult.append(item["id"])
                        else:
                            await interaction.followup.send("Error getting friends.", ephemeral=True)
                        
                        if Fresult:
                            response = requests.post("https://users.roblox.com/v1/users", json={"userIds": Fresult, "excludeBannedUsers": True})
                            if response.status_code == 200:
                                responseJSON = response.json()

                                data = responseJSON.get("data", [])
                                if data and "id" in data[0]:
                                    embed = discord.Embed(color=8585471,title=f"{tName} is added with:",description="".join(f"**{i+1}.** ``{str(v["name"])}`` **|** {str(v["id"])}\n" for i,v in enumerate(data)))

                                    await interaction.followup.send(embed=embed)
                                else:
                                    await interaction.followup.send("Error getting usernames.", ephemeral=True)
                            else:
                                await interaction.followup.send("Request status code isn't 200 (Users API).", ephemeral=True)
                        else:
                            await interaction.followup.send("The given usernames are not added with the target.")
                    else:
                        await interaction.followup.send("Request status code isn't 200 (friends API).", ephemeral=True)
            else:
                await interaction.followup.send("Error getting usernames.", ephemeral=True)
        else:
            await interaction.followup.send("Request status code isn't 200 (Users API).", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(FriendsCommands(bot))