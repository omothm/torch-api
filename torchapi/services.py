from .util import _get_image, _response_builder


def _banknote(req):
    image = _get_image(req)
    return _response_builder(res="50")