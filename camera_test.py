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

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    detect_camera()



"""
# -2.425893332189294 -0.8035449188888781 -3.0457305710674603
# -2.047113726328204 -1.1516732427643563 0.0589255248789424

# l -3.1177383558028877 0.7446308736302729 3.101381330199983
# j -3.1094804975807544 -0.9253293392235616 -2.798527625382971

# j -178.16010898961642 -53.017465797139344 -160.34382178521255
# l -178.63324941356205 42.66420635415398 177.69606088112818


r_yaw, r_roll, r_pitch = euler_matrix(rotation_vector)
# calculate head rotation in degrees
yaw = 180 - 180 * r_yaw / math.pi
pitch = 180 * r_pitch / math.pi
roll = 180 - abs(180 * r_roll / math.pi)

# looking straight ahead wraps at -180/180, so make the range smooth
pitch = np.sign(pitch) * 180 - pitch
print(yaw, pitch, roll)  # l2 -174.5075072561355 -133.96026749848522 -138.99344948337438
# j: -160.34382178521258 -126.98253420286065 -178.16010898961642
# l: 177.69606088112818 137.33579364584602 -178.63324941356205
# the yaw angle must be in the -25..25 range

print('pt2')
r_yaw, r_roll, r_pitch = euler_matrix(rotation_vector)
# calculate head rotation in degrees
yaw = 180 * r_pitch / math.pi
pitch = 180 * r_roll / math.pi
roll = 180 * r_yaw / math.pi

# looking straight ahead wraps at -180/180, so make the range smooth
pitch = np.sign(pitch) * 180 - pitch
print(yaw, pitch, roll)  # l2 -174.5075072561355 -133.96026749848522 -138.99344948337438

# j -53.017465797139344 -1.8398910103835817 -160.34382178521258
# l 42.66420635415399 -1.366750586437945 177.69606088112818

# the pitch angle must be in the -10..10 range
if -25 <= yaw <= 25 and -10 <= pitch <= 10:
    print("no tilt")

# Project a 3D point (0, 0, 1000.0) onto the image plane.
# We use this to draw a line sticking out of the nose


(nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 500.0)]), rotation_vector, translation_vector,
                                                 camera_matrix, dist_coeffs)

for p in image_points:
    cv2.circle(im, (int(p[0]), int(p[1])), 3, (0, 0, 255), -1)

p1 = (int(image_points[0][0]), int(image_points[0][1]))
p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))

cv2.line(im, p1, p2, (255, 0, 0), 2)

# Display image
cv2.imshow("Output", im)
cv2.waitKey(0)
"""
