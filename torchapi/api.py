import base64
import json
import re

from .services_interface import _banknote
from .util import _error_response


services = {
    "banknote": _banknote
}


unknown_service = _error_response(origin="server", msg="Unknown service")


def handle(req: str) -> str:
    jsonstr = json.loads(req)
    func = services.get(jsonstr["request"], lambda _: unknown_service)
    return func(jsonstr)
