# https://github.com/anilsathyan7/Portrait-Segmentation

import cv2
import numpy as np
from PIL import Image
from keras.models import load_model
import tensorflow as tf


# Normalize the input image
def normalize(imgOri, scale=1, mean=[103.94, 116.78, 123.68], val=[0.017, 0.017, 0.017]):
    img = np.array(imgOri.copy(), np.float32) / scale
    return (img - mean) * val


model_path = 'fipu_face/segmentation/models/portrait_net/portrait_video.h5'
# In the architecture tf was used in a lambda expression so must pass tf as a custom object
__model = load_model(model_path, compile=False, custom_objects={'tf': tf})


def portrait_segmentation(frame):

    width, height = 256, 256
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Resize the image
    img = image.resize((width, height), Image.ANTIALIAS)
    img = np.asarray(img)

    # Normalize the input
    img = normalize(img)

    # Add fourth channel
    img = np.dstack([img, np.zeros((height, width, 1))])
    prepimg = img[np.newaxis, :, :, :]

    outputs = __model.predict(np.array(prepimg, dtype=np.float32))

    outputs = outputs.reshape(height, width, 1)

    out = np.float32((outputs > 1e-1))
    # Process the output
    out = cv2.resize(out, (frame.shape[1], frame.shape[0]))

    # Output mask
    out = np.expand_dims(out, -1)
    # out = out * image
    res = cv2.bitwise_and(frame.astype('uint8'), frame.astype('uint8'), mask=out.astype('uint8'))
    #  cv2 image -> res
    return res
