from fer import FER

__detector = FER(mtcnn=True)

EMOTION_ANGRY = 'angry'
EMOTION_DISGUST = 'disgust'
EMOTION_FEAR = 'fear'
EMOTION_HAPPY = 'happy'
EMOTION_NEUTRAL = 'neutral'
EMOTION_SAD = 'sad'
EMOTION_SURPRISE = 'surprise'
EMOTION_NONE = "no emotion"


def detect_emotion(frame, f):
    w = frame.shape[1]
    h = frame.shape[0]

    left = f.bbox[0] - 50
    top = f.bbox[1] - 100
    right = f.bbox[2] + 50
    bottom = f.bbox[3] + 50

    frame = frame[int(max(top, 0)):int(min(bottom, h)), int(max(left, 0)):int(min(right, w))]
    if len(__detector.detect_emotions(frame)) > 0:
        return __detector.top_emotion(frame)[0]
    return EMOTION_NONE
