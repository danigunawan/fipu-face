import pytest
from app import face_app
import io
import cv2
import json


# Run the command below to run the tests for face_app.py api
# py.test -p no:warnings


@pytest.fixture
def client():
    face_app.app.config['TESTING'] = True
    with face_app.app.test_client() as client:
        yield client


def read_img(path, fmt='file'):
    if fmt == 'file':
        with io.open(path, 'rb') as f:
            return f.read()
    if fmt == 'base64':
        return face_app.fipu_face.convert_img(cv2.imread(path), face_app.fipu_face.ENCODING_BASE64)
    if fmt == 'bytes':
        return face_app.fipu_face.convert_img(cv2.imread(path), face_app.fipu_face.ENCODING_BYTES)


def get_good_img(fmt):
    return read_img('app/test/good.jpg', fmt)


def get_bad_img(fmt):
    return read_img('app/test/bad.jpg', fmt)


def test_no_img(client):
    resp = client.post('/crop-face')
    assert resp.status_code == 400
    json = resp.get_json()
    assert len(json.keys()) == 1
    assert json is not None
    assert 'message' in json
    assert json['message'] == face_app.NO_IMAGE_ERROR


def test_invalid_format(client):
    def check_response(resp):
        assert resp.status_code == 400
        json = resp.get_json()
        assert json is not None
        assert len(json.keys()) == 2
        assert 'errors' in json
        assert 'img' in json
        assert len(json['errors']) == 1
        assert 'error_code' in json['errors'][0]
        assert json['errors'][0]['error_code'] == face_app.fipu_face.INVALID_IMAGE_FORMAT
        assert json['img'] is None

    data = {face_app.IMG_FMT: face_app.fipu_face.ImgX_300x300,
            face_app.IMG_FILE: (io.BytesIO(b"=="), 'test.jpg')}
    resp = client.post('/crop-face', data=data, content_type='multipart/form-data')
    check_response(resp)

    data = {face_app.IMG_FMT: face_app.fipu_face.ImgX_300x300,
            face_app.IMG_FILE64: "abcdf"}
    resp = client.post('/crop-face', data=data)
    check_response(resp)

    data = {face_app.IMG_FMT: face_app.fipu_face.ImgX_300x300,
            face_app.IMG_FILE_BYTES: b"=="}
    resp = client.post('/crop-face', data=data, content_type='multipart/form-data')
    check_response(resp)


def check_img_response(resp, is_ok):
    if is_ok:
        assert resp.status_code == 201
        json = resp.get_json()
        assert json is not None
        assert len(json.keys()) == 1
        assert 'img' in json
        assert json['img'] is not None
    else:
        assert resp.status_code == 400
        json = resp.get_json()
        assert json is not None
        print(json.keys())
        assert len(json.keys()) == 2
        assert 'img', 'errors' in json
        assert json['img'] is not None
        assert len(json['errors']) > 0


def do_img_upload(client, img_key, good_img, bad_img):
    data = {face_app.IMG_FMT: face_app.fipu_face.IMG_FORMAT_X_300x300,
            img_key: good_img}

    resp = client.post('/crop-face', data=data, content_type='multipart/form-data')
    check_img_response(resp, True)

    data = {face_app.IMG_FMT: face_app.fipu_face.IMG_FORMAT_X_300x300,
            img_key: bad_img}

    resp = client.post('/crop-face', data=data, content_type='multipart/form-data')
    check_img_response(resp, False)


def test_file_upload(client):
    do_img_upload(client,
                  face_app.IMG_FILE,
                  (io.BytesIO(get_good_img('file')), 'good.jpg'),
                  (io.BytesIO(get_bad_img('file')), 'bad.jpg'))


def test_base64_upload(client):
    do_img_upload(client, face_app.IMG_FILE64, get_good_img('base64'), get_bad_img('base64'))


def test_bytes_upload(client):
    do_img_upload(client, face_app.IMG_FILE_BYTES, get_good_img('bytes').decode('iso-8859-1'),
                  get_bad_img('bytes').decode('iso-8859-1'))


def check_multiple_response(resp, formats, is_ok):
    if is_ok:
        assert resp.status_code == 201
        json = resp.get_json()
        assert json is not None
        assert len(json.keys()) == len(formats)
        for k, v in json.items():
            assert v is not None
        if type(formats) in [tuple, list]:
            for i in range(len(formats)):
                assert 'img{}'.format(i) in json
        elif type(formats) is dict:
            for k in formats.keys():
                assert k in json
    else:
        check_img_response(resp, False)


def do_multiple_response_sizes(client, formats):
    data = {face_app.IMG_FMT: formats,
            face_app.IMG_FILE64: get_good_img('base64')}

    resp = client.post('/crop-face', data=json.dumps(data), content_type='application/json')
    check_multiple_response(resp, formats, True)

    data[face_app.IMG_FILE64] = get_bad_img('base64')

    resp = client.post('/crop-face', data=json.dumps(data), content_type='application/json')
    check_multiple_response(resp, formats, False)


def test_multiple_response_sizes(client):
    do_multiple_response_sizes(client,
                               [face_app.fipu_face.IMG_FORMAT_X_300x300, face_app.fipu_face.IMG_FORMAT_X_220x300])
    do_multiple_response_sizes(client, {"big": face_app.fipu_face.IMG_FORMAT_X_300x300,
                                        "small": face_app.fipu_face.IMG_FORMAT_X_220x300})
