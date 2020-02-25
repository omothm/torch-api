"""Common services functions

Functions that are useful for all services that does not belong to a specific
class.
"""

__author__ = "Omar Othman"


import base64
import os
import re

from pathlib import Path

from ..exceptions import TorchException

_LOCAL_PATH = os.path.dirname(__file__)

_ASSETS_DIR = os.path.join(_LOCAL_PATH, "assets")
_TEMP_DIR = os.path.join(_LOCAL_PATH, "temp")


def _file(base_dir: str, svc: str, filename: str) -> str:
    svc_dir = os.path.join(base_dir, svc)
    # create the directory if it does not exist
    Path(svc_dir).mkdir(parents=True, exist_ok=True)
    return os.path.join(svc_dir, filename)


def asset_file(svc: str, filename: str) -> str:
    """Returns a full path for an asset file for the given service (`svc`) and
    with the given `filename`. Ensures that the directory to that file exists.

    Asset files are saved to the directory `assets` in the same location where
    this function is defined, with each `svc` in its own subdirectory.
    """
    return _file(_ASSETS_DIR, svc, filename)


def temp_file(svc: str, filename: str) -> str:
    """Returns a full path for a temp file for the given service (`svc`) and
    with the given `filename`. Ensures that the directory to that file exists.

    Temp files are saved to the directory `temp` in the same location where
    this function is defined, with each `svc` in its own subdirectory.
    """
    return _file(_TEMP_DIR, svc, filename)


def base64_to_image_obj(req: dict):
    """Extracts the base-64 image string from the given `req`uest and converts
    it to a bytes object. This bytes object can then be written (in binary mode)
    to an image file.
    """
    image_base64 = req.get("image", None)
    if not image_base64:
        raise TorchException("No image")
    encoding_regex = re.search(
        r"^data:image(/(.*))?;base64,(.+)$", image_base64)
    if not encoding_regex:
        raise TorchException("Invalid image format")
    encoding = encoding_regex.group(3)
    image = base64.b64decode(encoding)
    return image
