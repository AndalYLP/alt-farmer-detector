from discord import app_commands

friends_group = app_commands.Group(name="friends", description="Friends commands")
snipe_group = app_commands.Group(name="snipe", description="Snipe commands")
track_group = app_commands.Group(name="track", description="Track commands")
utils_group = app_commands.Group(name="utils", description="Utils commands")
list_group = app_commands.Group(name="list", description="List commands")
reports_group = app_commands.Group(name="reports", description="Reports commands")

add_sub_group = app_commands.Group(
    name="add", description="Add commands", parent=reports_group
)
joinsoff_sub_group = app_commands.Group(
    name="joinsoff", description="joinsoff commands", parent=snipe_group
)
