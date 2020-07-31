# https://github.com/anilsathyan7/Portrait-Segmentation

# Import the packages
from tensorflow.keras.layers import Input, Conv2D, Add, MaxPool2D, Conv2DTranspose, PReLU, Lambda
from tensorflow.keras.layers import concatenate
from tensorflow.keras.layers import DepthwiseConv2D, SeparableConv2D
from tensorflow.keras.models import Model
import tensorflow as tf
import cv2
import numpy as np


def bilinear_resize(x, rsize):
    return tf.image.resize(x, [rsize, rsize])


def encode_bottleneck(x, proj_ch, out_ch, strides=1, dilation=1, separable=True, depthwise=True, preluop=False,
                      pool=False):
    x = PReLU(shared_axes=[1, 2])(x)
    y = Conv2D(filters=proj_ch, kernel_size=strides, strides=strides, padding='same')(x)
    y = PReLU(shared_axes=[1, 2])(y)

    if separable:

        if depthwise:
            y = SeparableConv2D(filters=proj_ch, kernel_size=3, strides=1, padding='same')(y)
            y = PReLU(shared_axes=[1, 2])(y)
            y = DepthwiseConv2D(kernel_size=3, padding='same')(y)
        else:
            y = SeparableConv2D(filters=proj_ch, kernel_size=5, strides=1, padding='same')(y)
    else:
        y = Conv2D(filters=out_ch, kernel_size=3, dilation_rate=dilation, strides=1, padding='same')(y)

    y = PReLU(shared_axes=[1, 2])(y)
    y = Conv2D(filters=out_ch, kernel_size=1, strides=1, padding='same')(y)

    if pool:
        m = MaxPool2D((2, 2), padding='same')(x)
        if m.shape[-1] != 128:
            x = Conv2D(filters=out_ch, kernel_size=1, strides=1, padding='same')(m)
        else:
            x = m
        z = Add()([x, y])
        return z, m

    z = Add()([x, y])

    if preluop:
        return z, x

    return z


def decode_bottleneck(x, res1, res2, proj_ch1, out_ch, proj_ch2, strides=1, rsize=32, pconv=True):
    x = PReLU(shared_axes=[1, 2])(x)
    y = Conv2D(filters=proj_ch1, kernel_size=strides, strides=strides, padding='same')(x)
    y = PReLU(shared_axes=[1, 2])(y)

    y = Conv2DTranspose(filters=8, kernel_size=3, strides=2, padding='same')(y)

    y = PReLU(shared_axes=[1, 2])(y)
    y = Conv2D(filters=out_ch, kernel_size=1, strides=1, padding='same')(y)

    x = Conv2D(filters=out_ch, kernel_size=1, strides=1, padding='same')(x)
    r = Add()([x, res1])
    x = Lambda(lambda r: bilinear_resize(r, rsize))(r)

    z = Add()([x, y])
    z = PReLU(shared_axes=[1, 2])(z)
    if pconv:
        z = concatenate([z, res2])
    b = Conv2D(filters=proj_ch2, kernel_size=strides, strides=strides, padding='same')(z)
    b = PReLU(shared_axes=[1, 2])(b)
    b = Conv2D(filters=proj_ch2, kernel_size=3, strides=1, padding='same')(b)
    b = PReLU(shared_axes=[1, 2])(b)
    b = Conv2D(filters=out_ch, kernel_size=1, strides=1, padding='same')(b)

    if pconv == True:
        z = Conv2D(filters=out_ch, kernel_size=1, strides=1, padding='same')(z)

    c = Add()([z, b])

    return c


def slim_net():
    # Initial spatial phase [Reduces input by a factor 1/4]
    input = Input(shape=(512, 512, 3), name='ip')
    x = Conv2D(filters=8, kernel_size=2, strides=2, padding='valid')(input)
    x = PReLU(shared_axes=[1, 2])(x)
    x = Conv2D(filters=32, kernel_size=2, strides=2, padding='valid')(x)

    b1, r1 = encode_bottleneck(x, proj_ch=16, out_ch=64, strides=2, separable=True, depthwise=True, pool=True)
    b2, p1 = encode_bottleneck(b1, proj_ch=16, out_ch=64, strides=1, separable=True, depthwise=True, preluop=True,
                               pool=False)
    b3 = encode_bottleneck(b2, proj_ch=16, out_ch=64, strides=1, separable=True, depthwise=True, pool=False)
    b4, r2 = encode_bottleneck(b3, proj_ch=32, out_ch=128, strides=2, separable=True, depthwise=True, pool=True)

    b5, p2 = encode_bottleneck(b4, proj_ch=16, out_ch=128, strides=1, separable=True, depthwise=True, preluop=True,
                               pool=False)
    b6 = encode_bottleneck(b5, proj_ch=16, out_ch=128, strides=1, separable=True, depthwise=True, pool=False)
    b7 = encode_bottleneck(b6, proj_ch=16, out_ch=128, strides=1, separable=True, depthwise=True, pool=False)
    b8 = encode_bottleneck(b7, proj_ch=16, out_ch=128, strides=1, separable=True, depthwise=True, pool=False)

    b9, r3 = encode_bottleneck(b8, proj_ch=16, out_ch=128, strides=2, separable=True, depthwise=True, pool=True)
    b10 = encode_bottleneck(b9, proj_ch=8, out_ch=128, strides=1, separable=True, depthwise=True, pool=False)
    b11 = encode_bottleneck(b10, proj_ch=8, out_ch=128, strides=1, dilation=2, separable=False, depthwise=False,
                            pool=False)  # dil -2
    b12 = encode_bottleneck(b11, proj_ch=8, out_ch=128, strides=1, separable=True, depthwise=False, pool=False)
    b13 = encode_bottleneck(b12, proj_ch=8, out_ch=128, strides=1, dilation=4, separable=False, depthwise=False,
                            pool=False)  # dil -4
    b14 = encode_bottleneck(b13, proj_ch=8, out_ch=128, strides=1, separable=True, depthwise=True, pool=False)
    b15 = encode_bottleneck(b14, proj_ch=8, out_ch=128, strides=1, dilation=8, separable=False, depthwise=False,
                            pool=False)  # dil -8
    b16 = encode_bottleneck(b15, proj_ch=8, out_ch=128, strides=1, separable=True, depthwise=True, pool=False)
    b17 = encode_bottleneck(b16, proj_ch=8, out_ch=128, strides=1, dilation=2, separable=False, depthwise=False,
                            pool=False)  # dil -2
    b18 = encode_bottleneck(b17, proj_ch=8, out_ch=128, strides=1, separable=True, depthwise=False, pool=False)
    b19 = encode_bottleneck(b18, proj_ch=8, out_ch=128, strides=1, dilation=4, separable=False, depthwise=False,
                            pool=False)  # dil -4
    b20 = encode_bottleneck(b19, proj_ch=8, out_ch=128, strides=1, separable=True, depthwise=True, pool=False)
    b21 = encode_bottleneck(b20, proj_ch=8, out_ch=128, strides=1, dilation=8, separable=False, depthwise=False,
                            pool=False)  # dil -8

    b22 = encode_bottleneck(b21, proj_ch=4, out_ch=128, strides=1, separable=False, depthwise=False,
                            pool=False)  # dil -1

    d1 = decode_bottleneck(b22, res1=r3, res2=p2, proj_ch1=8, proj_ch2=8, out_ch=128, strides=1, rsize=32, pconv=True)
    d2 = decode_bottleneck(d1, res1=r2, res2=p1, proj_ch1=8, proj_ch2=4, out_ch=64, strides=1, rsize=64, pconv=True)
    d3 = decode_bottleneck(d2, res1=r1, res2=None, proj_ch1=4, proj_ch2=4, out_ch=32, strides=1, rsize=128, pconv=False)

    pout1 = PReLU(shared_axes=[1, 2])(d3)
    cout1 = Conv2DTranspose(filters=8, kernel_size=2, strides=2, padding='same')(pout1)  # output size: 256
    pout2 = PReLU(shared_axes=[1, 2])(cout1)
    cout2 = Conv2DTranspose(filters=2, kernel_size=2, strides=2, padding='same')(pout2)  # output size: 512

    model = Model(inputs=input, outputs=cout2)
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])  # Ensure you have sparse labels

    return model


def __load_model():
    model = slim_net()
    model_path = 'fipu_face/segmentation/models/slim_net/slim_net.h5'
    model.load_weights(model_path)
    return model


__model = __load_model()


def portrait_segmentation(frame):
    img = cv2.resize(frame, (512, 512))
    # Perform batch prediction and obtain masks
    input = np.float32([np.array(img)]) / 255.0
    result = __model.predict(input)
    argmax = np.argmax(result, axis=3)
    output = list(argmax[..., np.newaxis] * input)
    img = output[0].squeeze()
    img = img.astype('float32')
    img = img[:, :, ::-1].copy()
    img = cv2.resize(img, (frame.shape[1], frame.shape[0]))

    # cv2 image -> (img * 255).astype('uint8')[:, :, ::-1]
    return img

