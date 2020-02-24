from keras.models import load_model
from keras.preprocessing import image
import numpy as np
import time
import os
import sys

local_path = os.path.dirname(__file__)

model_file = os.path.join(local_path, "assets\\banknote.h5")
temp_image = os.path.join(local_path, "temp\\banknote.tmp")
desired_image_size = (224,224)

class_map = {
        0: 10, 
        1: 100, 
        2: 20, 
        3: 200, 
        4: 5, 
        5: 50, 
    }


def _get_class(result):
    return class_map.get(result, -1)


def predict(image_obj):
    with open(temp_image, "wb") as f:
        f.write(image_obj)
    try:
        model = load_model(model_file)
    except:
        return -2
    try:
        image = _load_image(temp_image)
    except:
        return -3
    pred = model.predict(image)
    result = np.argmax(pred,axis=1)
    prediction_class = _get_class(result[0])
    return prediction_class


def _load_image(img_path):
    """
        Resize the image and map the pixel values between 0 and 1
    """
    #Load the image with given size
    img = image.load_img(img_path, target_size=desired_image_size)
    # convert the image into array format (height, width, channels)
    img_tensor = image.img_to_array(img)               
    # add a dimension because the model expects this shape: (batch_size, height, width, channels) 
    img_tensor = np.expand_dims(img_tensor, axis=0)   
    # imshow expects values in the range [0, 1]      
    img_tensor /= 255.                                      

    return img_tensor