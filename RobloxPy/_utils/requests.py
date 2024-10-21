"""
RobloxPy._utils.requests
~~~~~~~~~~~~~~~~~~~~~~~~

This module provides the request's response that other modules requested.
The available services include friends, games, presence, thumbnails, and users.
"""

from inspect import currentframe as CurrentFrame
from urllib.parse import urlencode
import asyncio

from loguru import logger
import requests
import aiohttp

from .._CookieManager import cookies
from ._urls import API_URLS
from .. import _exceptions


async def async_request(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    headers: dict = None,
    json=None,
):
    attempts = 0
    while True:
        async with getattr(session, method)(
            url=url,
            headers=headers,
            json=json,
        ) as response:
            response: aiohttp.ClientResponse
            try:
                http_error_msg = ""
                if isinstance(response.reason, bytes):
                    try:
                        reason = response.reason.decode("utf-8")
                    except UnicodeDecodeError:
                        reason = response.reason.decode("iso-8859-1")
                else:
                    reason = response.reason

                if 400 <= response.status < 500:
                    http_error_msg = f"{response.status} Client Error: {reason} for url: {response.url} response text: {await response.text()}"

                elif 500 <= response.status < 600:
                    http_error_msg = f"{response.status} Server Error: {reason} for url: {response.url} response text: {await response.text()}"

                if http_error_msg:
                    raise requests.exceptions.HTTPError(
                        http_error_msg, response=response
                    )

                return await response.json()
            except Exception as e:
                errorCode = (await response.json())["errors"][0]["code"]

                if errorCode != 0:
                    attempts += 1
                    if attempts == 4:
                        logger.exception(
                            _exceptions.MaxAttempts(
                                f"Max attempts reached for url: {response.url}"
                            )
                        )
                        raise

                logger.exception(e)
                logger.info(
                    f"Trying again in 500ms {f"({attempts}/3)"  if errorCode != 0 else ""}"
                )

        await asyncio.sleep(0.5)


def _get_url(*params: str, special: bool = False, query: dict[str, str] = {}):
    frame = CurrentFrame().f_back
    classNames: list[str] = (
        frame.f_locals["cls"].__qualname__.replace("_", "").split(".")
    )
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


class _FriendsAPI:
    class V1:
        class Friends:
            @classmethod
            async def users__friends_find(
                cls, *userIds: int, limit: int = 50
            ) -> dict[int, list]:
                async with aiohttp.ClientSession() as session:
                    sem = asyncio.Semaphore(10)
                    results = {}

                    async def get_friends(userId: int, url: str):
                        result = []
                        nextCursor = None

                        while True:
                            responseJson: dict = await async_request(
                                session=session,
                                method="get",
                                url=f"{url}{f"&cursor={nextCursor}" if nextCursor else ""}",
                                headers={
                                    "Cookie": cookies.get_cookie(),
                                },
                            )

                            data = responseJson.get("PageItems", [])
                            nextCursor = responseJson.get("NextCursor")

                            if data:
                                result.extend([item["id"] for item in data])
                            else:
                                break

                            if not nextCursor:
                                break

                        return userId, result

                    async def run_with_semaphore(task):
                        async with sem:
                            return await task

                    tasks = [
                        run_with_semaphore(
                            get_friends(
                                userId, _get_url(userId, query={"limit": limit})
                            )
                        )
                        for userId in userIds
                    ]

                    responses = await asyncio.gather(
                        *tasks,
                        return_exceptions=True,
                    )
                    for response in responses:
                        if isinstance(response, Exception):
                            logger.exception(response)
                            raise
                        elif response:
                            userId, friends = response
                            results[userId] = friends

                return results


class _GamesAPI:
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
                    _get_url(
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
                    return response
                except Exception as e:
                    logger.exception(e)
                    raise


class _PresenceAPI:
    class V1:
        class Presence:
            @classmethod
            def presence_last___online(cls, *userIds):
                response = requests.post(
                    _get_url(),
                    headers={"Cookie": cookies.get_cookie()},
                    json={"userIds": list(userIds)},
                )

                try:
                    response.raise_for_status()
                    return response
                except Exception as e:
                    logger.exception(e)
                    raise

            @classmethod
            async def presence_users(cls, *userIds) -> list[dict]:
                groups = [
                    [userId for userId in userIds[i : i + 30]]
                    for i in range(0, len(userIds), 30)
                ]

                async with aiohttp.ClientSession() as session:
                    sem = asyncio.Semaphore(10)
                    results = []

                    async def run_with_semaphore(task):
                        async with sem:
                            return await task

                    tasks = [
                        run_with_semaphore(
                            async_request(
                                session=session,
                                method="post",
                                url=_get_url(),
                                headers={
                                    "Cookie": cookies.get_cookie(),
                                },
                                json={"userIds": group},
                            )
                        )
                        for group in groups
                    ]

                    responses = await asyncio.gather(
                        *tasks,
                        return_exceptions=True,
                    )
                    for response in responses:
                        if isinstance(response, Exception):
                            logger.exception(response)
                            raise
                        elif response:
                            results.extend(response["userPresences"])

                return results


class _ThumbnailsAPI:
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
                    _get_url(
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
                    return response
                except Exception as e:
                    logger.exception(e)
                    raise

            @classmethod
            def users_avatar___3d(cls, userId: int):
                response = requests.get(
                    _get_url(query={"userId": userId}),
                    headers={"Cookie": cookies.get_cookie()},
                )

                try:
                    response.raise_for_status()
                    return response
                except Exception as e:
                    logger.exception(e)
                    raise

        class Batch:
            @classmethod
            async def batch(cls, *requests: dict) -> list[dict]:
                groups = [
                    [request for request in requests[i : i + 50]]
                    for i in range(0, len(requests), 50)
                ]

                async with aiohttp.ClientSession() as session:
                    sem = asyncio.Semaphore(10)
                    results = []

                    async def run_with_semaphore(task):
                        async with sem:
                            return await task

                    tasks = [
                        run_with_semaphore(
                            async_request(
                                session=session,
                                method="post",
                                url=_get_url(),
                                headers={
                                    "Cookie": cookies.get_cookie(),
                                },
                                json=group,
                            )
                        )
                        for group in groups
                    ]

                    responses = await asyncio.gather(
                        *tasks,
                        return_exceptions=True,
                    )
                    for response in responses:
                        if isinstance(response, Exception):
                            logger.exception(response)
                            raise
                        elif response:
                            results.extend(response["data"])

                return results


class _UsersAPI:
    class V1:
        class Users:

            @classmethod
            def users_authenticated(cls, cookie: str = cookies.get_cookie()):
                response = requests.get(url=_get_url(), headers={"Cookie": cookie})

                try:
                    response.raise_for_status()
                    return response
                except Exception as e:
                    logger.exception(e)
                    raise

            @classmethod
            def usernames_users(cls, *usernames: str, excludeBanned: bool = False):
                response = requests.post(
                    url=_get_url(),
                    headers={"Cookie": cookies.get_cookie()},
                    json={
                        "usernames": list(usernames),
                        "excludeBannedUsers": excludeBanned,
                    },
                )

                try:
                    response.raise_for_status()
                    return response
                except Exception as e:
                    logger.exception(e)
                    raise

            @classmethod
            def users(cls, *userIds: int, excludeBanned: bool = False):
                response = requests.post(
                    url=_get_url(),
                    headers={"Cookie": cookies.get_cookie()},
                    json={
                        "userIds": list(userIds),
                        "excludeBannedUsers": excludeBanned,
                    },
                )

                try:
                    response.raise_for_status()
                    return response
                except Exception as e:
                    logger.exception(e)
                    raise
