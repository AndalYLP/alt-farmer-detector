"""
RobloxPy.Games
~~~~~~~~~~~~~~
"""

from ._utils.requests import _GamesAPI
from ._utils.classes import Servers


def get_server_page(
    gameId: int,
    useCookie: bool = False,
    serverType: int = 0,
    sortOrder: int = 2,
    excludeFullGames: bool = False,
    limit: int = 100,
    cursor: str = "",
) -> Servers.ServerGroup:
    response = _GamesAPI.V1.GameInstances.games__servers__(
        gameId, useCookie, serverType, sortOrder, excludeFullGames, limit, cursor
    )

    return Servers.ServerGroup(response.json())


def get_all_servers(
    gameId: int,
    serverType: int = 0,
    excludeFullGames: bool = False,
    useCookie: bool = False,
) -> Servers.ServerGroup:
    currentPage = get_server_page(
        gameId, useCookie, serverType, excludeFullGames=excludeFullGames
    )
    mainPage = currentPage

    while True:
        if currentPage.nextPageCursor:
            currentPage = get_server_page(
                gameId,
                useCookie=useCookie,
                serverType=serverType,
                excludeFullGames=excludeFullGames,
                cursor=currentPage.nextPageCursor,
            )

            mainPage += currentPage
        else:
            break

    return mainPage
