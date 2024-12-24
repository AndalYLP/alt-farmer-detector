import asyncio
from time import time

import discord

import RobloxPy
from utils.channels import ALT_STATUS_CHANNEL, GAMEID_CHANNEL, GAMEID_WITH_ALTS_CHANNEL


async def same_gameid(user_presences: RobloxPy.Presence.Presences.UserPresenceGroup):
    gameids = {}

    user_presences.filter_by_presence_types(2)
    user_presences.filter_by_gameids(6872265039)

    for presence in user_presences.presences:
        if not presence.jobId:
            continue

        if gameids.get(presence.jobId):
            gameids[presence.jobId][0].append(presence.userId)
        else:
            gameids[presence.jobId] = [
                [presence.userId],
                {"game_name": presence.lastlocation, "is_lobby": presence.lobbyStatus},
            ]

    embeds = []
    for gameid, ids in gameids.items():
        info = ids[1]
        ids = ids[0]

        title = "GameId" + gameid
        description = f"## GameId description\nGame: **{info["game_name"]}**\nLobby: **{info["is_lobby"]}**\n## In-game player ({len(ids)})"
        everyone = False

        for userid in ids:
            presence = user_presences.get_by_userid(userid)
            description += (
                f"\nUsername: **{presence.username}**\n- isAlt: **{presence.isAlt}**"
            )

            if presence.isAlt == True:
                everyone = True

        embed = discord.Embed(
            color=2686720 if info["is_lobby"] == "True" else 1881856,
            title=title,
            description=description,
        )
        embeds.append(embed)

        if everyone:
            asyncio.create_task(
                GAMEID_WITH_ALTS_CHANNEL.send(
                    content=f"<t:{round(time())}:R><@&1288980643061170188>",
                    embed=embed,
                )
            )

        for embed_group in [embeds[i : i + 10] for i in range(0, len(embeds), 10)]:
            await GAMEID_CHANNEL.send(
                content=f"<t:{round(time.time())}:R>", embeds=embed_group
            )
