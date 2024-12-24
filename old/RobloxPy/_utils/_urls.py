"""
RobloxPy._utils.urls
~~~~~~~~~~~~~~~~~~~~

Provides URLs for utilities module requests.
The available services include friends, games, presence, thumbnails, and users.
"""

_API_NAMES = ["friends", "games", "presence", "thumbnails", "users"]
API_URLS: dict[str, str] = {
    apiName: f"https://{apiName}.roblox.com" for apiName in _API_NAMES
}
"""
    Gives a dictionary mapping API names to their corresponding base URLs.
    
    ## Format:
        dict: A dictionary where the keys are API names (str) and the values are URLs (str).

    ##### The available APIs include friends, games, presence, thumbnails, and users
    """
