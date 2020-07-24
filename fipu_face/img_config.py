# https://mup.gov.hr/UserDocsImages/BannerZona/Upute%20za%20fotografije%202013%20(2).pdf
# 30x35
# w = 30
# h = 35
# sirina glave: 15-21.4
# visina glave: 24.5-28 (beba(<11 god): 17.5-28)

# 35x45
# w = 35
# h = 45
# sirina glave: 17.5-25
# visina glave: 31.5-36 (beba(<11 god): 22.5-36)

# from fipu_face.facial_landmarks.emotion import *

IMG_FORMAT_X = 'x'
IMG_FORMAT_30x35_11Plus = '30x35_11Plus'
IMG_FORMAT_30x35_11 = '30x35_11'
IMG_FORMAT_35x45_11Plus = '35x45_11Plus'
IMG_FORMAT_35x45_11 = '35x45_11'


# Image config class that describes the cropping properties of the image
class ImgConfig:
    dpi = 300

    def __init__(self, width, height, hw_range, hh_range, blur_threshold=30,
                 max_non_white_bg_pct=1.5):  # , emotions=tuple([EMOTION_NEUTRAL]), glasses=False):
        self.w = width
        self.h = height
        # Head width and height ranges
        self.hw_range = hw_range
        self.hh_range = hh_range

        # Blur should be adjusted for each sizeX
        self.blur_threshold = blur_threshold

        # Maximum percentage of non white background. Should be adjusted for each size
        self.max_non_white_bg_pct = max_non_white_bg_pct

        # self.allowed_emotions = emotions
        # self.glasses = glasses


Img30x35_11Plus = ImgConfig(width=30,
                            height=35,
                            hw_range=(15, 21.4),
                            hh_range=(24.5, 28))

Img30x35_11 = ImgConfig(width=30,
                        height=35,
                        hw_range=(15, 21.4),
                        hh_range=(17.5, 28))

Img35x45_11Plus = ImgConfig(width=35,
                            height=45,
                            hw_range=(17.5, 25),
                            hh_range=(31.5, 36))

Img35x45_11 = ImgConfig(width=35,
                        height=45,
                        hw_range=(17.5, 25),
                        hh_range=(22.5, 36))

ImgX = ImgConfig(width=18.6,
                 height=25.4,
                 hw_range=(14, 15),
                 hh_range=(16, 17),
                 blur_threshold=30,
                 max_non_white_bg_pct=2)

"""
# V2 of the dimensions for x-ica
ImgX = ImgConfig(width=25,
                 height=30,
                 hw_range=(16, 17),
                 hh_range=(18, 20),
                 blur_threshold=30,
                 max_non_white_bg_pct=1.5)
"""

"""
# The initial version of dimensions for x-ica
ImgX = ImgConfig(width=25,
                 height=30,
                 hw_range=(12.5, 13.5),
                 hh_range=(15.5, 16.5))  # ,
                # emotions=(EMOTION_NEUTRAL, EMOTION_HAPPY),
                # glasses=False)
"""

__all_formats = {
    IMG_FORMAT_X: ImgX,
    IMG_FORMAT_30x35_11Plus: IMG_FORMAT_30x35_11Plus,
    IMG_FORMAT_30x35_11: IMG_FORMAT_30x35_11,
    IMG_FORMAT_35x45_11Plus: IMG_FORMAT_35x45_11Plus,
    IMG_FORMAT_35x45_11: IMG_FORMAT_35x45_11
}


# Get format by name
def get_format(format_name):
    return __all_formats.get(format_name, ImgX)
