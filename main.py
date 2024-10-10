from dataclasses import dataclass
from discord.ext import commands
from pymongo import MongoClient
from threading import Thread
from waitress import serve
from flask import Flask
import traceback
import discord
import aiohttp
import asyncio
import time
import os

# --------------------------- Environment variables -------------------------- #

MONGOURI = os.environ.get("MONGO_URI")
COOKIE = os.environ.get("COOKIE")
TOKEN = os.environ.get("TOKEN")

# ----------------------------- DataBase ----------------------------- #

Client = MongoClient(MONGOURI)
dataBase = Client["AltFarmerDetector"]
UsersCollection = dataBase["Users"]

# ---------------------------------- Server ---------------------------------- #

app = Flask(__name__)

@app.route("/")
def answer():
      return "Alive"

Thread(target=lambda: serve(app, host="0.0.0.0", port=8080)).start()

# ------------------------------------ Bot ----------------------------------- #

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is ready")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Bedwars Ranked"))

    bot.loop.create_task(GetStatus())
    try:
        print("Comandos slash registrados:")
        for command in bot.tree.get_commands():
            print(command.name)

        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

bot.Tracking = {}
bot.TrackingStatus = {}
bot.MuteAll = False
bot.OnlineMuted = bot.OfflineMuted = bot.OtherGame = True
GameIdList = {}

# -------------------------- Get status fnction -------------------------- #

async def GetData(session,userIds, i):
    async with session.post("https://presence.roblox.com/v1/presence/users",json={"userIds": userIds},headers={"Cookie": COOKIE}) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("userPresences", f"Request status code isn't 200.\n{data, i}")

async def GetStatus():
    GameIdWithAltsChannel = bot.get_channel(1277089252676472894)
    GameIdChannel = bot.get_channel(1277046568033194115)
    Altchannel = bot.get_channel(1277302313949593742)
    channel = bot.get_channel(1277039650401423471)

    while True:
        try:
            if channel:
                Documents = list(UsersCollection.find({}))
                if Documents:
                    IDLists = [[doc["UserID"] for doc in Documents[i:i + 30]] for i in range(0, len(Documents), 30)]
                    
                    async with aiohttp.ClientSession() as session:
                        tasks = [GetData(session, subList, i) for i, subList in enumerate(IDLists)]
                        results = await asyncio.gather(*tasks)

                    userPresences = []
                    for result in results:
                        if isinstance(result, str):
                            await channel.send(result)
                            continue
                        userPresences.extend(result)
                    
                    await channel.purge(limit=100)
                    await Altchannel.purge(limit=100)
                    await asyncio.gather(
                        UserStatus(userPresences, channel, Altchannel),
                        SameGameId(userPresences, GameIdChannel, GameIdWithAltsChannel)
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

# ----------------------- User status function ----------------------- #

@dataclass
class UserPresence:
    Username: str
    UserID : str
    isAlt: str
    PresenceType: int
    LobbyStatus: str
    GameName: str
    GameId: str
    Group: str

async def UserStatus(userPresences, channel, AltChannel):
    embeds = {}
    if userPresences:
        userIDs = [presence["userId"] for presence in userPresences]
        
        results = list(UsersCollection.find({"UserID": {"$in": userIDs}}))

        for presence in userPresences:
            Data = next((doc for doc in results if doc["UserID"] == presence["userId"]))
            ud = UserPresence(Data["Username"], presence["userId"], Data["isAlt"], presence["userPresenceType"], "True" if presence["placeId"] == 6872265039 else "False", presence["lastLocation"] or "None", presence["gameId"], Data.get("GroupName", "None"))

            if ud.UserID not in GameIdList:
                GameIdList[ud.UserID] = [["nil", ud.GameId or "nil"], ["nil", f"<t:{round(time.time())}:R>"], ud.LobbyStatus, ud.GameName, ud.PresenceType]

            userGameInfo = GameIdList[ud.UserID]
            currentGameId = userGameInfo[0][1]
            isDifferentGame = ud.GameId and currentGameId != ud.GameId
            isOffline = ud.PresenceType == 0 and currentGameId

            if isDifferentGame or isOffline:
                if bot.Tracking.get(ud.UserID):
                    try:
                        resultTime = round(time.time()) - int(userGameInfo[1][1][3:-3])
                        timeInGame = f"{resultTime} Seconds" if resultTime < 60 else f"{resultTime // 60}:{resultTime % 60:02d} Minutes"

                        embed = discord.Embed(color=46847,title="Time in game: " + timeInGame)
                        embed.add_field(name="From:", value=f"Game: **{userGameInfo[3]}**\nGameId: **{userGameInfo[0][1]}**\nLobby: **{userGameInfo[2]}**", inline=True)
                        embed.add_field(name="To:", value=f"Game: **{ud.GameName}**\nGameId: **{ud.GameId}**\nLobby: **{ud.LobbyStatus}**", inline=True)

                        await bot.Tracking[ud.UserID][0].send(content=f"<t:{round(time.time())}:R>{"".join(bot.Tracking[ud.UserID][1])}", embed=embed)
                    except Exception as e:
                        print(f"Error enviando trackingtimes: {e}.")
                        traceback.print_exc()
                
                userGameInfo[2] = ud.LobbyStatus
                userGameInfo[3] = ud.GameName
                userGameInfo[1][0] = userGameInfo[1][1]
                userGameInfo[0][0] = currentGameId
                userGameInfo[1][1] = f"<t:{round(time.time())}:R>"
                userGameInfo[0][1] = ud.GameId
            
            LastGameId = userGameInfo[0][0]
            TimeInGameId = userGameInfo[1][1]

            color = (2686720 if ud.PresenceType == 2 else 46847 if ud.PresenceType == 1 else 7763574) if ud.PresenceType != 2 or ud.LobbyStatus == "True" else 1881856
            title = ud.Username + (" is in a game" if ud.PresenceType == 2 else " is online" if ud.PresenceType == 1 else f" is offline")
            description = f"Game: **{ud.GameName}**" + (f"\nLobby: **{ud.LobbyStatus}**\nGameId: **{ud.GameId}**\nLastGameId: **{LastGameId}**\nTime in gameId: **{TimeInGameId}**" if ud.PresenceType == 2 and presence["rootPlaceId"] == 6872265039 else "")
            embed = discord.Embed(color=color,title=title,description=description if ud.PresenceType == 2 and presence["rootPlaceId"] != None else None)

            if ud.Group != "None":
                embed.set_footer(text= "Group: " + ud.Group)

            if ud.isAlt and (ud.PresenceType == 2 and not bot.MuteAll and (presence["rootPlaceId"] == None or presence["rootPlaceId"] == 6872265039)):
                await AltChannel.send(content=f"<t:{round(time.time())}:R><@&1288980643061170188>",embed=embed)

            if bot.TrackingStatus.get(ud.UserID) and not userGameInfo[4] == ud.PresenceType:
                try:
                    await bot.TrackingStatus[ud.UserID][0].send(content=f"<t:{round(time.time())}:R>{"".join(bot.TrackingStatus[ud.UserID][1])}",embed=embed)
                except Exception as e:
                    print(f"Error enviando trackingstatus: {e}.")
                    traceback.print_exc()

            userGameInfo[4] = ud.PresenceType

            if (ud.PresenceType == 2 and ((presence["rootPlaceId"] == 6872265039 or presence["rootPlaceId"] == None) or not bot.OtherGame) and not bot.MuteAll) or (ud.PresenceType == 1 and not (bot.OnlineMuted or bot.MuteAll)) or (ud.PresenceType == 0 and not (bot.OfflineMuted or bot.MuteAll)):
                if not ud.Group in embeds:
                    embeds[ud.Group] = [ud.PresenceType == 2 and (presence["rootPlaceId"] == None or (presence["rootPlaceId"] == 6872265039 and not presence["placeId"] == 6872265039))]
                    embeds[ud.Group].append(embed)
                else:
                    if not ud.Group == "None":
                        if embeds[ud.Group][1] == False:
                            embeds[ud.Group][1] = ud.PresenceType == 2 and (presence["rootPlaceId"] == None or (presence["rootPlaceId"] == 6872265039 and not presence["placeId"] == 6872265039))
                    else:
                        embeds[ud.Group].append(ud.PresenceType == 2 and (presence["rootPlaceId"] == None or (presence["rootPlaceId"] == 6872265039 and not presence["placeId"] == 6872265039)))
                    embeds[ud.Group].append(embed)
            
        for groupName, Embeds in embeds.items():
            if not groupName == "None":
                SubGroups = [Embeds[i:i + 10] for i in range(0,len(Embeds), 10)]
                for group in SubGroups:
                    await channel.send(content=f"<t:{round(time.time())}:R>" + ("<@&1288980643061170188>" if group[0] else ""),embeds=group[1:])

        if embeds.get("None"):
            for i, embed in enumerate(embeds["None"]):
                if not (i % 2) == 0:
                    await channel.send(content=f"<t:{round(time.time())}:R>" + ("<@&1288980643061170188>" if embeds["None"][i-1] else ""),embed=embed)
    else:
        await channel.send("Error: 2", delete_after=3)

# ----------------------- Same game id function ---------------------- #

async def SameGameId(userPresences, channel, channel2):
    userIDs = [presence["userId"] for presence in userPresences]
    results = list(UsersCollection.find({"UserID": {"$in": userIDs}}))

    GameIds = {}
    
    for presence in userPresences:
        if presence.get("gameId") and presence.get("rootPlaceId") == 6872265039:
            if GameIds.get(presence["gameId"]):
                GameIds[presence["gameId"]][0].append(presence["userId"])
            else:
                GameIds[presence["gameId"]] = [[presence["userId"]],{"gameName": presence["lastLocation"], "isLobby": "True" if presence["placeId"] == 6872265039 else "False"}]

    embeds = []
    for gameId, Ids in GameIds.items():
        list2 = Ids[1]
        Ids = Ids[0]
        Title = "GameId: " + gameId
        Description = f"## GameId description\nGame: **{list2["gameName"]}**\nLobby: **{list2["isLobby"]}**\n## In-game player ({len(Ids)})"
        Everyone = False

        for Userid in Ids:
            doc = next((doc for doc in results if doc["UserID"] == Userid))
            Username = doc["Username"]
            Description += f"\nUsername: **{Username}**\n- isAlt: **{doc["isAlt"]}**"

            if doc["isAlt"] == True:
                Everyone = True

        Embed = discord.Embed(color=2686720 if list2["isLobby"] == "True" else 1881856, title=Title, description=Description)
        embeds.append(Embed)
        if Everyone:
            await channel2.send(content=f"<t:{round(time.time())}:R><@&1288980643061170188>", embed=Embed)
    
    for embedgroup in [embeds[i:i + 10] for i in range(0,len(embeds), 10)]:
        await channel.send(content=f"<t:{round(time.time())}:R>", embeds=embedgroup)

# ----------------------------------- start ---------------------------------- #

async def loadExtensions():
    await bot.load_extension("Commands.ReportsCommands")
    await bot.load_extension("Commands.FriendsCommands")
    await bot.load_extension("Commands.SnipeCommands")
    await bot.load_extension("Commands.TrackCommands")
    await bot.load_extension("Commands.ListCommands")

async def main():
    await loadExtensions()
    await bot.start(TOKEN)

asyncio.run(main())