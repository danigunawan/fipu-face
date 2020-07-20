# Custom image exception class
class ImageException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

    def __call__(self, *args, **kwargs):
        a = args[0]


def raise_error(msg, tokens=None):
    if tokens:
        msg = msg.format(*tokens)
    raise ImageException(msg)


# All errors
NO_FACES_EXCEPTION = "Nije detektirano niti jedno lice"
TOO_MANY_FACES_EXCEPTION = "Detektirana je previše lica ({} lica)"

NO_LANDMARKS_EXCEPTION = "Nisu očitana sva obilježja lica (oči, nos, usta)"
PICTURED_TO_CLOSE_EXCEPTION = "Slikano preblizu ili nije centrirano.\nProstor:\n- Lijevo: {}\n- Desno: {}\n- Gore: {}\n- Dolje: {}"
TILTED_HEAD_EXCEPTION = "Glava je nakrivljena. Potrebno je gledati prema kameri"

BLURRY_IMAGE_EXCEPTION = "Slika je mutna"

BASE64_DECODING_EXCEPTION = "Invalid base64 encoded image"
BYTES_DECODING_EXCEPTION = "Invalid image bytes"
