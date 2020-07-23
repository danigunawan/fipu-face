# *******************************************************************
#
# Author : Thanh Nguyen, 2018
# Email  : sthanhng@gmail.com
# Github : https://github.com/sthanhng
#
# BAP, AI Team
# Face detection using the YOLOv3 algorithm
#
# Description : utils.py
# This file contains the code of the parameters and help functions
#
# *******************************************************************


import datetime
import numpy as np
import cv2

# Default colors
COLOR_BLUE = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_YELLOW = (0, 255, 255)


# -------------------------------------------------------------------
# Help functions
# -------------------------------------------------------------------

# Blur the face within the bounding box
def blur_face(frame, left, top, right, bottom, factor=1.0):
    # automatically determine the size of the blurring kernel based
    # on the spatial dimensions of the input image
    image = frame[top:bottom, left:right]
    (h, w) = image.shape[:2]
    kW = int(w / factor)
    kH = int(h / factor)
    # ensure the width of the kernel is odd
    if kW % 2 == 0:
        kW -= 1
    # ensure the height of the kernel is odd
    if kH % 2 == 0:
        kH -= 1

    kW = max(1, kW)
    kH = max(1, kH)
    # apply a Gaussian blur to the input image using our computed kernel size
    frame[top:bottom, left:right] = cv2.GaussianBlur(image, (kW, kH), 0)


# Draw the predicted bounding box
def draw_predict(frame, conf, left, top, right, bottom, blur=False, name=''):
    left = int(left)
    top = int(top)
    right = int(right)
    bottom = int(bottom)
    # Draw a bounding box.
    cv2.rectangle(frame, (left, top), (right, bottom), COLOR_YELLOW, 5)

    text = '{:.2f} {}'.format(conf, name)

    # Display the label at the top of the bounding box
    label_size, base_line = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

    top = max(top, label_size[1])
    cv2.putText(frame, text, (left, top - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                COLOR_WHITE, 1)

    if blur:
        blur_face(frame, left, top, right, bottom)


def draw_marks(frame, f, blur_faces=False):
    b = f.bbox
    draw_predict(frame, f.det_score, b[0], b[1], b[2], b[3], blur_faces)
    if f.landmark is not None:
        landmark = f.landmark.astype(np.int)
        for l in range(landmark.shape[0]):
            color = (0, 0, 255)
            if l == 0 or l == 3:
                color = (0, 255, 0)
            cv2.circle(frame, (landmark[l][0], landmark[l][1]), 1, color, 5)


def draw_ellipses(frame, imc):
    w = frame.shape[1]
    h = frame.shape[0]
    ax_len = (int(np.max(imc.hh_range) / imc.h * h / 2), int(np.max(imc.hw_range) / imc.w * w / 2))
    cv2.ellipse(frame, (int(w / 2), int(h / 2)), ax_len, 90, 0, 360, COLOR_RED, 1)


def double_arrowed_line(img, pt1, pt2, color, thickness):
    cv2.arrowedLine(img, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])), color, thickness)
    cv2.arrowedLine(img, (int(pt2[0]), int(pt2[1])), (int(pt1[0]), int(pt1[1])), color, thickness)


def draw_no_space(img, f, spaces, color, thickness):
    h, w = img.shape[:2]
    b = f.bbox
    f_h_m = (b[3] + b[1]) / 2
    f_w_m = (b[2] + b[0]) / 2

    # Order of spaces should be: left, top, right, bottom
    # just like in the face bbox
    for i, s in enumerate(spaces):
        if s:

            # Top or bottom
            if i % 2 != 0:
                pt1 = (f_w_m, b[i])
                pt2 = (pt1[0], 0 if i == 1 else h)
            # Left or right
            else:
                pt1 = (b[i], f_h_m)
                pt2 = (0 if i == 0 else w, pt1[1])

            double_arrowed_line(img, pt1, pt2, color, thickness)


def draw_head_turn(img, f, is_left, color, thickness):
    left = f.bbox[0]
    right = f.bbox[2]
    nose = f.landmark.astype(np.int)[2]

    pt1 = (nose[0], nose[1])
    pt2 = (int(right), nose[1])
    if is_left:
        pt2 = (int(left), nose[1])

    cv2.arrowedLine(img, pt1, pt2, color, thickness)


def draw_head_tilt(img, f, is_left, color, thickness):
    b = f.bbox
    top = b[1]
    f_h_m = (b[3] + b[1]) / 2
    f_w_m = (b[2] + b[0]) / 2

    f_h = b[3] - b[1]
    f_w = b[2] - b[0]

    start_angle = -70
    end_angle = 270

    if not is_left:
        start_angle, end_angle = 250, -90

    ax_len = (int(f_w / 2), int(f_h / 2))
    cv2.ellipse(img, (int(f_w_m), int(f_h_m)), ax_len, 0, start_angle, end_angle, color, thickness)

    a_l = f_w * 0.05
    if not is_left:
        a_l *= -1
    pts = np.array([[int(f_w_m - a_l), int(top - a_l)],
                    [int(f_w_m), int(top)],
                    [int(f_w_m - a_l), int(top + a_l)]],
                   dtype=np.int32)

    cv2.polylines(img, [pts], False, color, thickness)


def draw_non_white_bg(img, f, color, thickness):
    h, w = img.shape[:2]
    n_stripes = 10

    left = f.bbox[0] * 0.9
    top = f.bbox[1] - (f.bbox[3] - f.bbox[1]) / 3
    right = f.bbox[2] * 1.1
    bottom = f.bbox[3] * 1.1

    space = bottom / n_stripes
    for i in range(n_stripes + 1):
        y = int(space * i)
        if y < top:
            cv2.line(img, (0, y), (int(w), y), color, thickness)
        else:
            diff = i * (right - left) * 0.02
            cv2.line(img, (0, y), (int(left - diff), y), color, thickness)
            cv2.line(img, (int(right + diff), y), (int(w), y), color, thickness)


def calc_thickness_scale(img):
    return max(1, round(max(img.shape[1] / 295, img.shape[0] / 354)))

#   import cv2
# from fipu_face.fipu_face import *
# img = cv2.imread('imgs/new/r.jpg')
# f = rf.detect_faces(img, scale=calc_scale(img))[0]
# draw_no_space(img, f, [1, 1, 1, 1])
# draw_non_white_bg(img, f, COLOR_WHITE, 2)
# cv2.imwrite('imgs/new/r1.jpg', img)

