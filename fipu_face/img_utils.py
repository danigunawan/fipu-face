import cv2
import numpy as np
from exceptions.image_exception import *
import base64

ENCODING_BASE64 = 'base64'
ENCODING_BYTES = 'bytes'
JPEG_QUALITY = 80

INCH = 25.4


# Resize's the image to the image configuration resolution at given dip
def scale_img(frame, imc):
    img_res = (round(imc.w / INCH * imc.dpi), round(imc.h / INCH * imc.dpi))
    # print(img_res)
    frame = cv2.resize(frame, img_res)
    return frame


# Calculating scale for RetinaFace
# The train images were at 640x640 so the scale is calculated based on that assumption
def calc_scale(frame):
    w = frame.shape[1]
    h = frame.shape[0]
    return min(640 / w, 640 / h)
    # scale_w = 1920 / w
    # scale_h = 1080 / h
    # print(min(scale_w, scale_h, 1) * 0.5, min(640 / w, 640 / h))
    # return min(scale_w, scale_h, 1) * 0.5  # Scale lowered by a factor to speed up the detection


# Decodes the image from a bytes stream
def cv2_read_img(stream):
    try:
        img = cv2.imdecode(np.frombuffer(stream, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise_error(INVALID_IMAGE_FORMAT)
        return img
    except:
        raise_error(INVALID_IMAGE_FORMAT)


# Encodes the image in the given method: ENCODING_BASE64 or ENCODING_BYTES
def convert_img(img, method):
    if img is None:
        return None
    success, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])

    if not success:
        return None

    if method == ENCODING_BASE64:
        return base64.b64encode(buffer).decode('utf-8')
    elif method == ENCODING_BYTES:
        return buffer.tobytes()

    raise_error(INVALID_ENCODING_METHOD, [method, (ENCODING_BASE64, ENCODING_BYTES)])
