import json
import os
from tqdm import tqdm

from torchapi import handle, get_config


TEST_DIR = os.path.join(os.path.dirname(__file__), "data", "base64")


def predict(images, desc="Inference"):
    """Yields (response_json, actual_class)
    """
    for (image, class_name) in tqdm(images, desc=desc, unit="img"):
        # build the request
        request_json = {"request": "banknote", "image": image}
        request = json.dumps(request_json)

        # infer
        response = handle(request)
        response_json = json.loads(response)
        yield (response_json, class_name)


def assert_banknote_threshold(thresh):
    """Ensures that the configured threshold for the banknote service is as
    required.
    """
    config = get_config("banknote")
    current_thresh = config["background_threshold"]
    thresh_pass = True
    if isinstance(current_thresh, list) and not isinstance(thresh, list):
        thresh_pass = sum([1 for x in current_thresh if x != thresh]) == 0
    else:
        thresh_pass = thresh == current_thresh
    if not thresh_pass:
        raise Exception("Threshold is not configured correctly.")


def load_base64(class_name, class_path, desc="Loading images"):
    """Returns a list of tuples (base64, class_name)
    """
    images = []
    (_, _, filenames) = next(os.walk(class_path))
    for filename in tqdm(filenames, desc=desc, unit="file"):
        # get the base64 image string
        with open(os.path.join(class_path, filename), "r") as base64_file:
            images.append((base64_file.read(), class_name))
    return images
