from discord.ui import Button, View
from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient
from threading import Thread
from flask import Flask
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

# ------------------------------ On ready event ------------------------------ #

@bot.event
async def on_ready():
    print("Bot is ready")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Bedwars Ranked"))

    bot.tree.add_command(snipe)
    bot.loop.create_task(Start())
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# ------------------------------- Main function ------------------------------ #

Tracking = {}
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
        #try:
            todelete = []
            todelete2 = []
            if channel:
                Docs = UsersCollection.find({})
                if Docs:
                    UserIDs = []

                    for doc in Docs:
                        UserIDs.append(doc["UserID"])

                    IDLists = [UserIDs[i:i + 30] for i in range(0,len(UserIDs), 30)]
                    
                    userPresences = []
                    for SubList in IDLists:
                        response = requests.post("https://presence.roblox.com/v1/presence/users",json={"userIds": SubList},headers={"Cookie": Cookie})
                        if response.status_code == 200:
                            userPresences.extend(response.json().get("userPresences", []))
                        else:
                            await channel.send("Request status code isn't 200.", delete_after=3)

                    await asyncio.gather(
                        UserStatus(userPresences, channel, Altchannel, todelete, todelete2),
                        SameGameid(userPresences, GameIdChannel, GameIdWithAltsChannel)
                    )
                else:
                    print("Docs not found")
            else:
                print("Channel doesn't exist or not added")
                await asyncio.sleep(10)
                continue

            await asyncio.sleep(10)
            await channel.delete_messages(todelete)
            await Altchannel.delete_messages(todelete2)

        #except Exception as e:
        #    print(f"Error en el bucle principal: {e}.")

# --------------------------- User status function --------------------------- #

async def UserStatus(userPresences, channel, AltChannel, todelete, todelete2):
    if userPresences:
        for doc in userPresences:
            PresenceType = doc["userPresenceType"]
            ResultFound = UsersCollection.find_one({"UserID": doc["userId"]})
            isAlt = ResultFound["isAlt"]
            Username = ResultFound["Username"]
            LobbyStatus = "True" if doc["placeId"] == 6872265039 else "False"
            GameName = doc["lastLocation"]
            GameId = doc["gameId"]

            if GameId not in GameIdList:
                GameIdList[GameId] = [["nil", "nil" if GameId is None else GameId], ["nil", f"<t:{int(time.time())}:R>"], "True" if doc["placeId"] == 6872265039 else "False"]

            if GameId and not GameIdList.get(GameId)[0][1] == GameId:
                if Tracking.get(Username):
                    Result = int(time.time()) - int(GameIdList.get(doc["userId"])[1][0][3:-3])
                    embed = discord.Embed(color=46847,title=f"Time in game: {(Result + "Seconds") if Result < 60 else (int(Result / 60) + ":" + Result % 60 + "Minutes" ) }", description=f"Game: **{GameName}**\nGameId: **{GameId}**\nLobby: **{LobbyStatus}**")
                    await Tracking[Username].send(embed=embed)
                GameIdList.get(doc["userId"])[2] = "True" if doc["placeId"] == 6872265039 else "False"
                GameIdList.get(doc["userId"])[1][0] = GameIdList.get(doc["userId"])[1][1]
                GameIdList.get(doc["userId"])[0][0] = GameIdList.get(doc["userId"])[0][1]
                GameIdList.get(doc["userId"])[1][1] = f"<t:{int(time.time())}:R>"
                GameIdList.get(doc["userId"])[0][1] = GameId

            LastGameId = GameIdList.get(doc["userId"])[0][0]
            TimeInGameId = GameIdList.get(doc["userId"])[1][1]

            color = 2686720 if PresenceType == 2 else 46847 if PresenceType == 1 else 7763574
            title = f"{Username} is in a game" if PresenceType == 2 else f"{Username} is online" if PresenceType == 1 else f"{Username} is offline"
            description = f"Game: **{GameName}**" + (f"\nLobby: **{LobbyStatus}**\nGameId: **{GameId}**\nLastGameId: **{LastGameId}**\nTime in gameId: **{TimeInGameId}**" if PresenceType == 2 and doc["rootPlaceId"] == 6872265039 else "")
            embed = discord.Embed(color=color if LobbyStatus == "True" else 1881856,title=title,description=description if PresenceType == 2 and not doc["rootPlaceId"] == None else None)

            if isAlt and (PresenceType == 2 and not bot.MuteAll and (doc["rootPlaceId"] == None or doc["rootPlaceId"] == 6872265039)):
                todelete2.append(await AltChannel.send(content=f"<t:{int(int(time.time()))}:R>@everyone",embed=embed))

            if (PresenceType == 2 and ((doc["rootPlaceId"] == 6872265039 or doc["rootPlaceId"] == None) or not bot.OtherGame) and not bot.MuteAll) or (PresenceType == 1 and not (bot.OnlineMuted or bot.MuteAll)) or (PresenceType == 0 and not (bot.OfflineMuted or bot.MuteAll)):
                todelete.append(await channel.send(content=f"<t:{int(int(time.time()))}:R>" + ("@everyone" if PresenceType == 2 and (doc["rootPlaceId"] == None or (doc["rootPlaceId"] == 6872265039 and not doc["placeId"] == 6872265039)) else ""),embed=embed))

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
@app_commands.describe(altaccount="True if its an alt account.")
async def addPlayer(interaction: discord.Interaction, username:str, altaccount:bool):
    print(interaction.user.name + " Used addplayer command")
    if not UsersCollection.find_one({"Username": username}):
        response = requests.post("https://users.roblox.com/v1/usernames/users",json={"usernames": [username],"excludeBannedUsers": True})
        if response.status_code == 200:
            responseJSON = response.json()
    
            data = responseJSON.get("data", [])
            if data[0] and "requestedUsername" in data[0]:
                result = UsersCollection.insert_one({"UserID": data[0].get("id"), "Username": data[0].get("name"), "isAlt": True if altaccount else False })
                if result.inserted_id:
                    await interaction.response.send_message("Username added to the loop.", delete_after=3)
            else:
                await interaction.response.send_message("Username doesn't exist.", delete_after=3, ephemeral=True)
        else:
            await interaction.response.send_message("Error trying to verify username.", delete_after=3, ephemeral=True)
    else:
        await interaction.response.send_message("That username is already in the list.", delete_after=3, ephemeral=True)

# --------------------------- Snipe player command --------------------------- #

@snipe.command(name="player",description="Send player status.")
@app_commands.describe(username="Player username to snipe.")
async def Snipe(interaction: discord.Interaction, username:str):
    print(interaction.user.name + " Used snipe player command")
    response = requests.post("https://users.roblox.com/v1/usernames/users",json={"usernames": [username],"excludeBannedUsers": True})
    if response.status_code == 200:
        responseJSON = response.json()

        data = responseJSON.get("data", [])
        if data[0] and "requestedUsername" in data[0]:
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
                    embed = discord.Embed(color=color if LobbyStatus == "True" else 1881856,title=title,description=description if PresenceType == 2 and not doc["rootPlaceId"] == None else None)

                    if (PresenceType == 2 and not (bot.MuteAll or ((not doc["rootPlaceId"] == 6872265039 and not doc["rootPlaceId"] == None) and bot.OtherGame))) or (PresenceType == 1 and not (bot.OnlineMuted or bot.MuteAll)) or (PresenceType == 0 and not (bot.OfflineMuted or bot.MuteAll)):
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

@snipe.command(name="tracktimes", description="Creates a channel and tracks the queue times from a username.")
@app_commands.describe(username="Player username to track.")
async def TrackQueueTimes(interaction: discord.Interaction, username: str):
    print(interaction.user.name + " used track times command")
    
    response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True})
    
    if response.status_code == 200:
        responseJSON = response.json()
        data = responseJSON.get("data", [])

        if data and "requestedUsername" in data[0]:
            if not Tracking.get(data[0]["name"], False):
                guild = interaction.guild
                existingChannel = discord.utils.get(guild.channels, name=data[0]["name"])
                
                if not existingChannel:
                    channel = await guild.create_text_channel(data[0]["name"])
                    Tracking[data[0]["name"]] = channel
                    await interaction.response.send_message("Starting...", delete_after=5)
                else:
                    await interaction.response.send_message("Channel with the same name as username already exists.", delete_after=5)
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