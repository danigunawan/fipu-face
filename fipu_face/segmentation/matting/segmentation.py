from pymatting import *
import cv2
import time
# from fipu_face.segregation.slim_net import segregate_portrait
from fipu_face.segregation.models.munet import segregate_portrait
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
import os


def create_mask(im_path):
    frame = cv2.imread(im_path)
    img = segregate_portrait(frame)

    img[img>0] = 255
    cv2.imwrite(im_path.split('.')[0] + '_mask.' + im_path.split('.')[-1], img)


def fix_trimap(trimap, threshold=0.1):
    is_bg = trimap < threshold
    is_fg = trimap > 1.0 - threshold
    fixed = 0.5 * np.ones_like(trimap)
    fixed[is_fg] = 1
    fixed[is_bg] = 0
    return fixed


def create_trimap(image, size, erosion=False):
    """
    This function creates a trimap based on simple dilation algorithm
    Inputs [4]: a binary image (black & white only), name of the image, dilation pixels
                the last argument is optional; i.e., how many iterations will the image get eroded
    Output    : a trimap
    """
    row = image.shape[0]
    col = image.shape[1]
    pixels = 2 * size + 1  ## Double and plus 1 to have an odd-sized kernel
    kernel = np.ones((pixels, pixels), np.uint8)  ## Pixel of extension I get

    if erosion is not False:
        erosion = int(erosion)
        erosion_kernel = np.ones((3, 3), np.uint8)  ## Design an odd-sized erosion kernel
        image = cv2.erode(image, erosion_kernel, iterations=erosion)  ## How many erosion do you expect
        image = np.where(image > 0, 255, image)  ## Any gray-clored pixel becomes white (smoothing)
        # Error-handler to prevent entire foreground annihilation
        if cv2.countNonZero(image) == 0:
            print("ERROR: foreground has been entirely eroded")
            # sys.exit()

    dilation = cv2.dilate(image, kernel, iterations=1)

    dilation = np.where(dilation == 255, 127, dilation)  ## WHITE to GRAY
    dilation = np.where(dilation != 127, 0, dilation)  ## Smoothing
    remake = np.where(image > 127, 200, dilation)  ## mark the tumor inside GRAY

    remake = np.where(remake < 127, 0, remake)  ## Embelishment
    remake = np.where(remake > 200, 0, remake)  ## Embelishment
    remake = np.where(remake == 200, 255, remake)  ## GRAY to WHITE

    #############################################
    # Ensures only three pixel values available #
    # TODO: Optimization with Cython            #
    #############################################
    for i in range(0, row):
        for j in range(0, col):
            if remake[i, j] != 0 and remake[i, j] != 255:
                remake[i, j] = 127
    return remake

"""
im_path = 'imgs/new/stock_female_1.jpg'
mask = cv2.imread(im_path.split('.')[0] + '_mask.' + im_path.split('.')[-1], cv2.IMREAD_GRAYSCALE)
trimap = create_trimap(mask, 20, 10)
cv2.imwrite(im_path.split('.')[0] + '_trimap.' + im_path.split('.')[-1], trimap)
"""


def do_seg(im_path, estimate_fn):
    scale = 1
    mask_path = im_path.split('.')[0] + '_mask.' + im_path.split('.')[-1]
    if not os.path.exists(mask_path):
        create_mask(im_path)

    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    trimap = create_trimap(mask, 50, 20)
    cv2.imwrite(im_path.split('.')[0] + '_trimap.' + im_path.split('.')[-1], trimap)

    image = load_image(im_path, "RGB", scale, "box")
    trimap = load_image(im_path.split('.')[0] + '_trimap.' + im_path.split('.')[-1], "GRAY", scale, "nearest")
    trimap = fix_trimap(trimap)
    # estimate alpha from image and trimap
    alpha = estimate_fn(image, trimap)

    # make gray background
    new_background = np.zeros(image.shape)
    new_background[:, :] = [1, 1, 1]
    # estimate foreground from image and alpha
    foreground, background = estimate_foreground_ml(image, alpha, return_background=True)
    # blend foreground with background and alpha
    new_image = blend(foreground, new_background, alpha)
    save_image(
        im_path.split('.')[0] + '_out' + estimate_fn.__name__.replace('estimate_alpha', '') + '.' + im_path.split('.')[
            -1], new_image)


if __name__ == '__main__':
    # im_path = 'imgs/new/test_m.png'
    # im_path = 'imgs/new/test_m1.png'
    # im_path = 'imgs/new/stock_female_1.jpg'
    # im_path = 'imgs/new/stock_female_2.jpg'
    # im_path = 'imgs/new/l2.jpg'
    # im_path = 'imgs/test3.png'
    im_path = 'imgs/new/aa5.png'
    do_seg(im_path, estimate_alpha_lkm)
    # do_seg(im_path, estimate_alpha_knn)
    # do_seg(im_path, estimate_alpha_rw)
    # do_seg(im_path, estimate_alpha_lbdm)
    # do_seg(im_path, estimate_alpha_cf)
