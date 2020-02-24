import base64
import json
import re

from .services import _banknote
from .util import _response_builder


services = {"banknote": _banknote}


invalid_request = _response_builder(res="invalid request")


def handle(req: str):
    jsonstr = json.loads(req)
    func = services.get(jsonstr["request"])
    if func:
        return func(jsonstr)
    else:
        return invalid_request
