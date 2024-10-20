"""
RobloxPy._utils.Users
~~~~~~~~~~~~~~~~~~~~~
"""

from ._utils.requests import UsersAPI
from ._utils.classes import Users


def get_users_by_userid(
    *userIds: int, excludeBanned: bool = True
) -> Users.UserGroup | None:
    response = UsersAPI.V1.Users.users(*userIds, excludeBanned=excludeBanned)
    responseJson: dict = response.json()
    data: list = responseJson.get("data")

    return Users.UserGroup(data)


def get_users_by_username(
    *usernames: int, excludeBanned: bool = True
) -> Users.UserGroup | None:
    response = UsersAPI.V1.Users.usernames_users(
        *usernames, excludeBanned=excludeBanned
    )
    responseJson: dict = response.json()
    data: list = responseJson.get("data")

    return Users.UserGroup(data)
