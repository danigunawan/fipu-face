from fipu_face.segregation.slim_net import segregate_portrait
import cv2


def get_non_white_bg_pct(frame):
    img = segregate_portrait(frame)

    frame = frame.astype('float32')

    img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 0, 255, cv2.THRESH_BINARY)

    m1 = cv2.bitwise_or(frame.astype('uint8'), frame.astype('uint8'), mask=cv2.bitwise_not(mask.astype('uint8')))

    _, m2 = cv2.threshold(cv2.cvtColor(m1, cv2.COLOR_BGR2GRAY), 160, 255, cv2.THRESH_BINARY)
    final = cv2.bitwise_or(m1, m1, mask=cv2.bitwise_not(m2))
    final = cv2.cvtColor(final, cv2.COLOR_BGR2GRAY)

    return cv2.countNonZero(final) / (final.shape[0] * final.shape[1]) * 100
