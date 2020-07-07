from fipu_face import retina_face as rf

import time
from fipu_face.utils import *
from fipu_face.img_utils import *
from exceptions.image_exception import ImageException
from fipu_face.img_config import *

IMAGE_PADDING_UP_DOWN = 0.5

MAX_EYES_Y_DIFF_PCT = 5
MAX_NOSE_EYES_DIST_DIFF_PCT = 10

IMG_WIDTH = 25
IMG_HEIGHT = 30
IMG_DPI = 300
INCH = 25.4

IMG_CONFIG = Img35x45_11Plus


def crop_img(frame, f):
    pad_ud = IMAGE_PADDING_UP_DOWN

    left = f.bbox[0]
    top = f.bbox[1]
    right = f.bbox[2]
    bottom = f.bbox[3]

    y = top
    h = bottom - top

    x = left
    w = right - left

    y_start = y - h * pad_ud
    y_end = bottom + h * pad_ud

    i_h = y_end - y_start
    i_w = i_h * (IMG_WIDTH / IMG_HEIGHT)

    x_start = x - abs(w - i_w) / 2
    x_end = right + abs(w - i_w) / 2

    return __do_crop(frame, x_start, x_end, y_start, y_end)


def __do_crop(frame, x_start, x_end, y_start, y_end):
    if min(y_start, x_start) < 0 or x_end > frame.shape[1] or y_end > frame.shape[0]:
        # print(y_start, x_start, x_end, y_end)
        raise ImageException("Slikano preblizu ili nije centrirano")

    frame = frame[int(y_start):int(y_end), int(x_start):int(x_end)]
    return frame


def mup_crop(frame, f):
    imc = IMG_CONFIG

    left = f.bbox[0] * 0.99
    top = f.bbox[1] * 0.99
    right = f.bbox[2] * 1.01
    bottom = f.bbox[3] * 1.01

    y = top
    h = bottom - top

    x = left
    w = right - left

    imw_pct = np.min(imc.hw_range) / imc.w
    imh_pct = np.min(imc.hh_range) / imc.h

    max_i_h_pct = np.max(imc.hh_range) / imc.h
    total_h_diff_pct = max_i_h_pct - imh_pct + (1 - max_i_h_pct)

    total_h_diff = total_h_diff_pct / imh_pct * h
    head_to_max = (max_i_h_pct - imh_pct) / (1 - imh_pct) * total_h_diff
    pad_tb = (total_h_diff - head_to_max) / 2

    y_start = top - head_to_max - pad_tb
    y_end = bottom + pad_tb

    i_h = y_end - y_start
    i_w = i_h * (imc.w / imc.h)

    x_start = x - abs(w - i_w) / 2
    x_end = right + abs(w - i_w) / 2

    """
    print(imc.hh_range[0] / imc.h, h / i_h, imc.hh_range[1] / imc.h)
    print(imc.hw_range[0] / imc.w, w / i_w, imc.hw_range[1] / imc.w)

    print(imh_pct, h / i_h, imc.hh_range[0] / imc.h <= h / i_h <= imc.hh_range[1] / imc.h)
    print(imw_pct, w / (x_end - x_start), imc.hw_range[0] / imc.w <= w / (x_end - x_start) <= imc.hw_range[1] / imc.w)

    print(imc.w / imc.h, i_w / i_h)
    print(pad_tb / i_h, (1 - np.max(imc.hh_range) / imc.h) / 2)

    print("Ratio: ", imc.w / imc.h, i_w / i_h)
    """
    return __do_crop(frame, x_start, x_end, y_start, y_end)


def scale_img(frame):
    img_res = (round(IMG_WIDTH / INCH * IMG_DPI), round(IMG_HEIGHT / INCH * IMG_DPI))
    # print(img_res)
    frame = cv2.resize(frame, img_res)
    return frame


def check_face_alignment(f):
    l = f.landmark.astype(np.int)
    if len(l) < 5:
        raise ImageException("Nisu očitana sva obilježja lica (oči, nos, usta)")

    left_eye = l[0]
    right_eye = l[1]
    nose = l[2]
    # left_lip = l[3]
    # right_lip = l[4]

    f_w = f.bbox[2] - f.bbox[0]
    f_h = f.bbox[3] - f.bbox[1]

    eyes_tilt = abs(left_eye[1] - right_eye[1]) / f_h * 100
    nose_tilt = abs(abs(nose[0] - left_eye[0]) - abs(nose[0] - right_eye[0])) / f_w * 100

    # print("Eyes: ", eyes_tilt, "Nose-Eyes: ", nose_tilt)

    if eyes_tilt > MAX_EYES_Y_DIFF_PCT:
        raise ImageException("Glava je nakrivljena")

    if nose[0] < left_eye[0] or nose[0] > right_eye[0] or nose_tilt > MAX_NOSE_EYES_DIST_DIFF_PCT:
        raise ImageException("Ne gleda ravno")


def detect(frame):
    # start_time = time.time()
    # print("Scale: ", calc_scale(frame))
    faces = rf.detect_faces(frame, thresh=0.1, scale=calc_scale(frame))

    # print("--- %s seconds ---" % (time.time() - start_time))
    # print('[i] ==> # detected faces: {}'.format(len(faces)))

    if len(faces) == 0 or len(faces) > 1:
        raise ImageException("Nije pronađeno lice ili je pronađeno više od jednog lica")

    f = faces[0]
    # print(f.det_score)
    # draw_marks(frame, f, False)

    check_face_alignment(f)

    frame = crop_img(frame, f)
    # frame = mup_crop(frame, f)
    frame = scale_img(frame)
    # draw_ellipses(IMG_CONFIG, frame)

    return frame


def __do_detect(frame, encoding=ENCODING_BASE64):
    frame = detect(frame)
    return convert_img(frame, encoding)


def get_from_file(file, encoding=ENCODING_BASE64):
    return __do_detect(cv2_read_img(file.read()), encoding)


def get_from_base64(uri, encoding=ENCODING_BASE64):
    encoded_data = uri.split('base64,')[-1]
    try:
        img = cv2_read_img(base64.b64decode(encoded_data))
    except:
        raise ImageException("Invalid base64 encoded image")

    return __do_detect(img, encoding)


def get_from_bytes(img_bytes, encoding=ENCODING_BASE64):
    try:
        return __do_detect(img_bytes, encoding)
    except:
        raise ImageException("Invalid image bytes")
