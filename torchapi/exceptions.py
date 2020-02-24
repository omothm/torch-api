class TorchException(Exception):
    """Represents errors that end up in the response from the server.

    Internal API errors should not use this class. They should use the base
    `Exception` class instead."""
    pass
