from fipu_face.fipu_face import *


###############
#   TESTING   #
###############

def do_detect(stream_path):
    print(stream_path)
    frame = cv2.imread('imgs/' + stream_path)
    try:
        frame = detect(frame, imc=ImgX)
        cv2.imwrite('imgs/new/' + stream_path.replace('.jpg', '.jpg'), frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        # success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        # print(len(buffer.tobytes())/(1024*1024), " MB")
    except ImageException as e:
        print(e.message)


if __name__ == '__main__':
    # """
    for i in ['1.jpg', 'a.jpg', 'j.jpg', 'm.jpg', 'w.jpg', 's1.jpg', 's2.jpg', 'l1.jpg', 'l2.jpg', 'l3.jpg', 'd.jpg', 'msk.jpg', 'e.jpg', 'e1.jpg',
              'g1.jpg', 'g2.jpg', 'g3.jpg', 'g4.jpg', 'g5.jpg', 'g6.jpg', ]:
        do_detect(i)
    # """
    # do_detect('a.jpg')
