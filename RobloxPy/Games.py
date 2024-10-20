"""
RobloxPy.Games
~~~~~~~~~~~~~~
"""

from .Thumbnails import ThumbnailBatchObject, BatchObject, batch
from ._utils.requests import GamesAPI
from ._utils.classes import Servers


def getServerPage(
    gameId: int,
    useCookie: bool = False,
    serverType: int = 0,
    sortOrder: int = 2,
    excludeFullGames: bool = False,
    limit: int = 100,
    cursor: str = "",
) -> Servers.ServerGroup:
    response = GamesAPI.V1.GameInstances.games__servers__(
        gameId, useCookie, serverType, sortOrder, excludeFullGames, limit, cursor
    )

    return Servers.ServerGroup(response.json())


def getAllServers(
    gameId: int,
    serverType: int = 0,
    excludeFullGames: bool = False,
    useCookie: bool = False,
) -> Servers.ServerGroup:
    currentPage = getServerPage(
        gameId, useCookie, serverType, excludeFullGames=excludeFullGames
    )
    mainPage = currentPage

    while True:
        if currentPage.nextPageCursor:
            currentPage = getServerPage(
                gameId,
                serverType,
                excludeFullGames=excludeFullGames,
                cursor=currentPage.nextPageCursor,
                useCookie=useCookie,
            )

            mainPage += currentPage
        else:
            break

    return mainPage
