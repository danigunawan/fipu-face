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
    cv2.rectangle(frame, (left, top), (right, bottom), COLOR_YELLOW, 20)

    text = '{:.2f} {}'.format(conf, name)

    # Display the label at the top of the bounding box
    label_size, base_line = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

    top = max(top, label_size[1])
    cv2.putText(frame, text, (left, top - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                COLOR_WHITE, 1)

    if blur:
        blur_face(frame, left, top, right, bottom)


def draw_marks(frame, f, blur_faces):
    b = f.bbox
    draw_predict(frame, f.det_score, b[0], b[1], b[2], b[3], blur_faces)
    if f.landmark is not None:
        landmark = f.landmark.astype(np.int)
        for l in range(landmark.shape[0]):
            color = (0, 0, 255)
            if l == 0 or l == 3:
                color = (0, 255, 0)
            cv2.circle(frame, (landmark[l][0], landmark[l][1]), 1, color, 50)


def draw_ellipses(frame, imc):
    w = frame.shape[1]
    h = frame.shape[0]
    ax_len = (int(np.max(imc.hh_range) / imc.h * h / 2), int(np.max(imc.hw_range) / imc.w * w / 2))
    cv2.ellipse(frame, (int(w / 2), int(h / 2)), ax_len, 90, 0, 360, COLOR_RED, 1)
