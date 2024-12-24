class UserNotFound(Exception):
    def __init__(self, username):
        super().__init__(f"didn't find the requested username: **{username}**")


class InvalidAmountOfUsernames(Exception):
    def __init__(self, amount):
        super().__init__(f"Please provide more than **{amount}** username")


class ProtectedCategory(Exception):
    def __init__(self, category, command):
        super().__init__(f"**{category}** is protected from **{command}** command.")
