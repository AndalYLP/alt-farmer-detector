"""
RobloxPy.Presence
~~~~~~~~~~~~~~~~~
"""

from datetime import datetime

from loguru import logger

from ._utils.classes import Presences, Users
from ._utils.requests import _PresenceAPI


def get_last_online(*userIds: int) -> dict[int, datetime]:
    response = _PresenceAPI.V1.Presence.presence_last___online(*userIds)

    responseJson: dict = response.json()
    data: list = responseJson.get("lastOnlineTimestamps")

    if data and "lastOnline" in data[0]:
        result = {}
        for value in data:
            result[value["userId"]] = datetime.fromisoformat(
                value["lastOnline"].replace("Z", "+00:00")
            )

        return result
    else:
        logger.exception(
            KeyError(f"LastOnline not found in the response json", response.text)
        )


async def get_presence(*userIds: int) -> Presences.UserPresenceGroup:
    data = await _PresenceAPI.V1.Presence.users(*userIds)

    return Presences.UserPresenceGroup(data)


async def get_presence_from_username(
    *usernames: str,
) -> tuple[Presences.UserPresenceGroup, Users.UserGroup]:
    from .Users import get_users_by_username

    users = get_users_by_username(*usernames)

    return await get_presence(*users.userIds), users
