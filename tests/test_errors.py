from fipu_face.fipu_face import *
import os

##############################
#   TESTING   IMAGE ERRORS   #
##############################

# Not all images are in this repo, but that wont cause problems with this script

IMG_ERRORS = {'1.jpg': [NON_WHITE_BG_EXCEPTION],
              'a.jpg': [NON_WHITE_BG_EXCEPTION],
              'b1.jpg': [BLURRY_IMAGE_EXCEPTION],
              'b2.jpg': [BLURRY_IMAGE_EXCEPTION, TILTED_HEAD_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'b3.jpg': [NO_FACES_EXCEPTION],
              'b4.jpg': [BLURRY_IMAGE_EXCEPTION, TURNED_HEAD_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'b5.jpg': [BLURRY_IMAGE_EXCEPTION, TILTED_HEAD_EXCEPTION, TURNED_HEAD_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'b6.jpg': [BLURRY_IMAGE_EXCEPTION, TURNED_HEAD_EXCEPTION],
              'b7.png': [BLURRY_IMAGE_EXCEPTION],
              'c1.png': [PICTURED_TO_CLOSE_EXCEPTION],
              'c2.png': [TURNED_HEAD_EXCEPTION, PICTURED_TO_CLOSE_EXCEPTION],
              'c3.png': [PICTURED_TO_CLOSE_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'c4.png': [PICTURED_TO_CLOSE_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'c5.png': [PICTURED_TO_CLOSE_EXCEPTION],
              'd.jpg': [NON_WHITE_BG_EXCEPTION],
              'd1.png': [NON_WHITE_BG_EXCEPTION],
              'd2.png': [PICTURED_TO_CLOSE_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'e.jpg': [NON_WHITE_BG_EXCEPTION],
              'e1.jpg': [NON_WHITE_BG_EXCEPTION],
              'g2.jpg': [NON_WHITE_BG_EXCEPTION],
              'g3.jpg': [PICTURED_TO_CLOSE_EXCEPTION],
              'g4.jpg': [TURNED_HEAD_EXCEPTION, PICTURED_TO_CLOSE_EXCEPTION],
              'g5.jpg': [TILTED_HEAD_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'g6.jpg': [NON_WHITE_BG_EXCEPTION],
              'j.jpg': [TILTED_HEAD_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'l3.jpg': [NON_WHITE_BG_EXCEPTION],
              'm.jpg': [NON_WHITE_BG_EXCEPTION],
              'mil1.png': [NON_WHITE_BG_EXCEPTION],
              'mil2.png': [NON_WHITE_BG_EXCEPTION],
              'mil3.jpg': [NON_WHITE_BG_EXCEPTION],
              'n.jpg': [NON_WHITE_BG_EXCEPTION],
              'n2.png': [NON_WHITE_BG_EXCEPTION],
              'n9.jpg': [NON_WHITE_BG_EXCEPTION],
              'n12.png': [NON_WHITE_BG_EXCEPTION],
              'n18.png': [NON_WHITE_BG_EXCEPTION],
              'n20.png': [PICTURED_TO_CLOSE_EXCEPTION],
              'n21.png': [NON_WHITE_BG_EXCEPTION],
              'n22.png': [NON_WHITE_BG_EXCEPTION],
              'n24.png': [NON_WHITE_BG_EXCEPTION],
              'n28.png': [NON_WHITE_BG_EXCEPTION],
              'r1.jpg': [BLURRY_IMAGE_EXCEPTION],
              'r2.jpg': [NON_WHITE_BG_EXCEPTION],
              'r3.jpg': [NON_WHITE_BG_EXCEPTION],
              'r4.jpg': [NON_WHITE_BG_EXCEPTION],
              'r5.jpg': [BLURRY_IMAGE_EXCEPTION, TURNED_HEAD_EXCEPTION],
              'r6.jpg': [BLURRY_IMAGE_EXCEPTION, PICTURED_TO_CLOSE_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'r9.jpg': [NON_WHITE_BG_EXCEPTION],
              'r10.jpg': [BLURRY_IMAGE_EXCEPTION],
              'r11.jpg': [NON_WHITE_BG_EXCEPTION],
              'r12.jpg': [PICTURED_TO_CLOSE_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'r13.jpg': [NON_WHITE_BG_EXCEPTION],
              'r14.png': [BLURRY_IMAGE_EXCEPTION, TILTED_HEAD_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'r15.png': [BLURRY_IMAGE_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'r16.png': [BLURRY_IMAGE_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'r17.png': [BLURRY_IMAGE_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'r18.png': [BLURRY_IMAGE_EXCEPTION],
              'r19.png': [BLURRY_IMAGE_EXCEPTION, TILTED_HEAD_EXCEPTION, TURNED_HEAD_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'r20.png': [TILTED_HEAD_EXCEPTION],
              'r21.png': [PICTURED_TO_CLOSE_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'r22.png': [BLURRY_IMAGE_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'r23.png': [BLURRY_IMAGE_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'r24.png': [NON_WHITE_BG_EXCEPTION],
              'r25.png': [BLURRY_IMAGE_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'r27.png': [BLURRY_IMAGE_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'r29.png': [PICTURED_TO_CLOSE_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              'r30.png': [NON_WHITE_BG_EXCEPTION],
              'rm1.jpg': [BLURRY_IMAGE_EXCEPTION, NON_WHITE_BG_EXCEPTION, TILTED_HEAD_EXCEPTION],
              'rm2.jpg': [BLURRY_IMAGE_EXCEPTION],
              'rm4.png': [BLURRY_IMAGE_EXCEPTION],
              'rm6.png': [TILTED_HEAD_EXCEPTION],
              'rm7.png': [BLURRY_IMAGE_EXCEPTION],
              'rm8.png': [TILTED_HEAD_EXCEPTION],
              'rm10.png': [BLURRY_IMAGE_EXCEPTION],
              's1.jpg': [TURNED_HEAD_EXCEPTION, NON_WHITE_BG_EXCEPTION],
              's2.jpg': [TURNED_HEAD_EXCEPTION],
              'sig.jpg': [NO_FACES_EXCEPTION],
              'w.jpg': [NON_WHITE_BG_EXCEPTION]}

ACC_ERR_COUNT = {
    NO_FACES_EXCEPTION: 0,
    TOO_MANY_FACES_EXCEPTION: 0,
    NO_LANDMARKS_EXCEPTION: 0,
    PICTURED_TO_CLOSE_EXCEPTION: 0,
    TILTED_HEAD_EXCEPTION: 0,
    TURNED_HEAD_EXCEPTION: 0,
    BLURRY_IMAGE_EXCEPTION: 0,
    NON_WHITE_BG_EXCEPTION: 0,
}

NOT_ACC_ERR_COUNT = ACC_ERR_COUNT.copy()


def do_detect(stream_path):
    print(stream_path)
    frame = cv2.imread('imgs/' + stream_path, cv2.IMREAD_UNCHANGED)
    try:
        detect(frame, imc=ImgX)
    except ImageException as e:
        errs = e.get_error_codes()
        for er in errs:
            if stream_path not in IMG_ERRORS:
                NOT_ACC_ERR_COUNT[er] += 1
                print('Misclassified:', er)
                continue
            im_errs = IMG_ERRORS[stream_path]
            if er in im_errs:
                ACC_ERR_COUNT[er] += 1
            else:
                NOT_ACC_ERR_COUNT[er] += 1
                print('Misclassified:', er)
        # print(e.get_error_codes())


if __name__ == '__main__':
    files = [f for f in os.listdir('imgs/') if f.split('.')[-1] in ['jpg', 'jpeg', 'png']]

    for i in sorted_alphanumeric(files):
        do_detect(i)

    print('\n--- Accuracy ---\n')
    for err in ACC_ERR_COUNT:
        c, nc = ACC_ERR_COUNT[err], NOT_ACC_ERR_COUNT[err]
        count = c + nc
        if count > 0:
            acc = c / count
        else:
            acc = 1

        print("{}: {:.3f}".format(err, acc*100))
