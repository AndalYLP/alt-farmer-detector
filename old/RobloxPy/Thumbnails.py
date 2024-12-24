"""
RobloxPy.Thumbnails
~~~~~~~~~~~~~~~~~~~
"""

from ._common.thumbnails import Thumbnails, get_users_avatar, batch
from ._utils.requests import _ThumbnailsAPI
from ._utils.classes import Users


class ThumbnailBatchObject(Thumbnails.ThumbnailBatchObject): ...


def get_users_avatar_from_username(
    *usernames: str,
    type: str = "headshot",
    size: str = "48x48",
    format: str = "Png",
    isCircular: bool = False,
    excludeBanned: bool = False,
) -> tuple[Thumbnails.BatchObject, Users.UserGroup]:
    from .Users import get_users_by_username

    users = get_users_by_username(*usernames, excludeBanned=excludeBanned)

    return (
        get_users_avatar(
            *users.userIds, type=type, size=size, format=format, isCircular=isCircular
        ),
        users,
    )
