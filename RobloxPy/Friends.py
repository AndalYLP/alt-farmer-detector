"""
RobloxPy.Friends
~~~~~~~~~~~~~~~~
"""

from ._common.friends import get_friend_users
from ._utils.requests import _FriendsAPI


async def get_friend_users_from_username(*usernames: str, limit: int = None):
    from .Users import get_users_by_username

    users = get_users_by_username(*usernames)
    return await get_friend_users(*users.userIds, limit=limit), users
