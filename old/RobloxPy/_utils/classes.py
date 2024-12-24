"""
RobloxPy._utils.classes
~~~~~~~~~~~~~~~~~~~~~~~

This module provides classes to other modules that need it.
"""

from datetime import datetime
from typing import Optional

from .._common.thumbnails import Thumbnails, get_users_avatar, batch
from .._common.friends import get_friend_users
from .._common.presence import get_last_online


def unique_by_key(data, key):
    seen = set()
    uniqueData = []
    for item in data:
        value = item[key]
        if value not in seen:
            seen.add(value)
            uniqueData.append(item)
    return uniqueData


class Users:
    class UserGroup:
        def __init__(self, data: list[dict]):
            self.data = data

            self.userIds: list[int] = [user["id"] for user in data]
            self.usernames: list[str] = [user["name"] for user in data]
            self.displayNames: list[str] = [user["displayName"] for user in data]
            self.users = [Users.User(user) for user in data]

            self._userIdsDict: dict[int, Users.User] = {
                user.userId: user for user in self.users
            }
            self._usernamesDict: dict[str, Users.User] = {
                user.username: user for user in self.users
            }
            self._requestedUsernameDict: dict[str, Users.User] = {
                user.requestedUsername: user for user in self.users
            }

        def __contains__(self, item):
            if isinstance(item, Users.User):
                return item in self.users

            return False

        def __bool__(self):
            return bool(self.users)

        def __len__(self):
            return len(self.users)

        def __eq__(self, other):
            if isinstance(other, Users.UserGroup):
                return set(self.users) == set(other.users)

            return False

        def __add__(self, other):
            if isinstance(other, Users.UserGroup):
                return Users.UserGroup(unique_by_key(self.data + other.data, "id"))
            elif isinstance(other, Users.User):
                return Users.UserGroup(unique_by_key(self.data + other.data, "id"))

            return NotImplemented

        def __iadd__(self, other):
            if isinstance(other, Users.UserGroup):
                return Users.UserGroup(unique_by_key(self.data + other.data, "id"))
            elif isinstance(other, Users.User):
                return Users.UserGroup(unique_by_key(self.data + other.data, "id"))

            return NotImplemented

        def __sub__(self, other):
            if isinstance(other, Users.UserGroup):
                for value in other.data:
                    self.data.remove(value)

                return Users.UserGroup(self.data)
            elif isinstance(other, Users.User):
                self.data.remove(other.data)

                return Users.UserGroup(self.data)

        def get_by_userid(self, userId: int) -> Optional["Users.User"]:
            return self._userIdsDict.get(userId)

        def get_by_username(self, username: str) -> Optional["Users.User"]:
            return self._usernamesDict.get(username)

        def get_by_requested_username(
            self, requestedUsername: str
        ) -> Optional["Users.User"]:
            return self._requestedUsernameDict.get(requestedUsername)

        def get_last_onlines(self) -> dict[int, datetime]:
            result = get_last_online(*self.userIds)
            return result

    class User:
        def __init__(self, data: dict):
            self.data = data

            self.userId: int = data["id"]
            self.username: str = data["name"]
            self.displayName: str = data["displayName"]
            self.requestedUsername: str = data.get("requestedUsername")

        def __bool__(self):
            return bool(self.userId)

        def __eq__(self, other):
            if isinstance(other, Users.User):
                return self.userId == other.userId

            return False

        def __add__(self, other) -> "Users.UserGroup":
            if isinstance(other, Users.User):
                return Users.UserGroup(unique_by_key(self.data + other.data, "id"))
            elif isinstance(other, Users.UserGroup):
                return Users.UserGroup(unique_by_key(self.data + other.data, "id"))

            return NotImplemented

        def __iadd__(self, other) -> "Users.UserGroup":
            if isinstance(other, Users.User):
                return Users.UserGroup(unique_by_key(self.data + other.data, "id"))
            elif isinstance(other, Users.UserGroup):
                return Users.UserGroup(unique_by_key(self.data + other.data, "id"))

            return NotImplemented

        def get_thumbnail(self) -> Thumbnails.ThumbnailObject:
            return get_users_avatar(self.userId, size="150x150").get_by_targetid(
                self.userId
            )

        async def get_friends(self) -> list:
            response = await get_friend_users(self.userId)
            return response[self.userId]

        def get_last_online(self) -> datetime:
            result = get_last_online(self.userId)[self.userId]
            return result


class Servers:
    class ServerGroup:
        def __init__(self, data: dict):
            self.json = data
            self.data: list[dict] = data["data"]

            self.previousPageCursor: str = data["previousPageCursor"]
            self.nextPageCursor: str = data["nextPageCursor"]

            self.jobIds = [server["id"] for server in self.data]
            self.servers = [Servers.Server(server) for server in self.data]

        def __contains__(self, item):
            if isinstance(item, Servers.Server):
                return item in self.servers

            return False

        def __bool__(self):
            return bool(self.servers)

        def __eq__(self, other):
            if isinstance(other, Servers.ServerGroup):
                return set(self.servers) == set(other.servers)

            return False

        def __add__(self, other):
            if isinstance(other, Servers.ServerGroup):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": other.previousPageCursor,
                        "nextPageCursor": other.nextPageCursor,
                        "data": unique_by_key(self.data + other.data, "id"),
                    }
                )
            elif isinstance(other, Servers.Server):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": self.previousPageCursor,
                        "nextPageCursor": self.nextPageCursor,
                        "data": unique_by_key(self.data + other.data, "id"),
                    }
                )

            return NotImplemented

        def __iadd__(self, other):
            if isinstance(other, Servers.ServerGroup):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": other.previousPageCursor,
                        "nextPageCursor": other.nextPageCursor,
                        "data": unique_by_key(self.data + other.data, "id"),
                    }
                )
            elif isinstance(other, Servers.Server):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": self.previousPageCursor,
                        "nextPageCursor": self.nextPageCursor,
                        "data": unique_by_key(self.data + other.data, "id"),
                    }
                )

            return NotImplemented

        def __sub__(self, other):
            if isinstance(other, Servers.ServerGroup):
                for value in other.data:
                    self.data.remove(value)

                return Users.UserGroup(self.data)
            elif isinstance(other, Servers.Server):
                self.data.remove(other.data)

                return Users.UserGroup(self.data)

            return NotImplemented

        def __len__(self):
            return len(self.servers)

        async def get_player_thumbnails(
            self,
            type: str = "AvatarHeadShot",
            size: str = "48x48",
            format: str = "png",
            isCircular: bool = False,
        ) -> Thumbnails.BatchObject:
            batchObject = [
                Thumbnails.ThumbnailBatchObject(
                    requestId=jobId,
                    token=playerToken,
                    type=type,
                    size=size,
                    format=format,
                    isCircular=isCircular,
                )
                for jobId, playerTokens in {
                    server.jobId: server.playerTokens for server in self.servers
                }.items()
                for playerToken in playerTokens
            ]
            return await batch(*batchObject)

    class Server:
        def __init__(self, data: dict):
            self.data = data

            self.jobId = data["id"]
            self.playing = data["playing"]
            self.maxPlayers = data["maxPlayers"]
            self.playerTokens = data["playerTokens"]

            self.fps = data.get("fps")
            self.ping = data.get("ping")

        def __bool__(self):
            return bool(self.jobId)

        def __eq__(self, other):
            if isinstance(other, Servers.Server):
                return self.jobId == other.jobId

            return False

        def __add__(self, other) -> "Servers.ServerGroup":
            if isinstance(other, Servers.Server):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": None,
                        "nextPageCursor": None,
                        "data": list(dict.fromkeys([self.data, other.data])),
                    }
                )
            elif isinstance(other, Servers.ServerGroup):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": other.previousPageCursor,
                        "nextPageCursor": other.nextPageCursor,
                        "data": list(dict.fromkeys([self.data, *other.data])),
                    }
                )

            return NotImplemented

        def __iadd__(self, other) -> "Servers.ServerGroup":
            if isinstance(other, Servers.Server):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": None,
                        "nextPageCursor": None,
                        "data": list(dict.fromkeys([self.data, other.data])),
                    }
                )
            elif isinstance(other, Servers.ServerGroup):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": other.previousPageCursor,
                        "nextPageCursor": other.nextPageCursor,
                        "data": list(dict.fromkeys([self.data, *other.data])),
                    }
                )

            return NotImplemented

        def get_player_thumbnails(
            self,
            type: str = "AvatarHeadShot",
            size: str = "48x48",
            format: str = "png",
            isCircular: bool = False,
        ) -> Thumbnails.BatchObject:
            batchObject = [
                Thumbnails.ThumbnailBatchObject(
                    requestId=playerToken,
                    token=playerToken,
                    type=type,
                    size=size,
                    format=format,
                    isCircular=isCircular,
                )
                for playerToken in self.playerTokens
            ]
            return batch(*batchObject)


class Presences:
    class UserPresenceGroup:
        def __init__(self, data: list):
            self.data = data
            self.presences = [Presences.UserPresence(presence) for presence in data]
            self.userIds: list[int] = [presence.userId for presence in self.presences]

            self._userIdsDict: dict[int, Presences.UserPresence] = {
                presence.userId: presence for presence in self.presences
            }

        def __contains__(self, item):
            if isinstance(item, Presences.UserPresence):
                return item in self.presences

            return False

        def __bool__(self):
            return bool(self.presences)

        def __len__(self):
            return len(self.presences)

        def __eq__(self, other):
            if isinstance(other, Presences.UserPresenceGroup):
                return set(self.presences) == set(other.presences)

            return False

        def __add__(self, other):
            if isinstance(other, Presences.UserPresenceGroup):
                return Presences.UserPresenceGroup(
                    unique_by_key(self.data + other.data, "userId")
                )
            elif isinstance(other, Presences.UserPresence):
                return Presences.UserPresenceGroup(
                    unique_by_key(self.data + other.data, "userId")
                )

            return NotImplemented

        def __iadd__(self, other):
            if isinstance(other, Presences.UserPresenceGroup):
                return Presences.UserPresenceGroup(
                    unique_by_key(self.data + other.data, "userId")
                )
            elif isinstance(other, Presences.UserPresence):
                return Presences.UserPresenceGroup(
                    unique_by_key(self.data + other.data, "userId")
                )

            return NotImplemented

        def __sub__(self, other):
            if isinstance(other, Presences.UserPresenceGroup):
                for value in other.data:
                    self.data.remove(value)

                return Presences.UserPresence(self.data)
            elif isinstance(other, Presences.UserPresence):
                self.data.remove(other.data)

                return Presences.UserPresence(self.data)

        def get_by_userid(self, userId: str) -> Optional["Presences.UserPresence"]:
            return self._userIdsDict.get(userId)

        def filter_by_gameids(self, *gameIds: int):
            self.presences = [
                presence for presence in self.presences if presence.gameId in gameIds
            ]

        def filter_by_placeid(self, *placeIds: int):
            self.presences = [
                presence for presence in self.presences if presence.placeId in placeIds
            ]

        def filter_by_presence_types(self, *presenceTypes: int):
            self.presences = [
                presence
                for presence in self.presences
                if presence.userPresenceType in presenceTypes
            ]

    class UserPresence:
        def __init__(self, data: list):
            self.data = data

            self.userPresenceType = data["userPresenceType"]
            self.lastlocation = data["lastLocation"]
            self.placeId = data["placeId"]
            self.gameId = data["rootPlaceId"]
            self.jobId = data["gameId"]
            self.universeId = data["universeId"]
            self.userId = data["userId"]
            self.lastOnline = datetime.fromisoformat(
                data["lastOnline"].replace("Z", "+00:00")
            )

        def __bool__(self):
            return bool(self.userId)

        def __eq__(self, other):
            if isinstance(other, Presences.UserPresence):
                return (self.userId == other.userId) or (self.jobId == other.jobId)

            return False

        def __add__(self, other) -> "Presences.UserPresenceGroup":
            if isinstance(other, Presences.UserPresence):
                return Presences.UserPresenceGroup(
                    unique_by_key(self.data + other.data, "userId")
                )
            elif isinstance(other, Presences.UserPresenceGroup):
                return Presences.UserPresenceGroup(
                    list(dict.fromkeys([self.data, *other.data]))
                )

            return NotImplemented

        def __iadd__(self, other) -> "Presences.UserPresenceGroup":
            if isinstance(other, Presences.UserPresence):
                return Presences.UserPresenceGroup(
                    unique_by_key(self.data + other.data, "userId")
                )
            elif isinstance(other, Presences.UserPresenceGroup):
                return Presences.UserPresenceGroup(
                    unique_by_key(self.data + other.data, "userId")
                )

            return NotImplemented
