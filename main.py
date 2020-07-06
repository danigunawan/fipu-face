import retina_face as rf

import cv2
import time
from utils import *

# IMAGE_PADDING_LEFT_RIGHT = 0.5
IMAGE_PADDING_UP_DOWN = 0.6
IMG_W_TO_H_RATIO = 2.5 / 3.5

MAX_EYES_Y_DIFF_PCT = 5
MAX_NOSE_EYES_DIST_DIFF_PCT = 10


def calc_scale(frame):
    w = frame.shape[1]
    h = frame.shape[0]
    scale_w = 1920 / w
    scale_h = 1080 / h
    return min(scale_w, scale_h, 1)


def crop_img(frame, f):
    # pad_lr = IMAGE_PADDING_LEFT_RIGHT
    pad_ud = IMAGE_PADDING_UP_DOWN

    left = f.bbox[0]
    bottom = f.bbox[1]
    right = f.bbox[2]
    top = f.bbox[3]

    y = bottom
    h = top - bottom

    x = left
    w = right - left

    y_start = y - h * pad_ud
    y_end = (y + h) + h * pad_ud

    i_h = y_end - y_start
    i_w = i_h * IMG_W_TO_H_RATIO

    x_start = abs(x - abs(w - i_w) / 2)
    x_end = abs(right + abs(w - i_w) / 2)

    """
    x_start = x - w * pad_lr
    x_end = right + w * pad_lr

    i_w = x_end - x_start
    i_h = i_w * IMG_W_TO_H_RATIO

    y_start = abs(y - abs(h - i_h)/2)
    y_end = abs(top + abs(h - i_h)/2)

    y_start = int(y - h * pad_ud)
    y_end = int((y + h) + h * pad_ud)
    """

    if min(y_start, x_start) < 0 or x_end > frame.shape[1] or y_end > frame.shape[0]:
        # print(y_start, x_start, x_end, y_end)
        return frame, "Slikano preblizu ili nije centrirano"

    frame = frame[int(y_start):int(y_end), int(x_start):int(x_end)]
    return frame, None


def scale_img(frame):
    frame = cv2.resize(frame, (591, 827))
    return frame


def check_face_alignment(f):
    l = f.landmark.astype(np.int)
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
        return "Head tilted"

    if nose[0] < left_eye[0] or nose[0] > right_eye[0] or nose_tilt > MAX_NOSE_EYES_DIST_DIFF_PCT:
        return "Not looking straight"

    return None


def do_detect(stream_path):
    print(stream_path)
    frame = cv2.imread('imgs/' + stream_path)
    if frame is None:
        return 'Image {} not found'.format(stream_path)

    # start_time = time.time()
    # print("Scale: ", calc_scale(frame))
    faces = rf.detect_faces(frame, thresh=0.1, scale=calc_scale(frame))

    # print("--- %s seconds ---" % (time.time() - start_time))
    # print('[i] ==> # detected faces: {}'.format(len(faces)))

    if len(faces) == 0 or len(faces) > 1:
        return "No/multiple faces detected"

    f = faces[0]
    # print(f.det_score)
    # draw_marks(frame, f, blur_faces)

    err = check_face_alignment(f)
    if err is not None:
        return err

    frame, err = crop_img(frame, f)
    if err is not None:
        return err

    cv2.imwrite('imgs/new/' + stream_path, scale_img(frame))
    return None


if __name__ == '__main__':
    # """
    for i in ['1.jpg', 'a.jpg', 'j.jpg', 'm.jpg', 'w.jpg', 's1.jpg', 's2.jpg', 'l1.jpg', 'l2.jpg', 'l3.jpg']:
        msg = do_detect(i)
        if msg is not None:
            print(msg)
    # """
    # do_detect('a.jpg')
