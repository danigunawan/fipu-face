from fipu_face.fipu_face import *


def draw_predict_info(frame, msg):
    info = {'Message': msg}

    # text_list = [k + ':  '+ v for k,v in zip(info.keys(), info.values())]
    text_list = [v for k, v in zip(info.keys(), info.values())]

    height, width = frame.shape[:2]
    fontScale = width / 1000
    COLOR_RED = (0, 0, 255)
    for i, line in enumerate(text_list):
        cv2.putText(frame, line, (10, (i + 1) * int(30 * fontScale)),
                    cv2.FONT_HERSHEY_SIMPLEX, fontScale, COLOR_RED, 2)


def detect_on_img(frame):
    # start_time = time.time()

    try:
        frame = detect(frame, imc=ImgX)

        return frame
    except ImageException as e:
        print(e.message)
        draw_predict_info(frame, e.message)
        return frame


def detect_camera():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("no frame")
            break

        frame = detect_on_img(frame)
        # faces = rf.detect_faces(frame, scale=calc_scale(frame))
        # if len(faces)>0:
        #     is_not_looking_straight(frame, faces[0])
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    detect_camera()
