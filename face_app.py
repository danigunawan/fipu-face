from flask import Flask, request, jsonify

from fipu_face import fipu_face
from exceptions.image_exception import ImageException

app = Flask(__name__)
app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max image size

ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg')

IMG_FILE = 'img'
IMG_FILE64 = 'img64'
IMG_FILE_BYTES = 'img_bytes'
IMG_RESPONSE_ENCODING = 'resp_enc'
IMG_FMT = 'img_fmt'

ALLOWED_KEYS = (IMG_FILE, IMG_FILE64, IMG_FILE_BYTES)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_file():
    return IMG_FILE in request.files


def get_value(k):
    if request.form is not None and k in request.form:
        return request.form[k]
    if request.json is not None and k in request.json:
        return request.json[k]
    return None


def is_file64():
    return get_value(IMG_FILE64) is not None


def is_file_bytes():
    return get_value(IMG_FILE_BYTES) is not None


def get_response_encoding():
    return get_value(IMG_RESPONSE_ENCODING) or fipu_face.ENCODING_BASE64


def get_img_format():
    return get_value(IMG_FMT) or fipu_face.IMG_FORMAT_X


def create_response(img):
    resp = jsonify({'img': img})
    resp.status_code = 201
    return resp


def handle_file():
    file = request.files[IMG_FILE]
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        img = fipu_face.get_from_file(request.files[IMG_FILE], get_img_format(), get_response_encoding())
        return create_response(img)
    else:
        resp = jsonify({'message': 'Allowed file types are {0}'.format(ALLOWED_EXTENSIONS)})
        resp.status_code = 400
        return resp


@app.route('/crop-face', methods=['POST'])
def upload_file():
    if is_file():
        return handle_file()

    elif is_file64():
        file64 = get_value(IMG_FILE64)
        img = fipu_face.get_from_base64(file64, get_img_format(), get_response_encoding())
        return create_response(img)

    elif is_file_bytes():
        file_bytes = get_value(IMG_FILE_BYTES)
        img = fipu_face.get_from_bytes(file_bytes, get_img_format(), get_response_encoding())
        return create_response(img)

    resp = jsonify({'message': 'No image in the request. Use {} in either form or json request'.format(ALLOWED_KEYS)})
    resp.status_code = 400
    return resp


@app.errorhandler(ImageException)
def handle_image_exception(error):
    # Response returns a list of errors
    errors = error.to_dict()
    errors['img'] = fipu_face.convert_img(errors['img'], get_response_encoding())
    response = jsonify(errors)

    response.status_code = error.status_code
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="6000")
