# Custom image exception class
class ImageException(Exception):

    def __init__(self, message, error_code='error', status_code=400):  # , payload=None):
        Exception.__init__(self)
        # self.message = message
        # self.error_code = error_code
        # self.payload = payload
        self.status_code = status_code
        self.errors = [{'message': message, 'error_code': error_code}]

    def to_dict(self):
        # rv = dict(self.payload or ())
        # rv['message'] = self.message
        # rv['error_code'] = self.error_code
        rv = dict()
        rv['errors'] = self.errors
        return rv


def raise_error(msg, tokens=None):
    if msg in DETAIL_MESSAGES:
        detail = DETAIL_MESSAGES[msg]
    else:
        detail = msg

    if tokens:
        detail = detail.format(*tokens)
    raise ImageException(message=detail, error_code=msg)


# All errors
NO_FACES_EXCEPTION = "no_face"
TOO_MANY_FACES_EXCEPTION = "too_many_faces"

NO_LANDMARKS_EXCEPTION = "no_landmarks"
PICTURED_TO_CLOSE_EXCEPTION = "too_close"
TILTED_HEAD_EXCEPTION = "head_tilted"

BLURRY_IMAGE_EXCEPTION = "image_blurry"

INVALID_IMAGE_FORMAT = "invalid_image_format"

INVALID_ENCODING_METHOD = "invalid_encoding_method"

DETAIL_MESSAGES = {
    NO_FACES_EXCEPTION: "Nije detektirano niti jedno lice",
    TOO_MANY_FACES_EXCEPTION: "Detektirana je previše lica ({} lica)",

    NO_LANDMARKS_EXCEPTION: "Nisu očitana sva obilježja lica (oči, nos, usta)",
    PICTURED_TO_CLOSE_EXCEPTION: "Slikano preblizu ili nije centrirano.\nProstor:\n- Lijevo: {}\n- Desno: {}\n- Gore: {}\n- Dolje: {}",
    TILTED_HEAD_EXCEPTION: "Glava je nakrivljena. Potrebno je gledati prema kameri",

    BLURRY_IMAGE_EXCEPTION: "Slika je mutna",

    INVALID_IMAGE_FORMAT: "Invalid image format/encoding",
    INVALID_ENCODING_METHOD: "Encoding method {} not implemented. Use {}"

}
