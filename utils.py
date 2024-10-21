from datetime import datetime
import traceback

import discord
from humanize import naturaltime

import RobloxPy

generalColorCode = 8585471
errorColorCode = 16765440
presenceTypeCode = {
    0: [8421761, "is offline"],
    1: [2535920, "is online"],
    2: [308308, "is in a game"],
    3: [15960836, "is in studio"],
    "match": [1881856, "is in a game"],
}


def format_user_embed(
    presenceType,
    username,
    game=None,
    lobby=None,
    jobId=None,
    lastJobId=None,
    timeIn=None,
    groupOrLastOnline=None,
    thumbnail=None,
):
    embed = discord.Embed(
        color=presenceTypeCode[presenceType][0],
        title=f"{username} {presenceTypeCode[presenceType][1]}",
        description=f"""{f"Game: {game}" if game else ""}
{f"Lobby: {lobby}" if lobby else ""}
{f"JobId: {jobId}" if jobId else ""}
{f"Last jobId: {lastJobId}" if lastJobId else ""}
{f"Time in jobId: {timeIn}" if timeIn else ""}""",
    )

    if groupOrLastOnline:
        if isinstance(groupOrLastOnline, datetime):
            embed.set_footer(text=f"Last online: {naturaltime(groupOrLastOnline)}")
        else:
            embed.set_footer(text=f"Group: {groupOrLastOnline}")

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    return embed


def format_mutuals_embed(
    mutuals: dict, users: RobloxPy.Users.Users.UserGroup, strict: bool
):
    mutualsUsers = RobloxPy.Users.get_users_by_userid(*mutuals)

    embed = discord.Embed(
        color=generalColorCode,
        title="Mutuals between:",
        description=f"{", ".join(users.usernames)}\n\n"
        + "".join(
            f"**{i + 1}.** ``{mutualsUsers.get_by_userid(userId)}`` **|** {userId}{f" **({count})**" if not strict else ""}"
            for i, (userId, count) in enumerate(mutuals.values)
        ),
    )

    return embed


def format_addedwith_embed(
    target, addedwith: list, users: RobloxPy.Users.Users.UserGroup
):
    embed = discord.Embed(
        color=generalColorCode,
        title=f"{target} is added with:",
        description="".join(
            f"**{i + 1}.** ``{users.get_by_userid(userId)}`` **|** {userId}"
            for i, userId in enumerate(addedwith)
        ),
    )

    return embed


def error_embed(exception: Exception):
    embed = discord.Embed(
        color=errorColorCode,
        title=f"{type(exception).__name__}",
        description=traceback.format_exc(),
    )

    return embed


# -------------------------------- exceptions -------------------------------- #


class UserNotFound(Exception):
    def __init__(self, username):
        super().__init__(f"didn't find the requested username: {username}")
