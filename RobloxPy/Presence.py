from .CookieManager import cookies
from datetime import datetime
import requests
import aiohttp
import asyncio
import sys

presenceApi = "https://presence.roblox.com"

class UserPresence:
    def __init__(self, data:dict):
        self.data = data
        self.userPresenceType = data["userPresenceType"]
        self.lastlocation = data["lastLocation"]
        self.placeId = data["placeId"]
        self.gameId = data["rootPlaceId"]
        self.jobId = data["gameId"]
        self.universeId = data["universeId"]
        self.userId = data["userId"]
        self.lastOnline = datetime.fromisoformat(data["lastOnline"].replace("Z", "+00:00"))
    
    def json(self):
        names = ["userPresenceType", "lastlocation", "placeId", "universeId", "userId"]
        result = {name: getattr(self, name) for name in names if getattr(self, name)}

        result["gameId"] = self.jobId
        result["rootPlaceId"] = self.gameId
        result["lastOnline"] = self.lastOnline.isoformat()
        return result

class UserPresenceGroup:
    def __init__(self, data:dict):
        self.data = data
        self.presences = [UserPresence(presence) for presence in data]
        self.userIds = [presence.userId for presence in self.presences]
    
    def getByUserId(self, userId:str) -> (UserPresence | None):
        result = [presence for presence in self.presences if presence.userId == userId]
        return result[0] if result else None

    def filterByGameIds(self, *gameIds:int):
        self.presences = [presence for presence in self.presences if presence.gameId in gameIds]

    def filterByPlaceIds(self, *placeIds:int):
        self.presences = [presence for presence in self.presences if presence.placeId in placeIds]
    
    def filterByPresenceTypes(self, *presenceTypes:int):
        self.presences = [presence for presence in self.presences if presence.userPresenceType in presenceTypes]
    
def getLastOnline(*userIds:int) -> (dict[int, datetime] | datetime):
    response = requests.post(presenceApi + "/v1/presence/last-online",
        headers={
            "Cookie": cookies.getCookie()
        },
        json={
            "userIds": list(userIds)
        }
    )

    if response.status_code == 200:
        responseJson:dict = response.json()
        data:list = responseJson.get("lastOnlineTimestamps")

        if data and "lastOnline" in data[0]:
            result = datetime.fromisoformat(data[0]["lastOnline"].replace("Z", "+00:00"))

            if len(userIds) > 1:
                result = {value["userId"]: datetime.fromisoformat(value["lastOnline"].replace("Z", "+00:00")) for value in data}
                result.update({userId: result.get(userId, None) for userId in userIds})

            return result
        else:
            raise KeyError(f"LastOnline not found in the response json", response.text)
    else:
        raise requests.exceptions.HTTPError(f"Error in the request: {response.status_code}", response.text)

async def getPresence(*userIds:int) -> UserPresenceGroup:
    async def fetchData(session:aiohttp.ClientSession, userIds):
        while True:
            async with session.post(presenceApi + "/v1/presence/users",
                    headers={
                        "Cookie": cookies.getCookie()
                    },
                    json={
                        "userIds": userIds
                    }
                ) as response:
            
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Error in the request: {response.status}\n{await response.text()}\nTrying again in 500ms", file=sys.stderr)
            await asyncio.sleep(0.5)

    groups = [[userId for userId in userIds[i:i + 30]] for i in range(0, len(userIds), 30)]

    async def proccessGroups():
        async with aiohttp.ClientSession() as session:
            sem = asyncio.Semaphore(5)
            results = []

            tasks = [asyncio.create_task(fetchData(session,userIds)) for userIds in groups]

            async def runWithSemaphore(task):
                async with sem:
                    return await task
            
            responses = await asyncio.gather(*[runWithSemaphore(task) for task in tasks], return_exceptions=True)
            for response in responses:
                if isinstance(response, Exception):
                    print(f"Error encountered: {response}", file=sys.stderr)
                else:
                    results.extend(response["userPresences"])
        
        return results
    
    results = await proccessGroups()

    return UserPresenceGroup(results)
    
async def getPresenceFromUsername(*usernames:str) -> tuple[UserPresenceGroup, UserGroup]:
    users = getUsersFromUsername(*list(usernames))

    return await getPresence(*users.userIds), users

from .Users import getUsersFromUsername, UserGroup