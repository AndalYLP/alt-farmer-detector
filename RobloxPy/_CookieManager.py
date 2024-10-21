"""
RobloxPy._CookieManager
~~~~~~~~~~~~~~~~~~~~~~~

This module lets you set a cookie and provide it to other modules.
recommended to use RobloxPy.cookies instead of this module!
"""

from loguru import logger

from ._exceptions import CookieWarning
import requests


class CookieManager:
    """
    ## You should use "cookies".
    """

    def __init__(self):
        self._cookie = None

    def set_cookie(self, cookie: str) -> None:
        from ._utils.requests import _UsersAPI

        self._cookie = cookie.replace(".ROBLOSECURITY=", "")
        index = self._cookie.rfind("|_")
        if index != -1:
            self._cookie[:index]

        response = None

        try:
            response = _UsersAPI.V1.Users.users_authenticated(self.get_cookie())
            responseJson: dict = response.json()

            if responseJson.get("id"):
                logger.info(
                    f"\n    Logged in as {responseJson["name"]}\n    User id: {responseJson["id"]}\n    Display name: {responseJson["displayName"]}",
                )
            else:
                raise Exception

        except requests.exceptions.HTTPError as e:
            logger.warning(
                CookieWarning(
                    "Error verifying cookie, restart recommended",
                    e.response.status_code,
                    e.response.text,
                )
            )

    def get_cookie(self) -> str:
        return f".ROBLOSECURITY={self._cookie}"


cookies = CookieManager()
