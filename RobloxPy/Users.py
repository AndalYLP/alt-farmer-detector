from RobloxPy.Common import getUsersFromUserId, getUsersFromUsername
from .CookieManager import cookies
from datetime import datetime
import requests

userApi = "https://users.roblox.com"

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