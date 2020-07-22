from fipu_face.segregation.slim_net import segregate_portrait
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os


# frame = cv2.imread('imgs/new/l2.jpg')
# frame = cv2.imread('imgs/new/mil.jpg')
# frame = cv2.imread('imgs/new/msk.jpg')
# frame = cv2.imread('imgs/new/w.jpg')
# frame = cv2.imread('imgs/new/m.jpg')
# frame = cv2.imread('imgs/n7.jpg')
def get_non_white_bg_pct(frame):
    img = segregate_portrait(frame)

    frame = frame.astype('float32')

    img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 0, 255, cv2.THRESH_BINARY)

    m1 = cv2.bitwise_or(frame.astype('uint8'), frame.astype('uint8'), mask=cv2.bitwise_not(mask.astype('uint8')))
    m1_gray = cv2.cvtColor(m1, cv2.COLOR_BGR2GRAY)

    total = frame.shape[0] * frame.shape[1]
    background = cv2.countNonZero(m1_gray)

    # _, m2 = cv2.threshold(m1_gray, 190, 255, cv2.THRESH_BINARY)

    # Every color except white
    # lower_white = np.array([0, 42, 0], dtype=np.uint8)
    # upper_white = np.array([179, 255, 255], dtype=np.uint8)

    hsv = cv2.cvtColor(m1, cv2.COLOR_BGR2HSV)

    # Lower and upper bound of the acceptable white color
    lower_white = np.array([0, 0, 0])
    upper_white = np.array([255, 23, 255])
    # White background mask
    wb = cv2.inRange(hsv, lower_white, upper_white)

    # plt.imshow(wb)
    # plt.imshow(hsv)
    # plt.imshow(m1_gray)
    # plt.imshow(frame.astype('uint8'))

    # Portion of non-white background compared to the total area of the background
    return (total - cv2.countNonZero(wb)) / background * 100


# Testing
if __name__ == '__main__':
    path = 'imgs/'
    vals = {'imgs/': [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0],
            'imgs/new/': [1, 1, 1, 1, 1, 1, 1, 1, 1]}

    for i, j in zip(sorted([f for f in os.listdir(path) if f.split('.')[-1] in ['jpg', 'jpeg', 'png']]), vals[path]):
        im = cv2.imread(path + i)
        nwp = round(get_non_white_bg_pct(im), 2)
        print(i, nwp, (nwp <= 1.5) == j)

