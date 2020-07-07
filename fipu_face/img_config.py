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
