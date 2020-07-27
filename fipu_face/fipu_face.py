from fipu_face import retina_face as rf

import time
from fipu_face.utils import *
from fipu_face.img_utils import *
from exceptions.image_exception import *
from fipu_face.img_config import *
from fipu_face.segregation.segregation import get_non_white_bg_pct

# from fipu_face.facial_landmarks.emotion import *
# from fipu_face.facial_landmarks.glasses import has_glasses

# Maximum difference in percentage in elevation between both eyes (y axis)
# Sometimes the detections are not as accurate so that should be taken into consideration
MAX_EYES_Y_DIFF_PCT = 3

# Maximum percentage difference between left eye-nose : right eye-nose
# This helps to detect if the person is looking to the side
MAX_NOSE_EYES_DIST_DIFF_PCT = 9

# When testing, when true draw bounding box and landmarks
DRAW_MARKS = False


# Crops the face based on the image configuration
def crop_img(frame, f, imc, err):
    # Just add a little bit space around the bbox
    left = f.bbox[0] * 0.99
    top = f.bbox[1] * 0.99
    right = f.bbox[2] * 1.01
    bottom = f.bbox[3] * 1.01

    y = top
    h = bottom - top

    x = left
    w = right - left

    # Calculate the percentage that the head should have in the image
    # Eg. head should fill 80% of height and 60% of width
    # Here we take the minimum of width and height ranges because the detections never overestimate head size
    imw_pct = np.min(imc.hw_range) / imc.w
    imh_pct = np.min(imc.hh_range) / imc.h

    # Calculate the maximum percentage of head in the image
    max_i_h_pct = np.max(imc.hh_range) / imc.h

    # Calculate the percentage from the top of the head to the top of the image
    total_h_diff_pct = max_i_h_pct - imh_pct + (1 - max_i_h_pct)

    # Calculate pixes between top of the head and top of the image
    total_h_diff = total_h_diff_pct / imh_pct * h

    # Calculate the pixels between top of the head and maximum head range
    head_to_max = (max_i_h_pct - imh_pct) / (1 - imh_pct) * total_h_diff

    # Calculate bottom and top padding (they should be the same)
    pad_tb = (total_h_diff - head_to_max) / 2

    # Cropping top (y) is above the max head range + padding
    y_start = top - head_to_max - pad_tb
    # Cropping bottom (y) is bellow the face by adding padding
    y_end = bottom + pad_tb

    # Calculate the image height to which the image will be cropped
    i_h = y_end - y_start
    # Image width is proportional to that height based on the image confige dimensions
    i_w = i_h * (imc.w / imc.h)

    # Padding to left and right is calculated as (image width - face width) / 2
    pad_lr = abs(w - i_w) / 2
    # Add the calculated padding to the left and right side of the face
    x_start = x - pad_lr
    x_end = right + pad_lr

    # Testing purposes
    """
    print(imc.hh_range[0] / imc.h, h / i_h, imc.hh_range[1] / imc.h)
    print(imc.hw_range[0] / imc.w, w / i_w, imc.hw_range[1] / imc.w)

    print(imh_pct, h / i_h, imc.hh_range[0] / imc.h <= h / i_h <= imc.hh_range[1] / imc.h)
    print(imw_pct, w / (x_end - x_start), imc.hw_range[0] / imc.w <= w / (x_end - x_start) <= imc.hw_range[1] / imc.w)

    print(imc.w / imc.h, i_w / i_h)
    print(pad_tb / i_h, (1 - np.max(imc.hh_range) / imc.h) / 2)

    print("Ratio: ", imc.w / imc.h, i_w / i_h)
    """
    return __do_crop(frame, x_start, x_end, y_start, y_end, err)


# Does the cropping and raises the exception if the cropping points are not in the frame
def __do_crop(frame, x_start, x_end, y_start, y_end, err):
    h, w = frame.shape[:2]

    # Before cropping check if the copping points are not outside the frame
    if min(y_start, x_start) < 0 or x_end > w or y_end > h:
        # print(y_start, x_start, x_end, y_end, frame.shape[:2])
        s_i = [a < 0 for a in [x_start, y_start, w - x_end, h - y_end]]
        sides = [SIDES_STR[i] for i, a in enumerate(s_i) if a]
        err(PICTURED_TO_CLOSE_EXCEPTION, [', '.join(sides)], s_i)
        return frame

    # Crop the image
    frame = frame[int(y_start):int(y_end), int(x_start):int(x_end)]
    return frame


def check_face_alignment(frame, f, err):
    l = f.landmark.astype(np.int)
    # Should never happen, but just to make sure
    if len(l) < 5:
        err(NO_LANDMARKS_EXCEPTION)
        return
        # raise_error(NO_LANDMARKS_EXCEPTION)

    # Save the references to the landmarks
    left_eye = l[0]
    right_eye = l[1]
    nose = l[2]
    left_lip = l[3]
    right_lip = l[4]

    # Face width and height
    f_w = f.bbox[2] - f.bbox[0]
    f_h = f.bbox[3] - f.bbox[1]

    # Eyes should be leveled - at least within the MAX_EYES_Y_DIFF_PCT percentage
    eyes_tilt = abs(left_eye[1] - right_eye[1]) / f_h * 100

    if eyes_tilt > MAX_EYES_Y_DIFF_PCT:
        err(TILTED_HEAD_EXCEPTION, payload=left_eye[1] < right_eye[1])

    # Is the nose looking left or right?
    # Calculate the difference between the (left_eye-nose) and (right_eye-nose)
    l_n_e = abs(nose[0] - left_eye[0])
    r_n_e = abs(nose[0] - right_eye[0])
    # The percentage in differences between eyes and the nose should be less than MAX_NOSE_EYES_DIST_DIFF_PCT
    nose_tilt = abs(l_n_e - r_n_e) / f_w * 100

    # If the nose x position is smaller than the left eye x position or greater than the right eye y position
    # then the person is looking to the side, otherwise it still may be a slight head tilt to either side
    turns = [nose[0] < left_eye[0], nose[0] > right_eye[0], nose_tilt > MAX_NOSE_EYES_DIST_DIFF_PCT]
    if any(turns):
        is_left = turns[0]
        # If last error then make a guess about the turn
        # This is purely for error display purposes
        if not any(turns[:2]) and turns[2]:
            is_left = l_n_e < r_n_e

        err(TURNED_HEAD_EXCEPTION, payload=is_left)

    # mouth = (left_lip[1] + right_lip[1]) / 2
    # eyes = (left_eye[1] + right_eye[1]) / 2
    # print(np.mean(left_lip, right_lip))

    # print("Diff: ", nose[1] - eyes,  mouth - nose[1])
    # print("Eyes: ", eyes_tilt)
    # print("Nose: ", nose_tilt)


# Checks whether the image is blurry
# The blur value also depends on the image resolution,
# so each image configuration should have its own threshold
# Old method which is not very stable
def check_blur(frame, imc, err):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Calculate the blur
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    # print('Blur: {}'.format(round(blur, 3)))
    if blur < imc.blur_threshold:
        err(BLURRY_IMAGE_EXCEPTION)
        # raise_error(BLURRY_IMAGE_EXCEPTION)


def check_face_blur(frame, f, imc, err):
    left = f.bbox[0]
    top = f.bbox[1]
    right = f.bbox[2]
    bottom = f.bbox[3]

    h, w = frame.shape[:2]
    # Since the face can be outside the frame, the image would be empty with negative numbers
    # Also is it necessary to check for blur when the whole face is not in frame?
    face = frame[max(0, int(top)):min(int(bottom), h), min(0, int(left)):max(w, int(right))]

    h, w = face.shape[:2]
    # print(h, w)
    # Scale the head to the approx size to what it would be in the final crop
    # This way we get somewhat consistent results
    scale_y = (imc.hh_range[1] / INCH * imc.dpi) / h
    scale_x = w / h * scale_y * h / w
    img = cv2.resize(face, None, None, fx=scale_x, fy=scale_y)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = np.max(cv2.convertScaleAbs(cv2.Laplacian(img, cv2.CV_64F)))
    # print('Blur: {}'.format(round(blur, 3)))
    if blur < imc.blur_threshold:
        err(BLURRY_IMAGE_EXCEPTION)


# Ensures that only one faces is detected
def check_num_faces(faces, err):
    if len(faces) == 0:
        # raise_error(NO_FACES_EXCEPTION)
        err(NO_FACES_EXCEPTION)
        raise err
    elif len(faces) > 1:
        # raise_error(TOO_MANY_FACES_EXCEPTION, [len(faces)])
        err(TOO_MANY_FACES_EXCEPTION, [len(faces)])
        raise err


# Ensures that the background is white
def check_white_bg(frame, imc, err):
    try:
        non_white_pct = get_non_white_bg_pct(frame)
        # print('Non-white pct: {}'.format(round(non_white_pct, 3)))
        if non_white_pct > imc.max_non_white_bg_pct:
            err(NON_WHITE_BG_EXCEPTION)
    except Exception as e:
        # only occurs when the required tensorflow version is not installed
        print("Error while trying to detect background: ", e)


def detect_face(frame, err):
    # Detect the faces... images are scaled to the training resolution to speed up the detection
    faces = rf.detect_faces(frame, scale=calc_scale(frame))

    check_num_faces(faces, err)
    return faces[0]


def pre_process_check(frame):
    frame = alpha_to_white(frame)

    err = ImageException(frame)
    f = detect_face(frame, err)

    # print(f.det_score)

    # Testing: face box and landmark drawing
    # Need to draw before cropping because the landmarks have the position on the initial frame
    if DRAW_MARKS:
        draw_marks(frame, f)

    check_face_alignment(frame, f, err)
    return frame, f, err


# Detects and crop's the image if all checks are successful
def detect(frame, imcs=None):
    imcs = imcs or [ImgX]  # Default value

    # Do the pre checks which are irrelevant of the image size
    frame, f, err = pre_process_check(frame)
    frames = {}
    for imc in imcs:
        # Need to check before resizing and cropping
        # otherwise we would need to perform another detection
        check_face_blur(frame, f, imc, err)

        __frame = crop_img(frame, f, imc, err)
        __frame = scale_img(__frame, imc)

        # Check background of the final image
        check_white_bg(__frame, imc, err)

        # Testing: ellipse around the head
        if DRAW_MARKS:
            draw_ellipses(__frame, imc)

        frames[imc.name] = __frame

    if err.has_errors():
        draw_errors(err.image, f, err)
        raise err

    return frames if len(imcs) > 1 else frames[imcs[0].name]


# Shortcut method to crop the image and covert it back to the given format
def __do_detect(frame, img_formats, encoding):
    frames = detect(frame, [get_format(f) for f in img_formats])
    for img_fmt in frames.keys():
        frames[img_fmt] = convert_img(frames[img_fmt], encoding)
    return frames


# API method called when the file is uploaded using standard file upload
def get_from_file(file, img_formats, encoding):
    return __do_detect(cv2_read_img(file.read()), img_formats, encoding)


# API method called when the file is uploaded as a field in base64 format
def get_from_base64(uri, img_formats, encoding):
    # Just in case the uri contains base64 prefix, split and take the last part
    encoded_data = uri.split('base64,')[-1]
    img = cv2_read_img(base64.b64decode(encoded_data))
    return __do_detect(img, img_formats, encoding)


# API method called when the file is uploaded as a field in bytes format
def get_from_bytes(img_bytes, img_formats, encoding):
    return __do_detect(cv2_read_img(img_bytes), img_formats, encoding)


def draw_errors(frame, f, err):
    thickness = 2 * calc_thickness_scale(frame)

    if err.has_error(PICTURED_TO_CLOSE_EXCEPTION):
        draw_no_space(frame, f, err.get_payload(PICTURED_TO_CLOSE_EXCEPTION), COLOR_RED, thickness)

    if err.has_error(TURNED_HEAD_EXCEPTION):
        # Draw arrow to opposite direction to where the person face is rotated
        draw_head_turn(frame, f, not err.get_payload(TURNED_HEAD_EXCEPTION), COLOR_RED, thickness)

    if err.has_error(TILTED_HEAD_EXCEPTION):
        # Draw arrow to opposite direction to where the person is looking
        draw_head_tilt(frame, f, not err.get_payload(TILTED_HEAD_EXCEPTION), COLOR_RED, thickness)

    if err.has_error(NON_WHITE_BG_EXCEPTION):
        draw_non_white_bg(frame, f, COLOR_WHITE, thickness * 2)


"""
def check_face_emotion(frame, f, imc):
    emotion = detect_emotion(frame, f)
    if emotion not in imc.allowed_emotions:
        if emotion == EMOTION_NONE:
            raise ImageException(
                "Nemoguće očitati emociju. Maknite sve predmete koji sakrivaju lice (maska, ruke itd.)")
        else:
            raise ImageException(
                "Nedozvoljena emocija {}. Dozvoljene emocije: {}".format(emotion, imc.allowed_emotions))

def check_face_obstacles(frame, f, imc):
    if not imc.glasses and has_glasses(frame, f):
        raise ImageException("Nočale nisu dozvoljene.")
"""
