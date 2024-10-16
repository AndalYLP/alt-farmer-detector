from .CookieManager import cookies
from .Users import getIds
import requests
import aiohttp
import asyncio
import sys

thumbnailsApi = "https://thumbnails.roblox.com"

class ThumbnailObject:
    def __init__(self, data:dict):
        self.data = data

        self.requestId = data.get("requestId")
        self.imageUrl = data["imageUrl"]
        self.targetId = data["targetId"]

        self.state = data["state"]
        errorMessage = data.get("errorMessage", False)
        self.error:(str | bool) = errorMessage if errorMessage != "" else False

class BatchObject:
    """
    ### You are probably searching for ThumbnailBatchObject!
    """
    def __init__(self, data:dict):
        self.data = data
        self.thumbnails = [ThumbnailObject(thumbnail) for thumbnail in data]
    
    def getByImageUrl(self, url:str) -> (ThumbnailObject | None):
        result = [thumbnail for thumbnail in self.thumbnails if thumbnail.imageUrl == url]
        return result[0] if result else None
    
    def getByRequestId(self, requestId:str) -> (ThumbnailObject | None):
        result = [thumbnail for thumbnail in self.thumbnails if thumbnail.requestId == requestId]
        return result[0] if result else None

    def getByTargetId(self, targetId:int) -> (ThumbnailObject | None):
        result = [thumbnail for thumbnail in self.thumbnails if thumbnail.targetId == targetId]
        return result[0] if result else None

    def getAllImageUrls(self) -> dict[any , str]:
        """
        #### dict keys are the image urls, values are the requestIds
        """
        return {thumbnail.requestId: thumbnail.imageUrl for thumbnail in self.thumbnails}
     
class ThumbnailBatchObject:
    """
    ### Types:
    1. Avatar
    2. AvatarHeadShot
    3. GameIcon
    4. BadgeIcon
    5. GameThumbnail
    6. GamePass
    7. Asset
    8. BundleThumbnail
    9. Outfit
    10. GroupIcon
    11. DeveloperProduct
    12. AutoGeneratedAsset
    13. AvatarBust
    14. PlaceIcon
    15. AutoGeneratedGameIcon
    16. ForceAutoGeneratedGameIcon
    17. Look
    """

    def __init__(self, requestId:str = None, targetId:int = None, token:str = None, alias:str = None, type:str = "AvatarHeadShot", size:str = "48x48", format:str = "png", isCircular:bool = False):
        self.requestId = requestId
        self.targetId = targetId
        self.token = token
        self.alias = alias
        self.type = type
        self.size = size
        self.format = format
        self.isCircular = isCircular
    
    def json(self):
        names = ["requestId", "targetId", "token", "alias", "type", "size", "format", "isCircular"]

        return {name: getattr(self, name) for name in names if getattr(self, name)}
    
def getUsersAvatar(*userIds:int, type:str = "headshot", size:str = "48x48", format:str = "Png", isCircular:bool = False)  -> (BatchObject | ThumbnailObject):
    response = requests.get(thumbnailsApi + f"/v1/users/avatar-{type}?userIds={",".join(map(str, userIds))}&size={size}&format={format}&isCircular={isCircular}",
        headers={
            "Cookie": cookies.getCookie()
        },
    )

    if response.status_code == 200:
        responseJson = response.json()
        data:list = responseJson["data"]

        if len(userIds) == 1:
            if data:
                return ThumbnailObject(data[0])
            else:
                return ThumbnailObject({
                    "targetId": userIds[0],
                    "errorMessage": "Didn't find thumbnail data.",
                    "state": "Error",
                    "imageUrl": None,
                })
        else:
            for id in userIds:
                if not next((thumbnail for thumbnail in data if thumbnail["targetId"] == id), None):
                    data.append({
                    "targetId": userIds[0],
                    "errorMessage": "Didn't find thumbnail data.",
                    "state": "Error",
                    "imageUrl": None,
                })

            return BatchObject(data)
    else:
        raise requests.exceptions.HTTPError(f"Error in the request: {response.status_code}", response.text)

def getUsersAvatarFromUsername(*usernames:int, type:str = "headshot", size:str = "48x48", format:str = "Png", isCircular:bool = False)  -> tuple[(BatchObject | ThumbnailObject), dict[str, int]]:
    userIds = getIds(*usernames, excludeBanned=False)

    return getUsersAvatar(*userIds, type=type, size=size, format=format, isCircular=isCircular), userIds
    
def batch(*batchObjects:ThumbnailBatchObject) -> BatchObject:
    async def fetchData(session:aiohttp.ClientSession, group):
        while True:
            async with session.post(thumbnailsApi + "/v1/batch",
                    headers={
                        "Cookie": cookies.getCookie()
                    },
                    json=[object.json() for object in group]
                ) as response:

                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Error in the request: {response.status}\n{await response.text()}\nTrying again in 500ms", file=sys.stderr)
            await asyncio.sleep(0.5)

    groups = [[batchObject for batchObject in batchObjects[i:i + 50]] for i in range(0, len(batchObjects), 50)]

    async def proccessGroups():
        async with aiohttp.ClientSession() as session:
            sem = asyncio.Semaphore(5)
            results = []
            
            tasks = [asyncio.create_task(fetchData(session, group)) for group in groups]

            async def runWithSemaphore(task):
                async with sem:
                    return await task

            responses = await asyncio.gather(*[runWithSemaphore(task) for task in tasks], return_exceptions=True)
            for response in responses:
                if isinstance(response, Exception):
                    print(f"Error encountered: {response}", file=sys.stderr)
                else:
                    results.extend(response["data"])

        return results
        
    results = asyncio.run(proccessGroups())

    return BatchObject(results)