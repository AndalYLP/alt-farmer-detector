class FriendsDesc:
    mutuals = "Check mutuals between users."
    usernamesMutuals = "List of usernames, e.g: OrionYeets, chasemaser, ..."
    strict = "True = Everyone should have the same user added."
    ingame = "Check in-game friends."
    sameServer = "True will only show in same server friends."
    username = "Player username to check."
    added = "Check if the target is added with the given users."
    target = "User to check his friends."
    usernamesAdded = "Users you want to check if they are added with the target."


class ListDesc:
    by_group = "Get a list of players in a group."
    group_name = "Name of the group to get"
    get_list = "List of users being tracked."


class ReportsDesc:
    add_player = "Add a player to the loop."
    username = "the username to add."
    group_name = "Group name, None = no group."
    alt_account = "True if its an alt account."
    mute = "Mute a notification type."

    def mute_type(type: str):
        return f"Dont show {type} notifications."

    notifications = "Enable/disable notifications."
    resume = "Resume the reports."
    stop = "Stop all notifications"


class SnipeDesc:
    snipePlayer = "Send player status."
    usernamesSnipe = "Players to snipe, e.g: OrionYeets, chasemaser, ..."
    snipePlayerJoinsOff = "Send player status, only works with BedWars."
    usernameJoinsOff = "Player username to snipe."
    forceUpdate = "If true you will get the latest data and update the current data, if false you will search through the current data"


class TrackDesc:
    trackPlayer = "Creates a channel and tracks the status from a user."
    username = "Player username to track."
    stopTracking = "stop notifications/tracking for a user."
    usernameStop = "Player username to stop tracking."


class UtilsDesc:
    purge = "Purge messages."
    amount = "Amount of messages to delete 1-100."
