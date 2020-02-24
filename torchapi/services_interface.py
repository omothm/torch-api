from .services import banknote
from .util import _get_image_obj, _response_builder, _error_response
from .exceptions import TorchException


def _banknote(req: dict) -> dict:
    try:
        image_obj = _get_image_obj(req)
    except TorchException as e:
        return _error_response(origin="banknote", msg=str(e))
    prediction = banknote.predict(image_obj)
    return _response_builder(response=prediction)
