# encoding: utf-8

import pytest
from app.tests.data.data_for_tests_app import *


def test_home_page_positive(client):
    """
    REST Api: Test Home page
    """
    response = client.get('/home')
    assert response.status_code == 200, 'Status code 200 - OK!'
    assert response.text == 'Hello World!'
    print(response.status)


@pytest.mark.parametrize("testdata", [DATA0, DATA1, DATA2, DATA3, DATA5, DATA6, DATA7, DATA8, DATA9, DATA10])
def test_send_message_positive(client, testdata):
    """
    REST Api: Test Send data page
    """
    response = client.post('/send_data', data=testdata, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    assert 'Данный формат отправленного сообщения СООТВЕТСТВУЕТ формату JSON! Сообщение успешно записано!' in response.text
    print(response.status)


def test_read_messages_positive(client):
    """
    REST Api: Test Read data page
    """
    response = client.get('/read_data')
    assert response.status_code == 200 or response.status_code == 204
    if response.status_code == 200:
        assert response.status == '200 OK'
        print(response.status)
    if response.status_code == 204:
        assert response.status == '204 NO CONTENT'
        print(response.status)


def test_metrics(client):
    """
    REST Api: Test Metrics
    """
    response = client.get('/metrics')
    assert response.status_code == 308
    print(response.status)


def test_swagger_ui_spec(client):
    """
    REST Api: Test Swagger UI Spec
    """
    response = client.get('/apidocs/')
    assert response.status_code == 200
    assert b'Flasgger Parsed Method/Function View Example' in response.data
    print(response.status)


def test_home_page_negative(client):
    """
    REST Api: Negative Test Home page
    """
    response = client.post('/home')
    assert response.status_code == 405
    assert 'Method Not Allowed' in response.text
    print(response.status)


@pytest.mark.parametrize("testdata", [DATA0, DATA1, DATA2, DATA3, DATA5, DATA6, DATA7])
def test_send_message_negative(client, testdata):
    """
    REST Api: Negative Test Send data page
    """
    response = client.get('/send_data', data=testdata, headers={"Content-Type": "application/json"})
    assert response.status_code == 405
    assert response.status == '405 METHOD NOT ALLOWED'
    print(response.status)


def test_read_messages_negative(client):
    """
    REST Api: Negative Test Read data page
    """
    response = client.post('/read_data')
    assert response.status_code == 405
    assert response.status == '405 METHOD NOT ALLOWED'
    print(response.status)
