from discord.ui import Button, View
from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient
from collections import Counter
from threading import Thread

from flask import Flask
import traceback
import requests
import discord
import asyncio
import time
import os

# ---------------------------------- Server ---------------------------------- #

MongURI = os.environ.get("MONGO_URI")
Client = MongoClient(MongURI)
dataBase = Client["AltFarmerDetector"]
UsersCollection = dataBase["Users"]

app = Flask(__name__)

@app.route("/")
def answer():
      return "Alive"

def run():
      from waitress import serve
      serve(app, host="0.0.0.0", port=8080)
      
def keep_alive():
  t = Thread(target=run)
  t.start()
      
keep_alive()

# ------------------------------------ Bot ----------------------------------- #

Cookie = os.environ.get("COOKIE")
TOKEN = os.environ.get("TOKEN")
bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())

# ------------------------------- Groups setup ------------------------------- #

class Group(app_commands.Group):
    ...

snipe = Group(name="snipe",description="Snipe commands")
friends = Group(name="friends",description="Friends commands")
track = Group(name="track",description="Tracking commands")

# ------------------------------ On ready event ------------------------------ #

@bot.event
async def on_ready():
    print("Bot is ready")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Bedwars Ranked"))
    bot.tree.add_command(snipe)
    bot.tree.add_command(friends)
    bot.tree.add_command(track)
    bot.loop.create_task(Start())
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# ------------------------------- Main function ------------------------------ #

Tracking = {}
TrackingStatus = {}
bot.MuteAll = False
bot.OnlineMuted = True
bot.OfflineMuted = True
bot.OtherGame = True
GameIdList = {}

async def Start():
    channel = bot.get_channel(1277039650401423471)
    Altchannel = bot.get_channel(1277302313949593742)
    GameIdChannel = bot.get_channel(1277046568033194115)
    GameIdWithAltsChannel = bot.get_channel(1277089252676472894)

    while True:
        try:
            if channel:
                Docs = UsersCollection.find({})
                if Docs:
                    UserIDs = []
                    for doc in Docs:
                        UserIDs.append(doc["UserID"])

                    IDLists = [UserIDs[i:i + 30] for i in range(0,len(UserIDs), 30)]
                    userPresences = []
                    for i, SubList in enumerate(IDLists):
                        response = requests.post("https://presence.roblox.com/v1/presence/users",json={"userIds": SubList},headers={"Cookie": Cookie})
                        if response.status_code == 200:
                            userPresences.extend(response.json().get("userPresences", []))
                        else:
                            await channel.send(f"Request status code isn't 200.\n{response.json(), i}", delete_after=3)
                            if response.json().get("errors", [])[0].get("message", []) == "Too many requests. Please wait a bit.":
                                await asyncio.sleep(15)
                    await channel.purge(limit=100)
                    await Altchannel.purge(limit=100)
                    await asyncio.gather(
                        UserStatus(userPresences, channel, Altchannel),
                        SameGameid(userPresences, GameIdChannel, GameIdWithAltsChannel)
                    )
                else:
                    print("Docs not found")
            else:
                print("Channel doesn't exist or not added")
                await asyncio.sleep(10)
                continue

            await asyncio.sleep(10)

        except Exception as e:
            print(f"Error en el bucle principal: {e}.")
            traceback.print_exc()

# --------------------------- User status function --------------------------- #

async def UserStatus(userPresences, channel, AltChannel):
    embeds = {}
    if userPresences:
        for doc in userPresences:
            PresenceType = doc["userPresenceType"]
            ResultFound = UsersCollection.find_one({"UserID": doc["userId"]})
            isAlt = ResultFound["isAlt"]
            Username = ResultFound["Username"]
            LobbyStatus = "True" if doc["placeId"] == 6872265039 else "False"
            GameName = doc["lastLocation"] or "None"
            GameId = doc["gameId"]
            Group = ResultFound.get("GroupName", "None")

            if doc["userId"] not in GameIdList:
                GameIdList[doc["userId"]] = [["nil", "nil" if GameId is None else GameId], ["nil", f"<t:{int(time.time())}:R>"], "True" if doc["placeId"] == 6872265039 else "False", GameName, PresenceType]

            if (GameId and not GameIdList.get(doc["userId"])[0][1] == GameId) or (PresenceType == 0 and GameIdList.get(doc["userId"])[0][1]):
                if Tracking.get(Username):
                    try:
                        Result = int(time.time()) - int(GameIdList.get(doc["userId"])[1][1][3:-3])
                        embed = discord.Embed(color=46847,title=f"Time in game: {(str(Result) + " Seconds") if Result < 60 else (str(int(Result / 60)) + ":" + str((Result % 60)).zfill(2) + " Minutes" ) }")
                        embed.add_field(name="From:",value=f"Game: **{GameIdList.get(doc["userId"])[3] }**\nGameId: **{GameIdList.get(doc["userId"])[0][1]}**\nLobby: **{GameIdList.get(doc["userId"])[2]}**",inline=True)
                        embed.add_field(name="To:",value=f"Game: **{GameName}**\nGameId: **{GameId}**\nLobby: **{LobbyStatus}**",inline=True)
                        await Tracking[Username].send(embed=embed)
                    except Exception as e:
                        print(f"Error enviando trackingtimes: {e}.")
                        traceback.print_exc()
                GameIdList.get(doc["userId"])[2] = "True" if doc["placeId"] == 6872265039 else "False"
                GameIdList.get(doc["userId"])[3] = GameName
                GameIdList.get(doc["userId"])[1][0] = GameIdList.get(doc["userId"])[1][1]
                GameIdList.get(doc["userId"])[0][0] = GameIdList.get(doc["userId"])[0][1]
                GameIdList.get(doc["userId"])[1][1] = f"<t:{int(time.time())}:R>"
                GameIdList.get(doc["userId"])[0][1] = GameId

            LastGameId = GameIdList.get(doc["userId"])[0][0]
            TimeInGameId = GameIdList.get(doc["userId"])[1][1]

            color = 2686720 if PresenceType == 2 else 46847 if PresenceType == 1 else 7763574
            title = f"{Username} is in a game" if PresenceType == 2 else f"{Username} is online" if PresenceType == 1 else f"{Username} is offline"
            description = f"Game: **{GameName}**" + (f"\nLobby: **{LobbyStatus}**\nGameId: **{GameId}**\nLastGameId: **{LastGameId}**\nTime in gameId: **{TimeInGameId}**" if PresenceType == 2 and doc["rootPlaceId"] == 6872265039 else "")
            embed = discord.Embed(color=color if (not PresenceType == 2 or LobbyStatus == "True") else 1881856,title=title,description=description if PresenceType == 2 and not doc["rootPlaceId"] == None else None)

            if not Group == "None":
                embed.set_footer(text= "Group: " + Group)

            if isAlt and (PresenceType == 2 and not bot.MuteAll and (doc["rootPlaceId"] == None or doc["rootPlaceId"] == 6872265039)):
                await AltChannel.send(content=f"<t:{int(int(time.time()))}:R>@everyone",embed=embed)

            if TrackingStatus.get(Username) and not GameIdList.get(doc["userId"])[4] == PresenceType:
                try:
                    await TrackingStatus[Username][0].send(description=f"<t:{int(int(time.time()))}:R>{TrackingStatus[Username][1]}",embed=embed)
                except Exception as e:
                    print(f"Error enviando trackingstatus: {e}.")
                    traceback.print_exc()

            GameIdList.get(doc["userId"])[4] = PresenceType

            if (PresenceType == 2 and ((doc["rootPlaceId"] == 6872265039 or doc["rootPlaceId"] == None) or not bot.OtherGame) and not bot.MuteAll) or (PresenceType == 1 and not (bot.OnlineMuted or bot.MuteAll)) or (PresenceType == 0 and not (bot.OfflineMuted or bot.MuteAll)):
                if not Group in embeds:
                    embeds[Group] = [PresenceType == 2 and (doc["rootPlaceId"] == None or (doc["rootPlaceId"] == 6872265039 and not doc["placeId"] == 6872265039))]
                    embeds[Group].append(embed)
                else:
                    if not Group == "None":
                        if embeds[Group][1] == False:
                            embeds[Group][1] = PresenceType == 2 and (doc["rootPlaceId"] == None or (doc["rootPlaceId"] == 6872265039 and not doc["placeId"] == 6872265039))
                    else:
                        embeds[Group].append(PresenceType == 2 and (doc["rootPlaceId"] == None or (doc["rootPlaceId"] == 6872265039 and not doc["placeId"] == 6872265039)))
                    embeds[Group].append(embed)
        
        for groupName, Embeds in embeds.items():
            if not groupName == "None":
                SubGroups = [Embeds[i:i + 10] for i in range(0,len(Embeds), 10)]
                for group in SubGroups:
                    await channel.send(content=f"<t:{int(int(time.time()))}:R>" + ("@everyone" if group[0] else ""),embeds=group[1:])

        for i, embed in enumerate(embeds["None"]):
            if not (i % 2) == 0:
                await channel.send(content=f"<t:{int(int(time.time()))}:R>" + ("@everyone" if embeds["None"][i-1] else ""),embed=embed)
    else:
        await channel.send("Error: 2", delete_after=3)

# --------------------------- Same game id function -------------------------- #

async def SameGameid(userPresences, channel, channel2):
    GameIds = {}
    for doc in userPresences:
        if doc.get("gameId") and doc.get("rootPlaceId") and doc["rootPlaceId"] == 6872265039:
            if GameIds.get(doc["gameId"]):
                GameIds[doc["gameId"]][0].append(doc["userId"])
            else:
                GameIds[doc["gameId"]] = [[doc["userId"]],{"gameName": doc["lastLocation"], "isLobby": "True" if doc["placeId"] == 6872265039 else "False"}]

    for gameId, Ids in GameIds.items():
        list2 = Ids[1]
        Ids = Ids[0]
        Title = "GameId: " + gameId
        Description = f"## GameId description\nGame: **{list2["gameName"]}**\nLobby: **{list2["isLobby"]}**\n## In-game player ({len(Ids)})"
        Everyone = False
        for Userid in Ids:
            doc = UsersCollection.find_one({"UserID": Userid})
            Username = doc["Username"]
            Description += f"\nUsername: **{Username}**\n- isAlt: **{doc["isAlt"]}**"

            if doc["isAlt"] == True:
                Everyone = True
        Embed = discord.Embed(color=2686720 if list2["isLobby"] == "True" else 1881856, title=Title, description=Description)
        await channel.send(content=f"<t:{int(int(time.time()))}:R>", embed=Embed)
        if Everyone:
            await channel2.send(content=f"<t:{int(int(time.time()))}:R>@everyone", embed=Embed)

# ------------------------------ Resume command ------------------------------ #

@snipe.command(name="resume",description="Resume the notifications.")
async def startLoop(interaction: discord.Interaction):
    print(interaction.user.name + " Used resume command")
    if bot.MuteAll:
        bot.MuteAll = False
        await interaction.response.send_message("Loop resumed.", delete_after=3)
    else:
        await interaction.response.send_message("Loop is already running.", delete_after=3, ephemeral=True)

# ------------------------------- Stop command ------------------------------- #

@snipe.command(name="stop",description="Stop all notifications.")
async def stopLoop(interaction: discord.Interaction):
    print(interaction.user.name + " Used stop command")
    if bot.MuteAll == False:
        bot.MuteAll = True
        await interaction.response.send_message("Loop stopped.", delete_after=3)
    else:
        await interaction.response.send_message("Loop is already stopped.", delete_after=3)

# ------------------------------- Mute command ------------------------------- #

@snipe.command(name="mute",description="Mute a notification type.")
@app_commands.describe(muteonline="Dont show online notifications")
@app_commands.describe(muteoffline="Dont show offline notifications")
@app_commands.describe(othergame="Dont show other game notifications")
async def Mute(interaction: discord.Interaction, muteonline:bool, muteoffline:bool,othergame:bool):
    print(interaction.user.name + " Used mute command")
    bot.OnlineMuted = muteonline
    bot.OfflineMuted = muteoffline
    bot.OtherGame = othergame

    await interaction.response.send_message("changes added.", delete_after=3)

# ------------------------------- List command ------------------------------- #

@snipe.command(name="list", description="List of the players in the loop.")
async def List(interaction: discord.Interaction):
    print(interaction.user.name + " Used list command")
    Docs = list(UsersCollection.find({}))   
    page = 0
    pages = [Docs[i:i + 15] for i in range(0,len(Docs), 15)]
    print(len(pages))
    PreviousPage = Button(label="Previous Page", style=discord.ButtonStyle.blurple,disabled=True)
    NextPage = Button(label="Next Page", style=discord.ButtonStyle.blurple)

    view = View()
    view.add_item(PreviousPage)
    view.add_item(NextPage)
    async def NextPageCB(interaction):
        nonlocal page
        if page < len(pages) - 1:
            page += 1

            PreviousPage.disabled = False if not page == 0 else True
            NextPage.disabled = False if page < len(pages) - 1 else True

            embed = discord.Embed(color=8585471,title="Player list",description="".join(f"**{i+1+(page*15)}.** ``{str(v["Username"])}`` **|** {str(v["UserID"])}\n" for i,v in enumerate(pages[page])))
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            NextPage.disabled = True

    async def PreviousPageCB(interaction):
        nonlocal page
        if not page == 0:
            page -= 1
        
            PreviousPage.disabled = False if not page == 0 else True
            NextPage.disabled = False if page < len(pages) - 1 else True

            embed = discord.Embed(color=8585471,title="Player list",description="".join(f"**{i+1+(page*15)}.** ``{str(v["Username"])}`` **|** {str(v["UserID"])}\n" for i,v in enumerate(pages[page])))
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            PreviousPage.disabled = True
    NextPage.callback = NextPageCB
    PreviousPage.callback = PreviousPageCB

    embed = discord.Embed(color=8585471,title="Player list",description="".join(f"**{i+1+(page*15)}.** ``{str(v["Username"])}`` **|** {str(v["UserID"])}\n" for i,v in enumerate(pages[page])))
    await interaction.response.send_message(embed=embed, view=view)

# ---------------------------- Add player command ---------------------------- #

@snipe.command(name="addplayer",description="Add a player to the loop.")
@app_commands.describe(username="the username to add.")
@app_commands.describe(groupname="Group name NN, None = no group.")
@app_commands.describe(altaccount="True if its an alt account.")
async def addPlayer(interaction: discord.Interaction, username:str, altaccount:bool, groupname:str):
    print(interaction.user.name + " Used addplayer command")
    if not UsersCollection.find_one({"Username": username}):
        response = requests.post("https://users.roblox.com/v1/usernames/users",json={"usernames": [username],"excludeBannedUsers": True})
        if response.status_code == 200:
            responseJSON = response.json()
    
            data = responseJSON.get("data", [])
            if data and "requestedUsername" in data[0]:
                if not UsersCollection.find_one({"UserID": data[0].get("id")}):
                    result = UsersCollection.insert_one({"UserID": data[0].get("id"), "Username": data[0].get("name"), "isAlt": True if altaccount else False, "GroupName": groupname })
                    if result.inserted_id:
                        await interaction.response.send_message("Username added to the loop.", delete_after=3)
                else:
                    UsersCollection.update_one({"UserID": data[0].get("id")}, {"Username": data[0].get("name"), "isAlt": True if altaccount else False, "GroupName": groupname})
                    await interaction.response.send_message("That username is already on the list, updated his data.", delete_after=3, ephemeral=True)
            else:
                await interaction.response.send_message("Username doesn't exist.", delete_after=3, ephemeral=True)
        else:
            await interaction.response.send_message("Error trying to verify username.", delete_after=3, ephemeral=True)
    else:
        await interaction.response.send_message("That username is already on the list.", delete_after=3, ephemeral=True)

# --------------------------- Snipe player command --------------------------- #

@snipe.command(name="player",description="Send player status.")
@app_commands.describe(username="Player username to snipe.")
async def player(interaction: discord.Interaction, username:str):
    print(interaction.user.name + " Used snipe player command")
    response = requests.post("https://users.roblox.com/v1/usernames/users",json={"usernames": [username],"excludeBannedUsers": True})
    if response.status_code == 200:
        responseJSON = response.json()

        data = responseJSON.get("data", [])
        if data and "requestedUsername" in data[0]:
            id = data[0].get("id")
            Username = data[0].get("name")

            response = requests.post("https://presence.roblox.com/v1/presence/users",json={"userIds": [id]},headers={"Cookie": Cookie})
            
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

                    await interaction.response.send_message(content=f"<t:{int(int(time.time()))}:R>", embed=embed)
                else:
                    await interaction.response.send_message("Error: 2", delete_after=3, ephemeral=True)
            else:
                await interaction.response.send_message("Request status code isn't 200 (Presence API).", delete_after=3, ephemeral=True)
        else:
            await interaction.response.send_message("Username doesn't exist.", delete_after=3, ephemeral=True)
    else:
        await interaction.response.send_message("Request status code isn't 200 (Users API).", delete_after=3, ephemeral=True)

# -------------------------------- Track times ------------------------------- #

@track.command(name="times", description="Creates a channel and tracks the queue times from a user.")
@app_commands.describe(username="Player username to track.")
async def TrackQueueTimes(interaction: discord.Interaction, username: str):
    print(interaction.user.name + " used track times command")
    response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True})
    
    if response.status_code == 200:
        responseJSON = response.json()
        data = responseJSON.get("data", [])

        if data and "requestedUsername" in data[0]:
            guild = interaction.guild
            category = guild.get_channel(1288638401947504725)
            if not Tracking.get(data[0]["name"], False) or not discord.utils.get(category.channels, name=data[0]["name"].lower()):

                channel = discord.utils.get(category.channels, name=data[0]["name"].lower()) or await guild.create_text_channel(data[0]["name"], category=category)
                Tracking[data[0]["name"]] = channel
                await interaction.response.send_message(f"Tracking in {channel.mention}", delete_after=5)
            else:
                await interaction.response.send_message("This username is already being tracked.", delete_after=5)
        else:
            await interaction.response.send_message("Username doesn't exist.", delete_after=3, ephemeral=True)
    else:
        await interaction.response.send_message("Error trying to verify username.", delete_after=3, ephemeral=True)

# ---------------------------------- Mutuals --------------------------------- #

@friends.command(name="mutuals", description="check mutuals between users.")
@app_commands.describe(usernames="list of usernames, e.g: OrionYeets, chasemaser, ...")
@app_commands.describe(strict="True = Everyone should have the same player added")
async def mutuals(interaction: discord.Interaction, usernames: str, strict:bool):
    print(interaction.user.name + " Used mutuals command")
    await interaction.response.defer(thinking=True)

    UsernamesArray = usernames.split(",")
    UsernamesArray = [username.strip() for username in UsernamesArray if username.strip()] 

    if len(UsernamesArray) < 2:
        await interaction.followup.send("You need to give 2+ players, e.g: OrionYeets, chasemaser, ...", ephemeral=True)
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
                    response = requests.get(f"https://friends.roblox.com/v1/users/{id}/friends/find?userSort=2&limit=200", headers={"Cookie": Cookie})
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

@friends.command(name="ingame", description="check in-game friends.")
@app_commands.describe(sameserver="True will only show in same server friends.")
@app_commands.describe(username="Player username to check.")
async def ingame(interaction: discord.Interaction, username: str, sameserver:bool):
    print(interaction.user.name + " Used ingame command")
    await interaction.response.defer(thinking=True)

    response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True})
    
    if response.status_code == 200:
        responseJSON = response.json()
        data = responseJSON.get("data", [])

        if data and "requestedUsername" in data[0]:
            response = requests.post("https://presence.roblox.com/v1/presence/users",json={"userIds": [data[0]["id"]]},headers={"Cookie": Cookie})
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
            
            response = requests.get(f"https://friends.roblox.com/v1/users/{data[0]["id"]}/friends/find?userSort=2&limit=200", headers={"Cookie": Cookie})
            responseJSON = response.json()

            data = responseJSON.get("PageItems", [])
            Friends = [Pdata["id"] for Pdata in data]
            if Friends:
                IDLists = [Friends[i:i + 30] for i in range(0,len(Friends), 30)]
                userPresences = []
                userIds  = []
                UsernamesFromId = {}
                for i, SubList in enumerate(IDLists):
                    response = requests.post("https://presence.roblox.com/v1/presence/users",json={"userIds": SubList},headers={"Cookie": Cookie})
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
                            await interaction.followup.send(content=f"<t:{int(int(time.time()))}:R>", embeds=embeds)
                        else:
                            await interaction.channel.send(content=f"<t:{int(int(time.time()))}:R>", embeds=embeds)
            else:
                await interaction.followup.send("No friends found.", ephemeral=True)
        else:
            await interaction.followup.send("Error getting username.", ephemeral=True)
    else:
        await interaction.followup.send("Request status code isn't 200 (Users API).", ephemeral=True)

# ------------------------------- track status ------------------------------- #

@track.command(name="status", description="Creates a channel and tracks the status from a user.")
@app_commands.describe(username="Player username to track.")
async def TrackStatus(interaction: discord.Interaction, username: str):
    print(interaction.user.name + " used track status command")
    response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True})
    
    if response.status_code == 200:
        responseJSON = response.json()
        data = responseJSON.get("data", [])

        if data and "requestedUsername" in data[0]:
            guild = interaction.guild
            category = guild.get_channel(1288642965882933301)
            if not TrackingStatus.get(data[0]["name"], False) or not discord.utils.get(category.channels, name=data[0]["name"].lower()):

                channel = discord.utils.get(category.channels, name=data[0]["name"].lower()) or await guild.create_text_channel(data[0]["name"], category=category)
                TrackingStatus[data[0]["name"]] = [channel, interaction.user.mention]
                await interaction.response.send_message(f"Tracking in {channel.mention}", delete_after=5)
            else:
                await interaction.response.send_message("This username is already being tracked.", delete_after=5)
        else:
            await interaction.response.send_message("Username doesn't exist.", delete_after=3, ephemeral=True)
    else:
        await interaction.response.send_message("Error trying to verify username.", delete_after=3, ephemeral=True)

# --------------------------------- Bot start -------------------------------- #

def main() -> None:
    bot.run(TOKEN)

if __name__ == "__main__":
    main()