from discord import app_commands

cache = {}


def get_friends_group():
    if not cache["f"]:
        cache["f"] = app_commands.Group(name="friends", description="friends commands")

    return cache["f"]


def get_snipe_group():
    return app_commands.Group(name="snipe", description="Snipe commands")


def get_joinsoff_group(snipe_group):
    return app_commands.Group(
        name="joinsoff", description="joinsoff commands", parent=snipe_group
    )


def get_track_group():
    return app_commands.Group(name="track", description="Track commands")


def get_stop_sub_group(track_group):
    return app_commands.Group(
        name="stop", description="stop commands", parent=track_group
    )


def get_utils_group():
    return app_commands.Group(name="utils", description="Utils commands")
