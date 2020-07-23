# All errors
NO_FACES_EXCEPTION = "no_face"
TOO_MANY_FACES_EXCEPTION = "too_many_faces"

NO_LANDMARKS_EXCEPTION = "no_landmarks"
PICTURED_TO_CLOSE_EXCEPTION = "too_close"
TILTED_HEAD_EXCEPTION = "head_tilted"
TURNED_HEAD_EXCEPTION = "head_turned"

BLURRY_IMAGE_EXCEPTION = "image_blurry"

NON_WHITE_BG = "non_white_bg"

INVALID_IMAGE_FORMAT = "invalid_image_format"

INVALID_ENCODING_METHOD = "invalid_encoding_method"

DETAIL_MESSAGES = {

    NO_FACES_EXCEPTION: "Nije detektirano niti jedno lice",
    TOO_MANY_FACES_EXCEPTION: "Detektirana je previše lica ({} lica)",

    NO_LANDMARKS_EXCEPTION: "Nisu očitana sva obilježja lica (oči, nos, usta)",
    # PICTURED_TO_CLOSE_EXCEPTION: "Slikano preblizu ili nije centrirano.\nProstor:\n- Lijevo: {}\n- Desno: {}\n- Gore: {}\n- Dolje: {}",
    PICTURED_TO_CLOSE_EXCEPTION: "Slikano preblizu, malo se udaljite od kamere. Nedostaje mjesta - {}",
    TILTED_HEAD_EXCEPTION: "Glava je nakrivljena. Potrebno je gledati prema kameri",
    TURNED_HEAD_EXCEPTION: "Glava je zakrenuta. Potrebno je gledati prema kameri",

    BLURRY_IMAGE_EXCEPTION: "Slika je mutna",

    NON_WHITE_BG: "Pozadina mora biti svijetle bijele boje. Stanite ispred zida i upalite svjetlo",

    INVALID_IMAGE_FORMAT: "Invalid image format/encoding",
    INVALID_ENCODING_METHOD: "Encoding method {} not implemented. Use {}"

}

SIDES_STR = ['Lijevo', 'Gore', 'Desno', 'Dolje']


def raise_error(msg, tokens=None):
    e = ImageException()
    e(msg, tokens)
    raise e


# Custom image exception class
class ImageException(Exception):
    def __init__(self, image=None, status_code=400):
        Exception.__init__(self)
        # self.message = message
        # self.error_code = error_code
        # self.payload = payload
        self.status_code = status_code
        self.image = image
        self.errors = []
        # self.errors = [{'message': message, 'error_code': error_code}]

    @staticmethod
    def __bind_msg(msg, tokens=None):
        if msg in DETAIL_MESSAGES:
            detail = DETAIL_MESSAGES[msg]
        else:
            detail = msg

        if tokens:
            detail = detail.format(*tokens)
        return detail

    def __call__(self, msg, tokens=None, payload=None):
        err_msg = {'message': self.__bind_msg(msg, tokens), 'error_code': msg}
        if payload:
            err_msg['payload'] = payload
        self.errors.append(err_msg)

    def has_errors(self):
        return len(self.errors) > 0

    def to_dict(self):
        # rv = dict(self.payload or ())
        # rv['message'] = self.message
        # rv['error_code'] = self.error_code
        rv = dict()
        rv['errors'] = self.errors.copy()
        for er in rv['errors']:
            er.pop('payload')
        rv['img'] = self.image
        return rv

    def get_error_codes(self):
        return [e['error_code'] for e in self.errors]

    def has_error(self, err_code):
        return err_code in self.get_error_codes()

    def get_error(self, err_code):
        e = [er for er in self.errors if err_code == er['error_code']]
        if len(e) > 0:
            return e[0]
        return None

    def get_payload(self, err_code):
        e = self.get_error(err_code)
        if e and 'payload' in e:
            return e['payload']
        return None
