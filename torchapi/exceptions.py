"""Torch exceptions

Exceptions that are raised throughout the Torch API.
"""

__author__ = "Omar Othman"


class TorchException(Exception):
    """Represents errors that end up in the response from the server.

    Internal API errors should not use this class. They should use the base
    `Exception` class instead.

    ### Arguments
    `origin`: the origin of the error to be added to the error response.
    """

    def __init__(self, origin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.origin = origin
