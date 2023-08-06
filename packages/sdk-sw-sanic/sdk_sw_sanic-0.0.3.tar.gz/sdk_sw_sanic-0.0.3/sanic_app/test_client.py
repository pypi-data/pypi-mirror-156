import json

import pytest
from sanic import Sanic, response
from http import HTTPStatus
import requests

payload = {
    "id": 10,
    "request_id": "SDT10",
    "is_file_created": True,
    "file_name": "Ayush",
    "created_at": "16-06-2022",
    "request_by": "Ashique",
    "status": False
}

payload_update = {
    "id": 5,
    "request_id": "SDT32",
    "is_file_created": False,
    "file_name": "Ayush",
    "created_at": "16-06-2022",
    "request_by": "Ashique",
    "status": False
}

is_file_created_missing = {
    "id": 6,
    "request_id": "SDT03",
    "file_name": "Ayush",
    "created_at": "16-06-2022",
    "request_by": "Ashique",
    "status": False
}

request_id_missing = {
    "id": 7,
    "is_file_created": True,
    "file_name": "Ayush",
    "created_at": "16-06-2022",
    "request_by": "Ashique",
    "status": False
}

request_by_missing = {
    "id": 5,
    "request_id": "SDT03",
    "is_file_created": True,
    "file_name": "Ayush",
    "created_at": "16-06-2022",
    "status": False
}
status_missing = {
    "id": 5,
    "request_id": "SDT03",
    "is_file_created": True,
    "file_name": "Ayush",
    "created_at": "16-06-2022",
    "request_by": "Ashique"
}

@pytest.fixture
def app():
    sanic_app = Sanic("TestSanic")

    @sanic_app.get("/")
    def basic(request):
        return response.text("foo")

    return sanic_app


def test_basic_test_client(app):
    request, response = app.test_client.get("/")

    assert request.method.lower() == "get"
    assert response.body == b"foo"
    assert response.status == 200


def test_get_all(app):
    """test getting all data"""
    request, response = app.test_client.get("http://127.0.0.1:5823/gets")
    assert response.status == 200

def test_post_data(app):
    """test post data"""
    request, response = app.test_client.post("http://127.0.0.1:5823/gets", data=json.dumps(payload))
    assert response.status == 200

def test_get_by_id(app):
    """test get by id"""
    request, response = app.test_client.get("http://127.0.0.1:5823/get/5")
    assert response.status == 200

def test_update_by_id(app):
    """test getting all data"""
    request, response = app.test_client.put("http://127.0.0.1:5823/get/5", data=json.dumps(payload_update))
    assert response.status == 200


def test_post_is_file_created_missing(app):
    """test post missing by is_file_created_missing"""
    request, response = app.test_client.post("http://127.0.0.1:5823/gets", data=json.dumps(is_file_created_missing))
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_post_request_id_missing(app):
    """test post missing by request_id_missing"""
    request, response = app.test_client.post("http://127.0.0.1:5823/gets", data=json.dumps(request_id_missing))
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_post_request_by_missing(app):
    """test post missing by request_id_missing"""
    request, response = app.test_client.post("http://127.0.0.1:5823/gets", data=json.dumps(request_id_missing))
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_post_status_missing(app):
    """test post missing by status"""
    request, response = app.test_client.post("http://127.0.0.1:5823/gets", data=json.dumps(status_missing))
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_busser_beep(app):
    """test get busser beep"""
    request, response = app.test_client.get("http://127.0.0.1:5823/busser_beep")
    assert response.status == 200

def test_get_media(app):
    """test get media url"""
    request, response = app.test_client.get("http://127.0.0.1:5823/get_media")
    assert response.status == 200


def test_camera_off(app):
    """test camera off"""
    request, response = app.test_client.get("http://127.0.0.1:5823/camera_off")
    assert response.status == 200

# def test_import_c(app):
#     """test import_c to python"""
#     request, response = app.test_client.get("http://127.0.0.1:5823/import_c")
#     assert response.status == 200

def test_derived_key(app):
    """test getting derived_key"""
    request, response = app.test_client.get("http://127.0.0.1:5823/derived_key")
    assert response.status == 200

def test_same_derived_key(app):
    """test getting same_derived_key"""
    request, response = app.test_client.get("http://127.0.0.1:5823/same_derived_key")
    assert response.status == 200