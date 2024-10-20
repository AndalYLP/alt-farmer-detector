"""
RobloxPy._utils.classes
~~~~~~~~~~~~~~~~~~~~~~~

This module provides classes to other modules that need it.
"""

from typing import Optional
from ..Thumbnails import get_users_avatar


class Users:
    class UserGroup:
        def __init__(self, data: list[dict]):
            self.data = data

            self.userIds: list[int] = [user["id"] for user in data]
            self.usernames: list[str] = [user["name"] for user in data]
            self.displayNames: list[str] = [user["displayName"] for user in data]
            self.users: list[Users.User] = [Users.User(user) for user in data]

            self._userIdsDict: dict[int, Users.User] = {
                user.userId: user for user in self.users
            }
            self._usernamesDict: dict[str, Users.User] = {
                user.username: user for user in self.users
            }
            self._requestedUsernameDict: dict[str, Users.User] = {
                user.requestedUsername: user for user in self.users
            }

        def __bool__(self):
            return bool(self.users)

        def __eq__(self, value):
            if isinstance(value, Users.UserGroup):
                return set(self.users) == set(value.users)

            return False

        def __add__(self, value):
            if isinstance(value, Users.UserGroup):
                return Users.UserGroup(list(dict.fromkeys([*self.data, *value.data])))
            elif isinstance(value, Users.User):
                return Users.UserGroup(list(dict.fromkeys([*self.data, value.data])))

            return NotImplemented

        def __iadd__(self, value):
            if isinstance(value, Users.UserGroup):
                return Users.UserGroup(list(dict.fromkeys([*self.data, *value.data])))
            elif isinstance(value, Users.User):
                return Users.UserGroup(list(dict.fromkeys([*self.data, value.data])))

            return NotImplemented

        def __sub__(self, value):
            if isinstance(value, Users.UserGroup):
                for value in value.data:
                    self.data.remove(value)

                return Users.UserGroup(self.data)
            elif isinstance(value, Users.User):
                self.data.remove(value.data)

                return Users.UserGroup(self.data)

        def __len__(self):
            return len(self.users)

        def get_by_userid(self, userId: int) -> Optional["Users.User"]:
            return self._userIdsDict.get(userId)

        def get_by_username(self, username: str) -> Optional["Users.User"]:
            return self._usernamesDict.get(username)

        def get_by_requested_username(
            self, requestedUsername: str
        ) -> Optional["Users.User"]:
            return self._requestedUsernameDict.get(requestedUsername)

    class User:
        def __init__(self, data: dict):
            self.data = data

            self.userId: int = data["id"]
            self.username: str = data["name"]
            self.displayName: str = data["displayName"]
            self.requestedUsername: str = data.get("requestedUsername")

        def __bool__(self):
            return bool(self.userId)

        def __eq__(self, value):
            if isinstance(value, Users.User):
                return self.userId == value.userId

            return False

        def __add__(self, value) -> "Users.UserGroup":
            if isinstance(value, Users.User):
                return Users.UserGroup([self.data, value.data])
            elif isinstance(value, Users.UserGroup):
                return Users.UserGroup(list(dict.fromkeys([self.data, *value.data])))

            return NotImplemented

        def __iadd__(self, value) -> "Users.UserGroup":
            if isinstance(value, Users.User):
                return Users.UserGroup([self.data, value.data])
            elif isinstance(value, Users.UserGroup):
                return Users.UserGroup(list(dict.fromkeys([self.data, *value.data])))

            return NotImplemented


class Servers:
    class ServerGroup:
        def __init__(self, data: dict):
            self.json = data
            self.data: list[dict] = data["data"]

            self.previousPageCursor: str = data["previousPageCursor"]
            self.nextPageCursor: str = data["nextPageCursor"]

            self.jobIds = [server["id"] for server in self.data]
            self.servers = [Servers.Server(server) for server in self.data]

        def __bool__(self):
            return bool(self.servers)

        def __eq__(self, value):
            if isinstance(value, Servers.ServerGroup):
                return set(self.servers) == set(value.servers)

            return False

        def __add__(self, value):
            if isinstance(value, Servers.ServerGroup):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": value.previousPageCursor,
                        "nextPageCursor": value.nextPageCursor,
                        "data": list(dict.fromkeys([*self.data, *value.data])),
                    }
                )
            elif isinstance(value, Servers.Server):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": self.previousPageCursor,
                        "nextPageCursor": self.nextPageCursor,
                        "data": list(dict.fromkeys([*self.data, value.data])),
                    }
                )

            return NotImplemented

        def __iadd__(self, value):
            if isinstance(value, Servers.ServerGroup):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": value.previousPageCursor,
                        "nextPageCursor": value.nextPageCursor,
                        "data": list(dict.fromkeys([*self.data, *value.data])),
                    }
                )
            elif isinstance(value, Servers.Server):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": self.previousPageCursor,
                        "nextPageCursor": self.nextPageCursor,
                        "data": list(dict.fromkeys([*self.data, value.data])),
                    }
                )

            return NotImplemented

        def __sub__(self, value):
            if isinstance(value, Servers.ServerGroup):
                for value in value.data:
                    self.data.remove(value)

                return Users.UserGroup(self.data)
            elif isinstance(value, Servers.Server):
                self.data.remove(value.data)

                return Users.UserGroup(self.data)

            return NotImplemented

        def __len__(self):
            return len(self.servers)

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

        def __eq__(self, value):
            if isinstance(value, Servers.Server):
                return self.jobId == value.jobId

            return False

        def __add__(self, value) -> "Servers.ServerGroup":
            if isinstance(value, Servers.Server):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": None,
                        "nextPageCursor": None,
                        "data": list(dict.fromkeys([self.data, value.data])),
                    }
                )
            elif isinstance(value, Servers.ServerGroup):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": value.previousPageCursor,
                        "nextPageCursor": value.nextPageCursor,
                        "data": list(dict.fromkeys([self.data, *value.data])),
                    }
                )

            return NotImplemented

        def __iadd__(self, value) -> "Servers.ServerGroup":
            if isinstance(value, Servers.Server):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": None,
                        "nextPageCursor": None,
                        "data": list(dict.fromkeys([self.data, value.data])),
                    }
                )
            elif isinstance(value, Servers.ServerGroup):
                return Servers.ServerGroup(
                    {
                        "previousPageCursor": value.previousPageCursor,
                        "nextPageCursor": value.nextPageCursor,
                        "data": list(dict.fromkeys([self.data, *value.data])),
                    }
                )

            return NotImplemented
