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

IMG_DPI = 300

IMG_FORMAT_X = 'x'
IMG_FORMAT_30x35_11Plus = '30x35_11Plus'
IMG_FORMAT_30x35_11 = '30x35_11'
IMG_FORMAT_35x45_11Plus = '35x45_11Plus'
IMG_FORMAT_35x45_11 = '35x45_11'


class ImgConfig:
    def __init__(self, width, height, hw_range, hh_range):
        self.w = width
        self.h = height
        self.hw_range = hw_range
        self.hh_range = hh_range


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

ImgX = ImgConfig(width=25,
                 height=30,
                 hw_range=(12.5, 13.5),
                 hh_range=(15.5, 16.5))

__all_formats = {
    IMG_FORMAT_X: ImgX,
    IMG_FORMAT_30x35_11Plus: IMG_FORMAT_30x35_11Plus,
    IMG_FORMAT_30x35_11: IMG_FORMAT_30x35_11,
    IMG_FORMAT_35x45_11Plus: IMG_FORMAT_35x45_11Plus,
    IMG_FORMAT_35x45_11: IMG_FORMAT_35x45_11
}


def get_format(format_name):
    return __all_formats.get(format_name, ImgX)
