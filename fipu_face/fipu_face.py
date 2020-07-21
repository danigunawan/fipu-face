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
MAX_EYES_Y_DIFF_PCT = 5

# Maximum percentage difference between left eye-nose : right eye-nose
# This helps to detect if the person is looking to the side
MAX_NOSE_EYES_DIST_DIFF_PCT = 10

# Maximum percentage of non white background
MAX_NON_WHITE_BG_PCT = 3


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
        sides = [SIDES_STR[i] for i, a in enumerate([x_start, w - x_end, y_start, h - y_end]) if a < 0]
        print(sides, [x_start, w - x_end, y_start, h - y_end])
        err(PICTURED_TO_CLOSE_EXCEPTION, [', '.join(sides)])
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

    # print("Eyes: ", eyes_tilt, "Nose-Eyes: ", nose_tilt)

    # Is the nose looking left or right?
    # Calculate the difference between the (left_eye-nose) and (right_eye-nose)
    # The percentage in differences between eyes and the nose should be less than MAX_NOSE_EYES_DIST_DIFF_PCT
    nose_tilt = abs(abs(nose[0] - left_eye[0]) - abs(nose[0] - right_eye[0])) / f_w * 100

    # If the nose x position is smaller than the left eye x position or greater than the right eye y position
    # then the person is looking to the side, otherwise it still may be a slight head tilt to either side
    if eyes_tilt > MAX_EYES_Y_DIFF_PCT or nose[0] < left_eye[0] or nose[0] > right_eye[
        0] or nose_tilt > MAX_NOSE_EYES_DIST_DIFF_PCT:
        err(TILTED_HEAD_EXCEPTION)
        # raise_error(TILTED_HEAD_EXCEPTION)

    # mouth = (left_lip[1] + right_lip[1]) / 2
    # eyes = (left_eye[1] + right_eye[1]) / 2
    # print(np.mean(left_lip, right_lip))

    # print("Diff: ", nose[1] - eyes,  mouth - nose[1])


# Checks whether the image is blurry
# The blur value also depends on the image resolution,
# so each image configuration should have its own threshold
def check_blur(frame, imc, err):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Calculate the blur
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    print('Blur: {}'.format(round(blur, 3)))
    if blur < imc.blur_threshold:
        err(BLURRY_IMAGE_EXCEPTION)
        # raise_error(BLURRY_IMAGE_EXCEPTION)


# Ensures that only one faces is detected
def check_num_faces(faces):
    if len(faces) == 0:
        raise_error(NO_FACES_EXCEPTION)
    elif len(faces) > 1:
        raise_error(TOO_MANY_FACES_EXCEPTION, [len(faces)])


# Ensures that the background is white
def check_white_bg(frame, err):
    try:
        non_white_pct = get_non_white_bg_pct(frame)
        print('White pct: {}'.format(round(non_white_pct, 3)))
        if non_white_pct > MAX_NON_WHITE_BG_PCT:
            err(NON_WHITE_BG)
    except Exception as e:
        print(e)


# Detects and crop's the image if all checks are successful
def detect(frame, imc=ImgX):
    frame = frame[:, :, :3]
    # start_time = time.time()
    # Detect the faces... images are scaled to the training resolution to speed up the detection
    faces = rf.detect_faces(frame, scale=calc_scale(frame))

    check_num_faces(faces)
    f = faces[0]
    # print(f.det_score)
    err = ImageException()

    check_face_alignment(frame, f, err)
    # check_face_emotion(frame, f, imc)
    # check_face_obstacles(frame, f, imc)

    frame = crop_img(frame, f, imc, err)
    frame = scale_img(frame, imc)

    # Blur should only be checked after cropping/scaling since it also depends on the resolution
    check_blur(frame, imc, err)

    check_white_bg(frame, err)

    # Testing: draws rectangle, landmarks and ellipse around the head
    if DRAW_MARKS:
        draw_marks(frame, f)
        draw_ellipses(frame, imc)

    # print("--- %s seconds ---" % (round(time.time() - start_time, 3)))

    if err.has_errors():
        raise err

    return frame


# Shortcut method to crop the image and covert it back to the given format
def __do_detect(frame, img_format=IMG_FORMAT_X, encoding=ENCODING_BASE64):
    frame = detect(frame, get_format(img_format))
    return convert_img(frame, encoding)


# API method called when the file is uploaded using standard file upload
def get_from_file(file, img_format=IMG_FORMAT_X, encoding=ENCODING_BASE64):
    return __do_detect(cv2_read_img(file.read()), img_format, encoding)


# API method called when the file is uploaded as a field in base64 format
def get_from_base64(uri, img_format=IMG_FORMAT_X, encoding=ENCODING_BASE64):
    # Just in case the uri contains base64 prefix, split and take the last part
    encoded_data = uri.split('base64,')[-1]
    img = cv2_read_img(base64.b64decode(encoded_data))
    return __do_detect(img, img_format, encoding)


# API method called when the file is uploaded as a field in bytes format
def get_from_bytes(img_bytes, img_format=IMG_FORMAT_X, encoding=ENCODING_BASE64):
    return __do_detect(cv2_read_img(img_bytes), img_format, encoding)


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
