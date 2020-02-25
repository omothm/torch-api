import base64
import json

from .exceptions import TorchException
from .services.banknote import BanknoteService
from .util import error_response, response_builder


# service instances defined here should live as long as the session
_SERVICES = {
    "banknote": BanknoteService()
}


unknown_service = _error_response(origin="server", msg="Unknown service")


def handle(req: str) -> str:
    jsonstr = json.loads(req)
    service = _SERVICES.get(jsonstr["request"])
    if not service:
        return _UNKNOWN_SERVICE_ERROR
    try:
        prediction = service.predict(jsonstr)
    except TorchException as exception:
        return error_response(origin=exception.origin, msg=str(exception))
    return response_builder(response=prediction)
