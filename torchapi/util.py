"""Torch utilities

Helper functions for the API.
"""

__author__ = "Omar Othman"

import datetime


def response_builder(status="ok", **kwargs) -> dict:
    """Ensures the format of the response is valid according to docs.
    ### Returns
    a `dict` containing the response JSON."""
    response = {}
    response["status"] = status
    response["time"] = str(datetime.datetime.now())
    response.update(kwargs)
    if status == "ok":
        if "response" not in kwargs:
            raise Exception("Invalid response message: no 'response'")
    # if response is "error", kwargs must include "source" and "error"
    if status == "error":
        if not all(x in kwargs for x in ["error_origin", "error_message"]):
            raise Exception("Invalid error message: one or more of " +
                            "'error_origin' and 'error_message' is missing")
    return response


def error_response(origin: str, msg: str) -> dict:
    """Convenience wrapper around `_response_builder` for errors."""
    return response_builder(status="error", error_origin=origin, error_message=msg)
