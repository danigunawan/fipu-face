import insightface

# https://github.com/deepinsight/insightface/tree/master/RetinaFace
# RetinaFace and ArcFace


def __load_model():
    # No recognition model and no gender-age model
    # Also using the smallest model to speed up the detection
    fa = insightface.app.FaceAnalysis(det_name='retinaface_mnet025_v2', rec_name=None, ga_name=None)
    fa.prepare(-1)
    return fa


__model = __load_model()


def detect_faces(frame, thresh=0.89, scale=1):
    faces = __model.get(frame,
                        det_thresh=thresh,
                        det_scale=scale
                        )
    return faces
