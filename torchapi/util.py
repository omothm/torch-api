import datetime
import base64
import re

from .exceptions import TorchException


def _response_builder(status="ok", **kwargs) -> dict:
    """Ensures the format of the response is valid according to docs.
    Returns
    =======
    A `dict` containing the response JSON."""
    response = {}
    response["status"] = status
    response["time"] = str(datetime.datetime.now())
    response.update(kwargs)
    if status == "ok":
        if not "response" in kwargs:
            raise Exception("Invalid response message: no 'response'")
    # if response is "error", kwargs must include "source" and "error"
    if status == "error":
        if not all(x in kwargs for x in ["error_origin", "error_message"]):
            raise Exception(
                "Invalid error message: one or more of 'error_origin' and 'error_message' is missing")
    return response


def _error_response(origin: str, msg: str):
    """Convenience wrapper around `_response_builder` for errors."""
    return _response_builder(status="error", error_origin=origin, error_message=msg)


def _get_image_obj(req):
    image_base64 = req.get("image", None)
    if not image_base64:
        raise TorchException("No image")
    encoding_regex = re.search(
        r"^data:image/(png|jpg|gif);base64,(.+)$", image_base64)
    if not encoding_regex:
        raise TorchException("Invalid image format")
    encoding = encoding_regex.group(2)
    image = base64.b64decode(encoding)
    return image
