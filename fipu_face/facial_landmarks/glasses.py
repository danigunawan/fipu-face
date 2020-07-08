"""
import cv2
import numpy as np


# Source: https://github.com/TianxingWu/realtime-glasses-detection

def get_aligned_face(img, left, right):
    desired_w = 256
    desired_h = 256
    desired_dist = desired_w * 0.5

    eyescenter = ((left[0] + right[0]) * 0.5, (left[1] + right[1]) * 0.5)
    dx = right[0] - left[0]
    dy = right[1] - left[1]
    dist = np.sqrt(dx * dx + dy * dy)
    scale = desired_dist / dist
    angle = np.degrees(np.arctan2(dy, dx))
    M = cv2.getRotationMatrix2D(eyescenter, angle, scale)

    # update the translation component of the matrix
    tX = desired_w * 0.5
    tY = desired_h * 0.5
    M[0, 2] += (tX - eyescenter[0])
    M[1, 2] += (tY - eyescenter[1])

    aligned_face = cv2.warpAffine(img, M, (desired_w, desired_h))

    return aligned_face


def judge_eyeglass(img):
    img = cv2.GaussianBlur(img, (11, 11), 0)

    sobel_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=-1)
    sobel_y = cv2.convertScaleAbs(sobel_y)

    edgeness = sobel_y

    retVal, thresh = cv2.threshold(edgeness, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    d = len(thresh) * 0.5
    x = np.int32(d * 6 / 7)
    y = np.int32(d * 3 / 4)
    w = np.int32(d * 2 / 7)
    h = np.int32(d * 2 / 4)

    x_2_1 = np.int32(d * 1 / 4)
    x_2_2 = np.int32(d * 5 / 4)
    w_2 = np.int32(d * 1 / 2)
    y_2 = np.int32(d * 8 / 7)
    h_2 = np.int32(d * 1 / 2)

    roi_1 = thresh[y:y + h, x:x + w]
    roi_2_1 = thresh[y_2:y_2 + h_2, x_2_1:x_2_1 + w_2]
    roi_2_2 = thresh[y_2:y_2 + h_2, x_2_2:x_2_2 + w_2]
    roi_2 = np.hstack([roi_2_1, roi_2_2])

    measure_1 = sum(sum(roi_1 / 255)) / (np.shape(roi_1)[0] * np.shape(roi_1)[1])
    measure_2 = sum(sum(roi_2 / 255)) / (np.shape(roi_2)[0] * np.shape(roi_2)[1])
    measure = measure_1 * 0.3 + measure_2 * 0.7

    print(measure)

    return measure > 0.3


def has_glasses(frame, f):
    landmarks = f.landmark.astype(np.int)

    left_eye = landmarks[0]
    right_eye = landmarks[1]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aligned_face = get_aligned_face(gray, left_eye, right_eye)

    judge = judge_eyeglass(aligned_face)
    return judge
"""


def has_glasses(frame, f):
    return False
