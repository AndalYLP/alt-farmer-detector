"""
RobloxPy._common.friends
~~~~~~~~~~~~~~~~~~~~~~~~

Common module for friends.
"""

from .._utils.requests import _FriendsAPI


async def get_friend_users(*userIds: int, limit: int = None):
    data: dict[int, list] = await _FriendsAPI.V1.Friends.users__friends_find(*userIds)

    if limit:
        data = {userId: friends[:limit] for userId, friends in data.items()}

    return data
