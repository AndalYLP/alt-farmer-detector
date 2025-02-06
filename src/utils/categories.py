from discord import app_commands

friends_group = app_commands.Group(name="friends", description="friends commands")
snipe_group = app_commands.Group(name="snipe", description="Snipe commands")
joinsoff_group = app_commands.Group(
    name="joinsoff", description="joinsoff commands", parent=snipe_group
)
track_group = app_commands.Group(name="track", description="Track commands")
stop_sub_group = app_commands.Group(
    name="stop", description="stop commands", parent=track_group
)


def get_utils_group():
    app_commands.Group(name="utils", description="Utils commands")
