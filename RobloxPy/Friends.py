from ._CookieManager import cookies
import requests

userApi = "https://friends.roblox.com"


def getFriendsId(): ...


def getFriendsIdFromUsername(): ...


def getFriendsUser(): ...


def getFriendsUserFromUsername(): ...


from .Presence import getLastOnline, getPresence, UserPresence
from .Thumbnails import ThumbnailObject, getUsersAvatar
