from flask import Flask, request, jsonify

from fipu_face import fipu_face
from exceptions.image_exception import ImageException
import os
from dotenv import load_dotenv
import bugsnag
from bugsnag.flask import handle_exceptions


app = Flask(__name__)
app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max image size

ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg')

IMG_FILE = 'img'
IMG_FILE64 = 'img64'
IMG_FILE_BYTES = 'img_bytes'
IMG_RESPONSE_ENCODING = 'resp_enc'
IMG_FMT = 'img_sizes'

ALLOWED_KEYS = (IMG_FILE, IMG_FILE64, IMG_FILE_BYTES)

load_dotenv()
STAGE = os.environ.get("STAGE", os.environ.get("FLASK_ENV", "development"))
if STAGE != "development" and "BUGSNAG_API_KEY" in os.environ and os.environ.get("BUGSNAG_API_KEY"):
    bugsnag.configure(
        api_key=os.environ.get("BUGSNAG_API_KEY"),
        project_root="",
        app_version="0.0.1",
        release_stage=STAGE,
    )
    handle_exceptions(app)


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


def remap_format(fmt):
    if type(fmt) in [tuple, list]:
        return 'x_{}x{}'.format(*fmt)
    return fmt


# Format should be a dictionary, string, or a list
def get_img_formats():
    val = get_value(IMG_FMT)
    if type(val) is dict:
        for k in val.keys():
            val[k] = remap_format(val[k])

    elif type(val) is str:
        val = {'img': val}
    elif type(val) in [tuple, list]:
        d = dict()
        for i, v in enumerate(val):
            d['img{}'.format(i)] = v
        val = d
    return val or {'img': fipu_face.IMG_FORMAT_X}


def get_img_formats_list():
    fmts = get_img_formats()
    return fmts.values()


def create_response(imgs):
    r_imgs = dict()
    # resp = jsonify({'img': img})

    formats = get_img_formats()
    for k, v in formats.items():
        r_imgs[k] = imgs[v]

    resp = jsonify(r_imgs)
    resp.status_code = 201
    return resp


def handle_file():
    file = request.files[IMG_FILE]
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        imgs = fipu_face.get_from_file(request.files[IMG_FILE], get_img_formats_list(), get_response_encoding())
        return create_response(imgs)
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
        imgs = fipu_face.get_from_base64(file64, get_img_formats_list(), get_response_encoding())
        return create_response(imgs)

    elif is_file_bytes():
        file_bytes = get_value(IMG_FILE_BYTES)
        imgs = fipu_face.get_from_bytes(file_bytes, get_img_formats_list(), get_response_encoding())
        return create_response(imgs)

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


@app.errorhandler(Exception)
def handle_exception(e):
    bugsnag.notify(e)
    errors = dict()
    errors['errors'] = [{'message': 'An error has occurred while processing the image. Please try again in a few moments.', 'error_code': 'server_error'}]
    response = jsonify(errors)

    response.status_code = 500
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="6000")
