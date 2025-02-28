from datetime import datetime

from loguru import logger

from .._utils.requests import _PresenceAPI


def get_last_online(*userIds: int) -> dict[int, datetime]:
    """
    ### REMOVED: Api endpoint got removed
    """
    return
    response = _PresenceAPI.V1.Presence.presence_last___online(*userIds)

    responseJson: dict = response.json()
    data: list = responseJson.get("lastOnlineTimestamps")

    if data and "lastOnline" in data[0]:
        result = {}
        for value in data:
            result[value["userId"]] = datetime.fromisoformat(
                value["lastOnline"].replace("Z", "+00:00")
            )

        return result
    else:
        logger.exception(
            KeyError(f"LastOnline not found in the response json", response.text)
        )
