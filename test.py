from fipu_face.fipu_face import *
import os

###############
#   TESTING   #
###############


def do_detect(stream_path):
    print(stream_path)
    frame = cv2.imread('imgs/' + stream_path, cv2.IMREAD_UNCHANGED)
    try:
        frame = detect(frame, imc=ImgX)
        cv2.imwrite('imgs/new/' + stream_path.replace('.jpg', '.jpg'), frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    except ImageException as e:
        cv2.imwrite('imgs/draw/' + stream_path, frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        print(e.get_error_codes())


if __name__ == '__main__':
    files = [f for f in os.listdir('imgs/') if f.split('.')[-1] in ['jpg', 'jpeg', 'png']]

    for i in sorted_alphanumeric(files):
        do_detect(i)
