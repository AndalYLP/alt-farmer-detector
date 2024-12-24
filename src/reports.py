import asyncio

from loguru import logger

import RobloxPy
from config.constants import *
from same_gameid import same_gameid
from tracking import user_status
from utils.channels import ALT_STATUS_CHANNEL, STATUS_CHANNEL


async def get_status(bot):
    while True:
        try:
            if STATUS_CHANNEL:
                documents = list(USERS_COLLECTION.find({}))

                if documents:
                    user_presences = await RobloxPy.Presence.get_presence(
                        *[doc["UserID"] for doc in documents]
                    )
                    results = list(
                        USERS_COLLECTION.find(
                            {"UserID": {"$in": user_presences.userIds}}
                        )
                    )

                    if not user_presences:
                        return

                    for presence in user_presences.presences:
                        data = next(
                            (doc for doc in results if doc["UserID"] == presence.userId)
                        )

                        presence.username = data["Username"]
                        presence.lobbyStatus = (
                            "True" if presence.placeId == 6872265039 else "False"
                        )
                        presence.groupName = data.get("GroupName", "None")
                        presence.isAlt = data["isAlt"]

                    await asyncio.gather(
                        STATUS_CHANNEL.purge(limit=100),
                        ALT_STATUS_CHANNEL.purge(limit=100),
                    )
                    await asyncio.gather(
                        user_status(user_presences, bot),
                        same_gameid(user_presences),
                    )

        except Exception as e:
            logger.exception(e)
