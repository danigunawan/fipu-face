# https://github.com/anilsathyan7/Portrait-Segmentation

import numpy as np
from keras.models import load_model
from PIL import Image
# import matplotlib.pyplot as plt
import cv2

model_path = 'fipu_face/segmentation/models/munet/munet_mnv3_wm05.h5'

__model = load_model(model_path, compile=False)


def portrait_segmentation(frame):
    im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    # Inference
    im = im.resize((224, 224), Image.ANTIALIAS)
    img = np.float32(np.array(im) / 255.0)

    img = img[:, :, 0:3]

    # Reshape input and threshold output
    out = __model.predict(img.reshape(1, 224, 224, 3))
    out = np.float32((out > 0.5))
    # Output mask
    out = np.squeeze(out.reshape((224, 224)))

    out = np.expand_dims(out, -1)
    #  Output image
    out = out * img

    img = cv2.resize(out, (frame.shape[1], frame.shape[0]))
    # cv2 image -> (img * 255).astype('uint8')[:, :, ::-1]
    return img

