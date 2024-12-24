from datetime import datetime

import discord
from humanize import naturaltime

import RobloxPy

from .colors import *


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
        color=presenceTypeCode[
            presenceType if presenceType != 2 or lobby == "True" else "match"
        ][0],
        title=f"{username} {presenceTypeCode[presenceType][1]}",
        description=f"""{f"Game: **{game}**" if game else ""}
{f"Lobby: **{lobby}**" if lobby else ""}
{f"JobId: **```{jobId}```**" if jobId else ""}
{f"Last jobId: **{lastJobId}**" if lastJobId else ""}
{f"Time in jobId: **{timeIn}**" if timeIn else ""}""",
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
        title="Mutuals for:",
        description=f"{", ".join(users.usernames)}\n\n"
        + "\n".join(
            f"**{i + 1}.** ``{mutualsUsers.get_by_userid(userId).username}`` **|** {userId}{f" **({count})**" if not strict else ""}"
            for i, (userId, count) in enumerate(mutuals.items())
        ),
    )

    return embed


def format_added_with_embed(
    target, added_with: list, users: RobloxPy.Users.Users.UserGroup
):
    embed = discord.Embed(
        color=generalColorCode,
        title=f"{target} is added with:",
        description="\n".join(
            f"**{i + 1}.** ``{users.get_by_userid(userId).username}`` **|** {userId}"
            for i, userId in enumerate(added_with)
        ),
    )

    return embed


def error_embed(exception: Exception):
    embed = discord.Embed(
        color=errorColorCode,
        title=f"{type(exception).__name__}",
        description=str(exception),
    )

    return embed
