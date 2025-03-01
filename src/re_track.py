import re

from config.constants import TRACKING_CATEGORY
from main import Bot
from RobloxPy import Users


def re_track(bot: Bot):
    channels = bot.get_channel(TRACKING_CATEGORY).channels

    channelData = {}

    for channel in channels:
        channelData[channel.name] = (channel, channel.topic)

    users = Users.get_users_by_username(*channelData.keys())

    for data, (channel, mentions) in channelData.items():
        bot.tracking[users.get_by_username(data)] = [
            channel,
            re.findall(r"<@\d+>", mentions),
        ]
