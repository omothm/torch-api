import base64
import re


def _response_builder(res: str) -> dict:
    return {"response": res}


def _get_image(req):
    image_base64 = req["image"]
    encoding_regex = re.search(r"^data:image/(png|jpg|gif);base64,(.+)$", image_base64)
    if not encoding_regex:
        print("Cannot read base64 encoding")
        exit(1)
    # image_format = encoding_regex.group(1)
    encoding = encoding_regex.group(2)
    image = base64.b64decode(encoding)
    return image