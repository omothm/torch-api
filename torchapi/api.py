"""Torch API

Handles JSON requests and returns JSON responses as defined in Torch API
documentation.
"""

__author__ = "Omar Othman"


import json

from .exceptions import TorchException
from .services.banknote import BanknoteService
from .services.color_detection import ColorDetectionService
from .services.detailed_color import DetailedColor
from .services.ocr import OcrService
from .services.object_detection import ObjectDetectionService
from .util import error_response, get_config, response_builder

# service instances defined here should live as long as the session
_SERVICES = {
    "banknote": BanknoteService(config=get_config("banknote")),
    "ocr": OcrService(),
    "color": ColorDetectionService(ObjectDetectionService()),
    "detailed_color": DetailedColor(),
    "object_detection": ObjectDetectionService()
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
        response = _UNKNOWN_SERVICE_ERROR
    else:
        try:
            prediction, confidence = service.predict(jsonstr)
            response = response_builder(
                response=prediction, confidence=confidence)
        except TorchException as exception:
            response = error_response(
                origin=exception.origin, msg=str(exception))
    return json.dumps(response)
