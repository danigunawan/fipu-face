import insightface
import cv2
import numpy as np


# https://github.com/deepinsight/insightface/tree/master/RetinaFace
# RetinaFace and ArcFace

def __load_model():
    fa = insightface.app.FaceAnalysis()
    fa.prepare(-1)
    return fa


__model = __load_model()


def detect_faces(frame, thresh=0.1, scale=1):
    faces = __model.get(frame,
                        det_thresh=thresh,
                        det_scale=scale
                        )
    return faces
