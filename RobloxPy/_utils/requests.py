"""
RobloxPy._utils.requests
~~~~~~~~~~~~~~~~~~~~~~~~

This module provides the request's response that other modules requested.
The available services include friends, games, presence, thumbnails, and users.
"""

from inspect import currentframe as CurrentFrame
from urllib.parse import urlencode

from loguru import logger
import requests

from .._CookieManager import cookies
from .urls import API_URLS


def _getUrl(*params: str, special: bool = False, query: dict[str, str] = {}):
    frame = CurrentFrame().f_back
    classNames: list[str] = frame.f_locals["cls"].__qualname__.split(".")
    classNames = classNames[:-1] if len(classNames) == 3 else classNames
    functionName = (
        frame.f_code.co_name.replace("___", "-")
        .replace("__", "/{}/" if not special else "{}")
        .replace("_", "/")
    )

    baseApi = API_URLS[classNames[0].lower().replace("api", "")]
    version = classNames[1].lower()

    queryStr = urlencode(query)
    functionName = functionName.removesuffix("/")
    functionName = functionName.format(*params)

    return f"{baseApi}/{version}/{functionName}{f"?{queryStr}" if queryStr else ""}"


class FriendsAPI:
    class FriendsInfo: ...


class GamesAPI:
    class V1:
        class GameInstances:
            @classmethod
            def games__servers__(
                cls,
                gameId: int,
                useCookie: bool = False,
                serverType: int = 0,
                sortOrder: int = 2,
                excludeFullGames: bool = False,
                limit: int = 100,
                cursor: str = "",
            ):
                response = requests.get(
                    _getUrl(
                        gameId,
                        serverType,
                        query={
                            "sortOrder": sortOrder,
                            "excludeFullGames": excludeFullGames,
                            "limit": limit,
                            "cursor": cursor,
                        },
                    ),
                    headers={"Cookies": cookies.get_cookie()} if useCookie else None,
                )

                try:
                    response.raise_for_status()
                except Exception as e:
                    logger.error(e)

                return response


class PresenceAPI:
    class V1:
        class Presence:
            @classmethod
            def last___online(cls, *userIds):
                response = requests.post(
                    _getUrl(),
                    headers={"Cookie": cookies.get_cookie()},
                    json={"userIds": list(userIds)},
                )

                try:
                    response.raise_for_status()
                except Exception as e:
                    logger.error(e)

                return response

            @classmethod
            def users(cls, *userIds):
                response = requests.post(
                    _getUrl(),
                    headers={"Cookie": cookies.get_cookie()},
                    json={"userIds": list(userIds)},
                )

                try:
                    response.raise_for_status()
                except Exception as e:
                    logger.error(e)

                return response


class ThumbnailsAPI:
    class V1:
        class Avatar:
            @classmethod
            def users_avatar__(
                cls,
                *userIds: int,
                type: str = "headshot",
                size: str = "48x48",
                format: str = "png",
                isCircular: bool = False,
            ) -> requests.Response:
                response = requests.get(
                    _getUrl(
                        f"-{type}",
                        special=True,
                        query={
                            "userIds": ",".join(map(str, userIds)),
                            "size": size,
                            "format": format,
                            "isCircular": isCircular,
                        },
                    ),
                    headers={"Cookie": cookies.get_cookie()},
                )

                try:
                    response.raise_for_status()
                except Exception as e:
                    logger.error(e)

                return response

            @classmethod
            def users_avatar___3d(cls, userId: int):
                response = requests.get(
                    _getUrl(query={"userId": userId}),
                    headers={"Cookie": cookies.get_cookie()},
                )

                try:
                    response.raise_for_status()
                except Exception as e:
                    logger.error(e)

                return response


class UsersAPI:
    class V1:
        class Users:

            @classmethod
            def users_authenticated(cls, cookie: str = cookies.get_cookie()):
                response = requests.get(url=_getUrl(), headers={"Cookie": cookie})

                try:
                    response.raise_for_status()
                except Exception as e:
                    logger.error(e)

                return response

            @classmethod
            def usernames_users(cls, *usernames: str, excludeBanned: bool = True):
                response = requests.post(
                    url=_getUrl(),
                    headers={"Cookie": cookies.get_cookie()},
                    json={
                        "usernames": list(usernames),
                        "excludeBannedUsers": excludeBanned,
                    },
                )

                try:
                    response.raise_for_status()
                except Exception as e:
                    logger.error(e)

                return response

            @classmethod
            def users(cls, *userIds: int, excludeBanned: bool = True):
                response = requests.post(
                    url=_getUrl(),
                    headers={"Cookie": cookies.get_cookie()},
                    json={
                        "userIds": list(userIds),
                        "excludeBannedUsers": excludeBanned,
                    },
                )

                try:
                    response.raise_for_status()
                except Exception as e:
                    logger.error(e)

                return response
