"""
RobloxPy.Presence
~~~~~~~~~~~~~~~~~
"""

from loguru import logger

from ._common.presence import get_last_online
from ._utils.classes import Presences, Users
from ._utils.requests import _PresenceAPI


async def get_presence(*userIds: int) -> Presences.UserPresenceGroup:
    data = await _PresenceAPI.V1.Presence.presence_users(*userIds)

    return Presences.UserPresenceGroup(data)


async def get_presence_from_username(
    *usernames: str,
) -> tuple[Presences.UserPresenceGroup, Users.UserGroup]:
    from .Users import get_users_by_username

    users = get_users_by_username(*usernames)

    return await get_presence(*users.userIds), users
