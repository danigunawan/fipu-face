import math

import cv2
import numpy as np


def rotationMatrixToEulerAngles(R):
    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

    singular = sy < 1e-6

    if not singular:
        roll = math.atan2(R[2, 1], R[2, 2])
        pitch = math.atan2(-R[2, 0], sy)
        yaw = math.atan2(R[1, 0], R[0, 0])
    else:
        roll = math.atan2(-R[1, 2], R[1, 1])
        pitch = math.atan2(-R[2, 0], sy)
        yaw = 0

    return np.array([roll, pitch, yaw])


def is_not_looking_straight(frame, f, min_horizontal_tilt=1, max_horizontal_tilt=15, min_vertical_tilt=30, max_vertical_tilt=60):
    l = f.landmark.astype(np.int)
    left_eye = l[0]
    right_eye = l[1]
    nose = l[2]
    left_lip = l[3]
    right_lip = l[4]

    # 2D image points. If you change the image, you need to change vector
    image_points = np.array([
        nose,  # Nose tip
        np.array((((right_lip[0] - left_lip[0]) / 2 + left_lip[0]), f.bbox[3])),  # Chin
        left_eye,  # Left eye left corner
        right_eye,  # Right eye right corner
        left_lip,  # Left Mouth corner
        right_lip  # Right mouth corner
    ], dtype="double")

    # 3D model points.
    model_points = np.array([
        (0.0, 0.0, 0.0),  # Nose tip
        (0.0, -330.0, -65.0),  # Chin
        (-225.0, 170.0, -135.0),  # Left eye left corner
        (225.0, 170.0, -135.0),  # Right eye right corne
        (-150.0, -150.0, -125.0),  # Left Mouth corner
        (150.0, -150.0, -125.0)  # Right mouth corner

    ])

    # Camera internals
    height, width = frame.shape[:2]
    camera_matrix = np.array(
        [[width, 0, width / 2],
         [0, width, height / 2],
         [0, 0, 1]], dtype="double"
    )

    dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
    (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix,
                                                                  dist_coeffs)

    rmat = cv2.Rodrigues(rotation_vector)[0]  # rotation matrix

    roll, pitch, yaw = rotationMatrixToEulerAngles(rmat)
    # roll = 180 - round(abs(math.degrees(roll)))
    up_down = round(abs(math.degrees(pitch)))
    left_right = 180 - round(abs(math.degrees(yaw)))
    print(roll, up_down, left_right, '\n')
    return left_right > max_horizontal_tilt or left_right < min_horizontal_tilt or up_down > max_vertical_tilt or up_down < min_vertical_tilt
