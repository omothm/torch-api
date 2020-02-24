from .services import banknote
from .util import _get_image_obj, _response_builder


def _banknote(req):
    image_obj = _get_image_obj(req)
    return _response_builder(res=banknote.predict(image_obj))