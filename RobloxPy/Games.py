from .CookieManager import cookies
from .Thumbnails import ThumbnailBatchObject, BatchObject, ThumbnailObject, batch
import requests

gamesApi = "https://games.roblox.com"

class Server:
        def __init__(self, serverData):
            self.jobId = serverData["id"]
            self.playing = serverData["playing"]
            self.maxPlayers = serverData["maxPlayers"]
            self.playerTokens = serverData["playerTokens"]

            self.fps = serverData.get("fps")
            self.ping = serverData.get("ping")

        def getPlayerThumbnails(self, type:str = "AvatarHeadShot", size:str = "48x48", format:str = "png", isCircular:bool = False) -> BatchObject:
            batchObject = [ThumbnailBatchObject(requestId=playerToken, token=playerToken, type=type, size=size, format=format, isCircular=isCircular) for playerToken in self.playerTokens]
            return batch(*batchObject)
        
class ServerGroup:
    def __init__(self, data):
        self.json = data
        self.data = data["data"]

        self.previousPageCursor:str = data["previousPageCursor"]
        self.nextPageCursor:str = data["nextPageCursor"]

        self.jobIds = [server["id"] for server in data["data"]]
        self.servers = [Server(server) for server in data["data"]]
    
    def getPlayerThumbnails(self, type:str = "AvatarHeadShot", size:str = "48x48", format:str = "png", isCircular:bool = False) -> BatchObject:
            batchObject = [ThumbnailBatchObject(requestId=jobId, token=playerToken, type=type, size=size, format=format, isCircular=isCircular) for jobId, playerToken in {server.jobId: server.playerTokens for server in self.servers}.items()]
            return batch(*batchObject)
         

def getServerPage(gameId:int, serverType:int = 0, sortOrder:int = 2, excludeFullGames:bool = False, limit:int = 100, cursor:str = "", useCookie:bool = False) -> ServerGroup:
    response = requests.get(gamesApi + f"/v1/games/{gameId}/servers/{serverType}?sortOrder={sortOrder}&excludeFullGames={excludeFullGames}&limit={limit}&cursor={cursor}",
        headers={
            "Cookie": cookies.getCookie() if useCookie else ""
        }
    )

    if response.status_code == 200:
        return ServerGroup(response.json())
    else:
        raise requests.exceptions.HTTPError(f"Error in the request: {response.status_code}", response.text)
    
def getAllServers(gameId:int, serverType:int = 0, excludeFullGames:bool = False, useCookie:bool = False) -> ServerGroup:
    currentPage = getServerPage(gameId, serverType, excludeFullGames=excludeFullGames, useCookie=useCookie)
    firstPage = currentPage

    while True:
        if currentPage.nextPageCursor:
            currentPage = getServerPage(gameId, serverType, excludeFullGames=excludeFullGames, cursor=currentPage.nextPageCursor, useCookie=useCookie)
            
            firstPage.servers.extend(currentPage.servers)
        else:
            break
    
    return firstPage