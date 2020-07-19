import cv2
import numpy as np
from exceptions.image_exception import ImageException
import base64

ENCODING_BASE64 = 'base64'
ENCODING_BYTES = 'bytes'
JPEG_QUALITY = 80


def calc_scale(frame):
    w = frame.shape[1]
    h = frame.shape[0]
    return min(640 / w, 640 / h)
    # scale_w = 1920 / w
    # scale_h = 1080 / h
    # print(min(scale_w, scale_h, 1) * 0.5, min(640 / w, 640 / h))
    # return min(scale_w, scale_h, 1) * 0.5  # Scale lowered by a factor to speed up the detection


def cv2_read_img(stream):
    return cv2.imdecode(np.frombuffer(stream, np.uint8), cv2.IMREAD_UNCHANGED)


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

    raise ImageException("Encoding method {} not implemented. Use {}".format(method, (ENCODING_BASE64, ENCODING_BYTES)))
