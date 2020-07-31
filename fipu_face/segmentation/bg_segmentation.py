# from fipu_face.segmentation.models.slim_net import portrait_segmentation
from fipu_face.segmentation.models.portrait_net import portrait_segmentation
# from fipu_face.segmentation.models.munet import portrait_segmentation

import cv2
# import matplotlib.pyplot as plt
import numpy as np


TEST_BOUNDS = np.array([0, 60, 0]), np.array([255, 255, 255])
BOUNDS = np.array([0, 0, 180]), np.array([255, 150, 255])
OLD_BOUNDS = np.array([0, 0, 70]), np.array([255, 160, 255])


def increase_mask(mask, size):
    # Double and plus 1 to have an odd-sized kernel
    pixels = 2 * size + 1
    # Pixel of extension I get
    kernel = np.ones((pixels, pixels), np.uint8)

    dilation = cv2.dilate(mask, kernel, iterations=1)
    return dilation


def get_non_white_bg_pct(frame, bounds=OLD_BOUNDS):
    img = portrait_segmentation(frame)

    img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 0, 255, cv2.THRESH_BINARY)

    # Increase the mask to cover extra hair not detected properly by the detector
    mask = increase_mask(mask, 15)

    m1 = cv2.bitwise_or(frame.astype('uint8'), frame.astype('uint8'), mask=cv2.bitwise_not(mask.astype('uint8')))
    m1_gray = cv2.cvtColor(m1, cv2.COLOR_BGR2GRAY)

    background = cv2.countNonZero(m1_gray)
    if background == 0:
        return 0

    hsv = cv2.cvtColor(m1, cv2.COLOR_BGR2HSV)
    wb = cv2.inRange(hsv, bounds[0], bounds[1])
    # plt.imshow(wb)
    # plt.imshow(hsv)
    # plt.imshow(m1_gray)

    # Portion of non-white background compared to the total area of the background
    # return (total - cv2.countNonZero(wb)) / background * 100
    return 100 - cv2.countNonZero(wb) / background * 100


"""
def image_colorfulness(image):
    # split the image into its respective RGB components
    (B, G, R) = cv2.split(image.astype("float"))
    # compute rg = R - G
    rg = np.absolute(R - G)
    # compute yb = 0.5 * (R + G) - B
    yb = np.absolute(0.5 * (R + G) - B)
    # compute the mean and standard deviation of both `rg` and `yb`
    (rbMean, rbStd) = (np.mean(rg), np.std(rg))
    (ybMean, ybStd) = (np.mean(yb), np.std(yb))
    # combine the mean and standard deviations
    stdRoot = np.sqrt((rbStd ** 2) + (ybStd ** 2))
    meanRoot = np.sqrt((rbMean ** 2) + (ybMean ** 2))
    # derive the "colorfulness" metric and return it
    return stdRoot + (0.3 * meanRoot)


if __name__ == '__main__':
    # Testing color ranges
    import cv2
    import numpy as np
    import matplotlib.pyplot as plt

    get_non_white_bg_pct(cv2.imread('imgs/4297.png'))
    def color_spectar(lower=np.array([0, 0, 70]), upper=np.array([255, 100, 255])):
        cs = cv2.imread('fipu_face/segmentation/color_spectre.jpg')
        # cs = cv2.imread('imgs/4297.png')
        # cs = cv2.imread('imgs/mil1.png')
        # cs = cv2.imread('imgs/aaa.png')
        # cs = cv2.imread('imgs/n9.jpg')
        # cs = cv2.imread('imgs/s1.jpg')
        # plt.imshow(cs)
        hsv = cv2.cvtColor(cs, cv2.COLOR_BGR2HSV)

        plt.imshow(hsv[:, :, ::-1])
        wb = cv2.inRange(hsv, lower, upper)
        wb = np.expand_dims(wb, -1) / 255
        dst = cs * wb
        plt.imshow(dst.astype(np.uint8)[:, :, ::-1])


    color_spectar(np.array([0, 60, 0]), np.array([255, 255, 255]))

    color_spectar(np.array([0, 60, 0]), np.array([255, 130, 255]))

    # lower = [min blue, min white, min re
    color_spectar(np.array([0, 0, 0]), np.array([255, 60, 255]))

    sensitivity = 60
    color_spectar(np.array([0, 0, 255 - sensitivity]), np.array([255, sensitivity, 255]))

    # blue
    color_spectar(np.array([110, 50, 50]), np.array([130, 255, 255]))

    # cv2.imwrite('imgs/4296_1.png', cv2.cvtColor(cv2.imread('imgs/4297.png'), cv2.COLOR_BGR2GRAY))
    # plt.imshow(cv2.cvtColor(cv2.imread('imgs/4297.png'), cv2.COLOR_BGR2HLS)[:, :, ::-1])
    color_spectar(np.array([100, 100, 100]), np.array([255, 255, 255]))

    color_spectar(np.array([0, 0, 0]), np.array([60, 60, 60]))
    # hls
    # color_spectar(np.array([70, 80, 0]), np.array([255, 255, 255]))
    color_spectar(np.array([0, 70, 0]), np.array([255, 255, 100]))



    # Color HSV picker
    import cv2
    import sys
    import numpy as np


    def nothing(x):
        pass


    # Load in image
    image = cv2.imread('fipu_face/segmentation/color_spectre.jpg')

    # Create a window
    cv2.namedWindow('image')

    # create trackbars for color change
    cv2.createTrackbar('HMin', 'image', 0, 179, nothing)  # Hue is from 0-179 for Opencv
    cv2.createTrackbar('SMin', 'image', 0, 255, nothing)
    cv2.createTrackbar('VMin', 'image', 0, 255, nothing)
    cv2.createTrackbar('HMax', 'image', 0, 179, nothing)
    cv2.createTrackbar('SMax', 'image', 0, 255, nothing)
    cv2.createTrackbar('VMax', 'image', 0, 255, nothing)

    # Set default value for MAX HSV trackbars.
    cv2.setTrackbarPos('HMax', 'image', 179)
    cv2.setTrackbarPos('SMax', 'image', 255)
    cv2.setTrackbarPos('VMax', 'image', 255)

    # Initialize to check if HSV min/max value changes
    hMin = sMin = vMin = hMax = sMax = vMax = 0
    phMin = psMin = pvMin = phMax = psMax = pvMax = 0

    output = image
    wait_time = 33

    while (1):

        # get current positions of all trackbars
        hMin = cv2.getTrackbarPos('HMin', 'image')
        sMin = cv2.getTrackbarPos('SMin', 'image')
        vMin = cv2.getTrackbarPos('VMin', 'image')

        hMax = cv2.getTrackbarPos('HMax', 'image')
        sMax = cv2.getTrackbarPos('SMax', 'image')
        vMax = cv2.getTrackbarPos('VMax', 'image')

        # Set minimum and max HSV values to display
        lower = np.array([hMin, sMin, vMin])
        upper = np.array([hMax, sMax, vMax])

        # Create HSV Image and threshold into a range.
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        output = cv2.bitwise_and(image, image, mask=mask)

        # Print if there is a change in HSV value
        if ((phMin != hMin) | (psMin != sMin) | (pvMin != vMin) | (phMax != hMax) | (psMax != sMax) | (pvMax != vMax)):
            print("(hMin = %d , sMin = %d, vMin = %d), (hMax = %d , sMax = %d, vMax = %d)" % (
            hMin, sMin, vMin, hMax, sMax, vMax))
            phMin = hMin
            psMin = sMin
            pvMin = vMin
            phMax = hMax
            psMax = sMax
            pvMax = vMax

        # Display output image
        cv2.imshow('image', output)

        # Wait longer to prevent freeze for videos.
        if cv2.waitKey(wait_time) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
"""
