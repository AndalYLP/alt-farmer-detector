"""
RobloxPy.Users
~~~~~~~~~~~~~~
"""

from ._utils.classes import Users
from ._utils.requests import _UsersAPI


def get_users_by_userid(*userIds: int, excludeBanned: bool = False) -> Users.UserGroup:
    response = _UsersAPI.V1.Users.users(*userIds, excludeBanned=excludeBanned)
    responseJson: dict = response.json()
    data: list = responseJson.get("data")

    return Users.UserGroup(data)


def get_users_by_username(
    *usernames: str, excludeBanned: bool = False
) -> Users.UserGroup:
    response = _UsersAPI.V1.Users.usernames_users(
        *usernames, excludeBanned=excludeBanned
    )
    responseJson: dict = response.json()
    data: list = responseJson.get("data")

    return Users.UserGroup(data)
