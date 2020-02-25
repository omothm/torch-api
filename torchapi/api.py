"""Torch API

Handles JSON requests and returns JSON responses as defined in Torch API
documentation.
"""

__author__ = "Omar Othman"


import json

from .exceptions import TorchException
from .services.banknote import BanknoteService
from .util import error_response, response_builder


# service instances defined here should live as long as the session
_SERVICES = {
    "banknote": BanknoteService()
}

_UNKNOWN_SERVICE_ERROR = error_response(origin="server", msg="Unknown service")


def handle(req: str) -> str:
    """Accepts a JSON request (string) that is assumed to be conforming to the
    specification defined in the Torch API documentation, and returns a JSON
    response (string) from the requested service if it exists.

    If the request cannot be processed for any reason, an error response is
    returned.
    """
    jsonstr = json.loads(req)
    service = _SERVICES.get(jsonstr["request"])
    if not service:
        return _UNKNOWN_SERVICE_ERROR
    try:
        prediction = service.predict(jsonstr)
    except TorchException as exception:
        return error_response(origin=exception.origin, msg=str(exception))
    return response_builder(response=prediction)
