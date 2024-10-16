from discord.ext import commands
from pymongo import MongoClient
from threading import Thread
from waitress import serve
from flask import Flask
import traceback
import RobloxPy
import discord
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

# ------------------------------ RobloxPy start ------------------------------ #

RobloxPy.cookies.setCookie(COOKIE)

# ------------------------------------ Bot ----------------------------------- #

class Bot(commands.Bot):
    async def setup_hook(self):
        await self.loadExtensions()

    async def loadExtensions(self):
        extensions = []
        for filename in os.listdir("./Commands"):
            if filename.endswith(".py"):
                extensions.append("Commands." + filename[:-3])

        for extension in extensions:
            try:
                await self.load_extension(extension)
                print(f"Loaded {extension}")
            except Exception as e:
                print(f"Failed to load extension {extension}: {e}")

bot = Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is ready")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Bedwars Ranked"))

    bot.loop.create_task(getStatus())
    try:
        print("Comandos slash registrados:")
        for command in bot.tree.get_commands():
            print(command.name)
            traceback.print_exc()

        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
        traceback.print_exc()

bot.Tracking = {}
bot.TrackingStatus = {}
bot.MuteAll = False
bot.OnlineMuted = bot.OfflineMuted = bot.OtherGame = True
GameIdList = {}

# -------------------------- Get status fnction -------------------------- #

async def getStatus():
    gameIdWithAltsChannel = bot.get_channel(1277089252676472894)
    gameIdChannel = bot.get_channel(1277046568033194115)
    altChannel = bot.get_channel(1277302313949593742)
    channel = bot.get_channel(1277039650401423471)

    while True:
        try:
            if channel:
                documents = list(UsersCollection.find({}))
                if documents:
                    userPresences = await RobloxPy.Presence.getPresence(*[doc["UserID"] for doc in documents])
                    results = list(UsersCollection.find({"UserID": {"$in": userPresences.userIds}}))
                    
                    for presence in userPresences.presences:
                        data = next((doc for doc in results if doc["UserID"] == presence.userId))
                        presence.username = data["Username"]
                        presence.lobbyStatus = "True" if presence.placeId == 6872265039 else "False"
                        presence.groupName = data.get("GroupName", "None")
                        presence.isAlt = data["isAlt"]

                    if userPresences:
                        await channel.purge(limit=100)
                        await altChannel.purge(limit=100)
                        await asyncio.gather(
                            userStatus(userPresences, channel, altChannel),
                            sameGameId(userPresences, gameIdChannel, gameIdWithAltsChannel)
                        )
                else:
                    print("Docs not found")
            else:
                print("Channel doesn't exist or not added")

            await asyncio.sleep(20)
        except Exception as e:
            print(f"Error en el bucle principal: {e}.")
            traceback.print_exc()

# ----------------------- User status function ----------------------- #

async def userStatus(userPresences:RobloxPy.Presence.UserPresenceGroup, channel, altChannel):
    async def createEmbeds(presence:RobloxPy.Presence.UserPresence):
        if presence.userId not in GameIdList:
            GameIdList[presence.userId] = [["nil", presence.jobId or "nil"], ["nil", f"<t:{round(time.time())}:R>"], presence.lobbyStatus, presence.lastlocation, presence.userPresenceType]

        userGameInfo = GameIdList[presence.userId]
        currentGameId = userGameInfo[0][1]
        isDifferentGame = presence.jobId and currentGameId != presence.jobId
        isOffline = presence.userPresenceType == 0 and currentGameId

        if isDifferentGame or isOffline:
            if bot.Tracking.get(presence.username):
                try:
                    resultTime = round(time.time()) - int(userGameInfo[1][1][3:-3])
                    timeInGame = f"{resultTime} Seconds" if resultTime < 60 else f"{resultTime // 60}:{resultTime % 60:02d} Minutes"

                    embed = discord.Embed(title="Time in game: " + timeInGame, color=46847)
                    embed.add_field(name="From:",
                        value=f"Game: **{userGameInfo[3]}**\nGameId: **{userGameInfo[0][1]}**\nLobby: **{userGameInfo[2]}**",
                        inline=True
                    )
                    embed.add_field(name="To:",
                        value=f"Game: **{presence.lastlocation}**\nGameId: **{presence.jobId}**\nLobby: **{presence.lobbyStatus}**",
                        inline=True
                    )

                    await bot.Tracking[presence.username][0].send(content=f"<t:{round(time.time())}:R>{"".join(bot.Tracking[presence.username][1])}", embed=embed)
                except Exception as e:
                        print(f"Error sending tracking times: {e}.")
                        traceback.print_exc()
                
                userGameInfo[2] = presence.lobbyStatus
                userGameInfo[3] = presence.lastlocation
                userGameInfo[1][0] = userGameInfo[1][1]
                userGameInfo[0][0] = currentGameId
                userGameInfo[1][1] = f"<t:{round(time.time())}:R>"
                userGameInfo[0][1] = presence.jobId
            
        LastGameId = userGameInfo[0][0]
        TimeInGameId = userGameInfo[1][1]

        color = (2686720 if presence.userPresenceType == 2 else 46847 if presence.userPresenceType == 1 else 7763574) if presence.userPresenceType != 2 or presence.userPresenceType == "True" else 1881856
        title = presence.username + (" is in a game" if presence.userPresenceType == 2 else " is online" if presence.userPresenceType == 1 else f" is offline")
        description = f"Game: **{presence.lastlocation}**" + (f"\nLobby: **{presence.lobbyStatus}**\nGameId: **{presence.jobId}**\nLastGameId: **{LastGameId}**\nTime in gameId: **{TimeInGameId}**" if presence.userPresenceType == 2 and presence.gameId == 6872265039 else "")
        embed = discord.Embed(color=color,title=title,description=description if presence.userPresenceType == 2 and presence.gameId != None else None)

        if presence.groupName != "None":
            embed.set_footer(text= "Group: " + presence.groupName)

        if presence.isAlt and (presence.gameId == None or presence.gameId == 6872265039):
            asyncio.create_task(altChannel.send(content=f"<t:{round(time.time())}:R><@&1288980643061170188>",embed=embed))
        
        if bot.TrackingStatus.get(presence.username) and not userGameInfo[4] == presence.userPresenceType:
            try:
                await bot.TrackingStatus[presence.username][0].send(content=f"<t:{round(time.time())}:R>{"".join(bot.TrackingStatus[presence.username][1])}",embed=embed)
            except Exception as e:
                print(f"Error enviando trackingstatus: {e}.")
                traceback.print_exc()
        
        userGameInfo[4] = presence.userPresenceType

        if (presence.gameId == 6872265039 or presence.gameId == None) or not bot.OtherGame:
            if not presence.groupName in embeds:
                embeds[presence.groupName] = [presence.userPresenceType == 2 and (presence.gameId == None or (presence.gameId == 6872265039 and not presence.placeId == 6872265039))]
                embeds[presence.groupName].append(embed)
            else:
                if not presence.groupName == "None":
                    if embeds[presence.groupName][1] == False:
                        embeds[presence.groupName][1] = presence.userPresenceType == 2 and (presence.gameId == None or (presence.gameId == 6872265039 and not presence.placeId == 6872265039))
                else:
                    embeds[presence.groupName].append(presence.userPresenceType == 2 and (presence.gameId == None or (presence.gameId == 6872265039 and not presence.placeId == 6872265039)))
                embeds[presence.groupName].append(embed)

    embeds = {}
    presenceTypes = [0, 1, 2] if not bot.MuteAll else []
    presenceTypes = [p for p in presenceTypes if not ((p == 0 and bot.OfflineMuted) or (p == 1 and bot.OnlineMuted))]

    userPresences.filterByPresenceTypes(*presenceTypes)
    
    tasks = []
    for presence in userPresences.presences:
        tasks.append(asyncio.create_task(createEmbeds(presence)))

    await asyncio.gather(*tasks)

    for groupName, Embeds in embeds.items():
            if not groupName == "None":
                SubGroups = [Embeds[i:i + 10] for i in range(0,len(Embeds), 10)]
                for group in SubGroups:
                    await channel.send(content=f"<t:{round(time.time())}:R>" + ("<@&1288980643061170188>" if group[0] else ""),embeds=group[1:])

    if embeds.get("None"):
        for i, embed in enumerate(embeds["None"]):
            if not (i % 2) == 0:
                await channel.send(content=f"<t:{round(time.time())}:R>" + ("<@&1288980643061170188>" if embeds["None"][i-1] else ""),embed=embed)

# ----------------------- Same game id function ---------------------- #

async def sameGameId(userPresences:RobloxPy.Presence.UserPresenceGroup, channel, channel2):
    gameIds = {}

    userPresences.filterByPresenceTypes(2)
    userPresences.filterByGameIds(6872265039)
    for presence in userPresences.presences:
        if presence.jobId:
            if gameIds.get(presence.jobId):
                gameIds[presence.jobId][0].append(presence.userId)
            else:
                gameIds[presence.jobId] = [[presence.userId], {"gameName": presence.lastlocation, "isLobby": presence.lobbyStatus}]

    embeds = []
    for gameId, ids in gameIds.items():
        list2 = ids[1]
        Ids = ids[0]
        Title = "GameId: " + gameId
        description = f"## GameId description\nGame: **{list2["gameName"]}**\nLobby: **{list2["isLobby"]}**\n## In-game player ({len(Ids)})"
        Everyone = False

        for userId in Ids:
            presence = userPresences.getByUserId(userId)
            description += f"\nUsername: **{presence.username}**\n- isAlt: **{presence.isAlt}**"

            if presence.isAlt == True:
                Everyone = True

        Embed = discord.Embed(color=2686720 if list2["isLobby"] == "True" else 1881856, title=Title, description=description)
        embeds.append(Embed)
        if Everyone:
            asyncio.create_task(channel2.send(content=f"<t:{round(time.time())}:R><@&1288980643061170188>", embed=Embed))
    
    for embedgroup in [embeds[i:i + 10] for i in range(0,len(embeds), 10)]:
        await channel.send(content=f"<t:{round(time.time())}:R>", embeds=embedgroup)

# ----------------------------------- start ---------------------------------- #

asyncio.run(bot.start(TOKEN))