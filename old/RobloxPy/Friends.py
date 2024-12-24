"""
RobloxPy.Friends
~~~~~~~~~~~~~~~~
"""

from ._common.friends import get_friend_users
from .Users import get_users_by_username


async def get_friend_users_from_username(*usernames: str, limit: int = None):
    users = get_users_by_username(*usernames)
    return await get_friend_users(*users.userIds, limit=limit), users
