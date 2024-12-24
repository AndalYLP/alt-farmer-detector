"""
RobloxPy._exceptions
~~~~~~~~~~~~~~~~~~~~

This module contains the set of RobloxPy's exceptions and warnings.
"""


class MaxAttempts(Exception):
    """Reached maximum attempts within a request."""


# --------------------------------- Warnings --------------------------------- #


class CookieWarning(Warning):
    def __init__(self, Text, StatusCode, ResponseText):
        self.Text = Text
        self.StatusCode = StatusCode
        self.ResponseText = ResponseText

        super().__init__(
            f"{Text}. Some functions may not work properly. (Status code: {StatusCode})\nResponse text: {ResponseText}"
        )
