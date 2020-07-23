from fipu_face.fipu_face import *
import os

###############
#   TESTING   #
###############


def do_detect(stream_path):
    print(stream_path)
    frame = cv2.imread('imgs/' + stream_path)
    try:
        frame = detect(frame, imc=ImgX)
        cv2.imwrite('imgs/new/' + stream_path.replace('.jpg', '.jpg'), frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    except ImageException as e:
        cv2.imwrite('imgs/draw/' + stream_path, frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        print(e.get_error_codes())


if __name__ == '__main__':
    # """
    for i in sorted([f for f in os.listdir('imgs/') if f.split('.')[-1] in ['jpg', 'jpeg', 'png'] ]):
        do_detect(i)
    # """
    # do_detect('a.jpg')
