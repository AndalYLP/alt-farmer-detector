from .CookieManager import cookies
from datetime import datetime
import requests

userApi = "https://users.roblox.com"

class User:
    def __init__(self, data:dict):
        self.data = data
        self.userId = data["id"]
        self.username = data["name"]
        self.displayName = data["displayName"]
        self.hasVerifiedBadge = data["hasVerifiedBadge"]
        self.requestedUsername = data.get("requestedUsername")
    
    def getLastOnline(self) -> datetime:
        return getLastOnline(self.userId)

    async def getPresence(self) -> "UserPresence":
        return (await getPresence(self.userId)).getByUserId(self.userId)
    
    def getThumbnail(self) -> "ThumbnailObject":
        return getUsersAvatar(self.userId, size="150x150").getByTargetId(self.userId)

class UserGroup:
    def __init__(self, data):
        self.data = data
        self.users:list[User] = [User(user) for user in data]
        self.userIds:list[int] = [user["id"] for user in data]
        self.usernames:list[str] = [user["name"] for user in data]

    def getByUserId(self, userId:int) -> (User | None):
        result = [user for user in self.users if user.userId == userId]
        return result[0] if result else None

    def getByUsername(self, username:str) -> (User | None):
        result = [user for user in self.users if user.username == username]
        return result[0] if result else None
    
    def getByRequestedUsername(self, requestedUsername:str) -> (User | None):
        result = [user for user in self.users if user.requestedUsername == requestedUsername]
        return result[0] if result else None

def getIds(*usernames:str, excludeBanned:bool = True) -> dict[str, int | None]:
    response = requests.post(userApi + "/v1/usernames/users",
        json={
            "usernames": list(usernames),
            "excludeBannedUsers": excludeBanned
        },
        headers={
            "Cookie": cookies.getCookie()
        }
    )

    if response.status_code == 200:
        responseJson:dict = response.json()
        data:list = responseJson.get("data")

        if data and "id" in data[0]:     
            result = {value["requestedUsername"]: value["id"] for value in data}
            result.update({username: result.get(username, None) for username in usernames})

            return result
        else:
            raise KeyError(f"Id not found in the response json", response.text)
    else:
        raise requests.exceptions.HTTPError(f"Error in the request with {userApi}'s Endpoint: {response.status_code}", response.text)
    
def getUsernames(*userIds:int, excludeBanned:bool = True) -> dict[int, str, None]:
    response = requests.post(userApi + "/v1/users",
        json={
            "userIds": list(userIds),
            "excludeBannedUsers": excludeBanned
        },
        headers={
            "Cookie": cookies.getCookie()
        }
    )

    if response.status_code == 200:
        responseJson:dict = response.json()
        data:list = responseJson.get("data")

        if data and "name" in data[0]:
            result = {value["id"]: value["name"] for value in data}
            result.update({userId: result.get(userId, None) for userId in userIds})

            return result
        else:
            raise KeyError("Name not found in the response json")
    else:
        raise requests.exceptions.HTTPError(f"Error in the request: {response.status_code}\n{response.text}")
    
def getUsersFromUserId(*userIds:str, excludeBanned:bool = True) -> UserGroup:
    response = requests.post(userApi + "/v1/users",
        json={
            "userIds": list(userIds),
            "excludeBannedUsers": excludeBanned
        },
        headers={
            "Cookie": cookies.getCookie()
        }
    )

    if response.status_code == 200:
        responseJson:dict = response.json()
        data:list = responseJson.get("data")

        if data and "name" in data[0]:

            return UserGroup(data)
        else:
            raise KeyError("Name not found in the response json")
    else:
        raise requests.exceptions.HTTPError(f"Error in the request: {response.status_code}\n{response.text}")
    
def getUsersFromUsername(*usernames:str, excludeBanned:bool = True) -> UserGroup:
    response = requests.post(userApi + "/v1/usernames/users",
        json={
            "usernames": list(usernames),
            "excludeBannedUsers": excludeBanned
        },
        headers={
            "Cookie": cookies.getCookie()
        }
    )

    if response.status_code == 200:
        responseJson:dict = response.json()
        data:list = responseJson.get("data")

        if data and "id" in data[0]:     

            return UserGroup(data)
        else:
            raise KeyError(f"Id not found in the response json", response.text)
    else:
        raise requests.exceptions.HTTPError(f"Error in the request with {userApi}'s Endpoint: {response.status_code}", response.text)
    
from .Presence import getLastOnline, getPresence, UserPresence
from .Thumbnails import ThumbnailObject, getUsersAvatar