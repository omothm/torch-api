from PIL import Image
import cv2
import numpy as np
import os

path=os.path.dirname(__file__)
def histogram_of_test_image(test_image,frame=None):
    image=cv2.imread(test_image)

    if frame is None:
        feature_data = __calculate_histogram(image)
    else:
        im_width, im_height,_ = image.shape
        ymin, xmin, ymax, xmax = frame
        feature_data = __calculate_histogram(image[(int) (ymin * im_height):(int)(ymax * im_height) ,(int)(xmin * im_width):(int)(xmax * im_width)])
    
    try:
        with open(os.path.join(path, 'test.data'), "w") as myfile:
            myfile.write(feature_data)
    except:
        raise Exception("Test data histogram could not load.")

def __calculate_histogram(image:cv2):
    chans = cv2.split(image)
    colors = ('b', 'g', 'r')
    features = []
    feature_data = ''
    counter = 0
    for (chan, color) in zip(chans, colors):
        counter = counter + 1

        hist = cv2.calcHist([chan], [0], None, [256], [0, 256])
        features.extend(hist)

        # find the peak pixel values for R, G, and B
        elem = np.argmax(hist)

        if counter == 1:
            blue = str(elem)
        elif counter == 2:
            green = str(elem)
        elif counter == 3:
            red = str(elem)
            feature_data = red + ',' + green + ',' + blue
    return feature_data

# add color histogram of training image
def histogram_of_training_image(training_image,data_source):
    image=cv2.imread(training_image)
    feature_data= __calculate_histogram(image)
    try:
        with open(os.path.join(path, 'training.data'), "a") as myfile:
            myfile.write(feature_data + ',' + data_source + '\n')
    except:
        raise Exception("Training sample could not load.")